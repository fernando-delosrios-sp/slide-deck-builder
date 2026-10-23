#!/usr/bin/env python3
import os
import sys
import yaml
import base64
from style_parser import parse_style

def resolve_image_src(src, spec_dir):
    """
    Resolves an image source to a Base64 data URI if the file exists locally,
    or returns the URL/path as-is.
    """
    if not src:
        return ""
    if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
        return src
    
    # Check relative to spec directory, then repo root
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

def build_deck(spec_path, output_path=None):
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

    deck_title = spec.get("title", "Presentation")
    slides = spec.get("slides", [])

    # Theme CSS variables & background setup
    css_vars = style.get("css_variables", {})
    if "--sp-bg-gradient" in css_vars:
        bg_gradient = css_vars["--sp-bg-gradient"]
    elif "--theme-bg-gradient" in css_vars:
        bg_gradient = css_vars["--theme-bg-gradient"]
    elif mode == "light":
        bg_gradient = f"linear-gradient(135deg, {bg_color} 0%, {surface_color} 60%, {surface_soft} 100%)"
    else:
        bg_gradient = f"radial-gradient(circle at 85% 15%, {accent_color}33 0%, {surface_color} 50%, {bg_color} 100%)"

    # Logo resolution: only if explicit in spec or theme provides a logo
    logo_data_uri = None
    spec_logo = spec.get("logo")
    logo_target = spec_logo or style.get("logo_path")
    if logo_target:
        logo_data_uri = resolve_image_src(logo_target, spec_dir)

    sections_html = []

    for slide in slides:
        num = slide.get("slide_number", 1)
        layout = slide.get("layout", "Title and Content")
        role = slide.get("role", "slide")
        title = slide.get("title", "")
        subtitle = slide.get("subtitle", "")
        badge = slide.get("badge", "")
        content = slide.get("content", {})
        notes = slide.get("notes", "")

        layout_slug = layout.lower().replace(" ", "-")

        # Eyebrow / Category badge
        badge_html = f'<div class="eyebrow-badge">{badge}</div>' if badge else ''

        # Image resolution if defined on slide level or content level
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
            img_alt = title

        # Check content media array
        media_list = content.get("media", [])
        if not img_src and media_list and isinstance(media_list, list) and len(media_list) > 0:
            first_m = media_list[0]
            img_src = resolve_image_src(first_m.get("source") or first_m.get("src", ""), spec_dir)
            img_alt = first_m.get("alt", first_m.get("name", "Media visual"))

        # Build image HTML block
        image_html_block = ""
        if img_src:
            caption_tag = f'<div class="slide-image-caption">{img_caption}</div>' if img_caption else ''
            image_html_block = f'''
                <div class="slide-image-card">
                    <img src="{img_src}" alt="{img_alt}" class="slide-embedded-image" />
                    {caption_tag}
                </div>
            '''

        body_parts = []

        # 1. Cover slide layout
        if "title-slide" in layout_slug:
            cover_media_html = ""
            if img_src:
                cover_media_html = f'''
                    <div class="cover-media-container">
                        <img src="{img_src}" alt="{img_alt}" class="cover-hero-image" />
                    </div>
                '''
            body_parts.append(f'''
                <div class="title-slide-wrapper{' with-cover-image' if img_src else ''}">
                    <div class="cover-text-content">
                        {f'<div class="cover-logo"><img src="{logo_data_uri}" alt="Logo" class="brand-logo"></div>' if logo_data_uri else ''}
                        {badge_html}
                        <h1 class="cover-title">{title}</h1>
                        {f'<h2 class="cover-subtitle">{subtitle}</h2>' if subtitle else ''}
                        <div class="cover-footer">
                            {f'<p class="cover-author">{content.get("body", "")}</p>' if content.get("body") else ''}
                        </div>
                    </div>
                    {cover_media_html}
                </div>
            ''')

        # 2. Section Header layout
        elif "section-header" in layout_slug:
            body_parts.append(f'''
                <div class="section-header-wrapper">
                    {badge_html}
                    <h1 class="section-title">{title}</h1>
                    {f'<h3 class="section-subtitle">{subtitle}</h3>' if subtitle else ''}
                    {f'<p class="section-body">{content.get("body", "")}</p>' if content.get("body") else ''}
                </div>
            ''')

        # 3. Blank layout (Hero Visual)
        elif "blank" in layout_slug:
            body_parts.append(f'''
                <div class="blank-hero-layout">
                    {f'<img src="{img_src}" alt="{img_alt}" class="hero-full-bleed" />' if img_src else ''}
                    <div class="hero-overlay-card">
                        {badge_html}
                        <h2 class="slide-title">{title}</h2>
                        {f'<h4 class="slide-subtitle">{subtitle}</h4>' if subtitle else ''}
                        {f'<p class="slide-body-text">{content.get("body", "")}</p>' if content.get("body") else ''}
                    </div>
                </div>
            ''')

        # 4. Standard Content Layouts (Title and Content, Two Content, Comparison, Three Columns, Picture with Caption, etc.)
        else:
            header_block = f'''
                <div class="slide-header">
                    {badge_html}
                    <h2 class="slide-title">{title}</h2>
                    {f'<h4 class="slide-subtitle">{subtitle}</h4>' if subtitle else ''}
                </div>
            '''

            content_blocks = []

            # Bullets
            bullets = content.get("bullets", [])
            if bullets:
                b_items = "".join([f"<li>{b}</li>" for b in bullets])
                content_blocks.append(f'<ul class="styled-bullets">{b_items}</ul>')

            # Body narrative
            body_text = content.get("body", "")
            if body_text:
                content_blocks.append(f'<p class="slide-body-text">{body_text}</p>')

            # Metrics
            metrics = content.get("metrics", [])
            if metrics:
                m_cards = []
                for m in metrics:
                    glow_cls = " glowing" if m.get("highlight", False) else ""
                    m_cards.append(f'''
                        <div class="metric-card{glow_cls}">
                            <div class="metric-value">{m.get("value", "")}</div>
                            <div class="metric-label">{m.get("label", "")}</div>
                            {f'<div class="metric-subtext">{m.get("subtext")}</div>' if m.get("subtext") else ''}
                        </div>
                    ''')
                content_blocks.append(f'<div class="metrics-container count-{len(metrics)}">{"".join(m_cards)}</div>')

            # Cards
            cards = content.get("cards", [])
            if cards:
                c_cards = []
                for c in cards:
                    c_badge = f'<span class="card-badge">{c.get("badge")}</span>' if c.get("badge") else ''
                    c_glow = ' glowing' if c.get("highlight") else ''
                    c_cards.append(f'''
                        <div class="feature-card{c_glow}">
                            {c_badge}
                            <h3 class="card-title">{c.get("title", "")}</h3>
                            <p class="card-body">{c.get("body", "")}</p>
                        </div>
                    ''')
                content_blocks.append(f'<div class="cards-grid count-{len(cards)}">{"".join(c_cards)}</div>')

            # Comparison
            comparison = content.get("comparison", {})
            if comparison:
                left = comparison.get("left", {})
                right = comparison.get("right", {})
                l_bullets = "".join([f"<li>{b}</li>" for b in left.get("bullets", [])])
                r_bullets = "".join([f"<li>{b}</li>" for b in right.get("bullets", [])])
                content_blocks.append(f'''
                    <div class="comparison-container">
                        <div class="comparison-card left-card">
                            <span class="card-badge">{left.get("badge", "Traditional / Before")}</span>
                            <h3 class="card-title">{left.get("title", "Before")}</h3>
                            <ul class="styled-bullets">{l_bullets}</ul>
                        </div>
                        <div class="comparison-card right-card glowing">
                            <span class="card-badge accent-alt">{right.get("badge", "Modern / After")}</span>
                            <h3 class="card-title">{right.get("title", "After")}</h3>
                            <ul class="styled-bullets">{r_bullets}</ul>
                        </div>
                    </div>
                ''')

            # Regions (Two Content / Three Columns)
            regions = content.get("regions", [])
            if regions:
                r_cols = []
                for r in regions:
                    r_title = f'<h3 class="region-title">{r.get("title")}</h3>' if r.get("title") else ''
                    r_body = f'<p class="region-body">{r.get("body")}</p>' if r.get("body") else ''
                    r_bullets = "".join([f"<li>{b}</li>" for b in r.get("bullets", [])])
                    
                    # Check if region has media
                    reg_media = ""
                    reg_src = r.get("media_ref") or r.get("src") or r.get("image")
                    if reg_src or r.get("kind") == "media":
                        res_src = resolve_image_src(reg_src, spec_dir)
                        if res_src:
                            reg_media = f'<div class="region-image-wrapper"><img src="{res_src}" alt="{r.get("title", "Visual")}" class="region-image" /></div>'
                    
                    r_cols.append(f'''
                        <div class="region-col">
                            {r_title}
                            {reg_media}
                            {r_body}
                            {f'<ul class="styled-bullets">{r_bullets}</ul>' if r_bullets else ''}
                        </div>
                    ''')
                content_blocks.append(f'<div class="regions-container count-{len(regions)}">{"".join(r_cols)}</div>')

            # Diagram (only rendered if no image or explicitly requested)
            diagram = content.get("diagram", {})
            if diagram and not img_src:
                d_kind = diagram.get("kind", "flow")
                d_elems = diagram.get("elements", [])
                chips = []
                for i, elem in enumerate(d_elems):
                    chips.append(f'<div class="diagram-node"><span class="node-idx">{i+1}</span> {elem}</div>')
                    if i < len(d_elems) - 1:
                        chips.append('<div class="diagram-arrow">➔</div>')
                content_blocks.append(f'''
                    <div class="diagram-wrapper">
                        <div class="diagram-badge">Architecture / {d_kind.title()}</div>
                        <div class="diagram-nodes">{"".join(chips)}</div>
                    </div>
                ''')

            # Layout Assembly: If an image is present, place it side-by-side (2 columns)
            # to strictly prevent any vertical overflow!
            if image_html_block:
                if "picture-with-caption" in layout_slug:
                    main_body_html = f'''
                        <div class="picture-caption-grid">
                            <div class="picture-side">
                                {image_html_block}
                            </div>
                            <div class="caption-side">
                                {"".join(content_blocks)}
                            </div>
                        </div>
                    '''
                elif content_blocks:
                    main_body_html = f'''
                        <div class="slide-split-grid">
                            <div class="slide-split-text">
                                {"".join(content_blocks)}
                            </div>
                            <div class="slide-split-media">
                                {image_html_block}
                            </div>
                        </div>
                    '''
                else:
                    main_body_html = f'''
                        <div class="slide-center-media">
                            {image_html_block}
                        </div>
                    '''
            else:
                main_body_html = f'''
                    <div class="slide-content">
                        {"".join(content_blocks)}
                    </div>
                '''

            body_parts.append(f'''
                <div class="slide-layout {layout_slug}">
                    {header_block}
                    {main_body_html}
                </div>
            ''')

        # Presenter notes
        notes_block = f'<aside class="notes">{notes}</aside>' if notes else ''

        sections_html.append(f'''
            <section class="deck-slide slide-{num}" data-role="{role}">
                {"".join(body_parts)}
                {notes_block}
            </section>
        ''')

    slides_content = "\n".join(sections_html)

    # Pick reveal theme stylesheet based on light vs dark mode
    reveal_theme_css = "https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/theme/white.min.css" if mode == "light" else "https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/theme/black.min.css"

    # Theme-sensitive card styling
    card_shadow = "0 8px 24px rgba(0, 0, 0, 0.06)" if mode == "light" else "0 10px 30px rgba(0, 0, 0, 0.4)"
    card_bg_css = card_bg if mode == "light" else f"linear-gradient(145deg, {card_bg} 0%, {surface_color} 100%)"
    badge_bg = f"rgba(37, 99, 235, 0.08)" if mode == "light" else f"rgba(84, 192, 232, 0.15)"
    cover_title_gradient = f"linear-gradient(135deg, {ink_color} 0%, {accent_color} 100%)" if mode == "light" else f"linear-gradient(135deg, #FFFFFF 0%, #DAE1E9 60%, {accent_color} 100%)"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{deck_title}</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={google_font}&display=swap" rel="stylesheet">

    <!-- Reveal.js Stylesheets -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/reset.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/reveal.min.css">
    <link rel="stylesheet" href="{reveal_theme_css}">

    <!-- Deck Theme & Layout CSS -->
    <style>
        :root {{
            --deck-bg-gradient: {bg_gradient};
            --deck-bg: {bg_color};
            --deck-surface: {surface_color};
            --deck-card-bg: {card_bg};
            --deck-card-border: {card_border};
            --deck-accent: {accent_color};
            --deck-accent-alt: {accent_alt};
            --deck-ink: {ink_color};
            --deck-ink-muted: {ink_muted};
            --font-family: {font_family};
        }}

        body, .reveal {{
            font-family: var(--font-family) !important;
            background: var(--deck-bg-gradient) !important;
            color: var(--deck-ink) !important;
        }}

        .reveal .slides {{
            text-align: left;
        }}

        .reveal .slides section {{
            padding: 2.5rem 3.5rem;
            box-sizing: border-box;
            height: 100% !important;
            max-height: 1080px !important;
            overflow: hidden !important;
        }}

        /* Typography */
        h1, h2, h3, h4, h5 {{
            font-family: var(--font-family) !important;
            color: var(--deck-ink) !important;
            text-transform: none !important;
            letter-spacing: -0.015em;
        }}

        .eyebrow-badge {{
            display: inline-block;
            font-size: 0.95rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--deck-accent);
            background: {badge_bg};
            border: 1px solid var(--deck-accent);
            padding: 4px 14px;
            border-radius: 9999px;
            margin-bottom: 0.85rem;
        }}

        /* Title Slide Layout */
        .title-slide-wrapper {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
            max-height: 900px;
            box-sizing: border-box;
        }}
        .title-slide-wrapper.with-cover-image {{
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 3.5rem;
            align-items: center;
            height: 100%;
            max-height: 900px;
        }}
        .cover-text-content {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .cover-media-container {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .cover-hero-image {{
            max-width: 100%;
            max-height: 540px;
            width: auto;
            height: auto;
            border-radius: 20px;
            border: 1px solid var(--deck-card-border);
            box-shadow: {card_shadow};
            object-fit: contain;
            display: block;
        }}
        .brand-logo {{
            height: 48px;
            margin-bottom: 2rem;
        }}
        .cover-title {{
            font-size: 3.4rem !important;
            font-weight: 700 !important;
            line-height: 1.15 !important;
            margin-bottom: 1rem !important;
            background: {cover_title_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .cover-subtitle {{
            font-size: 1.45rem !important;
            font-weight: 400 !important;
            color: var(--deck-ink-muted) !important;
            margin-bottom: 2rem !important;
            max-width: 95%;
            line-height: 1.35 !important;
        }}
        .cover-footer {{
            color: var(--deck-ink-muted);
            font-size: 1.1rem;
            border-top: 1px solid var(--deck-card-border);
            padding-top: 1rem;
        }}

        /* Section Header Layout */
        .section-header-wrapper {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            height: 100%;
            max-height: 850px;
        }}
        .section-title {{
            font-size: 3.8rem !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            margin-bottom: 1rem !important;
        }}
        .section-subtitle {{
            font-size: 1.6rem !important;
            color: var(--deck-accent) !important;
            max-width: 75%;
        }}
        .section-body {{
            font-size: 1.3rem;
            color: var(--deck-ink-muted);
            max-width: 70%;
            margin-top: 1rem;
        }}

        /* Standard Slide Layout Container */
        .slide-layout {{
            height: 100%;
            max-height: 880px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}
        .slide-header {{
            margin-bottom: 1.5rem;
            flex-shrink: 0;
        }}
        .slide-title {{
            font-size: 2.5rem !important;
            font-weight: 600 !important;
            line-height: 1.2 !important;
            margin: 0.2rem 0 !important;
        }}
        .slide-subtitle {{
            font-size: 1.25rem !important;
            font-weight: 400 !important;
            color: var(--deck-ink-muted) !important;
        }}

        /* Standard Slide Content Area */
        .slide-content {{
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            flex: 1;
            overflow: hidden;
        }}
        .styled-bullets {{
            font-size: 1.3rem !important;
            line-height: 1.65 !important;
            color: var(--deck-ink-muted);
            padding-left: 2rem;
        }}
        .styled-bullets li {{
            margin-bottom: 0.75rem;
        }}
        .styled-bullets li::marker {{
            color: var(--deck-accent);
        }}
        .slide-body-text {{
            font-size: 1.3rem !important;
            line-height: 1.55 !important;
            color: var(--deck-ink-muted);
            max-width: 95%;
        }}

        /* Side-by-Side Split Grid when Image is Present */
        .slide-split-grid {{
            display: grid;
            grid-template-columns: 1.05fr 0.95fr;
            gap: 2.5rem;
            align-items: center;
            flex: 1;
            max-height: 720px;
            box-sizing: border-box;
            overflow: hidden;
        }}
        .slide-split-text {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            justify-content: center;
            max-height: 720px;
            overflow: hidden;
        }}
        .slide-split-text .styled-bullets {{
            font-size: 1.15rem !important;
            line-height: 1.55 !important;
            padding-left: 1.5rem;
        }}
        .slide-split-text .styled-bullets li {{
            margin-bottom: 0.6rem;
        }}
        .slide-split-text .slide-body-text {{
            font-size: 1.15rem !important;
            line-height: 1.5 !important;
        }}
        .slide-split-media {{
            display: flex;
            justify-content: center;
            align-items: center;
            max-height: 720px;
        }}

        /* Embedded Image Cards */
        .slide-image-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--deck-card-border);
            background: var(--deck-card-bg);
            box-shadow: {card_shadow};
            max-height: 600px;
            width: 100%;
        }}
        .slide-embedded-image {{
            max-width: 100%;
            max-height: 520px;
            width: auto;
            height: auto;
            object-fit: contain;
            border-radius: 14px;
            display: block;
        }}
        .slide-image-caption {{
            font-size: 0.88rem;
            color: var(--deck-ink-muted);
            padding: 0.5rem 1rem;
            text-align: center;
            border-top: 1px solid var(--deck-card-border);
            width: 100%;
            background: rgba(0, 0, 0, 0.02);
        }}

        /* Picture with Caption Grid */
        .picture-caption-grid {{
            display: grid;
            grid-template-columns: 1.05fr 0.95fr;
            gap: 2.5rem;
            align-items: center;
            flex: 1;
            max-height: 720px;
            overflow: hidden;
        }}
        .picture-side {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .caption-side {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            justify-content: center;
        }}

        /* Split Grid Component Adjustments */
        .slide-split-text .metrics-container {{
            grid-template-columns: 1fr;
            gap: 0.75rem;
            margin-top: 0;
        }}
        .slide-split-text .metric-card {{
            padding: 0.85rem 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-align: left;
        }}
        .slide-split-text .metric-value {{
            font-size: 2.2rem;
            margin-bottom: 0;
        }}
        .slide-split-text .metric-label {{
            font-size: 1.05rem;
            margin-bottom: 0;
        }}
        .slide-split-text .metric-subtext {{
            font-size: 0.85rem;
        }}

        .slide-split-text .cards-grid {{
            grid-template-columns: 1fr;
            gap: 0.85rem;
            margin-top: 0;
        }}
        .slide-split-text .feature-card {{
            padding: 1.1rem 1.35rem;
        }}
        .slide-split-text .card-title {{
            font-size: 1.25rem !important;
            margin-bottom: 0.35rem !important;
        }}
        .slide-split-text .card-body {{
            font-size: 1.05rem !important;
            line-height: 1.45 !important;
        }}

        .slide-split-text .comparison-container {{
            grid-template-columns: 1fr;
            gap: 0.85rem;
            margin-top: 0;
        }}
        .slide-split-text .comparison-card {{
            padding: 1.1rem 1.35rem;
        }}
        .slide-split-text .comparison-card .card-title {{
            font-size: 1.25rem !important;
            margin-bottom: 0.35rem !important;
        }}
        .slide-split-text .comparison-card .styled-bullets {{
            font-size: 1.05rem !important;
            line-height: 1.45 !important;
            padding-left: 1.2rem;
        }}

        .slide-split-text .regions-container {{
            grid-template-columns: 1fr;
            gap: 0.75rem;
            margin-top: 0;
        }}
        .slide-split-text .region-col {{
            padding: 0.85rem 1.15rem;
        }}
        .slide-split-text .region-title {{
            font-size: 1.15rem !important;
            margin-bottom: 0.25rem !important;
        }}
        .slide-split-text .region-col .styled-bullets {{
            font-size: 1.05rem !important;
            line-height: 1.45 !important;
            padding-left: 1.2rem;
        }}

        /* Metrics (Full Slide) */
        .metrics-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.75rem;
            margin-top: 0.5rem;
        }}
        .metric-card {{
            background: {card_bg_css};
            border: 1px solid var(--deck-card-border);
            border-radius: 18px;
            padding: 1.75rem;
            text-align: center;
            box-shadow: {card_shadow};
        }}
        .metric-card.glowing {{
            border-color: var(--deck-accent);
            box-shadow: 0 0 25px {accent_color}44;
        }}
        .metric-value {{
            font-size: 3.4rem;
            font-weight: 700;
            color: var(--deck-accent);
            line-height: 1.1;
            margin-bottom: 0.4rem;
        }}
        .metric-label {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--deck-ink);
            margin-bottom: 0.3rem;
        }}
        .metric-subtext {{
            font-size: 0.95rem;
            color: var(--deck-accent-alt);
        }}

        /* Cards Grid (Full Slide) */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.75rem;
            margin-top: 0.5rem;
        }}
        .feature-card {{
            background: {card_bg_css};
            border: 1px solid var(--deck-card-border);
            border-radius: 18px;
            padding: 1.75rem;
            box-shadow: {card_shadow};
        }}
        .feature-card.glowing {{
            border-color: var(--deck-accent-alt);
            box-shadow: 0 0 25px {accent_alt}33;
        }}
        .card-badge {{
            display: inline-block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--deck-accent);
            border: 1px solid var(--deck-accent);
            padding: 3px 10px;
            border-radius: 6px;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
        }}
        .card-badge.accent-alt {{
            color: var(--deck-accent-alt);
            border-color: var(--deck-accent-alt);
        }}
        .card-title {{
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            margin-bottom: 0.65rem !important;
        }}
        .card-body {{
            font-size: 1.15rem !important;
            line-height: 1.55 !important;
            color: var(--deck-ink-muted);
        }}

        /* Comparison Layout (Full Slide) */
        .comparison-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2.25rem;
            margin-top: 0.5rem;
        }}
        .comparison-card {{
            background: {card_bg_css};
            border: 1px solid var(--deck-card-border);
            border-radius: 18px;
            padding: 1.85rem;
            box-shadow: {card_shadow};
        }}
        .comparison-card.glowing {{
            border-color: var(--deck-accent);
            box-shadow: 0 0 25px {accent_color}44;
        }}

        /* Regions / Multi-column Layouts (Full Slide) */
        .regions-container {{
            display: grid;
            gap: 1.75rem;
            margin-top: 0.5rem;
        }}
        .regions-container.count-2 {{ grid-template-columns: 1fr 1fr; }}
        .regions-container.count-3 {{ grid-template-columns: 1fr 1fr 1fr; }}
        .region-col {{
            background: {card_bg_css};
            border: 1px solid var(--deck-card-border);
            border-radius: 18px;
            padding: 1.5rem;
            box-shadow: {card_shadow};
        }}
        .region-title {{
            font-size: 1.45rem !important;
            font-weight: 600 !important;
            color: var(--deck-accent) !important;
            margin-bottom: 0.75rem !important;
        }}

        /* Diagram Canvas */
        .diagram-wrapper {{
            background: {card_bg_css};
            border: 1.5px dashed var(--deck-accent);
            border-radius: 18px;
            padding: 1.75rem;
            margin-top: 0.5rem;
        }}
        .diagram-badge {{
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--deck-accent);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 1rem;
        }}
        .diagram-nodes {{
            display: flex;
            align-items: center;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .diagram-node {{
            background: var(--deck-card-bg);
            border: 1px solid var(--deck-accent);
            border-radius: 12px;
            padding: 1rem 1.4rem;
            font-size: 1.15rem;
            font-weight: 500;
            color: var(--deck-ink);
            box-shadow: {card_shadow};
        }}
        .node-idx {{
            color: var(--deck-accent-alt);
            font-weight: 700;
            margin-right: 0.4rem;
        }}
        .diagram-arrow {{
            font-size: 1.5rem;
            color: var(--deck-accent);
        }}

        /* Blank Hero Visual */
        .blank-hero-layout {{
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hero-full-bleed {{
            max-width: 100%;
            max-height: 850px;
            border-radius: 20px;
            box-shadow: {card_shadow};
            object-fit: contain;
        }}
        .hero-overlay-card {{
            position: absolute;
            bottom: 2.5rem;
            left: 2.5rem;
            background: rgba(255, 255, 255, 0.9) if mode == "light" else rgba(11, 17, 30, 0.9);
            backdrop-filter: blur(12px);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            border: 1px solid var(--deck-card-border);
            max-width: 600px;
        }}

        /* Progress Bar & Controls */
        .reveal .progress {{
            height: 5px;
            color: var(--deck-accent);
        }}
        .reveal .slide-number {{
            font-family: var(--font-family);
            font-size: 1rem;
            color: var(--deck-ink-muted);
            right: 2rem;
            bottom: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            {slides_content}
        </div>
    </div>

    <!-- Reveal.js Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/reveal.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/plugin/notes/notes.min.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            slideNumber: 'c/t',
            width: 1920,
            height: 1080,
            margin: 0.04,
            minScale: 0.2,
            maxScale: 2.0,
            transition: 'slide',
            plugins: [ RevealNotes ]
        }});
    </script>
</body>
</html>
'''
    if not output_path:
        output_path = os.path.join(spec_dir, "deck.html")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Presentation deck built: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder.py <spec_file.yaml> [output_deck.html]")
        sys.exit(1)
    spec_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    build_deck(spec_arg, out_arg)
