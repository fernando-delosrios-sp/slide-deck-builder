#!/usr/bin/env python3
"""
PowerPoint (.pptx) Exporter for Slide Deck Builder.

Exports Reveal.js presentations into 16:9 widescreen PowerPoint decks (.pptx)
built from scratch. By default, generates native editable PowerPoint objects
(text boxes, rounded rectangle cards, metric blocks, tables) with high-DPI
diagrams and screenshots placed as isolated editable picture shapes.
Supports a fallback '--mode flat' for full-bleed rasterized screenshots.
"""

import os
import re
import sys
import yaml
import shutil
import tempfile
import argparse
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Ensure engine path is available for style_parser
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from style_parser import parse_style, hex_to_rgb


def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
    ]
    for c in candidates:
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def hex_to_pptx_rgb(hex_code, fallback=(255, 255, 255)):
    if not hex_code:
        return RGBColor(*fallback)
    rgb = hex_to_rgb(hex_code)
    return RGBColor(*rgb)


def extract_primary_font(font_str, fallback="Poppins"):
    if not font_str or not isinstance(font_str, str):
        return fallback
    # Clean quotes and splits
    cleaned = font_str.replace("'", "").replace('"', '').split(",")[0].strip()
    return cleaned if cleaned else fallback


def render_svg_to_png(svg_str, chrome_path, width_px=1400, height_px=700):
    tmp_dir = tempfile.mkdtemp()
    html_path = os.path.join(tmp_dir, "render.html")
    png_path = os.path.join(tmp_dir, "render.png")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; overflow: hidden; width: {width_px}px; height: {height_px}px; display: flex; align-items: center; justify-content: center; }}
  svg {{ width: 100%; height: 100%; }}
</style>
</head>
<body>
{svg_str}
</body>
</html>""")

    cmd = [
        chrome_path,
        "--headless=new",
        f"--screenshot={png_path}",
        f"--window-size={width_px},{height_px}",
        f"file://{html_path}"
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0 and os.path.exists(png_path):
        return png_path, tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return None, None


def export_editable_pptx(spec_data, spec_dir, output_path):
    """
    Builds a 16:9 widescreen PowerPoint presentation from semantic spec.yaml
    with real editable text frames, rounded rectangle card shapes, and isolated
    diagram/screenshot picture shapes.
    """
    theme_name = spec_data.get("theme", "sailpoint-corporate-2026-design")
    style = parse_style(theme_name)
    colors = style.get("colors", {})
    typography = style.get("typography", {})

    font_name = extract_primary_font(typography.get("font-family"), "Poppins")
    bg_rgb = hex_to_pptx_rgb(colors.get("background", "#070C16"))
    card_bg_rgb = hex_to_pptx_rgb(colors.get("card-background", "#0B111E"))
    card_border_rgb = hex_to_pptx_rgb(colors.get("card-border", "#415364"))
    accent_rgb = hex_to_pptx_rgb(colors.get("accent", "#54C0E8"))
    accent_alt_rgb = hex_to_pptx_rgb(colors.get("accent-alt", "#D60EB5"))
    ink_rgb = hex_to_pptx_rgb(colors.get("ink", "#FFFFFF"))
    ink_muted_rgb = hex_to_pptx_rgb(colors.get("ink-muted", "#DAE1E9"))

    prs = Presentation()
    prs.slide_width = Inches(13.333333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    chrome_path = find_chrome()
    temp_dirs_to_clean = []

    def set_slide_background(slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0), prs.slide_width, prs.slide_height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = bg_rgb
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, s):
        badge_text = s.get("badge", "")
        if badge_text:
            tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.733), Inches(0.35))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = badge_text.upper()
            p.font.name = font_name
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = accent_rgb

        title_top = Inches(0.75) if badge_text else Inches(0.55)
        tb_title = slide.shapes.add_textbox(Inches(0.8), title_top, Inches(11.733), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = s.get("title", "")
        p_title.font.name = font_name
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = ink_rgb

        sub_text = s.get("subtitle", "")
        if sub_text:
            sub_top = title_top + Inches(0.55)
            tb_sub = slide.shapes.add_textbox(Inches(0.8), sub_top, Inches(11.733), Inches(0.4))
            tf_sub = tb_sub.text_frame
            tf_sub.word_wrap = True
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = sub_text
            p_sub.font.name = font_name
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = ink_muted_rgb

    for s in spec_data.get("slides", []):
        slide = prs.slides.add_slide(blank_layout)
        set_slide_background(slide)

        # Speaker notes
        notes = s.get("notes", "")
        if notes:
            slide.notes_slide.notes_text_frame.text = notes

        layout = s.get("layout", "")
        role = s.get("role", "")
        content = s.get("content", {}) or {}

        # 1. Cover Slide
        if role == "cover" or layout == "Title Slide":
            tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(6.0), Inches(5.2))
            tf = tb.text_frame
            tf.word_wrap = True

            if s.get("badge"):
                p_b = tf.paragraphs[0]
                p_b.text = s["badge"].upper()
                p_b.font.name = font_name
                p_b.font.size = Pt(11)
                p_b.font.bold = True
                p_b.font.color.rgb = accent_rgb
                p_b.space_after = Pt(14)
                p_t = tf.add_paragraph()
            else:
                p_t = tf.paragraphs[0]

            p_t.text = s.get("title", "")
            p_t.font.name = font_name
            p_t.font.size = Pt(36)
            p_t.font.bold = True
            p_t.font.color.rgb = ink_rgb
            p_t.space_after = Pt(8)

            if s.get("subtitle"):
                p_s = tf.add_paragraph()
                p_s.text = s["subtitle"]
                p_s.font.name = font_name
                p_s.font.size = Pt(18)
                p_s.font.color.rgb = accent_rgb
                p_s.space_after = Pt(18)

            if content.get("body"):
                p_body = tf.add_paragraph()
                p_body.text = content["body"]
                p_body.font.name = font_name
                p_body.font.size = Pt(13)
                p_body.font.color.rgb = ink_muted_rgb
                p_body.space_after = Pt(24)

            meta_items = []
            if content.get("presenter"):
                meta_items.append(content["presenter"])
            if content.get("date"):
                meta_items.append(str(content["date"]))
            if meta_items:
                p_meta = tf.add_paragraph()
                p_meta.text = " • ".join(meta_items)
                p_meta.font.name = font_name
                p_meta.font.size = Pt(11)
                p_meta.font.color.rgb = accent_rgb

            img_info = content.get("image", {})
            img_rel = img_info.get("src") if isinstance(img_info, dict) else None
            if img_rel:
                img_path = os.path.join(spec_dir, img_rel)
                if os.path.exists(img_path):
                    slide.shapes.add_picture(img_path, Inches(7.5), Inches(1.3), width=Inches(4.8), height=Inches(4.8))
            continue

        # Standard Slide Header
        add_header(slide, s)
        content_top = Inches(1.85)

        # 2. Diagram / SVG
        svg_content = None
        if "diagram" in content and isinstance(content["diagram"], dict):
            svg_content = content["diagram"].get("svg")
        elif "svg" in content and isinstance(content["svg"], str):
            svg_content = content["svg"]

        if svg_content and chrome_path:
            png_p, tmp_d = render_svg_to_png(svg_content, chrome_path)
            if png_p and os.path.exists(png_p):
                temp_dirs_to_clean.append(tmp_d)
                slide.shapes.add_picture(png_p, Inches(0.8), content_top, width=Inches(11.733), height=Inches(5.1))
                continue

        # 3. Cards (Four Tiles or Multi-Column)
        if "cards" in content and isinstance(content["cards"], list):
            cards = content["cards"]
            n = len(cards)
            if n == 4 and layout == "Four Tiles":
                c_w = Inches(5.7)
                c_h = Inches(2.35)
                gap_x = Inches(0.33)
                gap_y = Inches(0.25)
                for idx, c in enumerate(cards):
                    row = idx // 2
                    col = idx % 2
                    x = Inches(0.8) + col * (c_w + gap_x)
                    y = content_top + row * (c_h + gap_y)

                    c_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, c_w, c_h)
                    c_shape.fill.solid()
                    c_shape.fill.fore_color.rgb = card_bg_rgb
                    is_hi = c.get("highlight", False)
                    c_shape.line.color.rgb = accent_alt_rgb if is_hi else card_border_rgb
                    c_shape.line.width = Pt(1.5 if is_hi else 1.0)

                    tf = c_shape.text_frame
                    tf.word_wrap = True
                    tf.margin_left = Inches(0.25)
                    tf.margin_right = Inches(0.25)
                    tf.margin_top = Inches(0.2)
                    tf.margin_bottom = Inches(0.2)

                    p_first = tf.paragraphs[0]
                    if c.get("badge"):
                        p_first.text = c["badge"].upper()
                        p_first.font.name = font_name
                        p_first.font.size = Pt(9)
                        p_first.font.bold = True
                        p_first.font.color.rgb = accent_rgb
                        p_first.space_after = Pt(4)
                        p_title = tf.add_paragraph()
                    else:
                        p_title = p_first

                    p_title.text = c.get("title", "")
                    p_title.font.name = font_name
                    p_title.font.size = Pt(14)
                    p_title.font.bold = True
                    p_title.font.color.rgb = ink_rgb
                    p_title.space_after = Pt(6)

                    if c.get("body"):
                        p_body = tf.add_paragraph()
                        p_body.text = c["body"]
                        p_body.font.name = font_name
                        p_body.font.size = Pt(11)
                        p_body.font.color.rgb = ink_muted_rgb
            else:
                gap = Inches(0.35)
                avail_w = Inches(11.733)
                c_w = (avail_w - gap * (n - 1)) / max(n, 1)
                c_h = Inches(4.9)
                for idx, c in enumerate(cards):
                    x = Inches(0.8) + idx * (c_w + gap)
                    y = content_top

                    c_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, c_w, c_h)
                    c_shape.fill.solid()
                    c_shape.fill.fore_color.rgb = card_bg_rgb
                    is_hi = c.get("highlight", False)
                    c_shape.line.color.rgb = accent_alt_rgb if is_hi else card_border_rgb
                    c_shape.line.width = Pt(1.5 if is_hi else 1.0)

                    tf = c_shape.text_frame
                    tf.word_wrap = True
                    tf.margin_left = Inches(0.25)
                    tf.margin_right = Inches(0.25)
                    tf.margin_top = Inches(0.25)
                    tf.margin_bottom = Inches(0.25)

                    p_first = tf.paragraphs[0]
                    if c.get("badge"):
                        p_first.text = c["badge"].upper()
                        p_first.font.name = font_name
                        p_first.font.size = Pt(10)
                        p_first.font.bold = True
                        p_first.font.color.rgb = accent_rgb
                        p_first.space_after = Pt(8)
                        p_title = tf.add_paragraph()
                    else:
                        p_title = p_first

                    p_title.text = c.get("title", "")
                    p_title.font.name = font_name
                    p_title.font.size = Pt(15)
                    p_title.font.bold = True
                    p_title.font.color.rgb = ink_rgb
                    p_title.space_after = Pt(10)

                    if c.get("body"):
                        p_body = tf.add_paragraph()
                        p_body.text = c["body"]
                        p_body.font.name = font_name
                        p_body.font.size = Pt(11.5)
                        p_body.font.color.rgb = ink_muted_rgb

                    if c.get("bullets"):
                        for b in c["bullets"]:
                            p_b = tf.add_paragraph()
                            p_b.text = f"• {b}"
                            p_b.font.name = font_name
                            p_b.font.size = Pt(11)
                            p_b.font.color.rgb = ink_muted_rgb
                            p_b.space_after = Pt(4)
            continue

        # 4. Walkthrough / Picture with Caption
        if "image" in content and isinstance(content["image"], dict):
            img_rel = content["image"].get("src")
            img_path = os.path.join(spec_dir, img_rel) if img_rel else None

            if img_path and os.path.exists(img_path):
                slide.shapes.add_picture(img_path, Inches(0.8), content_top, width=Inches(7.8), height=Inches(4.9))

            cap_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.9), content_top, Inches(3.633), Inches(4.9))
            cap_shape.fill.solid()
            cap_shape.fill.fore_color.rgb = card_bg_rgb
            cap_shape.line.color.rgb = card_border_rgb
            cap_shape.line.width = Pt(1.0)

            tf = cap_shape.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.25)
            tf.margin_right = Inches(0.25)
            tf.margin_top = Inches(0.25)
            tf.margin_bottom = Inches(0.25)

            p_cap = tf.paragraphs[0]
            p_cap.text = content["image"].get("caption", "Console Walkthrough")
            p_cap.font.name = font_name
            p_cap.font.size = Pt(13)
            p_cap.font.bold = True
            p_cap.font.color.rgb = accent_rgb
            p_cap.space_after = Pt(12)

            if content.get("body"):
                p_body = tf.add_paragraph()
                p_body.text = content["body"]
                p_body.font.name = font_name
                p_body.font.size = Pt(12)
                p_body.font.color.rgb = ink_muted_rgb
                p_body.space_after = Pt(10)
            continue

        # 5. Bullets
        if "bullets" in content and isinstance(content["bullets"], list):
            b_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), content_top, Inches(11.733), Inches(4.9))
            b_shape.fill.solid()
            b_shape.fill.fore_color.rgb = card_bg_rgb
            b_shape.line.color.rgb = card_border_rgb
            b_shape.line.width = Pt(1.0)

            tf = b_shape.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.4)
            tf.margin_right = Inches(0.4)
            tf.margin_top = Inches(0.4)
            tf.margin_bottom = Inches(0.4)

            for idx, b in enumerate(content["bullets"]):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.text = f"•  {b}"
                p.font.name = font_name
                p.font.size = Pt(14)
                p.font.color.rgb = ink_muted_rgb
                p.space_after = Pt(14)
            continue

        # 6. Metrics
        if "metrics" in content and isinstance(content["metrics"], list):
            metrics = content["metrics"]
            n = len(metrics)
            gap = Inches(0.35)
            avail_w = Inches(11.733)
            c_w = (avail_w - gap * (n - 1)) / max(n, 1)
            c_h = Inches(4.9)
            for idx, m in enumerate(metrics):
                x = Inches(0.8) + idx * (c_w + gap)
                y = content_top

                m_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, c_w, c_h)
                m_shape.fill.solid()
                m_shape.fill.fore_color.rgb = card_bg_rgb
                is_hi = m.get("highlight", False)
                m_shape.line.color.rgb = accent_alt_rgb if is_hi else card_border_rgb
                m_shape.line.width = Pt(1.5 if is_hi else 1.0)

                tf = m_shape.text_frame
                tf.word_wrap = True
                tf.margin_left = Inches(0.2)
                tf.margin_right = Inches(0.2)
                tf.margin_top = Inches(0.4)
                tf.margin_bottom = Inches(0.2)

                p_val = tf.paragraphs[0]
                p_val.text = str(m.get("value", ""))
                p_val.font.name = font_name
                p_val.font.size = Pt(36)
                p_val.font.bold = True
                p_val.font.color.rgb = accent_alt_rgb if is_hi else accent_rgb
                p_val.space_after = Pt(12)

                p_lbl = tf.add_paragraph()
                p_lbl.text = str(m.get("label", ""))
                p_lbl.font.name = font_name
                p_lbl.font.size = Pt(15)
                p_lbl.font.bold = True
                p_lbl.font.color.rgb = ink_rgb
                p_lbl.space_after = Pt(8)

                if m.get("subtext"):
                    p_sub = tf.add_paragraph()
                    p_sub.text = str(m["subtext"])
                    p_sub.font.name = font_name
                    p_sub.font.size = Pt(11)
                    p_sub.font.color.rgb = ink_muted_rgb
            continue

        # 7. Comparison Table
        if "comparison" in content and isinstance(content["comparison"], dict):
            comp = content["comparison"]
            headers = comp.get("headers", ["Feature", "Current", "Target"])
            rows = comp.get("rows", [])
            if rows:
                num_rows = len(rows) + 1
                num_cols = len(headers)
                tbl_shape = slide.shapes.add_table(num_rows, num_cols, Inches(0.8), content_top, Inches(11.733), Inches(4.9))
                tbl = tbl_shape.table

                for c_i, h in enumerate(headers):
                    cell = tbl.cell(0, c_i)
                    cell.text = str(h)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = card_bg_rgb
                    for p in cell.text_frame.paragraphs:
                        p.font.name = font_name
                        p.font.size = Pt(13)
                        p.font.bold = True
                        p.font.color.rgb = accent_rgb

                for r_i, row_data in enumerate(rows):
                    row_vals = row_data if isinstance(row_data, list) else list(row_data.values())
                    for c_i, val in enumerate(row_vals[:num_cols]):
                        cell = tbl.cell(r_i + 1, c_i)
                        cell.text = str(val)
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = card_bg_rgb
                        for p in cell.text_frame.paragraphs:
                            p.font.name = font_name
                            p.font.size = Pt(11)
                            p.font.color.rgb = ink_muted_rgb
                continue

        # Fallback for plain body text
        if content.get("body"):
            body_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), content_top, Inches(11.733), Inches(4.9))
            body_shape.fill.solid()
            body_shape.fill.fore_color.rgb = card_bg_rgb
            body_shape.line.color.rgb = card_border_rgb
            body_shape.line.width = Pt(1.0)
            tf = body_shape.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = content["body"]
            p.font.name = font_name
            p.font.size = Pt(14)
            p.font.color.rgb = ink_muted_rgb

    prs.save(output_path)
    for td in temp_dirs_to_clean:
        shutil.rmtree(td, ignore_errors=True)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\nPowerPoint deck successfully generated: {output_path} ({len(prs.slides)} editable slides, {file_size_mb:.1f} MB)")
    return output_path


def export_flat_pptx(html_path, output_path, slides_notes=None):
    """
    Fallback flat screenshot exporter using decktape.
    """
    slides_notes = slides_notes or []
    chrome_path = find_chrome()
    file_url = f"file://{html_path}"
    print(f"Exporting flat PowerPoint screenshots from {html_path}...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_pdf = os.path.join(tmp_dir, "slide.pdf")
        cmd = [
            "npx", "--yes", "decktape", "reveal",
            "-s", "1920x1080",
            "--screenshots",
            "--screenshots-directory", tmp_dir,
            "--screenshots-format", "png",
            "--load-pause", "1000",
            "--pause", "500",
            file_url,
            tmp_pdf
        ]
        if chrome_path:
            cmd.extend(["--chrome-path", chrome_path])

        result = subprocess.run(cmd)
        if result.returncode != 0:
            print("Error: decktape failed to capture presentation slides.")
            sys.exit(result.returncode)

        screenshot_files = []
        pattern = re.compile(r"slide_(\d+)_\d+x\d+\.png")
        for fname in os.listdir(tmp_dir):
            match = pattern.match(fname)
            if match:
                index = int(match.group(1))
                screenshot_files.append((index, os.path.join(tmp_dir, fname)))

        screenshot_files.sort(key=lambda x: x[0])
        if not screenshot_files:
            print("Error: No slide screenshots were generated by decktape.")
            sys.exit(1)

        prs = Presentation()
        prs.slide_width = Inches(13.333333)
        prs.slide_height = Inches(7.5)
        blank_layout = prs.slide_layouts[6]

        for idx, (_, img_path) in enumerate(screenshot_files):
            slide = prs.slides.add_slide(blank_layout)
            slide.shapes.add_picture(
                img_path,
                Inches(0),
                Inches(0),
                width=prs.slide_width,
                height=prs.slide_height
            )

            note_text = slides_notes[idx] if idx < len(slides_notes) else ""
            if note_text:
                slide.notes_slide.notes_text_frame.text = note_text

        prs.save(output_path)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\nPowerPoint deck successfully generated: {output_path} ({len(screenshot_files)} flat slides, {file_size_mb:.1f} MB)")
    return output_path


def export_to_pptx(input_path, output_path=None, mode="editable"):
    """
    Exports a presentation to a 16:9 widescreen PowerPoint deck (.pptx).
    Accepts either a spec.yaml or a compiled deck.html.
    Defaults to mode='editable' (native shapes & text) with fallback to mode='flat'.
    """
    input_path = os.path.abspath(input_path)
    spec_data = None
    spec_dir = None
    spec_path = None

    if input_path.endswith(".yaml") or input_path.endswith(".yml"):
        spec_path = input_path
        spec_dir = os.path.dirname(spec_path)
        html_path = os.path.join(spec_dir, "deck.html")
        if not output_path:
            output_path = os.path.join(spec_dir, "deck.pptx")
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                spec_data = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not read spec file: {e}")
    else:
        html_path = input_path
        spec_dir = os.path.dirname(html_path)
        potential_spec = os.path.join(spec_dir, "spec.yaml")
        if os.path.exists(potential_spec):
            spec_path = potential_spec
            try:
                with open(potential_spec, "r", encoding="utf-8") as f:
                    spec_data = yaml.safe_load(f)
            except Exception:
                pass
        if not output_path:
            output_path = os.path.splitext(html_path)[0] + ".pptx"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Use editable mode whenever spec_data is available and mode != 'flat'
    if mode != "flat" and spec_data and isinstance(spec_data.get("slides"), list):
        print(f"Exporting editable native PowerPoint deck from spec ({len(spec_data['slides'])} slides)...")
        return export_editable_pptx(spec_data, spec_dir, output_path)

    # Fallback to flat decktape screenshot mode
    if not os.path.exists(html_path):
        if spec_path and os.path.exists(spec_path):
            print(f"deck.html not found at {html_path}. Compiling from spec...")
            builder_py = os.path.join(ENGINE_DIR, "builder.py")
            subprocess.run([sys.executable, builder_py, spec_path, html_path], check=True)
        else:
            print(f"Error: HTML presentation not found: {html_path}")
            sys.exit(1)

    slides_notes = []
    if spec_data and isinstance(spec_data.get("slides"), list):
        for s in spec_data["slides"]:
            slides_notes.append(s.get("notes", "") or "")

    return export_flat_pptx(html_path, output_path, slides_notes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export presentation to 16:9 PowerPoint deck (.pptx)")
    parser.add_argument("input_path", help="Path to spec.yaml or deck.html")
    parser.add_argument("output_path", nargs="?", default=None, help="Output .pptx file path")
    parser.add_argument("--mode", choices=["editable", "flat"], default="editable", help="Export mode: 'editable' (native shapes/text, default) or 'flat' (screenshots)")
    parser.add_argument("--flat", action="store_true", help="Alias for --mode flat")

    args = parser.parse_args()
    chosen_mode = "flat" if args.flat else args.mode
    export_to_pptx(args.input_path, args.output_path, mode=chosen_mode)
