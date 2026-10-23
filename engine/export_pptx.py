#!/usr/bin/env python3
import os
import sys
import yaml
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from style_parser import parse_style

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    return RGBColor(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

def export_to_pptx(spec_path, output_path=None):
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    theme_name = spec.get("theme", "sailpoint-corporate-2026-design")
    style = parse_style(theme_name)

    template_file = style.get("template_file")
    if template_file and not os.path.isabs(template_file) and not os.path.exists(template_file):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        candidate = os.path.join(repo_root, template_file)
        if os.path.exists(candidate):
            template_file = candidate
    use_template = template_file and os.path.exists(template_file)

    slides = spec.get("slides", [])

    if use_template:
        print(f"Using template: {template_file}")
        prs = pptx.Presentation(template_file)
        # Clear existing sample slides
        for i in range(len(prs.slides) - 1, -1, -1):
            rId = prs.slides._sldIdLst[i].rId
            prs.part.drop_rel(rId)
            del prs.slides._sldIdLst[i]

        layout_map = {l.name: l for l in prs.slide_layouts}

        # Resolve preferred layouts
        def get_layout(layout_name):
            name_lower = layout_name.lower()
            if "title slide" in name_lower or "cover" in name_lower:
                return layout_map.get("Title Slide-Motion") or layout_map.get("2_Title Slide") or prs.slide_layouts[0]
            elif "section header" in name_lower:
                return layout_map.get("Section Header Blue") or layout_map.get("Section Header") or prs.slide_layouts[0]
            elif "two content" in name_lower:
                return layout_map.get("Two Content") or prs.slide_layouts[0]
            elif "comparison" in name_lower:
                return layout_map.get("Comparison") or prs.slide_layouts[0]
            elif "three columns" in name_lower:
                return layout_map.get("Three Columns") or prs.slide_layouts[0]
            elif "four tiles" in name_lower:
                return layout_map.get("Four Tiles") or prs.slide_layouts[0]
            elif "title only" in name_lower:
                return layout_map.get("Title Only") or prs.slide_layouts[0]
            elif "blank" in name_lower:
                return layout_map.get("Blank") or prs.slide_layouts[0]
            else:
                return layout_map.get("Title and Content - Dark mode") or layout_map.get("Title and Content") or prs.slide_layouts[0]

        for s in slides:
            layout_spec = s.get("layout", "Title and Content")
            slide_layout = get_layout(layout_spec)
            slide = prs.slides.add_slide(slide_layout)

            stitle = s.get("title", "")
            subtitle = s.get("subtitle", "")
            content = s.get("content", {})
            notes = s.get("notes", "")

            # Set title
            if slide.shapes.title:
                slide.shapes.title.text = stitle

            # Handle placeholders by layout type
            layout_name_lower = slide_layout.name.lower()

            if "title slide" in layout_name_lower:
                for ph in slide.placeholders:
                    if ph.placeholder_format.idx == 1 and subtitle:
                        ph.text = subtitle
                    elif ph.placeholder_format.idx == 2 and content.get("body"):
                        ph.text = content.get("body")

            elif "section header" in layout_name_lower:
                for ph in slide.placeholders:
                    if ph.placeholder_format.idx == 1 and subtitle:
                        ph.text = subtitle

            elif "two content" in layout_name_lower:
                regions = content.get("regions", [])
                left_bullets = regions[0].get("bullets", []) if len(regions) > 0 else []
                right_bullets = regions[1].get("bullets", []) if len(regions) > 1 else []
                for ph in slide.placeholders:
                    if ph.placeholder_format.idx == 1:
                        tf = ph.text_frame
                        tf.clear()
                        for b in left_bullets:
                            p = tf.add_paragraph()
                            p.text = b
                            p.level = 0
                    elif ph.placeholder_format.idx == 13 or ph.placeholder_format.idx == 2:
                        tf = ph.text_frame
                        tf.clear()
                        for b in right_bullets:
                            p = tf.add_paragraph()
                            p.text = b
                            p.level = 0

            elif "comparison" in layout_name_lower:
                comp = content.get("comparison", {})
                left = comp.get("left", {})
                right = comp.get("right", {})
                for ph in slide.placeholders:
                    idx = ph.placeholder_format.idx
                    if idx == 1:
                        ph.text = left.get("title", "Before")
                    elif idx == 2:
                        tf = ph.text_frame
                        tf.clear()
                        for b in left.get("bullets", []):
                            p = tf.add_paragraph()
                            p.text = b
                    elif idx == 3:
                        ph.text = right.get("title", "After")
                    elif idx == 4:
                        tf = ph.text_frame
                        tf.clear()
                        for b in right.get("bullets", []):
                            p = tf.add_paragraph()
                            p.text = b

            else:
                # Standard Title and Content
                bullets = content.get("bullets", [])
                cards = content.get("cards", [])
                metrics = content.get("metrics", [])
                body = content.get("body", "")

                for ph in slide.placeholders:
                    if ph.placeholder_format.idx == 1:
                        tf = ph.text_frame
                        tf.clear()
                        if bullets:
                            for b in bullets:
                                p = tf.add_paragraph()
                                p.text = b
                                p.level = 0
                        elif cards:
                            for c in cards:
                                p = tf.add_paragraph()
                                p.text = f"{c.get('title')}: {c.get('body')}"
                                p.level = 0
                        elif metrics:
                            for m in metrics:
                                p = tf.add_paragraph()
                                p.text = f"{m.get('value')} - {m.get('label')} ({m.get('subtext', '')})"
                                p.level = 0
                        elif body:
                            p = tf.add_paragraph()
                            p.text = body

            # Image / Picture Embedding
            slide_image = content.get("image") or s.get("image")
            img_rel = None
            if isinstance(slide_image, dict):
                img_rel = slide_image.get("src")
            elif isinstance(slide_image, str):
                img_rel = slide_image
            
            if not img_rel:
                media_list = content.get("media", [])
                if media_list and isinstance(media_list, list) and len(media_list) > 0:
                    img_rel = media_list[0].get("source") or media_list[0].get("src")
            
            if img_rel:
                spec_dir = os.path.dirname(os.path.abspath(spec_path))
                img_path = os.path.join(spec_dir, img_rel) if not os.path.isabs(img_rel) else img_rel
                if os.path.exists(img_path):
                    try:
                        # Place picture on right side
                        slide.shapes.add_picture(img_path, Inches(7.5), Inches(2.2), width=Inches(5.0))
                    except Exception as e:
                        print(f"Warning: could not add image {img_path}: {e}")

            if notes:
                slide.notes_slide.notes_text_frame.text = notes

    else:
        # Fallback programmatic presentation
        print("Building programmatic PowerPoint presentation...")
        prs = pptx.Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        blank_layout = prs.slide_layouts[6] # blank

        colors = style.get("colors", {})
        bg_rgb = hex_to_rgb(colors.get("background", "#000000"))
        ink_rgb = hex_to_rgb(colors.get("ink", "#FFFFFF"))
        accent_rgb = hex_to_rgb(colors.get("accent", "#54C0E8"))
        muted_rgb = hex_to_rgb(colors.get("ink-muted", "#DAE1E9"))

        for s in slides:
            slide = prs.slides.add_slide(blank_layout)

            # Background fill
            bg = slide.background
            fill = bg.fill
            fill.solid()
            fill.fore_color.rgb = bg_rgb

            stitle = s.get("title", "")
            subtitle = s.get("subtitle", "")
            content = s.get("content", {})
            notes = s.get("notes", "")

            # Title Box
            title_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(1.2))
            tf = title_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = stitle
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = ink_rgb

            if subtitle:
                p2 = tf.add_paragraph()
                p2.text = subtitle
                p2.font.size = Pt(18)
                p2.font.color.rgb = muted_rgb

            # Content Box
            content_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(11.333), Inches(4.5))
            ctf = content_box.text_frame
            ctf.word_wrap = True

            bullets = content.get("bullets", [])
            body = content.get("body", "")
            if bullets:
                for b in bullets:
                    bp = ctf.add_paragraph()
                    bp.text = f"•  {b}"
                    bp.font.size = Pt(20)
                    bp.font.color.rgb = muted_rgb
            elif body:
                bp = ctf.add_paragraph()
                bp.text = body
                bp.font.size = Pt(20)
                bp.font.color.rgb = muted_rgb

            if notes:
                slide.notes_slide.notes_text_frame.text = notes

    if not output_path:
        spec_dir = os.path.dirname(os.path.abspath(spec_path))
        output_path = os.path.join(spec_dir, "deck.pptx")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    prs.save(output_path)
    print(f"PowerPoint deck generated: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_pptx.py <spec_file.yaml> [output_deck.pptx]")
        sys.exit(1)
    spec_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    export_to_pptx(spec_arg, out_arg)
