#!/usr/bin/env python3
import os
import sys
import yaml
import base64
from style_parser import parse_style

def resolve_image_src(src, spec_dir):
    if not src:
        return ""
    if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
        return src
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = [
        os.path.join(spec_dir, src),
        os.path.join(repo_root, src),
        os.path.abspath(src)
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.isfile(c):
            ext = os.path.splitext(c)[1].lower().lstrip(".")
            mime = "image/svg+xml" if ext == "svg" else f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
            try:
                with open(c, "rb") as img_f:
                    encoded = base64.b64encode(img_f.read()).decode('utf-8')
                    return f"data:{mime};base64,{encoded}"
            except Exception:
                break
    return src

def generate_preview(spec_path, output_path=None):
    spec_dir = os.path.dirname(os.path.abspath(spec_path))
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    theme_name = spec.get("theme", "sailpoint-corporate-2026-design")
    style = parse_style(theme_name)
    mode = style.get("mode", "dark")

    colors = style.get("colors", {})
    bg_color = colors.get("background", "#F0F3F6" if mode == "light" else "#000000")
    surface_color = colors.get("surface", "#F0F3F6" if mode == "light" else "#0B111E")
    surface_soft = colors.get("surface-soft", "#ffffff" if mode == "light" else "#111827")
    card_bg = colors.get("card-background", "#ffffff" if mode == "light" else "#0B111E")
    card_border = colors.get("card-border", "#e2e8f0" if mode == "light" else "#415364")
    accent_color = colors.get("accent", "#2563EB" if mode == "light" else "#54C0E8")
    accent_alt = colors.get("accent-alt", "#D60EB5")
    ink_color = colors.get("ink", "#1d1d1f" if mode == "light" else "#FFFFFF")
    ink_muted = colors.get("ink-muted", "#4b5563" if mode == "light" else "#DAE1E9")

    font_family = style.get("typography", {}).get("font-family", "'Plus Jakarta Sans', system-ui, sans-serif" if mode == "light" else "'Poppins', system-ui, sans-serif")
    google_font = style.get("typography", {}).get("google-fonts", "Plus+Jakarta+Sans:wght@300;400;500;600;700" if mode == "light" else "Poppins:wght@300;400;500;600;700")

    title = spec.get("title", "Untitled Presentation")
    goal = spec.get("goal", "")
    options = spec.get("options", {})
    audience = options.get("audience", "General")
    tone = options.get("tone", "Professional")
    slides = spec.get("slides", [])
    slide_count = len(slides)

    # Build slide cards HTML
    slides_html = []
    for slide in slides:
        num = slide.get("slide_number", "")
        layout = slide.get("layout", "Title and Content")
        role = slide.get("role", "slide")
        stitle = slide.get("title", "Untitled Slide")
        subtitle = slide.get("subtitle", "")
        badge = slide.get("badge", "")
        content = slide.get("content", {})
        notes = slide.get("notes", "")

        # Check images
        slide_image = content.get("image") or slide.get("image")
        img_src = ""
        img_alt = ""
        img_caption = ""
        if isinstance(slide_image, dict):
            img_src = resolve_image_src(slide_image.get("src", ""), spec_dir)
            img_alt = slide_image.get("alt", "Slide visual")
            img_caption = slide_image.get("caption", "")
        elif isinstance(slide_image, str):
            img_src = resolve_image_src(slide_image, spec_dir)
            img_alt = stitle

        media_list = content.get("media", [])
        if not img_src and media_list and isinstance(media_list, list) and len(media_list) > 0:
            first_m = media_list[0]
            img_src = resolve_image_src(first_m.get("source") or first_m.get("src", ""), spec_dir)
            img_alt = first_m.get("alt", first_m.get("name", "Media visual"))

        # Render content preview
        content_preview_html = []

        # Eyebrow badge
        if badge:
            content_preview_html.append(f'<div class="mini-badge">{badge}</div>')

        # Image preview
        if img_src:
            content_preview_html.append(f'''
                <div class="mini-image-card">
                    <img src="{img_src}" alt="{img_alt}" class="mini-image-thumb" />
                    {f'<span class="mini-image-caption">{img_caption}</span>' if img_caption else ''}
                </div>
            ''')

        # Bullets
        bullets = content.get("bullets", [])
        if bullets:
            b_items = "".join([f"<li>{b}</li>" for b in bullets[:4]])
            if len(bullets) > 4:
                b_items += f'<li class="more-items">+{len(bullets)-4} more...</li>'
            content_preview_html.append(f'<ul class="mini-bullets">{b_items}</ul>')

        # Body
        body = content.get("body", "")
        if body:
            content_preview_html.append(f'<p class="mini-body">{body}</p>')

        # Metrics
        metrics = content.get("metrics", [])
        if metrics:
            m_items = []
            for m in metrics:
                val = m.get("value", "")
                lbl = m.get("label", "")
                glow = ' glowing' if m.get("highlight", False) else ''
                m_items.append(f'''
                    <div class="mini-metric-card{glow}">
                        <div class="metric-val">{val}</div>
                        <div class="metric-lbl">{lbl}</div>
                    </div>
                ''')
            content_preview_html.append(f'<div class="mini-metrics-grid">{"".join(m_items)}</div>')

        # Cards
        cards = content.get("cards", [])
        if cards:
            c_items = []
            for c in cards:
                c_title = c.get("title", "")
                c_body = c.get("body", "")
                c_badge = c.get("badge", "")
                c_items.append(f'''
                    <div class="mini-content-card">
                        {f'<span class="card-tag">{c_badge}</span>' if c_badge else ''}
                        <strong>{c_title}</strong>
                        <p>{c_body}</p>
                    </div>
                ''')
            content_preview_html.append(f'<div class="mini-cards-grid">{"".join(c_items)}</div>')

        # Comparison
        comparison = content.get("comparison", {})
        if comparison:
            left = comparison.get("left", {})
            right = comparison.get("right", {})
            left_bullets = "".join([f"<li>{b}</li>" for b in left.get("bullets", [])[:2]])
            right_bullets = "".join([f"<li>{b}</li>" for b in right.get("bullets", [])[:2]])
            content_preview_html.append(f'''
                <div class="mini-comparison-grid">
                    <div class="mini-content-card">
                        <span class="card-tag">{left.get("badge", "Left")}</span>
                        <strong>{left.get("title", "Before")}</strong>
                        <ul class="mini-bullets">{left_bullets}</ul>
                    </div>
                    <div class="mini-content-card glowing">
                        <span class="card-tag" style="color: {accent_alt}; border-color: {accent_alt};">{right.get("badge", "Right")}</span>
                        <strong>{right.get("title", "After")}</strong>
                        <ul class="mini-bullets">{right_bullets}</ul>
                    </div>
                </div>
            ''')

        # Regions / Multi-columns
        regions = content.get("regions", [])
        if regions:
            r_items = []
            for r in regions:
                r_title = r.get("title", "")
                r_bullets = "".join([f"<li>{b}</li>" for b in r.get("bullets", [])[:2]])
                r_items.append(f'''
                    <div class="mini-content-card">
                        {f'<strong>{r_title}</strong>' if r_title else ''}
                        {f'<ul class="mini-bullets">{r_bullets}</ul>' if r_bullets else ''}
                    </div>
                ''')
            content_preview_html.append(f'<div class="mini-regions-grid">{"".join(r_items)}</div>')

        # Diagram
        diagram = content.get("diagram", {})
        if diagram:
            d_kind = diagram.get("kind", "diagram")
            d_elems = diagram.get("elements", [])
            chips = "".join([f'<span class="diagram-chip">{e}</span>' for e in d_elems[:4]])
            content_preview_html.append(f'''
                <div class="mini-diagram-box">
                    <div class="diagram-title">⬡ Diagram ({d_kind.upper()})</div>
                    <div class="diagram-chips">{chips}</div>
                </div>
            ''')

        content_body = "".join(content_preview_html)

        slides_html.append(f'''
        <div class="slide-card">
            <div class="slide-card-header">
                <span class="slide-num">#{num}</span>
                <span class="pill layout-pill">{layout}</span>
                <span class="pill role-pill">{role}</span>
            </div>
            <div class="slide-canvas">
                <div class="slide-title-area">
                    <h3 class="slide-title">{stitle}</h3>
                    {f'<div class="slide-subtitle">{subtitle}</div>' if subtitle else ''}
                </div>
                <div class="slide-content-area">
                    {content_body}
                </div>
            </div>
            {f'<div class="slide-notes"><span class="notes-tag">Notes:</span> {notes}</div>' if notes else ''}
        </div>
        ''')

    cards_joined = "".join(slides_html)

    # Dynamic preview background
    if mode == "light":
        preview_bg = f"linear-gradient(135deg, {bg_color} 0%, {surface_color} 100%)"
        header_bg = "rgba(255, 255, 255, 0.95)"
        header_shadow = "0 4px 20px rgba(0, 0, 0, 0.05)"
        card_bg_val = card_bg
        card_shadow = "0 4px 16px rgba(0, 0, 0, 0.06)"
        goal_bg = "rgba(37, 99, 235, 0.06)"
    else:
        preview_bg = f"radial-gradient(circle at 85% 15%, {accent_color}33 0%, {surface_color} 45%, {bg_color} 100%), {bg_color}"
        header_bg = "rgba(11, 17, 30, 0.85)"
        header_shadow = "0 10px 30px rgba(0, 0, 0, 0.5)"
        card_bg_val = f"linear-gradient(145deg, {card_bg} 0%, {surface_color} 100%)"
        card_shadow = "0 8px 24px rgba(0, 0, 0, 0.4)"
        goal_bg = f"rgba(1, 28, 72, 0.4)"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spec Preview: {title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={google_font}&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: {bg_color};
            --surface: {surface_color};
            --card-bg: {card_bg};
            --card-border: {card_border};
            --accent: {accent_color};
            --accent-alt: {accent_alt};
            --ink: {ink_color};
            --ink-muted: {ink_muted};
            --font-family: {font_family};
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: {preview_bg};
            color: var(--ink);
            font-family: var(--font-family);
            padding: 2rem 2.5rem;
            min-height: 100vh;
        }}
        .header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 2rem;
            background: {header_bg};
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: {header_shadow};
        }}
        .header-info h1 {{
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
            color: var(--ink);
        }}
        .header-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.9rem;
            color: var(--ink-muted);
            align-items: center;
        }}
        .pill {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 500;
            padding: 3px 10px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .theme-pill {{ background: rgba(37, 99, 235, 0.1); border: 1px solid var(--accent); color: var(--accent); }}
        .count-pill {{ background: rgba(214, 14, 181, 0.1); border: 1px solid var(--accent-alt); color: var(--accent-alt); }}
        .layout-pill {{ background: rgba(0, 0, 0, 0.04); border: 1px solid var(--card-border); color: var(--ink-muted); }}
        .role-pill {{ background: rgba(37, 99, 235, 0.08); color: var(--accent); }}

        .goal-banner {{
            padding: 1rem 1.5rem;
            background: {goal_bg};
            border-left: 4px solid var(--accent);
            border-radius: 8px;
            margin-bottom: 2.5rem;
            font-size: 0.95rem;
            color: var(--ink-muted);
        }}
        .goal-banner strong {{ color: var(--ink); }}

        .deck-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 2rem;
        }}
        .slide-card {{
            background: {card_bg_val};
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            box-shadow: {card_shadow};
        }}
        .slide-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 10px 24px rgba(37, 99, 235, 0.15);
        }}
        .slide-card-header {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--card-border);
        }}
        .slide-num {{
            font-weight: 700;
            font-size: 0.9rem;
            color: var(--accent);
        }}
        .slide-canvas {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            min-height: 220px;
        }}
        .mini-badge {{
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--accent);
            letter-spacing: 0.08em;
        }}
        .slide-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: var(--ink);
            line-height: 1.3;
        }}
        .slide-subtitle {{
            font-size: 0.82rem;
            color: var(--ink-muted);
            margin-top: 0.25rem;
        }}
        .slide-content-area {{
            flex: 1;
            font-size: 0.82rem;
            color: var(--ink-muted);
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }}
        .mini-image-card {{
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--card-border);
            max-height: 140px;
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(0,0,0,0.02);
        }}
        .mini-image-thumb {{
            max-width: 100%;
            max-height: 110px;
            object-fit: cover;
        }}
        .mini-image-caption {{
            font-size: 0.68rem;
            color: var(--ink-muted);
            padding: 2px 6px;
        }}
        .mini-bullets {{
            padding-left: 1.2rem;
            line-height: 1.6;
        }}
        .mini-bullets li {{ margin-bottom: 0.3rem; }}
        .mini-body {{ line-height: 1.5; }}

        .mini-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
            gap: 0.6rem;
            margin-top: 0.5rem;
        }}
        .mini-metric-card {{
            background: rgba(0,0,0,0.02);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.6rem;
            text-align: center;
        }}
        .mini-metric-card.glowing {{
            border-color: var(--accent);
        }}
        .metric-val {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--accent);
        }}
        .metric-lbl {{
            font-size: 0.75rem;
            color: var(--ink);
        }}

        .mini-cards-grid, .mini-regions-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.6rem;
            margin-top: 0.5rem;
        }}
        .mini-content-card {{
            background: rgba(0,0,0,0.02);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 0.65rem;
        }}
        .mini-content-card.glowing {{ border-color: var(--accent-alt); }}
        .mini-content-card strong {{ display: block; font-size: 0.85rem; color: var(--ink); margin-bottom: 0.2rem; }}
        .mini-content-card p {{ font-size: 0.78rem; color: var(--ink-muted); line-height: 1.4; }}
        .card-tag {{
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 600;
            color: var(--accent);
            border: 1px solid var(--accent);
            padding: 1px 6px;
            border-radius: 4px;
            margin-bottom: 0.3rem;
            text-transform: uppercase;
        }}

        .mini-comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.6rem;
            margin-top: 0.5rem;
        }}

        .mini-diagram-box {{
            background: rgba(0,0,0,0.02);
            border: 1px dashed var(--accent);
            border-radius: 8px;
            padding: 0.6rem;
            margin-top: 0.5rem;
        }}
        .diagram-title {{
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 0.4rem;
        }}
        .diagram-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
        }}
        .diagram-chip {{
            background: rgba(0,0,0,0.04);
            border: 1px solid var(--card-border);
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 0.72rem;
            color: var(--ink);
        }}

        .slide-notes {{
            margin-top: 0.85rem;
            padding-top: 0.65rem;
            border-top: 1px dashed var(--card-border);
            font-size: 0.75rem;
            color: var(--ink-muted);
            line-height: 1.4;
        }}
        .notes-tag {{
            font-weight: 600;
            color: var(--accent);
        }}
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="header-info">
            <h1>{title}</h1>
            <div class="header-meta">
                <span class="pill theme-pill">{theme_name} ({mode})</span>
                <span class="pill count-pill">{slide_count} Slides</span>
                <span><strong>Audience:</strong> {audience}</span>
                <span><strong>Tone:</strong> {tone}</span>
            </div>
        </div>
    </div>

    {f'<div class="goal-banner"><strong>Goal:</strong> {goal}</div>' if goal else ''}

    <div class="deck-grid">
        {cards_joined}
    </div>
</body>
</html>
'''
    if not output_path:
        output_path = os.path.join(spec_dir, "preview.html")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Spec preview generated: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preview.py <spec_file.yaml> [output_preview.html]")
        sys.exit(1)
    spec_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    generate_preview(spec_arg, out_arg)
