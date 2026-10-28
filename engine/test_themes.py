#!/usr/bin/env python3
"""
Multi-Theme Diagnostic & Regression Test Harness for Slide Deck Builder.

Verifies that the presentation engine (preview.py, builder.py, style_parser.py)
renders cleanly across contrasting design themes without layout or style regressions.

Usage:
  ./venv/bin/python engine/test_themes.py [--full]
"""

import os
import sys
import yaml
import tempfile
import argparse
from style_parser import parse_style, contrast_ratio
import preview as preview_mod
import builder as builder_mod

TEST_THEMES = [
    ("sailpoint-corporate-2026-design", "dark", "Radial Dark Gradient (Cobalt / Aqua / Pink)"),
    ("linear-design", "dark", "Pitch Minimal Dark (Charcoal / Lavender)"),
    ("cloud-topology-enterprise-saas-design", "light", "Clean Enterprise Light (Blue / Slate)")
]

CANONICAL_SPEC = {
    "title": "Theme Regression Verification Deck",
    "goal": "Verify cross-theme component rendering, color contrast, and layout geometry.",
    "slides": [
        {
            "slide_number": 1,
            "layout": "Title Slide",
            "role": "cover",
            "title": "Architectural Design System",
            "subtitle": "Cross-Theme Regression & Component Testing",
            "badge": "VERIFICATION HARNESS"
        },
        {
            "slide_number": 2,
            "layout": "Title and Content",
            "role": "slide",
            "title": "System Metrics & Infrastructure",
            "subtitle": "Testing metric callouts, container cards, and badge accents",
            "badge": "COMPONENTS",
            "content": {
                "metrics": [
                    {"value": "99.99%", "label": "Availability", "subtext": "Global active-active", "highlight": True, "icon": "shield-check"},
                    {"value": "< 15ms", "label": "P99 Latency", "subtext": "Edge compute nodes", "icon": "zap"},
                    {"value": "100%", "label": "WCAG AA", "subtext": "Verified contrast ratio", "icon": "check-circle"}
                ],
                "cards": [
                    {"title": "Separation of Concerns", "text": "Tokens belong in styles/*.md; geometry and layout belong in builder.py.", "icon": "layers", "badge": "Architecture"},
                    {"title": "Universal Compatibility", "text": "DESIGN.md standard ingested seamlessly with zero manual translation.", "icon": "cpu", "badge": "Ecosystem"}
                ]
            }
        },
        {
            "slide_number": 3,
            "layout": "Two Content",
            "role": "slide",
            "title": "Structured Bullet Hierarchies",
            "subtitle": "Two-column split testing bullet markers and hover states",
            "badge": "LAYOUT",
            "content": {
                "left": {
                    "title": "Core Responsibilities",
                    "bullets": [
                        "Tokens control color, typography family, glow, and border styles.",
                        "Engine controls grid fractions, overflow clamping, and DOM tree.",
                        "Spec controls domain facts, narrative arc, and component selection."
                    ]
                },
                "right": {
                    "title": "Quality Invariants",
                    "bullets": [
                        "Every theme must pass 4.5:1 text-to-canvas contrast ratio.",
                        "Slides must fit cleanly inside 1920x1080 16:9 canvas.",
                        "Zero style bleed between themes during compilation."
                    ]
                }
            }
        },
        {
            "slide_number": 4,
            "layout": "Comparison",
            "role": "slide",
            "title": "Before vs After Architecture",
            "subtitle": "Validating side-by-side comparison card geometry and typography",
            "badge": "DIAGNOSTICS",
            "content": {
                "comparison": {
                    "left": {
                        "badge": "LEGACY",
                        "title": "Monolithic Styles",
                        "bullets": [
                            "Hardcoded hex colors inside layout CSS.",
                            "Theme bugs fixed in builder.py instead of styles.",
                            "Broken contrast on third-party design systems."
                        ]
                    },
                    "right": {
                        "badge": "MODERN",
                        "title": "Layered Architecture",
                        "bullets": [
                            "DESIGN.md ingestion with auto-contrast verification.",
                            "100% token-driven CSS variables in builder.py.",
                            "Automated multi-theme regression test suite."
                        ]
                    }
                }
            }
        }
    ]
}

def run_tests(full_export=False):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("\n" + "="*70)
    print("🚀 SLIDE DECK BUILDER — MULTI-THEME DIAGNOSTIC HARNESS")
    print("="*70 + "\n")

    overall_success = True

    with tempfile.TemporaryDirectory() as tmp_dir:
        for theme_name, expected_mode, description in TEST_THEMES:
            print(f"▶ Testing Theme: {theme_name}")
            print(f"  Description: {description}")
            
            # Step 1: Parse Style
            try:
                style = parse_style(theme_name)
                mode = style.get("mode")
                assert mode == expected_mode, f"Expected mode {expected_mode}, got {mode}"
                ink = style["colors"]["ink"]
                bg = style["colors"]["background"]
                cr = contrast_ratio(ink, bg)
                print(f"  • Style parsed: mode={mode}, font={style['typography']['font-family'][:25]}...")
                print(f"  • Contrast ratio (ink vs bg): {cr:.1f}:1 {'[PASS]' if cr >= 4.5 else '[FAIL]'}")
                if cr < 4.5:
                    print(f"    ❌ FAILED: Contrast ratio {cr:.1f}:1 is below WCAG AA threshold 4.5:1")
                    overall_success = False
            except Exception as e:
                print(f"  ❌ FAILED to parse style '{theme_name}': {e}")
                overall_success = False
                continue

            # Step 2: Build spec file
            theme_spec = dict(CANONICAL_SPEC)
            theme_spec["theme"] = theme_name
            spec_file = os.path.join(tmp_dir, f"{theme_name}_spec.yaml")
            preview_file = os.path.join(tmp_dir, f"{theme_name}_preview.html")
            deck_file = os.path.join(tmp_dir, f"{theme_name}_deck.html")

            with open(spec_file, "w", encoding="utf-8") as f:
                yaml.dump(theme_spec, f, sort_keys=False)

            # Step 3: Test preview.py
            try:
                preview_mod.generate_preview(spec_file, preview_file)
                assert os.path.exists(preview_file) and os.path.getsize(preview_file) > 1000
                print(f"  • Preview generated: {os.path.getsize(preview_file):,} bytes [PASS]")
            except Exception as e:
                print(f"  ❌ FAILED to generate preview: {e}")
                overall_success = False

            # Step 4: Test builder.py
            try:
                builder_mod.build_deck(spec_file, deck_file)
                assert os.path.exists(deck_file) and os.path.getsize(deck_file) > 5000
                with open(deck_file, "r", encoding="utf-8") as df:
                    content = df.read()
                    assert "--deck-bg-gradient" in content
                    assert "--deck-ink" in content
                    assert "section" in content
                print(f"  • Reveal.js deck compiled: {os.path.getsize(deck_file):,} bytes [PASS]")
            except Exception as e:
                print(f"  ❌ FAILED to compile Reveal.js deck: {e}")
                overall_success = False

            # Optional Step 5: Full export test (PowerPoint via headless chrome)
            if full_export:
                try:
                    import export_pptx as pptx_mod
                    pptx_file = os.path.join(tmp_dir, f"{theme_name}_deck.pptx")
                    pptx_mod.export_to_pptx(spec_file, pptx_file)
                    assert os.path.exists(pptx_file) and os.path.getsize(pptx_file) > 20000
                    print(f"  • PPTX exported: {os.path.getsize(pptx_file):,} bytes [PASS]")
                except Exception as e:
                    print(f"  ❌ FAILED to export PPTX: {e}")
                    overall_success = False

            print()

    print("="*70)
    if overall_success:
        print("✅ ALL THEMES PASSED: Cross-theme compatibility and contrast verified.")
    else:
        print("❌ SOME TESTS FAILED: Check the output above for details.")
    print("="*70 + "\n")

    return 0 if overall_success else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test presentation themes and engine rendering.")
    parser.add_argument("--full", action="store_true", help="Include full headless PPTX export test.")
    args = parser.parse_args()
    sys.exit(run_tests(full_export=args.full))
