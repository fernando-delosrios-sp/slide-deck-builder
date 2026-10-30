#!/usr/bin/env python3
import os
import sys
import yaml
import base64
import re
from style_parser import parse_style
from icons import get_icon_svg
import jinja2

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True
)

def clean_bullet(text):
    """
    Strips leading string character bullets (•, -, *, etc.) from bullet items,
    preferring HTML/CSS formatting bullets over inline string bullets.
    Avoids double bullet scenarios (e.g. • • Item or - • Item).
    """
    if not text or not isinstance(text, str):
        return text if text is not None else ""

    cleaned = text.strip()
    bullet_sym = r'(?:[\u2022\u2023\u2043\u2219\u00b7\u25cf\u25cb\u25aa\u25ab\u25a0\u25a1\u25c6\u25c7\u25ba\u25b8\u25b6•‣⁃∙·●○▪▫■□◆◇►▸▶]|\&bull\;|\&\#8226\;|\&\#x2022\;)'

    # 1. Strip standalone tags that only contain a bullet, e.g. <span>•</span> or <b>&bull;</b>
    cleaned = re.sub(r'^(?:<[a-zA-Z0-9]+[^>]*>\s*' + bullet_sym + r'\s*</[a-zA-Z0-9]+>\s*)+', '', cleaned)

    # 2. Repeatedly strip leading raw bullets or ascii markers (- , * , + , etc.)
    while True:
        m = re.match(r'^(?:' + bullet_sym + r'|[-*+–—]\s+)\s*', cleaned)
        if m:
            cleaned = cleaned[m.end():]
        else:
            break

    # 3. Strip bullet immediately following an opening tag: <strong>• UC-05... -> <strong>UC-05...
    m_tag = re.match(r'^(<[a-zA-Z0-9]+[^>]*>)\s*(?:' + bullet_sym + r'|[-*+–—]\s+)\s*', cleaned)
    if m_tag:
        tag = m_tag.group(1)
        rest = cleaned[m_tag.end():]
        cleaned = tag + rest

    return cleaned.strip()

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
                <div class="mini-image-wrapper">
                    <div class="mini-image-card"><img src="{img_src}" alt="{img_alt}" class="mini-image-thumb" /></div>
                    {f'<span class="mini-image-caption">{img_caption}</span>' if img_caption else ''}
                </div>
            ''')

        # Agenda / Stepper
        if "agenda" in layout.lower() or role == "agenda":
            raw_cards = content.get("cards", [])
            raw_agenda = content.get("agenda", [])
            raw_bullets = content.get("bullets", [])
            items = raw_cards or raw_agenda or raw_bullets
            mini_steps = []
            for idx, itm in enumerate(items[:5], 1):
                if isinstance(itm, dict):
                    t = itm.get("title", "")
                elif isinstance(itm, str):
                    t = clean_bullet(itm.split(":", 1)[0].split(" — ", 1)[0].split(" - ", 1)[0].strip())
                else:
                    t = str(itm)
                mini_steps.append(f'<div class="mini-agenda-step"><span class="mini-step-num">{idx:02d}</span><span class="mini-step-text">{t}</span></div>')
            content_preview_html.append(f'<div class="mini-agenda-list">{"".join(mini_steps)}</div>')
        else:
            # Bullets
            bullets = content.get("bullets", [])
            if bullets:
                b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in bullets[:4]])
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
                m_icon = m.get("icon")
                m_icon_svg = get_icon_svg(m_icon, stroke_width="1.75", size="18px") if m_icon else ""
                m_icon_html = f'<div class="mini-metric-icon">{m_icon_svg}</div>' if m_icon_svg else ''
                m_items.append(f'''
                    <div class="mini-metric-card{glow}">
                        {m_icon_html}
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
                c_icon = c.get("icon")
                icon_svg = get_icon_svg(c_icon, stroke_width="1.75", size="18px") if c_icon else ""
                icon_html = f'<span class="mini-card-icon">{icon_svg}</span>' if icon_svg else ''
                c_items.append(f'''
                    <div class="mini-content-card">
                        <div class="mini-card-top">
                            {icon_html}
                            {f'<span class="card-tag">{c_badge}</span>' if c_badge else ''}
                        </div>
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
            left_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in left.get("bullets", [])[:2]])
            right_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in right.get("bullets", [])[:2]])
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
                r_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in r.get("bullets", [])[:2]])
                r_cards = r.get("cards", [])
                r_cards_html = ""
                if r_cards:
                    c_list = "".join([f'<div style="font-size:0.75rem; margin-top:0.25rem;">• <strong>{c.get("title", "")}</strong></div>' for c in r_cards[:2]])
                    r_cards_html = f'<div class="mini-cards-sub">{c_list}</div>'
                r_items.append(f'''
                    <div class="mini-content-card">
                        {f'<strong>{r_title}</strong>' if r_title else ''}
                        {f'<ul class="mini-bullets">{r_bullets}</ul>' if r_bullets else ''}
                        {r_cards_html}
                    </div>
                ''')
            content_preview_html.append(f'<div class="mini-regions-grid">{"".join(r_items)}</div>')

        # Two Content / Left & Right columns
        left_col = content.get("left") or content.get("col1")
        right_col = content.get("right") or content.get("col2")
        if (left_col or right_col) and not comparison and not regions:
            def render_mini_col(col_data):
                if not col_data:
                    return ""
                if isinstance(col_data, str):
                    return f'<p style="font-size:0.8rem; line-height:1.3;">{col_data[:70]}...</p>'
                if isinstance(col_data, list):
                    b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in col_data[:2]])
                    return f'<ul class="mini-bullets">{b_items}</ul>'

                parts = []
                c_title = col_data.get("title", "")
                c_badge = col_data.get("badge", "")
                bullets = col_data.get("bullets", [])
                img = col_data.get("image") or col_data.get("media_ref") or col_data.get("src")

                if c_badge:
                    parts.append(f'<span class="card-tag">{c_badge}</span>')
                if c_title:
                    parts.append(f'<strong>{c_title}</strong>')
                if img:
                    img_raw = img.get("src", "") if isinstance(img, dict) else img
                    img_s = resolve_image_src(img_raw, spec_dir)
                    if img_s:
                        parts.append(f'<div class="mini-image-card"><img src="{img_s}" class="mini-image-thumb" /></div>')
                if bullets:
                    b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in bullets[:2]])
                    parts.append(f'<ul class="mini-bullets">{b_items}</ul>')
                return "".join(parts)

            l_mini = render_mini_col(left_col)
            r_mini = render_mini_col(right_col)
            content_preview_html.append(f'''
                <div class="mini-regions-grid">
                    <div class="mini-content-card">{l_mini}</div>
                    <div class="mini-content-card">{r_mini}</div>
                </div>
            ''')

        # Chart
        chart = content.get("chart")
        if chart:
            c_type = chart.get("type", "chart").capitalize()
            c_labels = chart.get("labels", [])
            c_ds = chart.get("datasets", [])
            chart_icon_svg = get_icon_svg("bar-chart-3" if c_type.lower() == "bar" else ("pie-chart" if c_type.lower() in ("pie", "doughnut") else "trending-up"), stroke_width="1.75", size="18px")
            content_preview_html.append(f'''
                <div class="mini-chart-card" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.65rem 0.85rem; border-radius: 8px; background: rgba(84, 192, 232, 0.08); border: 1px solid rgba(84, 192, 232, 0.2); font-size: 0.85rem; margin-top: 0.4rem;">
                    {chart_icon_svg}
                    <strong style="color: {accent_color};">{c_type} Chart</strong>
                    <span class="card-tag" style="margin-left: auto;">{len(c_ds)} series &bull; {len(c_labels)} items</span>
                </div>
            ''')

        # Mermaid / SVG / Diagram
        diagram = content.get("diagram", {})
        svg_code = content.get("svg") or (diagram.get("svg") if isinstance(diagram, dict) else "")
        svg_src = diagram.get("src") or diagram.get("file") if isinstance(diagram, dict) else ""
        mermaid_code = content.get("mermaid") or (diagram.get("mermaid") if isinstance(diagram, dict) else "")
        if svg_code or svg_src or (isinstance(diagram, dict) and diagram.get("kind") == "svg"):
            d_title = diagram.get("title", "Architecture SVG Diagram") if isinstance(diagram, dict) else "Architecture SVG Diagram"
            content_preview_html.append(f'''
                <div class="mini-diagram-box">
                    <div class="diagram-title">⬡ {d_title} (SVG ARCHITECTURE)</div>
                    <div class="diagram-chips"><span class="diagram-chip">High-Fidelity SVG</span><span class="diagram-chip">Vector Diagram</span></div>
                </div>
            ''')
        elif diagram:
            d_kind = diagram.get("kind", "diagram")
            d_title = diagram.get("title", f"{d_kind.title()} Architecture")
            chips = []
            if d_kind == "pipeline":
                chips = [s.get("title", "") for s in diagram.get("stages", [])]
            elif d_kind in ["dual_track", "convergence"]:
                chips = [t.get("name", "") for t in diagram.get("tracks", [])] + [diagram.get("hub", {}).get("title", "Unified Hub")]
            elif d_kind == "cardinality":
                chips = [s.get("name", "") for s in diagram.get("sources", [])] + [diagram.get("profiles", {}).get("title", "Access Profiles"), diagram.get("roles", {}).get("title", "Roles")]
            elif d_kind in ["policy_flow", "abac"]:
                chips = ["Attributes", "Policy Engine", diagram.get("role", {}).get("title", "Role"), "Provisioning"]
            elif d_kind == "layered_stack":
                chips = [f"{l.get('tier')}: {l.get('title')}" for l in diagram.get("layers", [])]
            else:
                chips = diagram.get("elements", [])

            chips_html = "".join([f'<span class="diagram-chip">{c}</span>' for c in chips[:5]])
            content_preview_html.append(f'''
                <div class="mini-diagram-box">
                    <div class="diagram-title">⬡ {d_title} ({d_kind.upper()})</div>
                    <div class="diagram-chips">{chips_html}</div>
                </div>
            ''')
        elif mermaid_code:
            content_preview_html.append(f'''
                <div class="mini-mermaid-box">
                    <div class="diagram-title">⬡ Mermaid Architecture Diagram</div>
                    <pre class="mermaid">{mermaid_code.strip()}</pre>
                </div>
            ''')

        content_body = "".join(content_preview_html)

        slides_html.append(jinja_env.get_template("preview_card.html").render(
            num=num,
            layout=layout,
            role=role,
            stitle=stitle,
            subtitle=subtitle,
            content_body=content_body,
            notes=notes
        ))

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

    preview_css = jinja_env.get_template("preview.css").render({
        "bg_color": bg_color,
        "surface_color": surface_color,
        "card_bg": card_bg,
        "card_border": card_border,
        "accent_color": accent_color,
        "accent_alt": accent_alt,
        "ink_color": ink_color,
        "ink_muted": ink_muted,
        "font_family": font_family,
        "preview_bg": preview_bg,
        "header_bg": header_bg,
        "header_shadow": header_shadow,
        "card_bg_val": card_bg_val,
        "card_shadow": card_shadow,
        "goal_bg": goal_bg,
    })

    html = jinja_env.get_template("preview.html").render({
        "title": title,
        "google_font": google_font,
        "preview_css": preview_css,
        "theme_name": theme_name,
        "mode": mode,
        "slide_count": slide_count,
        "audience": audience,
        "tone": tone,
        "goal": goal,
        "cards_joined": cards_joined,
    })
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
