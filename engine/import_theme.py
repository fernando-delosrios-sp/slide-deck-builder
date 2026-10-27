#!/usr/bin/env python3
"""
Theme Importer & Contrast Validator for Slide Deck Builder.

Imports DESIGN.md files from URLs (e.g. getdesign.md, GitHub, or direct links)
or local markdown files, validates WCAG contrast ratios, synthesizes presentation
tokens, and saves them into styles/ for instant deck compilation.

Usage:
  ./venv/bin/python engine/import_theme.py <url-or-file> [--name <name>] [--preview]
"""

import os
import re
import sys
import yaml
import argparse
import urllib.request
import urllib.error
from style_parser import (
    parse_style,
    extract_fm_and_body,
    safe_load_yaml_frontmatter,
    normalize_colors,
    synthesize_typography,
    contrast_ratio,
    relative_luminance,
    hex_to_rgb,
    hex_with_alpha
)

def fetch_source(source_url_or_path):
    """Fetches raw markdown content from URL or local file."""
    if source_url_or_path.startswith("http://") or source_url_or_path.startswith("https://"):
        url = source_url_or_path
        # If user gave getdesign.md link like https://getdesign.md/linear/design-md,
        # check if it can be mapped or fetched
        headers = {"User-Agent": "Mozilla/5.0 (SlideDeckBuilder/2.0; +https://antigravity.ai)"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                raw_bytes = resp.read()
                content = raw_bytes.decode("utf-8", errors="replace")
                
                # If page returned HTML (e.g. from getdesign.md web page instead of raw markdown),
                # try to extract markdown inside code blocks or pre tags if present
                if "<html" in content.lower() and "```" in content:
                    code_match = re.search(r"```(?:markdown|yaml)?\n(.*?)\n```", content, re.DOTALL)
                    if code_match:
                        content = code_match.group(1)
                return content
        except urllib.error.URLError as e:
            sys.exit(f"Error fetching URL '{url}': {e}")
    else:
        path = os.path.abspath(source_url_or_path)
        if not os.path.exists(path):
            sys.exit(f"Error: Local file '{path}' not found.")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)

def run_contrast_audit(colors, mode="dark"):
    """Audits color contrast ratios against WCAG 2.1 AA/AAA standards."""
    bg = colors.get("background", "#000000")
    surface = colors.get("surface", "#0B111E")
    card_bg = colors.get("card-background", surface)
    ink = colors.get("ink", "#FFFFFF")
    ink_muted = colors.get("ink-muted", "#DAE1E9")
    accent = colors.get("accent", "#54C0E8")

    cr_text_bg = contrast_ratio(ink, bg)
    cr_muted_bg = contrast_ratio(ink_muted, bg)
    cr_text_card = contrast_ratio(ink, card_bg)
    cr_accent_bg = contrast_ratio(accent, bg)

    def grade(ratio, threshold_aa=4.5, threshold_aaa=7.0):
        if ratio >= threshold_aaa:
            return f"{ratio:.1f}:1 [AAA Pass]"
        elif ratio >= threshold_aa:
            return f"{ratio:.1f}:1 [AA Pass]"
        else:
            return f"{ratio:.1f}:1 [FAIL - < {threshold_aa}:1]"

    audit = {
        "text_on_canvas": (ink, bg, grade(cr_text_bg, 4.5, 7.0)),
        "muted_on_canvas": (ink_muted, bg, grade(cr_muted_bg, 3.0, 4.5)),
        "text_on_card": (ink, card_bg, grade(cr_text_card, 4.5, 7.0)),
        "accent_on_canvas": (accent, bg, grade(cr_accent_bg, 3.0, 4.5))
    }
    return audit

def import_theme(source, name=None, output_path=None, preview=False):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    styles_dir = os.path.join(repo_root, "styles")
    os.makedirs(styles_dir, exist_ok=True)

    print(f"\n🎨 Fetching theme specification from: {source}")
    content = fetch_source(source)

    fm_raw, body = extract_fm_and_body(content)
    raw_data = safe_load_yaml_frontmatter(fm_raw) if fm_raw else {}

    # Determine theme name
    theme_title = raw_data.get("name") or (os.path.basename(source).replace(".md", "") if not source.startswith("http") else "imported-theme")
    theme_slug = name or slugify(theme_title)
    if not theme_slug.endswith("-design"):
        theme_slug_full = f"{theme_slug}-design"
    else:
        theme_slug_full = theme_slug

    target_file = output_path or os.path.join(styles_dir, f"{theme_slug_full}.md")

    # Determine mode & normalize colors
    raw_colors = raw_data.get("colors", {})
    bg_candidate = raw_colors.get("background") or raw_colors.get("canvas") or raw_colors.get("bg") or "#000000"
    lum = relative_luminance(hex_to_rgb(bg_candidate))
    mode = raw_data.get("mode") or ("light" if lum > 0.35 else "dark")

    colors = normalize_colors(raw_colors, mode=mode)
    typography = synthesize_typography(raw_data.get("typography", {}), mode=mode)

    # Presentation tokens
    accent_color = colors["accent"]
    accent_alt = colors["accent-alt"]
    bg_color = colors["background"]
    surface_color = colors["surface"]
    card_bg = colors["card-background"]

    css_vars = dict(raw_data.get("css_variables", {}))
    if "--deck-bg-gradient" not in css_vars and "--theme-bg-gradient" not in css_vars:
        if mode == "dark":
            css_vars["--theme-bg-gradient"] = f"radial-gradient(ellipse at 85% 15%, {hex_with_alpha(accent_color, '26')} 0%, {surface_color} 50%, {bg_color} 100%)"
        else:
            css_vars["--theme-bg-gradient"] = f"linear-gradient(135deg, {bg_color} 0%, {surface_color} 55%, {colors['surface-soft']} 100%)"

    if "--theme-card-gradient" not in css_vars:
        css_vars["--theme-card-gradient"] = f"linear-gradient(145deg, {hex_with_alpha(card_bg, 'F2')} 0%, {surface_color} 100%)"

    components = dict(raw_data.get("components", {}))
    if "iconography" not in components:
        components["iconography"] = {
            "library": "lucide",
            "strokeWidth": "1.75px",
            "color": accent_color,
            "colorHighlight": accent_alt,
            "size": "26px",
            "container": "badge",
            "badgeBackground": hex_with_alpha(accent_color, "1A" if mode == "dark" else "12"),
            "badgeBorder": hex_with_alpha(accent_color, "40" if mode == "dark" else "30"),
            "badgeGlow": f"0 0 16px {hex_with_alpha(accent_color, '33')}"
        }

    # Construct clean frontmatter dictionary
    frontmatter_dict = {
        "version": raw_data.get("version", "2.0"),
        "name": theme_title,
        "description": raw_data.get("description", f"Slide deck design kit based on {theme_title}."),
        "mode": mode,
        "colors": colors,
        "typography": typography,
        "css_variables": css_vars,
        "components": components
    }

    # Run Contrast Audit
    print(f"\n📊 Contrast & Accessibility Audit ({mode.upper()} mode):")
    audit = run_contrast_audit(colors, mode=mode)
    print(f"  • Primary Text ({audit['text_on_canvas'][0]}) on Canvas ({audit['text_on_canvas'][1]}): {audit['text_on_canvas'][2]}")
    print(f"  • Muted Text ({audit['muted_on_canvas'][0]}) on Canvas ({audit['muted_on_canvas'][1]}): {audit['muted_on_canvas'][2]}")
    print(f"  • Primary Text on Card Surface ({audit['text_on_card'][1]}): {audit['text_on_card'][2]}")
    print(f"  • Primary Accent ({audit['accent_on_canvas'][0]}) on Canvas: {audit['accent_on_canvas'][2]}")
    print(f"  • Typography: {typography['font-family']} (Google Fonts: {typography['google-fonts']})")

    # Serialize to file
    frontmatter_yaml = yaml.dump(frontmatter_dict, sort_keys=False, default_flow_style=False)
    
    # Clean and preserve markdown body guidelines
    markdown_body = body.strip() if body.strip() else f"## Overview\n\nDesign system specification for {theme_title}."

    output_content = f"---\n{frontmatter_yaml}---\n\n{markdown_body}\n"

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"\n✅ Successfully saved theme to:\n   {target_file}")
    print(f"   Theme Identifier for spec.yaml: theme: {theme_slug_full} (or '{theme_slug}')")

    if preview:
        print("\n🖼 Generating immediate theme preview...")
        # Create a sample test spec to verify compilation
        test_dir = os.path.join(repo_root, "projects", "_theme_previews", theme_slug)
        os.makedirs(test_dir, exist_ok=True)
        test_spec_path = os.path.join(test_dir, "spec.yaml")
        preview_html_path = os.path.join(test_dir, "preview.html")
        deck_html_path = os.path.join(test_dir, "deck.html")

        test_spec = {
            "title": f"{theme_title} Showcase",
            "goal": f"Demonstration of the {theme_title} design system synthesized for slide presentations.",
            "theme": theme_slug_full,
            "slides": [
                {
                    "slide_number": 1,
                    "layout": "Title Slide",
                    "role": "cover",
                    "title": f"{theme_title} Design System",
                    "subtitle": "High-Fidelity Presentation Architecture",
                    "badge": "DESIGN.MD THEME"
                },
                {
                    "slide_number": 2,
                    "layout": "Title and Content",
                    "role": "slide",
                    "title": "System Architecture & Metrics",
                    "subtitle": "Structured semantic components with precision styling",
                    "badge": "COMPONENTS",
                    "content": {
                        "metrics": [
                            {"value": "99.99%", "label": "Reliability SLA", "subtext": "Continuous uptime", "highlight": True, "icon": "shield-check"},
                            {"value": "< 12ms", "label": "Edge Latency", "subtext": "Global delivery", "icon": "zap"},
                            {"value": "4.8x", "label": "Throughput Lift", "subtext": "Hardware accelerated", "icon": "trending-up"}
                        ],
                        "cards": [
                            {"title": "Visual Atmosphere", "text": "Curated palette, tight letter-tracking, and hairline card borders.", "icon": "layers", "badge": "Canvas"},
                            {"title": "Semantic Guardrails", "text": "Do's and don'ts prevent generic AI slop and ensure contrast.", "icon": "check-circle", "badge": "WCAG AA"}
                        ]
                    }
                }
            ]
        }
        with open(test_spec_path, "w", encoding="utf-8") as f:
            yaml.dump(test_spec, f, sort_keys=False)

        # Run preview.py
        import preview as preview_mod
        preview_mod.generate_preview(test_spec_path, preview_html_path)
        print(f"   Preview generated at: {preview_html_path}")

        # Run builder.py
        import builder as builder_mod
        builder_mod.build_deck(test_spec_path, deck_html_path)
        print(f"   Reveal.js deck generated at: {deck_html_path}")

    return target_file

def main():
    parser = argparse.ArgumentParser(description="Import DESIGN.md files and validate for slide presentations.")
    parser.add_argument("source", help="URL or file path to DESIGN.md file.")
    parser.add_argument("-n", "--name", help="Theme slug name (e.g. 'linear', 'vercel', 'stripe').")
    parser.add_argument("-o", "--output", help="Specific output file path.")
    parser.add_argument("-p", "--preview", action="store_true", help="Generate preview and test deck after import.")

    args = parser.parse_args()
    import_theme(args.source, name=args.name, output_path=args.output, preview=args.preview)

if __name__ == "__main__":
    main()
