#!/usr/bin/env python3
"""
Inspect a PowerPoint (.pptx) presentation and extract its slide hierarchy,
text blocks, tables, presenter notes, media assets, and diagram structures.
"""

import sys
import os
import json
import re
import zipfile
import xml.etree.ElementTree as ET
import pptx
from pptx.enum.shapes import MSO_SHAPE_TYPE

import shutil
import subprocess

def run_ocr_on_image(image_path):
    """
    Run tesseract on an image file if tesseract is installed.
    Returns the extracted text, or None if unavailable or on error.
    """
    if not shutil.which("tesseract"):
        return None
    try:
        res = subprocess.run(
            ["tesseract", image_path, "stdout", "--oem", "1", "-l", "eng"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=20,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def extract_media_and_rels(pptx_path, assets_output_dir):
    """
    Extract all embedded media files from the PPTX zip archive and map them to slides.
    """
    os.makedirs(assets_output_dir, exist_ok=True)
    slide_media_map = {}
    extracted_files = {}

    try:
        with zipfile.ZipFile(pptx_path, 'r') as z:
            # 1. Extract all media files
            for name in z.namelist():
                if name.startswith('ppt/media/'):
                    base = os.path.basename(name)
                    if not base:
                        continue
                    out_path = os.path.join(assets_output_dir, base)
                    with open(out_path, 'wb') as f:
                        f.write(z.read(name))
                    extracted_files[base] = out_path

            # 2. Map relationships from slide rels
            for name in z.namelist():
                m = re.match(r'ppt/slides/_rels/slide(\d+)\.xml\.rels', name)
                if m:
                    s_idx = int(m.group(1))
                    if s_idx not in slide_media_map:
                        slide_media_map[s_idx] = []
                    root = ET.fromstring(z.read(name))
                    for child in root:
                        target = child.attrib.get('Target', '')
                        if 'media/' in target:
                            media_base = os.path.basename(target)
                            if media_base not in slide_media_map[s_idx]:
                                slide_media_map[s_idx].append(media_base)
    except Exception as e:
        print(f"Warning: Failed to extract media: {e}", file=sys.stderr)

    return slide_media_map, extracted_files

def extract_shapes_recursive(shape, slide_info):
    """
    Recursively extract text, shapes, connectors, and diagrams from PowerPoint shapes,
    including grouped shapes.
    """
    # Group shape recursion
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        slide_info["diagram_elements"]["groups"] += 1
        for sub_shape in shape.shapes:
            extract_shapes_recursive(sub_shape, slide_info)
        return

    # Image shape
    if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
        slide_info["has_images"] = True
        slide_info["image_count"] += 1
        slide_info["diagram_elements"]["pictures"] += 1

    # Connector or line
    elif shape.shape_type == MSO_SHAPE_TYPE.LINE:
        slide_info["diagram_elements"]["connectors"] += 1

    # Auto shape (rectangles, circles, arrows, callouts)
    elif shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
        slide_info["diagram_elements"]["shapes"] += 1

    # Check for tables
    if shape.has_table:
        table = shape.table
        table_rows = []
        for row in table.rows:
            row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            table_rows.append(row_cells)
        slide_info["tables"].append(table_rows)
        return

    # Check for text frame
    if shape.has_text_frame:
        tf = shape.text_frame
        shape_text = []
        for p in tf.paragraphs:
            text = p.text.strip()
            if text:
                level = p.level if hasattr(p, "level") else 0
                shape_text.append({"level": level, "text": text})
        if shape_text:
            slide_info["text_blocks"].append(shape_text)
            # Record text as a candidate node in diagram elements
            combined_txt = " ".join(t["text"] for t in shape_text)
            slide_info["diagram_elements"]["node_labels"].append(combined_txt)

def is_slide_hidden(slide):
    """Returns True if the slide is marked as hidden in PowerPoint (show='0' or show='false')."""
    show = slide._element.get("show")
    return show is not None and show in ("0", "false")

def inspect_presentation(pptx_path, format="markdown", extract_assets=True, include_hidden=False):
    if not os.path.exists(pptx_path):
        print(f"Error: File not found: {pptx_path}", file=sys.stderr)
        sys.exit(1)

    pptx_dir = os.path.dirname(os.path.abspath(pptx_path))
    # Standard location: deck/assets if in a project directory
    deck_dir = os.path.join(pptx_dir, "deck")
    assets_dir = os.path.join(deck_dir, "assets") if os.path.exists(deck_dir) else os.path.join(pptx_dir, "assets")

    slide_media_map = {}
    extracted_files = {}
    if extract_assets:
        slide_media_map, extracted_files = extract_media_and_rels(pptx_path, assets_dir)

    prs = pptx.Presentation(pptx_path)
    slides_data = []
    hidden_count = 0

    for idx, slide in enumerate(prs.slides, 1):
        if is_slide_hidden(slide):
            hidden_count += 1
            if not include_hidden:
                continue

        layout_name = slide.slide_layout.name if slide.slide_layout else "Unknown"
        title = "Untitled Slide"
        if slide.shapes.title and slide.shapes.title.text.strip():
            title = slide.shapes.title.text.strip()

        slide_media_files = slide_media_map.get(idx, [])

        slide_info = {
            "slide_number": idx,
            "title": title,
            "layout": layout_name,
            "text_blocks": [],
            "tables": [],
            "notes": "",
            "has_images": len(slide_media_files) > 0,
            "image_count": len(slide_media_files),
            "media_files": slide_media_files,
            "diagram_elements": {
                "shapes": 0,
                "connectors": 0,
                "groups": 0,
                "pictures": 0,
                "node_labels": []
            },
            "is_diagram": False,
            "is_flattened_canvas": False,
            "canvas_image": None,
            "ocr_text": ""
        }

        # Inspect speaker notes
        if slide.has_notes_slide:
            notes_tf = slide.notes_slide.notes_text_frame
            if notes_tf and notes_tf.text.strip():
                slide_info["notes"] = notes_tf.text.strip()

        # Check for full-slide canvas picture candidates
        sw = prs.slide_width
        sh = prs.slide_height
        canvas_candidates = []
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                w = getattr(shape, "width", 0)
                h = getattr(shape, "height", 0)
                if sw and sh and (w >= 0.8 * sw and h >= 0.8 * sh):
                    canvas_candidates.append(shape)

        # Inspect shapes recursively
        for shape in slide.shapes:
            # Skip title shape from body blocks if it matches
            if shape == slide.shapes.title:
                continue
            extract_shapes_recursive(shape, slide_info)

        # Detect diagram heuristic:
        # If slide has connectors, or groups, or 3+ distinct shapes with node labels
        de = slide_info["diagram_elements"]
        if de["connectors"] > 0 or de["groups"] > 0 or (de["shapes"] >= 3 and len(de["node_labels"]) >= 3):
            slide_info["is_diagram"] = True

        # Detect flattened canvas slide: full-bleed picture covering slide with no native text/tables
        if canvas_candidates and len(slide_info["text_blocks"]) == 0 and len(slide_info["tables"]) == 0:
            slide_info["is_flattened_canvas"] = True
            if slide_media_files:
                canvas_img = slide_media_files[0]
                slide_info["canvas_image"] = canvas_img
                img_path = extracted_files.get(canvas_img)
                if img_path and os.path.exists(img_path):
                    ocr_res = run_ocr_on_image(img_path)
                    if ocr_res:
                        slide_info["ocr_text"] = ocr_res
                        lines = [line.strip() for line in ocr_res.split("\n") if line.strip()]
                        if slide_info["title"] == "Untitled Slide" and lines:
                            slide_info["title"] = lines[0]
                        # Populate text_blocks from OCR lines
                        ocr_blocks = []
                        for l in lines:
                            ocr_blocks.append([{"level": 0, "text": l}])
                        slide_info["text_blocks"] = ocr_blocks

        slides_data.append(slide_info)

    has_flattened = any(s["is_flattened_canvas"] for s in slides_data)

    if format == "json":
        return json.dumps({
            "slides": slides_data,
            "visible_slides": len(slides_data),
            "hidden_slides_ignored": hidden_count,
            "total_slides": len(prs.slides),
            "is_flattened_deck": has_flattened,
            "extracted_assets": extracted_files
        }, indent=2)

    # Markdown format
    lines = []
    lines.append(f"# PowerPoint Deck Inspection: {os.path.basename(pptx_path)}")
    if hidden_count > 0 and not include_hidden:
        lines.append(f"**Visible Slides:** {len(slides_data)} (ignored {hidden_count} hidden slides | {len(prs.slides)} total in file)")
    else:
        lines.append(f"**Total Slides:** {len(slides_data)}")
    if extracted_files:
        lines.append(f"**Extracted Media Assets:** {len(extracted_files)} files saved to `{os.path.relpath(assets_dir, pptx_dir)}/`")
    lines.append("")

    if has_flattened:
        lines.append("> [!WARNING]")
        lines.append("> **Flattened Presentation Detected (Picture-Only Slides):**")
        lines.append("> Slides in this deck are full-slide raster screenshots with no native text shapes.")
        lines.append("> Text content has been extracted using local OCR (Tesseract).")
        lines.append("> ")
        lines.append("> **Mandatory Reconstruction Rule:**")
        lines.append("> - **PROHIBITED:** Do **NOT** embed these full-slide canvas images (`assets/imageX.png`) into layout sub-frames or cards. Embedding a whole-slide screenshot as a sub-image creates a useless 'thumbnail in a frame' and wastes real estate.")
        lines.append("> - **REQUIRED:** Reconstruct each slide into native semantic components (`cards`, `comparison`, `metrics`, `bullets`) using the OCR text.")
        lines.append("> - **REQUIRED:** Redraw any architectural diagrams as clean SVGs (`diagram.svg` or native architecture components) or high-fidelity vector diagrams.")
        lines.append("")

    lines.append("## Slide Overview")
    lines.append("| Slide | Title | Layout | Canvas? | Diagram? | Media Files | Notes |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for s in slides_data:
        has_notes = "Yes" if s["notes"] else "No"
        media = ", ".join(s["media_files"]) if s["media_files"] else "-"
        diag = "Yes" if s["is_diagram"] else "No"
        canvas = "Yes (OCR)" if s["is_flattened_canvas"] else "No"
        safe_title = s['title'].replace('|', '-')
        lines.append(f"| {s['slide_number']} | {safe_title} | {s['layout']} | {canvas} | {diag} | {media} | {has_notes} |")

    lines.append("\n## Detailed Slide Content\n")

    for s in slides_data:
        lines.append(f"### Slide {s['slide_number']}: {s['title']}")
        lines.append(f"- **Layout:** `{s['layout']}`")
        if s["is_flattened_canvas"]:
            lines.append(f"- **Slide Type:** ⚠️ **Flattened Slide Canvas** (Full-slide bitmap `{s['canvas_image']}`)")
            lines.append(f"  > Reconstruct with native semantic components. Do NOT embed `{s['canvas_image']}` into sub-frames.")
        elif s["media_files"]:
            media_links = [f"`assets/{m}`" for m in s["media_files"]]
            lines.append(f"- **Media Assets:** {', '.join(media_links)}")

        if s["is_diagram"]:
            de = s["diagram_elements"]
            lines.append(f"- **Visual Structure:** **Architecture / Flow Diagram Detected** ({de['shapes']} shapes, {de['connectors']} connectors, {de['groups']} groups)")
            lines.append(f"  > [!IMPORTANT]")
            lines.append(f"  > **Diagram Preservation Mandate:** This slide contains an architectural/flow diagram. In the modernized spec, you MUST preserve or elevate it into a visual diagram (e.g. SVG or architecture component). Do NOT flatten it into plain bullet walls or generic text cards!")
            if de["node_labels"]:
                clean_labels = [re.sub(r'\s+', ' ', l) for l in de["node_labels"] if len(l.strip()) > 1]
                lines.append(f"  - **Diagram Nodes:** {', '.join(clean_labels[:12])}")

        if s["text_blocks"]:
            source_lbl = "OCR Extracted Text Hierarchy" if s["is_flattened_canvas"] else "Extracted Text Hierarchy"
            lines.append(f"- **{source_lbl}:**")
            seen_texts = set()
            for block in s["text_blocks"]:
                for p in block:
                    t = p["text"]
                    if t in seen_texts:
                        continue
                    seen_texts.add(t)
                    indent = "  " * (p["level"] + 1)
                    lines.append(f"{indent}- {t}")

        if s["tables"]:
            lines.append("- **Tables:**")
            for t_idx, tbl in enumerate(s["tables"], 1):
                lines.append(f"  *Table {t_idx}:*")
                if tbl:
                    header = " | ".join(tbl[0])
                    sep = " | ".join(["---"] * len(tbl[0]))
                    lines.append(f"  | {header} |")
                    lines.append(f"  | {sep} |")
                    for row in tbl[1:]:
                        row_str = " | ".join(row)
                        lines.append(f"  | {row_str} |")

        if s["notes"]:
            lines.append(f"- **Presenter Notes:**\n  > {s['notes'].replace(chr(10), chr(10) + '  > ')}")

        lines.append("")

    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: inspect_pptx.py <path-to-deck.pptx> [--json] [--no-extract] [--include-hidden]")
        sys.exit(1)

    pptx_path = sys.argv[1]
    fmt = "json" if "--json" in sys.argv else "markdown"
    extract = "--no-extract" not in sys.argv
    include_hidden = "--include-hidden" in sys.argv
    print(inspect_presentation(pptx_path, fmt, extract, include_hidden=include_hidden))

if __name__ == "__main__":
    main()
