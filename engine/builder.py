#!/usr/bin/env python3
import os
import sys
import yaml
import json
import base64
import re
import jinja2
from style_parser import parse_style
from icons import get_icon_svg

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

def render_native_architecture_diagram(diagram, mermaid_code="", spec_dir="", svg_code=""):
    """
    Renders high-fidelity, theme-colored native architecture diagram components via Jinja2 partials.
    Guarantees 100% theme color compliance, typography scaling, and zero layout/clipping bugs.
    """
    if not diagram and not mermaid_code and not svg_code:
        return ""
    
    kind = diagram.get("kind", "") if isinstance(diagram, dict) else ""
    has_custom_title = isinstance(diagram, dict) and bool(diagram.get("title"))
    has_custom_badge = isinstance(diagram, dict) and bool(diagram.get("badge"))
    show_header = has_custom_title or has_custom_badge
    diag_title = diagram.get("title", "") if isinstance(diagram, dict) else ""

    
    # 0. High-Fidelity SVG Diagram Component (Standalone SVG file, inline SVG, or kind: svg)
    if kind == "svg" or (isinstance(diagram, dict) and (diagram.get("svg") or diagram.get("src") or diagram.get("file"))) or svg_code:
        svg_markup = ""
        badge_text = ""
        if isinstance(diagram, dict) and diagram.get("badge"):
            badge_text = diagram.get("badge")
        elif isinstance(diagram, dict) and diagram.get("kind") and diagram.get("kind") != "svg":
            badge_text = f"{diagram.get('kind').title()} Blueprint"

        if isinstance(diagram, dict) and diagram.get("svg"):
            svg_markup = diagram.get("svg")
        elif svg_code:
            svg_markup = svg_code
        elif isinstance(diagram, dict) and (diagram.get("src") or diagram.get("file")):
            f_path = diagram.get("src") or diagram.get("file")
            abs_p = f_path if os.path.isabs(f_path) else os.path.join(spec_dir, f_path)
            if os.path.exists(abs_p) and abs_p.endswith(".svg"):
                with open(abs_p, "r", encoding="utf-8") as sf:
                    svg_markup = sf.read()
            elif os.path.exists(abs_p):
                res_src = resolve_image_src(f_path, spec_dir)
                svg_markup = f'<img src="{res_src}" alt="{diag_title}" class="arch-svg-img" />'

        if svg_markup:
            return jinja_env.get_template("diagrams/svg.html").render(
                diag_title=diag_title,
                badge_text=badge_text,
                show_header=show_header,
                svg_markup=svg_markup
            )

    # 1. Pipeline Flow Architecture (e.g. Identity Object Hierarchy)
    if kind == "pipeline":
        stages_data = []
        for i, st in enumerate(diagram.get("stages", [])):
            stages_data.append({
                "highlight": bool(st.get("highlight")),
                "num": st.get("step", f"0{i+1}"),
                "title": st.get("title", ""),
                "badge": st.get("badge"),
                "desc": st.get("desc"),
            })
        trigger_data = diagram.get("trigger", {})
        return jinja_env.get_template("diagrams/pipeline.html").render(
            diag_title=diag_title,
            badge_text="Deterministic Lineage",
            stages=stages_data,
            trigger=trigger_data
        )

    # 2. Dual-Track Convergence Architecture (Human vs Machine Governance)
    elif kind in ["dual_track", "convergence"]:
        tracks_data = []
        for t in diagram.get("tracks", []):
            t_icon_src = resolve_image_src(t.get("icon_src", ""), spec_dir)
            tracks_data.append({
                "highlight": bool(t.get("highlight")),
                "name": t.get("name", ""),
                "badge": t.get("badge"),
                "icon_src": t_icon_src,
                "steps": t.get("steps", [])
            })
        hub_data = diagram.get("hub", {})
        return jinja_env.get_template("diagrams/convergence.html").render(
            diag_title=diag_title,
            badge_text="Unified Governance Hub",
            tracks=tracks_data,
            hub=hub_data
        )

    # 3. Cardinality Architecture (Slide 4: 1:N Profiles & N:M Roles)
    elif kind == "cardinality":
        sources_data = []
        for s in diagram.get("sources", []):
            sources_data.append({
                "name": s.get("name", ""),
                "badge": s.get("badge"),
                "items": s.get("items", [])
            })
        profiles_data = diagram.get("profiles", {})
        roles_data = diagram.get("roles", {})
        return jinja_env.get_template("diagrams/cardinality.html").render(
            diag_title=diag_title,
            badge_text="Data Model Cardinality",
            sources=sources_data,
            profiles=profiles_data,
            roles=roles_data
        )

    # 4. Policy Flow / Dynamic ABAC Architecture (Slide 5)
    elif kind in ["policy_flow", "abac"]:
        inputs_data = diagram.get("inputs", {})
        engine_data = diagram.get("engine", {})
        role_data = diagram.get("role", {})
        prov_data = diagram.get("provisions", {})
        return jinja_env.get_template("diagrams/policy_flow.html").render(
            diag_title=diag_title,
            badge_text="Dynamic ABAC Execution",
            inputs=inputs_data,
            engine=engine_data,
            role=role_data,
            provisions=prov_data
        )

    # 5. Layered Stack Architecture (Slide 6: PoV Architecture)
    elif kind == "layered_stack":
        layers_data = []
        for l in diagram.get("layers", []):
            layers_data.append({
                "accent": l.get("accent", "blue"),
                "highlight": bool(l.get("highlight")),
                "tier": l.get("tier", ""),
                "badge": l.get("badge"),
                "title": l.get("title", ""),
                "desc": l.get("desc", "")
            })
        return jinja_env.get_template("diagrams/layered_stack.html").render(
            diag_title=diag_title,
            badge_text="Proof-of-Value Stack",
            layers=layers_data
        )

    # 6. Fallback Mermaid or Generic Flow
    elif mermaid_code:
        clean_mermaid = mermaid_code.strip().replace("&", "&amp;")
        return jinja_env.get_template("diagrams/mermaid.html").render(clean_mermaid=clean_mermaid)
        
    elif isinstance(diagram, dict) and diagram.get("elements"):
        return jinja_env.get_template("diagrams/generic_flow.html").render(
            d_kind=diagram.get("kind", "flow"),
            elements=diagram.get("elements", [])
        )
        
    return ""

def render_chart_canvas(chart_def, style, mode="dark"):
    """
    Renders a <canvas data-chart="..."> element with an embedded JSON comment
    conforming to reveal.js-plugins/chart and Chart.js.
    """
    if not chart_def or not isinstance(chart_def, dict):
        return ""

    chart_type = chart_def.get("type", "bar")
    labels = chart_def.get("labels", [])
    raw_datasets = chart_def.get("datasets", [])
    options_override = chart_def.get("options", {}) or {}

    colors = style.get("colors", {})
    accent_color = colors.get("accent", "#2563EB" if mode == "light" else "#54C0E8")
    accent_alt = colors.get("accent-alt", "#D60EB5")

    # Harmonious palette cycle derived from theme
    palette = [
        accent_color,
        accent_alt,
        "#10B981",
        "#F59E0B",
        "#8B5CF6",
        "#06B6D4",
        "#EC4899",
        "#3B82F6"
    ]

    def resolve_color(c, default):
        if not c:
            return default
        c_str = str(c).strip()
        if c_str == "accent":
            return accent_color
        if c_str == "accent-alt":
            return accent_alt
        return c_str

    datasets = []
    is_circular = chart_type in ("pie", "doughnut", "polarArea")

    for i, ds in enumerate(raw_datasets):
        if not isinstance(ds, dict):
            continue
        ds_copy = dict(ds)
        user_color = ds_copy.pop("color", None)
        chosen_color = resolve_color(user_color, palette[i % len(palette)])

        if is_circular:
            data_len = len(ds_copy.get("data", []))
            if "backgroundColor" not in ds_copy:
                ds_copy["backgroundColor"] = [palette[j % len(palette)] for j in range(data_len)]
            if "borderColor" not in ds_copy:
                ds_copy["borderColor"] = colors.get("surface", "#0B111E" if mode == "dark" else "#F0F3F6")
            if "borderWidth" not in ds_copy:
                ds_copy["borderWidth"] = 2
        else:
            if "borderColor" not in ds_copy:
                ds_copy["borderColor"] = chosen_color
            if "backgroundColor" not in ds_copy:
                if chart_type == "line":
                    if ds_copy.get("fill"):
                        # Transparent fill
                        ds_copy["backgroundColor"] = f"{chosen_color}33" if chosen_color.startswith("#") and len(chosen_color) == 7 else "rgba(84, 192, 232, 0.2)"
                    else:
                        ds_copy["backgroundColor"] = "transparent"
                else:
                    ds_copy["backgroundColor"] = f"{chosen_color}CC" if chosen_color.startswith("#") and len(chosen_color) == 7 else chosen_color
            if "borderWidth" not in ds_copy:
                ds_copy["borderWidth"] = 2

        datasets.append(ds_copy)

    # Base Chart.js configuration
    chart_json = {
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {
                    "display": options_override.get("legend", True),
                    "labels": {
                        "color": colors.get("ink-muted", "#DAE1E9" if mode == "dark" else "#4b5563"),
                        "font": {
                            "size": 14
                        }
                    }
                }
            }
        }
    }

    # Add axis scales for cartesian charts
    if not is_circular:
        is_stacked = bool(options_override.get("stacked", False))
        chart_json["options"]["scales"] = {
            "x": {
                "stacked": is_stacked,
                "grid": {
                    "color": colors.get("card-border", "#415364" if mode == "dark" else "#e2e8f0"),
                    "drawBorder": False
                },
                "ticks": {
                    "color": colors.get("ink-muted", "#DAE1E9" if mode == "dark" else "#4b5563"),
                    "font": { "size": 13 }
                }
            },
            "y": {
                "stacked": is_stacked,
                "grid": {
                    "color": colors.get("card-border", "#415364" if mode == "dark" else "#e2e8f0"),
                    "drawBorder": False
                },
                "ticks": {
                    "color": colors.get("ink-muted", "#DAE1E9" if mode == "dark" else "#4b5563"),
                    "font": { "size": 13 }
                }
            }
        }

    # Pass remaining overrides
    for k, v in options_override.items():
        if k not in ("legend", "stacked"):
            chart_json["options"][k] = v

    json_str = json.dumps(chart_json, indent=2)

    return f'''
        <div class="slide-chart-wrapper">
            <canvas data-chart="{chart_type}">
<!--
{json_str}
-->
            </canvas>
        </div>
    '''

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

    # Iconography theme configuration
    iconography = style.get("components", {}).get("iconography", {})
    icon_stroke_width = str(iconography.get("strokeWidth", "1.75")).replace("px", "").strip()
    icon_default_color = iconography.get("color", accent_color)
    icon_alt_color = iconography.get("colorHighlight", accent_alt)
    icon_size = iconography.get("size", "26px")
    icon_container = iconography.get("container", "badge")
    icon_badge_bg = iconography.get("badgeBackground", "rgba(84, 192, 232, 0.12)" if mode == "dark" else "rgba(37, 99, 235, 0.08)")
    icon_badge_border = iconography.get("badgeBorder", "rgba(84, 192, 232, 0.25)" if mode == "dark" else "rgba(37, 99, 235, 0.2)")
    icon_badge_glow = iconography.get("badgeGlow", f"0 0 16px {accent_color}33")

    deck_title = spec.get("title", "Presentation")
    slides = spec.get("slides", [])

    # Theme CSS variables & background setup
    css_vars = style.get("css_variables", {})
    if "--deck-bg-gradient" in css_vars:
        bg_gradient = css_vars["--deck-bg-gradient"]
    elif "--theme-bg-gradient" in css_vars:
        bg_gradient = css_vars["--theme-bg-gradient"]
    elif "--sp-bg-gradient" in css_vars:
        bg_gradient = css_vars["--sp-bg-gradient"]
    elif mode == "light":
        bg_gradient = f"linear-gradient(135deg, {bg_color} 0%, {surface_color} 60%, {surface_soft} 100%)"
    else:
        bg_gradient = f"radial-gradient(circle at 85% 15%, {accent_color}33 0%, {surface_color} 50%, {bg_color} 100%)"

    extra_css_vars = "\n            ".join([f"{k}: {v};" for k, v in css_vars.items() if not k.startswith("--deck-")])

    # Logo resolution: explicit in spec, theme default, or suppressed with 'none'
    logo_data_uri = None
    spec_logo = spec.get("logo")
    if spec_logo and str(spec_logo).strip().lower() in ("none", "false", "no", "null"):
        logo_target = None
    else:
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
                <div class="slide-image-wrapper">
                    <div class="slide-image-card"><img src="{img_src}" alt="{img_alt}" class="slide-embedded-image" /></div>
                    {caption_tag}
                </div>
            '''

        body_parts = []

        # 1. Cover slide layout
        if "title-slide" in layout_slug or "cover" in layout_slug:
            presenter_val = content.get("presenter", "")
            date_val = content.get("date", "")
            body_val = content.get("body", "")

            # Detect if image is a logo or small icon
            raw_img_path = slide_image.get("src", "") if isinstance(slide_image, dict) else (slide_image if isinstance(slide_image, str) else "")
            is_logo = False
            is_small_icon = False
            if raw_img_path:
                path_lower = raw_img_path.lower()
                alt_lower = (img_alt or "").lower()
                if "logo" in path_lower or "logo" in alt_lower or "image2.svg" in path_lower:
                    is_logo = True
                elif path_lower.endswith(".svg"):
                    abs_img = raw_img_path if os.path.isabs(raw_img_path) else os.path.join(spec_dir, raw_img_path)
                    if os.path.exists(abs_img) and os.path.getsize(abs_img) < 4000:
                        is_small_icon = True

            cover_logo_html = ""
            cover_hero_html = ""
            if img_src:
                if is_logo:
                    cover_logo_html = f'<div class="cover-brand-logo-wrapper"><img src="{img_src}" alt="{img_alt}" class="cover-brand-logo" /></div>'
                elif is_small_icon:
                    cover_hero_html = f'''
                        <div class="cover-media-container icon-container">
                            <div class="cover-icon-badge-box">
                                <img src="{img_src}" alt="{img_alt}" class="cover-accent-icon" />
                                {f'<span class="cover-icon-label">{img_caption or img_alt}</span>' if (img_caption or img_alt) else ''}
                            </div>
                        </div>
                    '''
                else:
                    cover_hero_html = f'''
                        <div class="cover-media-container">
                            <img src="{img_src}" alt="{img_alt}" class="cover-hero-image" />
                        </div>
                    '''
            elif logo_data_uri:
                cover_logo_html = f'<div class="cover-brand-logo-wrapper"><img src="{logo_data_uri}" alt="Brand Logo" class="cover-brand-logo" /></div>'

            bullets_list = content.get("bullets", [])
            cover_bullets_html = ""
            if bullets_list:
                bullets_items = "".join([f'<li>{clean_bullet(b)}</li>' for b in bullets_list])
                cover_bullets_html = f'<ul class="cover-bullets">{bullets_items}</ul>'

            body_val_html = body_val.replace("\n", "<br/>") if body_val else ""

            meta_items = []
            if presenter_val:
                meta_items.append({"label": "Presenter", "val": presenter_val})
            if date_val:
                meta_items.append({"label": "Date", "val": date_val})
            if badge:
                meta_items.append({"label": "Series", "val": badge})

            body_parts.append(jinja_env.get_template("slides/cover.html").render(
                cover_hero_html=cover_hero_html,
                cover_logo_html=cover_logo_html,
                badge_html=badge_html,
                title=title,
                subtitle=subtitle,
                body_val_html=body_val_html,
                cover_bullets_html=cover_bullets_html,
                meta_items=meta_items
            ))

        # 2. Section Header layout
        elif "section-header" in layout_slug:
            body_parts.append(jinja_env.get_template("slides/section_header.html").render(
                badge_html=badge_html,
                title=title,
                subtitle=subtitle,
                body=content.get("body", "")
            ))

        # 3. Blank layout (Hero Visual)
        elif "blank" in layout_slug:
            body_parts.append(jinja_env.get_template("slides/blank_hero.html").render(
                img_src=img_src,
                img_alt=img_alt,
                badge_html=badge_html,
                title=title,
                subtitle=subtitle,
                body=content.get("body", "")
            ))

        # 4. Agenda layout (Modern Executive Stepper)
        elif "agenda" in layout_slug or role == "agenda":
            agenda_items = []
            raw_cards = content.get("cards", [])
            raw_agenda = content.get("agenda", [])
            raw_bullets = content.get("bullets", [])

            raw_items = raw_cards or raw_agenda or raw_bullets
            for idx, item in enumerate(raw_items, 1):
                step_num = f"{idx:02d}"
                item_badge = ""
                highlight_cls = False

                if isinstance(item, dict):
                    item_title = item.get("title", "")
                    item_desc = item.get("body", item.get("desc", ""))
                    item_badge = item.get("badge", "")
                    if item.get("highlight"):
                        highlight_cls = True
                elif isinstance(item, str):
                    if ":" in item:
                        parts = item.split(":", 1)
                        item_title = clean_bullet(parts[0].strip())
                        item_desc = parts[1].strip()
                    elif " — " in item:
                        parts = item.split(" — ", 1)
                        item_title = clean_bullet(parts[0].strip())
                        item_desc = parts[1].strip()
                    elif " - " in item:
                        parts = item.split(" - ", 1)
                        item_title = clean_bullet(parts[0].strip())
                        item_desc = parts[1].strip()
                    else:
                        item_title = clean_bullet(item)
                        item_desc = ""
                else:
                    item_title = str(item)
                    item_desc = ""

                agenda_items.append({
                    "step_num": step_num,
                    "title": item_title,
                    "desc": item_desc,
                    "badge": item_badge,
                    "highlight": highlight_cls
                })

            body_parts.append(jinja_env.get_template("slides/agenda.html").render(
                badge_html=badge_html,
                title=title,
                subtitle=subtitle,
                agenda_items=agenda_items
            ))

        # 5. Standard Content Layouts (Title and Content, Two Content, Comparison, Three Columns, Picture with Caption, etc.)
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
                b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in bullets])
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
                    m_icon = m.get("icon")
                    m_icon_html = ""
                    if m_icon:
                        svg_code = get_icon_svg(
                            m_icon,
                            stroke_width=icon_stroke_width,
                            stroke_color="currentColor",
                            size="24px"
                        )
                        if svg_code:
                            m_icon_html = f'<div class="metric-icon-badge">{svg_code}</div>'
                    m_cards.append(f'''
                        <div class="metric-card{glow_cls}">
                            {m_icon_html}
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
                    c_icon = c.get("icon")
                    icon_html = ""
                    if c_icon:
                        svg_code = get_icon_svg(
                            c_icon,
                            stroke_width=icon_stroke_width,
                            stroke_color="currentColor",
                            size=icon_size
                        )
                        if svg_code:
                            container_cls = " bare" if icon_container == "none" else (" circle" if icon_container == "circle" else "")
                            icon_html = f'<div class="card-icon-container{container_cls}">{svg_code}</div>'

                    top_row = ""
                    if icon_html or c_badge:
                        top_row = f'''
                            <div class="card-header-row">
                                {icon_html if icon_html else "<div></div>"}
                                {c_badge}
                            </div>
                        '''

                    c_cards.append(f'''
                        <div class="feature-card{c_glow}">
                            {top_row}
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
                l_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in left.get("bullets", [])])
                r_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in right.get("bullets", [])])
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
                    r_badge = f'<span class="card-badge">{r.get("badge")}</span>' if r.get("badge") else ''
                    r_title = f'<h3 class="region-title">{r.get("title")}</h3>' if r.get("title") else ''
                    r_body = f'<p class="region-body">{r.get("body")}</p>' if r.get("body") else ''
                    r_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in r.get("bullets", [])])
                    
                    # Check if region has media
                    reg_media = ""
                    reg_src = r.get("media_ref") or r.get("src") or r.get("image")
                    if reg_src or r.get("kind") == "media":
                        res_src = resolve_image_src(reg_src, spec_dir)
                        if res_src:
                            reg_media = f'<div class="region-image-wrapper"><img src="{res_src}" alt="{r.get("title", "Visual")}" class="region-image" /></div>'
                    
                    # Check if region has cards
                    reg_cards_html = ""
                    reg_cards = r.get("cards", [])
                    if reg_cards:
                        c_cards = []
                        for c in reg_cards:
                            c_b = f'<span class="card-badge">{c.get("badge")}</span>' if c.get("badge") else ''
                            c_g = ' glowing' if c.get("highlight") else ''
                            c_i = c.get("icon")
                            i_html = ""
                            if c_i:
                                svg_code = get_icon_svg(c_i, stroke_width=icon_stroke_width, stroke_color="currentColor", size=icon_size)
                                if svg_code:
                                    container_cls = " bare" if icon_container == "none" else (" circle" if icon_container == "circle" else "")
                                    i_html = f'<div class="card-icon-container{container_cls}">{svg_code}</div>'
                            t_row = f'<div class="card-header-row">{i_html if i_html else "<div></div>"}{c_b}</div>' if (i_html or c_b) else ''
                            c_cards.append(f'''
                                <div class="feature-card{c_g}">
                                    {t_row}
                                    <h3 class="card-title">{c.get("title", "")}</h3>
                                    <p class="card-body">{c.get("body", "")}</p>
                                </div>
                            ''')
                        reg_cards_html = f'<div class="cards-grid count-{len(reg_cards)}">{"".join(c_cards)}</div>'

                    col_classes = ["region-col"]
                    if reg_media:
                        col_classes.append("has-media")
                    if r_bullets:
                        col_classes.append("has-bullets")
                    if reg_cards:
                        col_classes.append("has-cards")
                    col_cls = " ".join(col_classes)

                    r_cols.append(f'''
                        <div class="{col_cls}">
                            {r_badge}
                            {r_title}
                            {reg_media}
                            {r_body}
                            {f'<ul class="styled-bullets">{r_bullets}</ul>' if r_bullets else ''}
                            {reg_cards_html}
                        </div>
                    ''')
                content_blocks.append(f'<div class="regions-container count-{len(regions)}">{"".join(r_cols)}</div>')

            # Two Content / Left & Right Columns
            left_col = content.get("left") or content.get("col1")
            right_col = content.get("right") or content.get("col2")
            if (left_col or right_col) and not comparison and not regions:
                def render_col_content(col_data):
                    if not col_data:
                        return "", False, False
                    if isinstance(col_data, str):
                        return f'<p class="slide-body-text">{col_data}</p>', False, False
                    if isinstance(col_data, list):
                        b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in col_data])
                        return f'<ul class="styled-bullets">{b_items}</ul>', False, True

                    title = col_data.get("title", "")
                    badge = col_data.get("badge", "")
                    body = col_data.get("body", "")
                    bullets = col_data.get("bullets", [])
                    cards = col_data.get("cards", [])
                    img = col_data.get("image") or col_data.get("media_ref") or col_data.get("src")

                    parts = []
                    if badge:
                        parts.append(f'<span class="card-badge">{badge}</span>')
                    if title:
                        parts.append(f'<h3 class="card-title region-title">{title}</h3>')

                    has_media = False
                    if img:
                        img_s = ""
                        img_a = title or "Visual"
                        img_c = ""
                        if isinstance(img, dict):
                            img_s = resolve_image_src(img.get("src", ""), spec_dir)
                            img_a = img.get("alt", img_a)
                            img_c = img.get("caption", "")
                        elif isinstance(img, str):
                            img_s = resolve_image_src(img, spec_dir)
                            img_c = col_data.get("caption", "")

                        if img_s:
                            has_media = True
                            parts.append(f'''
                                <div class="slide-image-wrapper">
                                    <div class="console-mockup-frame">
                                        <div class="console-titlebar">
                                            <div class="console-dots">
                                                <span class="console-dot dot-red"></span>
                                                <span class="console-dot dot-yellow"></span>
                                                <span class="console-dot dot-green"></span>
                                            </div>
                                            <span class="console-title-text">{img_c or img_a}</span>
                                        </div>
                                        <div class="console-body">
                                            <img src="{img_s}" alt="{img_a}" class="slide-embedded-image" />
                                        </div>
                                    </div>
                                </div>
                            ''')

                    if body:
                        parts.append(f'<p class="slide-body-text">{body}</p>')

                    has_bullets = False
                    if bullets:
                        has_bullets = True
                        b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in bullets])
                        parts.append(f'<ul class="styled-bullets">{b_items}</ul>')

                    if cards:
                        c_cards = []
                        for c in cards:
                            c_b = f'<span class="card-badge">{c.get("badge")}</span>' if c.get("badge") else ''
                            c_g = ' glowing' if c.get("highlight") else ''
                            c_i = c.get("icon")
                            i_html = ""
                            if c_i:
                                svg_code = get_icon_svg(c_i, stroke_width=icon_stroke_width, stroke_color="currentColor", size=icon_size)
                                if svg_code:
                                    container_cls = " bare" if icon_container == "none" else (" circle" if icon_container == "circle" else "")
                                    i_html = f'<div class="card-icon-container{container_cls}">{svg_code}</div>'
                            t_row = f'<div class="card-header-row">{i_html if i_html else "<div></div>"}{c_b}</div>' if (i_html or c_b) else ''
                            c_cards.append(f'''
                                <div class="feature-card{c_g}">
                                    {t_row}
                                    <h3 class="card-title">{c.get("title", "")}</h3>
                                    <p class="card-body">{c.get("body", "")}</p>
                                </div>
                            ''')
                        parts.append(f'<div class="cards-grid count-{len(cards)}">{"".join(c_cards)}</div>')

                    return "".join(parts), has_media, has_bullets

                l_html, l_media, l_bullets = render_col_content(left_col)
                r_html, r_media, r_bullets = render_col_content(right_col)

                if l_media and not r_media:
                    container_cls = "two-content-container media-left"
                    l_cls = "two-content-col media-col"
                    r_cls = "two-content-col text-col"
                elif r_media and not l_media:
                    container_cls = "two-content-container media-right"
                    l_cls = "two-content-col text-col"
                    r_cls = "two-content-col media-col"
                elif l_media and r_media:
                    container_cls = "two-content-container side-by-side-proof"
                    l_cls = "two-content-col region-col proof-card proof-left"
                    r_cls = "two-content-col region-col proof-card proof-right glowing"
                else:
                    container_cls = "two-content-container text-cols"
                    l_cls = "two-content-col region-col"
                    r_cls = "two-content-col region-col"

                content_blocks.append(f'''
                    <div class="{container_cls}">
                        <div class="{l_cls}">
                            {l_html}
                        </div>
                        <div class="{r_cls}">
                            {r_html}
                        </div>
                    </div>
                ''')

            # Diagram / Architecture Rendering
            diagram = content.get("diagram", {})
            svg_content_field = content.get("svg", "")
            mermaid_code = content.get("mermaid") or (diagram.get("mermaid") if isinstance(diagram, dict) else "")

            diag_html = ""
            if diagram or mermaid_code or svg_content_field:
                diag_html = render_native_architecture_diagram(diagram, mermaid_code, spec_dir, svg_code=svg_content_field)

            if diag_html:
                # Dedicated Architecture Slide Layout (Sidebar for Cards/Icon + Full Right Canvas for Diagram)
                sidebar_items = []

                cards = content.get("cards", [])
                if cards:
                    c_cards = []
                    for c in cards:
                        c_badge = f'<span class="card-badge">{c.get("badge")}</span>' if c.get("badge") else ''
                        c_glow = ' glowing' if c.get("highlight") else ''
                        c_icon = c.get("icon")
                        icon_html = ""
                        if c_icon:
                            svg_code = get_icon_svg(
                                c_icon,
                                stroke_width=icon_stroke_width,
                                stroke_color="currentColor",
                                size=icon_size
                            )
                            if svg_code:
                                container_cls = " bare" if icon_container == "none" else (" circle" if icon_container == "circle" else "")
                                icon_html = f'<div class="card-icon-container{container_cls}">{svg_code}</div>'

                        top_row = ""
                        if icon_html or c_badge:
                            top_row = f'''
                                <div class="card-header-row">
                                    {icon_html if icon_html else "<div></div>"}
                                    {c_badge}
                                </div>
                            '''

                        c_cards.append(f'''
                            <div class="feature-card{c_glow}">
                                {top_row}
                                <h3 class="card-title">{c.get("title", "")}</h3>
                                <p class="card-body">{c.get("body", "")}</p>
                            </div>
                        ''')
                    sidebar_items.append(f'<div class="arch-cards-stack">{"".join(c_cards)}</div>')

                regions = content.get("regions", [])
                if regions and not cards and not content.get("bullets"):
                    r_cards = []
                    for r in regions:
                        r_title = f'<h4 class="card-title">{r.get("title")}</h4>' if r.get("title") else ''
                        r_body = f'<p class="card-body">{r.get("body")}</p>' if r.get("body") else ''
                        r_bullets = "".join([f"<li>{clean_bullet(b)}</li>" for b in r.get("bullets", [])])
                        r_cards.append(f'''
                            <div class="feature-card">
                                {r_title}
                                {r_body}
                                {f'<ul class="styled-bullets">{r_bullets}</ul>' if r_bullets else ''}
                            </div>
                        ''')
                    sidebar_items.append(f'<div class="arch-cards-stack">{"".join(r_cards)}</div>')

                bullets = content.get("bullets", [])
                if bullets:
                    b_items = "".join([f"<li>{clean_bullet(b)}</li>" for b in bullets])
                    sidebar_items.append(f'<ul class="styled-bullets">{b_items}</ul>')

                body_text = content.get("body", "")
                if body_text:
                    sidebar_items.append(f'<p class="slide-body-text">{body_text}</p>')

                # If an icon or image was passed for a diagram slide, display as an accent badge
                if img_src:
                    sidebar_items.append(f'''
                        <div class="arch-icon-badge">
                            <img src="{img_src}" alt="{img_alt}" />
                            <span>{img_caption or img_alt}</span>
                        </div>
                    ''')

                has_sidebar = len(sidebar_items) > 0
                main_body_html = f'''
                    <div class="architecture-slide-layout{' with-sidebar' if has_sidebar else ' full-width'}">
                        {f'<div class="arch-sidebar">{"".join(sidebar_items)}</div>' if has_sidebar else ''}
                        <div class="arch-diagram-canvas">
                            {diag_html}
                        </div>
                    </div>
                '''

            else:
                # Layout Assembly: Chart or Image with Content
                chart_def = content.get("chart")
                chart_html = render_chart_canvas(chart_def, style, mode=mode) if chart_def else ""

                if chart_html:
                    if content_blocks:
                        main_body_html = f'''
                            <div class="slide-split-grid">
                                <div class="slide-split-text">
                                    {"".join(content_blocks)}
                                </div>
                                <div class="slide-split-media">
                                    {chart_html}
                                </div>
                            </div>
                        '''
                    else:
                        main_body_html = f'''
                            <div class="slide-content">
                                {chart_html}
                            </div>
                        '''
                elif image_html_block:
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

            body_parts.append(jinja_env.get_template("slides/standard.html").render(
                layout_slug=layout_slug,
                badge_html=badge_html,
                title=title,
                subtitle=subtitle,
                main_body_html=main_body_html
            ))

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

    # Render presentation stylesheet
    deck_css = jinja_env.get_template("deck.css").render({
        "bg_gradient": bg_gradient,
        "bg_color": bg_color,
        "surface_color": surface_color,
        "surface_soft": surface_soft,
        "card_bg": card_bg,
        "card_border": card_border,
        "accent_color": accent_color,
        "accent_alt": accent_alt,
        "ink_color": ink_color,
        "ink_muted": ink_muted,
        "font_family": font_family,
        "icon_badge_bg": icon_badge_bg,
        "icon_badge_border": icon_badge_border,
        "icon_badge_glow": icon_badge_glow,
        "extra_css_vars": extra_css_vars,
        "mode": mode,
        "card_bg_css": card_bg_css,
        "card_shadow": card_shadow,
        "badge_bg": badge_bg,
    })

    # Render presentation master HTML document
    html = jinja_env.get_template("deck.html").render({
        "deck_title": deck_title,
        "google_font": google_font,
        "reveal_theme_css": reveal_theme_css,
        "deck_css": deck_css,
        "slides_content": slides_content,
        "mode": mode,
        "card_bg": card_bg,
        "surface_color": surface_color,
        "accent_color": accent_color,
        "accent_alt": accent_alt,
        "card_border": card_border,
        "ink_color": ink_color,
        "ink_muted": ink_muted,
        "font_family": font_family,
        "surface_soft": surface_soft,
        "bg_color": bg_color,
    })

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
    try:
        with open(spec_arg, "r", encoding="utf-8") as _sf:
            _has_baseline = bool((yaml.safe_load(_sf) or {}).get("baseline"))
    except Exception:
        _has_baseline = False
    if _has_baseline:
        import subprocess
        _gate = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_coverage.py"), spec_arg])
        if _gate.returncode != 0:
            print("Build aborted: modernization coverage gate failed (see errors above).")
            sys.exit(1)
    build_deck(spec_arg, out_arg)
