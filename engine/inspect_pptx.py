#!/usr/bin/env python3
"""
Inspect a PowerPoint (.pptx) presentation and extract its slide hierarchy,
text blocks, tables, and speaker notes into structured markdown.
"""

import sys
import os
import json
import pptx
from pptx.enum.shapes import MSO_SHAPE_TYPE

def inspect_presentation(pptx_path, format="markdown"):
    if not os.path.exists(pptx_path):
        print(f"Error: File not found: {pptx_path}", file=sys.stderr)
        sys.exit(1)

    prs = pptx.Presentation(pptx_path)
    slides_data = []

    for idx, slide in enumerate(prs.slides, 1):
        layout_name = slide.slide_layout.name if slide.slide_layout else "Unknown"
        title = "Untitled Slide"
        if slide.shapes.title and slide.shapes.title.text.strip():
            title = slide.shapes.title.text.strip()
        
        slide_info = {
            "slide_number": idx,
            "title": title,
            "layout": layout_name,
            "text_blocks": [],
            "tables": [],
            "notes": "",
            "has_images": False,
            "image_count": 0
        }

        # Inspect speaker notes
        if slide.has_notes_slide:
            notes_tf = slide.notes_slide.notes_text_frame
            if notes_tf and notes_tf.text.strip():
                slide_info["notes"] = notes_tf.text.strip()

        # Inspect shapes
        for shape in slide.shapes:
            # Check for images
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                slide_info["has_images"] = True
                slide_info["image_count"] += 1

            # Check for tables
            if shape.has_table:
                table = shape.table
                table_rows = []
                for row in table.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    table_rows.append(row_cells)
                slide_info["tables"].append(table_rows)
                continue

            # Check for text frame
            if shape.has_text_frame:
                # Avoid duplicating the title if this shape is the title shape
                if shape == slide.shapes.title:
                    continue

                tf = shape.text_frame
                block_paragraphs = []
                for p in tf.paragraphs:
                    text = p.text.strip()
                    if text:
                        level = p.level if hasattr(p, "level") else 0
                        block_paragraphs.append({"level": level, "text": text})
                if block_paragraphs:
                    slide_info["text_blocks"].append(block_paragraphs)

        slides_data.append(slide_info)

    if format == "json":
        return json.dumps({"slides": slides_data, "total_slides": len(slides_data)}, indent=2)

    # Markdown format
    lines = []
    lines.append(f"# PowerPoint Deck Inspection: {os.path.basename(pptx_path)}")
    lines.append(f"**Total Slides:** {len(slides_data)}\n")
    lines.append("## Slide Overview")
    lines.append("| Slide | Title | Layout | Notes | Media |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for s in slides_data:
        has_notes = "Yes" if s["notes"] else "No"
        media = f"{s['image_count']} image(s)" if s['image_count'] > 0 else "-"
        # Escape pipe symbols in titles
        safe_title = s['title'].replace('|', '-')
        lines.append(f"| {s['slide_number']} | {safe_title} | {s['layout']} | {has_notes} | {media} |")

    lines.append("\n## Detailed Slide Content\n")

    for s in slides_data:
        lines.append(f"### Slide {s['slide_number']}: {s['title']}")
        lines.append(f"- **Layout:** `{s['layout']}`")
        if s["image_count"] > 0:
            lines.append(f"- **Media:** {s['image_count']} image(s)")
        
        if s["text_blocks"]:
            lines.append("- **Content:**")
            for block in s["text_blocks"]:
                for p in block:
                    indent = "  " * (p["level"] + 1)
                    lines.append(f"{indent}- {p['text']}")

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
        print("Usage: inspect_pptx.py <path-to-deck.pptx> [--json]")
        sys.exit(1)

    pptx_path = sys.argv[1]
    fmt = "json" if "--json" in sys.argv else "markdown"
    print(inspect_presentation(pptx_path, fmt))

if __name__ == "__main__":
    main()
