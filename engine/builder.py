#!/usr/bin/env python3
import os
import sys
import yaml
import base64
from style_parser import parse_style
from icons import get_icon_svg

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
    Renders high-fidelity, theme-colored native architecture diagram components.
    Guarantees 100% theme color compliance (Aqua #54C0E8, Pink #D60EB5, Cobalt #0033A1),
    flawless typography scaling, and zero layout/clipping bugs.
    """
    if not diagram and not mermaid_code and not svg_code:
        return ""
    
    kind = diagram.get("kind", "") if isinstance(diagram, dict) else ""
    diag_title = diagram.get("title", "Architecture Blueprint") if isinstance(diagram, dict) else "Architecture Blueprint"
    
    # 0. High-Fidelity SVG Diagram Component (Standalone SVG file, inline SVG, or kind: svg)
    if kind == "svg" or (isinstance(diagram, dict) and (diagram.get("svg") or diagram.get("src") or diagram.get("file"))) or svg_code:
        svg_markup = ""
        badge_text = "Architecture Blueprint"
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
            return f'''
                <div class="native-arch-wrapper svg-arch-wrapper">
                    <div class="native-arch-header">
                        <span class="native-arch-title"><span class="arch-icon">⬡</span> {diag_title}</span>
                        <span class="native-arch-badge">{badge_text}</span>
                    </div>
                    <div class="arch-svg-diagram-canvas">
                        {svg_markup}
                    </div>
                </div>
            '''

    # 1. Pipeline Flow Architecture (e.g. Identity Object Hierarchy)
    if kind == "pipeline":
        stages = diagram.get("stages", [])
        stages_html = []
        for i, st in enumerate(stages):
            glow = " glowing" if st.get("highlight") else ""
            num = st.get("step", f"0{i+1}")
            title = st.get("title", "")
            badge = f'<span class="stage-badge">{st.get("badge")}</span>' if st.get("badge") else ""
            desc = f'<p class="stage-desc">{st.get("desc")}</p>' if st.get("desc") else ""
            arrow = '<div class="arch-pipeline-arrow">➔</div>' if i < len(stages) - 1 else ''
            stages_html.append(f'''
                <div class="arch-pipeline-stage{glow}">
                    <span class="stage-num">{num}</span>
                    <h4 class="stage-title">{title}</h4>
                    {badge}
                    {desc}
                    {arrow}
                </div>
            ''')
        
        trigger = diagram.get("trigger", {})
        trigger_html = ""
        if trigger:
            trigger_html = f'''
                <div class="arch-pipeline-trigger">
                    <span class="trigger-badge">{trigger.get("badge", "Trigger")}</span>
                    <div class="trigger-content">
                        <strong>{trigger.get("title", "")}</strong>: {trigger.get("desc", "")}
                    </div>
                </div>
            '''
        
        return f'''
            <div class="native-arch-wrapper pipeline-wrapper">
                <div class="native-arch-header">
                    <span class="native-arch-title"><span class="arch-icon">⬡</span> {diag_title}</span>
                    <span class="native-arch-badge">Deterministic Lineage</span>
                </div>
                <div class="arch-pipeline">
                    <div class="arch-pipeline-stages">
                        {"".join(stages_html)}
                    </div>
                    {trigger_html}
                </div>
            </div>
        '''

    # 2. Dual-Track Convergence Architecture (Human vs Machine Governance)
    elif kind in ["dual_track", "convergence"]:
        tracks = diagram.get("tracks", [])
        tracks_html = []
        for t in tracks:
            glow = " glowing" if t.get("highlight") else ""
            t_name = t.get("name", "")
            t_badge = f'<span class="track-badge">{t.get("badge")}</span>' if t.get("badge") else ""
            t_icon_src = resolve_image_src(t.get("icon_src", ""), spec_dir)
            t_icon = f'<img src="{t_icon_src}" alt="" class="track-icon" />' if t_icon_src else ""
            
            steps = t.get("steps", [])
            steps_html = "".join([f'<div class="arch-track-step">{s}</div>' for s in steps])
            
            tracks_html.append(f'''
                <div class="arch-track{glow}">
                    <div class="arch-track-header">
                        <div class="arch-track-identity">
                            {t_icon}
                            <span>{t_name}</span>
                        </div>
                        {t_badge}
                    </div>
                    <div class="arch-track-steps">
                        {steps_html}
                    </div>
                </div>
            ''')
        
        hub = diagram.get("hub", {})
        hub_html = f'''
            <div class="arch-hub-card">
                <span class="card-badge">{hub.get("badge", "Unified Hub")}</span>
                <h3 class="card-title">{hub.get("title", "Unified Policy & Audit Engine")}</h3>
                <p class="card-body">{hub.get("desc", "")}</p>
            </div>
        '''
        
        return f'''
            <div class="native-arch-wrapper convergence-wrapper">
                <div class="native-arch-header">
                    <span class="native-arch-title"><span class="arch-icon">⬡</span> {diag_title}</span>
                    <span class="native-arch-badge">Unified Governance Hub</span>
                </div>
                <div class="arch-convergence">
                    <div class="arch-tracks-col">
                        {"".join(tracks_html)}
                    </div>
                    <div class="arch-convergence-arrow">
                        <span>➔</span>
                    </div>
                    <div class="arch-hub-col">
                        {hub_html}
                    </div>
                </div>
            </div>
        '''

    # 3. Cardinality Architecture (Slide 4: 1:N Profiles & N:M Roles)
    elif kind == "cardinality":
        sources = diagram.get("sources", [])
        src_cards = []
        for s in sources:
            s_name = s.get("name", "")
            s_badge = f'<span class="card-badge">{s.get("badge")}</span>' if s.get("badge") else ""
            items = "".join([f'<span class="arch-chip">{it}</span>' for it in s.get("items", [])])
            src_cards.append(f'''
                <div class="arch-source-card">
                    {s_badge}
                    <h4 class="card-title">{s_name}</h4>
                    <div class="arch-item-chips">{items}</div>
                </div>
            ''')
            
        profiles = diagram.get("profiles", {})
        p_items = []
        for p in profiles.get("items", []):
            p_items.append(f'''
                <div class="arch-profile-subcard">
                    <strong>{p.get("name", "")}</strong>
                    <span class="subcard-meta">{p.get("source", "")}</span>
                </div>
            ''')
        prof_card = f'''
            <div class="arch-profile-card glowing">
                <span class="card-badge">{profiles.get("rule_badge", "1 : N Rule")}</span>
                <h4 class="card-title">{profiles.get("title", "Access Profiles")}</h4>
                <p class="card-body">{profiles.get("desc", "")}</p>
                <div class="arch-profile-items">{"".join(p_items)}</div>
            </div>
        '''
        
        roles = diagram.get("roles", {})
        r_items = []
        for r in roles.get("items", []):
            glow = " glowing" if r.get("highlight") else ""
            r_items.append(f'''
                <div class="arch-role-subcard{glow}">
                    <strong>{r.get("name", "")}</strong>
                    <span class="subcard-meta">{r.get("summary", "")}</span>
                </div>
            ''')
        role_card = f'''
            <div class="arch-role-card glowing">
                <span class="card-badge accent-alt">{roles.get("rule_badge", "N : M Rule")}</span>
                <h4 class="card-title">{roles.get("title", "Composite Roles")}</h4>
                <p class="card-body">{roles.get("desc", "")}</p>
                <div class="arch-role-items">{"".join(r_items)}</div>
            </div>
        '''
        
        return f'''
            <div class="native-arch-wrapper cardinality-wrapper">
                <div class="native-arch-header">
                    <span class="native-arch-title"><span class="arch-icon">⬡</span> {diag_title}</span>
                    <span class="native-arch-badge">Data Model Cardinality</span>
                </div>
                <div class="arch-cardinality">
                    <div class="arch-card-col sources-col">
                        {"".join(src_cards)}
                    </div>
                    <div class="arch-card-connector">
                        <span class="arch-connector-badge">1 : N Rule</span>
                        <span class="arch-connector-line">➔</span>
                    </div>
                    <div class="arch-card-col profiles-col">
                        {prof_card}
                    </div>
                    <div class="arch-card-connector">
                        <span class="arch-connector-badge">N : M Rule</span>
                        <span class="arch-connector-line">➔</span>
                    </div>
                    <div class="arch-card-col roles-col">
                        {role_card}
                    </div>
                </div>
            </div>
        '''

    # 4. Policy Flow / Dynamic ABAC Architecture (Slide 5)
    elif kind in ["policy_flow", "abac"]:
        inputs = diagram.get("inputs", {})
        attr_chips = []
        for a in inputs.get("attributes", []):
            attr_chips.append(f'''
                <div class="arch-attr-row">
                    <span class="attr-key">{a.get("key")}</span>
                    <span class="attr-op">=</span>
                    <span class="attr-val">{a.get("value")}</span>
                </div>
            ''')
        input_card = f'''
            <div class="arch-flow-col input-col">
                <span class="card-badge">{inputs.get("badge", "Inputs")}</span>
                <h4 class="card-title">{inputs.get("title", "Attributes")}</h4>
                <div class="arch-attrs-list">{"".join(attr_chips)}</div>
            </div>
        '''
        
        engine = diagram.get("engine", {})
        engine_card = f'''
            <div class="arch-flow-col engine-col glowing">
                <span class="card-badge">{engine.get("badge", "Evaluation Engine")}</span>
                <h4 class="card-title">{engine.get("title", "Dynamic Policy Engine")}</h4>
                <p class="card-body">{engine.get("desc", "")}</p>
                <div class="engine-status-badge">⚡ Real-Time ABAC Match</div>
            </div>
        '''
        
        role = diagram.get("role", {})
        role_card = f'''
            <div class="arch-flow-col role-col glowing">
                <span class="card-badge accent-alt">{role.get("badge", "Assigned Role")}</span>
                <h4 class="card-title">{role.get("title", "Store Manager")}</h4>
                <p class="card-body">{role.get("desc", "")}</p>
            </div>
        '''
        
        provisions = diagram.get("provisions", {})
        prov_chips = "".join([f'<span class="arch-chip">{s}</span>' for s in provisions.get("systems", [])])
        prov_card = f'''
            <div class="arch-flow-col prov-col">
                <span class="card-badge">{provisions.get("badge", "Fulfillment")}</span>
                <h4 class="card-title">{provisions.get("title", "Provisioned Access")}</h4>
                <div class="arch-item-chips">{prov_chips}</div>
            </div>
        '''
        
        return f'''
            <div class="native-arch-wrapper policy-flow-wrapper">
                <div class="native-arch-header">
                    <span class="native-arch-title"><span class="arch-icon">⬡</span> {diag_title}</span>
                    <span class="native-arch-badge">Dynamic ABAC Execution</span>
                </div>
                <div class="arch-policy-flow">
                    {input_card}
                    <div class="arch-flow-arrow">➔</div>
                    {engine_card}
                    <div class="arch-flow-arrow">➔</div>
                    {role_card}
                    <div class="arch-flow-arrow">➔</div>
                    {prov_card}
                </div>
            </div>
        '''

    # 5. Layered Stack Architecture (Slide 6: PoV Architecture)
    elif kind == "layered_stack":
        layers = diagram.get("layers", [])
        layers_html = []
        for l in layers:
            accent = l.get("accent", "blue")
            glow = " glowing" if l.get("highlight") else ""
            tier = l.get("tier", "")
            title = l.get("title", "")
            badge = f'<span class="card-badge {accent}">{l.get("badge")}</span>' if l.get("badge") else ""
            desc = l.get("desc", "")
            layers_html.append(f'''
                <div class="arch-layer-card {accent}{glow}">
                    <div class="arch-layer-tier">{tier}</div>
                    <div class="arch-layer-info">
                        {badge}
                        <h4 class="card-title">{title}</h4>
                    </div>
                    <div class="arch-layer-desc">
                        <p>{desc}</p>
                    </div>
                </div>
            ''')
            
        return f'''
            <div class="native-arch-wrapper layered-stack-wrapper">
                <div class="native-arch-header">
                    <span class="native-arch-title"><span class="arch-icon">⬡</span> {diag_title}</span>
                    <span class="native-arch-badge">Proof-of-Value Stack</span>
                </div>
                <div class="arch-layered-stack">
                    {"".join(layers_html)}
                </div>
            </div>
        '''
        
    # 6. Fallback Mermaid or Generic Flow
    elif mermaid_code:
        clean_mermaid = mermaid_code.strip().replace("&", "&amp;")
        return f'''
            <div class="mermaid-wrapper">
                <div class="mermaid-badge">Architecture / Dynamic Flow</div>
                <pre class="mermaid">{clean_mermaid}</pre>
            </div>
        '''
        
    elif isinstance(diagram, dict) and diagram.get("elements"):
        d_kind = diagram.get("kind", "flow")
        d_elems = diagram.get("elements", [])
        chips = []
        for i, elem in enumerate(d_elems):
            chips.append(f'<div class="diagram-node"><span class="node-idx">{i+1}</span> {elem}</div>')
            if i < len(d_elems) - 1:
                chips.append('<div class="diagram-arrow">➔</div>')
        return f'''
            <div class="diagram-wrapper">
                <div class="diagram-badge">Architecture / {d_kind.title()}</div>
                <div class="diagram-nodes">{"".join(chips)}</div>
            </div>
        '''
        
    return ""

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
    if "--sp-bg-gradient" in css_vars:
        bg_gradient = css_vars["--sp-bg-gradient"]
    elif "--theme-bg-gradient" in css_vars:
        bg_gradient = css_vars["--theme-bg-gradient"]
    elif mode == "light":
        bg_gradient = f"linear-gradient(135deg, {bg_color} 0%, {surface_color} 60%, {surface_soft} 100%)"
    else:
        bg_gradient = f"radial-gradient(circle at 85% 15%, {accent_color}33 0%, {surface_color} 50%, {bg_color} 100%)"

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
        if "title-slide" in layout_slug:
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
                bullets_items = "".join([f'<li>{b}</li>' for b in bullets_list])
                cover_bullets_html = f'<ul class="cover-bullets">{bullets_items}</ul>'

            body_val_html = body_val.replace("\n", "<br/>") if body_val else ""

            meta_items = []
            if presenter_val:
                meta_items.append(f'<div class="meta-item"><span class="meta-label">Presenter</span><span class="meta-val">{presenter_val}</span></div>')
            if date_val:
                meta_items.append(f'<div class="meta-item"><span class="meta-label">Date</span><span class="meta-val">{date_val}</span></div>')
            if badge:
                meta_items.append(f'<div class="meta-item"><span class="meta-label">Series</span><span class="meta-val">{badge}</span></div>')

            body_parts.append(f'''
                <div class="title-slide-wrapper{' with-cover-image' if cover_hero_html else ''}">
                    <div class="cover-text-content">
                        {cover_logo_html}
                        {badge_html if not cover_logo_html else ''}
                        <h1 class="cover-title">{title}</h1>
                        {f'<h2 class="cover-subtitle">{subtitle}</h2>' if subtitle else ''}
                        {f'<p class="cover-description">{body_val_html}</p>' if body_val else ''}
                        {cover_bullets_html}
                        {f'<div class="cover-meta-grid">{"".join(meta_items)}</div>' if meta_items else ''}
                    </div>
                    {cover_hero_html}
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

        # 4. Agenda layout (Modern Executive Stepper)
        elif "agenda" in layout_slug or role == "agenda":
            agenda_items = []
            raw_cards = content.get("cards", [])
            raw_agenda = content.get("agenda", [])
            raw_bullets = content.get("bullets", [])

            raw_items = raw_cards or raw_agenda or raw_bullets
            for idx, item in enumerate(raw_items, 1):
                step_num = f"{idx:02d}"
                is_last = (idx == len(raw_items))
                item_badge = ""
                highlight_cls = ""

                if isinstance(item, dict):
                    item_title = item.get("title", "")
                    item_desc = item.get("body", item.get("desc", ""))
                    item_badge = item.get("badge", "")
                    if item.get("highlight"):
                        highlight_cls = " glowing"
                elif isinstance(item, str):
                    if ":" in item:
                        parts = item.split(":", 1)
                        item_title = parts[0].strip()
                        item_desc = parts[1].strip()
                    elif " — " in item:
                        parts = item.split(" — ", 1)
                        item_title = parts[0].strip()
                        item_desc = parts[1].strip()
                    elif " - " in item:
                        parts = item.split(" - ", 1)
                        item_title = parts[0].strip()
                        item_desc = parts[1].strip()
                    else:
                        item_title = item
                        item_desc = ""
                else:
                    item_title = str(item)
                    item_desc = ""

                badge_markup = f'<span class="agenda-step-badge">{item_badge}</span>' if item_badge else ''
                desc_markup = f'<p class="agenda-step-desc">{item_desc}</p>' if item_desc else ''
                line_markup = '<span class="agenda-step-line"></span>' if not is_last else ''

                agenda_items.append(f'''
                    <div class="agenda-step-row{highlight_cls}">
                        <div class="agenda-step-indicator">
                            <span class="agenda-step-num">{step_num}</span>
                            {line_markup}
                        </div>
                        <div class="agenda-step-card">
                            <div class="agenda-step-content">
                                <h3 class="agenda-step-title">{item_title}</h3>
                                {desc_markup}
                            </div>
                            {badge_markup}
                        </div>
                    </div>
                ''')

            body_parts.append(f'''
                <div class="slide-layout agenda">
                    <div class="slide-header">
                        {badge_html}
                        <h2 class="slide-title">{title}</h2>
                        {f'<h4 class="slide-subtitle">{subtitle}</h4>' if subtitle else ''}
                    </div>
                    <div class="agenda-stepper">
                        {"".join(agenda_items)}
                    </div>
                </div>
            ''')

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
                        r_bullets = "".join([f"<li>{b}</li>" for b in r.get("bullets", [])])
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
                    b_items = "".join([f"<li>{b}</li>" for b in bullets])
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
            --deck-icon-badge-bg: {icon_badge_bg};
            --deck-icon-badge-border: {icon_badge_border};
            --deck-icon-badge-glow: {icon_badge_glow};
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
            padding: 3.5rem;
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
            object-fit: cover;
            display: block;
        }}
        .cover-icon-badge-box {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1.25rem;
            padding: 3.5rem;
            border-radius: 24px;
            background: linear-gradient(145deg, rgba(11, 17, 30, 0.9) 0%, rgba(0, 51, 161, 0.15) 100%);
            border: 1px solid var(--deck-card-border);
            box-shadow: {card_shadow};
        }}
        .cover-accent-icon {{
            width: 72px;
            height: 72px;
            object-fit: contain;
            filter: drop-shadow(0 0 16px var(--deck-accent));
        }}
        .cover-icon-label {{
            font-size: 1rem;
            font-weight: 500;
            color: var(--deck-accent);
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}
        .cover-brand-logo-wrapper {{
            margin-bottom: 2rem;
        }}
        .cover-brand-logo {{
            height: 52px;
            width: auto;
            max-width: 320px;
            object-fit: contain;
            filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));
        }}
        .cover-description {{
            font-size: 1.25rem;
            color: var(--deck-ink-muted);
            max-width: 900px;
            line-height: 1.6;
            margin-bottom: 1.25rem;
            white-space: pre-line;
        }}
        .cover-bullets {{
            list-style: none;
            padding: 0;
            margin: 0 0 1.75rem 0;
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }}
        .cover-bullets li {{
            font-size: 1.15rem;
            color: var(--deck-ink-muted);
            line-height: 1.5;
            position: relative;
            padding-left: 1.25rem;
        }}
        .cover-bullets li::before {{
            content: "•";
            color: var(--deck-accent);
            position: absolute;
            left: 0;
            font-size: 1.2rem;
            line-height: 1.2;
        }}
        .cover-meta-grid {{
            display: flex;
            align-items: center;
            gap: 3rem;
            border-top: 1px solid var(--deck-card-border);
            padding-top: 1.25rem;
            margin-top: 1rem;
        }}
        .cover-meta-grid .meta-item {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        .cover-meta-grid .meta-label {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--deck-accent);
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .cover-meta-grid .meta-val {{
            font-size: 1.15rem;
            font-weight: 500;
            color: var(--deck-ink);
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

        /* Modern Executive Stepper (Agenda Layout) */
        .slide-layout.agenda {{
            display: flex;
            flex-direction: column;
            height: 100%;
            max-height: 880px;
            box-sizing: border-box;
            justify-content: flex-start;
        }}
        .agenda-stepper {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            margin-top: 0.5rem;
            position: relative;
            width: 100%;
            max-width: 1180px;
        }}
        .agenda-step-row {{
            display: flex;
            align-items: stretch;
            gap: 1.5rem;
            position: relative;
        }}
        .agenda-step-indicator {{
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            flex-shrink: 0;
            width: 58px;
        }}
        .agenda-step-num {{
            width: 56px;
            height: 56px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(84, 192, 232, 0.15) 0%, rgba(0, 51, 161, 0.4) 100%);
            border: 1px solid rgba(84, 192, 232, 0.5);
            color: var(--deck-accent);
            font-size: 1.35rem;
            font-weight: 700;
            font-family: var(--deck-font-mono, monospace);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), 0 0 14px rgba(84, 192, 232, 0.25);
            z-index: 2;
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        }}
        .agenda-step-line {{
            position: absolute;
            top: 56px;
            bottom: -1.25rem;
            width: 2px;
            background: linear-gradient(to bottom, rgba(84, 192, 232, 0.55) 0%, rgba(0, 51, 161, 0.2) 100%);
            z-index: 1;
        }}
        .agenda-step-card {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(90deg, rgba(11, 17, 30, 0.7) 0%, rgba(1, 28, 72, 0.3) 100%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 3px solid rgba(84, 192, 232, 0.45);
            border-radius: 14px;
            padding: 1.15rem 1.75rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .agenda-step-row:hover .agenda-step-card {{
            background: linear-gradient(90deg, rgba(15, 23, 42, 0.9) 0%, rgba(0, 51, 161, 0.4) 100%);
            border-color: rgba(84, 192, 232, 0.5);
            border-left-color: var(--deck-accent);
            transform: translateX(8px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4), 0 0 16px rgba(84, 192, 232, 0.2);
        }}
        .agenda-step-row:hover .agenda-step-num {{
            transform: scale(1.06);
            border-color: var(--deck-accent);
            box-shadow: 0 0 22px rgba(84, 192, 232, 0.5);
        }}
        .agenda-step-row.glowing .agenda-step-card {{
            border-left-color: var(--deck-accent);
            border-color: rgba(84, 192, 232, 0.5);
            background: linear-gradient(90deg, rgba(15, 23, 42, 0.85) 0%, rgba(0, 51, 161, 0.45) 100%);
        }}
        .agenda-step-content {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        .agenda-step-title {{
            font-size: 1.35rem !important;
            font-weight: 600 !important;
            color: #FFFFFF !important;
            margin: 0 !important;
            line-height: 1.3 !important;
        }}
        .agenda-step-desc {{
            font-size: 1.05rem !important;
            font-weight: 400 !important;
            color: var(--deck-ink-muted) !important;
            margin: 0 !important;
            line-height: 1.4 !important;
        }}
        .agenda-step-badge {{
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.3rem 0.85rem;
            border-radius: 999px;
            background: rgba(84, 192, 232, 0.12);
            border: 1px solid rgba(84, 192, 232, 0.3);
            color: var(--deck-accent);
            flex-shrink: 0;
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
            list-style: none !important;
            padding: 0 !important;
            margin: 0.5rem 0 0 0 !important;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.75rem;
            width: 100%;
        }}
        .styled-bullets li {{
            position: relative;
            background: {card_bg_css};
            border: 1px solid var(--deck-card-border);
            border-radius: 18px;
            padding: 1.75rem;
            box-shadow: {card_shadow};
            font-size: 1.15rem !important;
            line-height: 1.55 !important;
            color: var(--deck-ink);
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            min-height: 130px;
            box-sizing: border-box;
            transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .styled-bullets li:hover {{
            border-color: var(--deck-accent);
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}
        .styled-bullets li::before {{
            display: none !important;
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
            gap: 0.65rem;
            margin-top: 0 !important;
        }}
        .slide-split-text .styled-bullets li {{
            font-size: 1.05rem !important;
            line-height: 1.45 !important;
            padding: 0.75rem 1.15rem;
            border-radius: 12px;
            gap: 0.85rem;
        }}
        .slide-split-text .styled-bullets li::before {{
            width: 8px;
            height: 8px;
            margin-top: 0.38rem;
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
            height: 100%;
            min-height: 0;
            width: 100%;
            box-sizing: border-box;
        }}
        .slide-split-media {{
            display: flex;
            justify-content: center;
            align-items: center;
            max-height: 720px;
            height: 100%;
            min-height: 0;
            width: 100%;
            box-sizing: border-box;
        }}
        .slide-split-media .slide-embedded-image {{
            max-height: 560px;
            max-width: 100%;
            object-fit: contain;
        }}

        .reveal section img {{
            margin: 0 !important;
        }}

        /* Embedded Image Cards & Frames */
        .slide-image-wrapper {{
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            max-width: 100%;
            max-height: 100%;
            box-sizing: border-box;
        }}
        .slide-image-card {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0;
            line-height: 0;
            border-radius: 18px;
            border: 1px solid var(--deck-card-border);
            background: var(--deck-card-bg);
            box-shadow: {card_shadow};
            padding: 1.25rem;
            width: fit-content;
            max-width: 100%;
            height: fit-content;
            max-height: 100%;
            box-sizing: border-box;
        }}
        .slide-embedded-image {{
            max-width: 100%;
            max-height: 540px;
            width: auto;
            height: auto;
            object-fit: contain;
            border-radius: 12px;
            display: block;
            margin: 0 !important;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        }}
        .slide-image-caption {{
            font-size: 0.88rem;
            color: var(--deck-ink-muted);
            padding: 0.4rem 1.25rem;
            text-align: center;
            border: 1px solid var(--deck-card-border);
            border-radius: 9999px;
            width: auto;
            max-width: 90%;
            background: rgba(11, 17, 30, 0.85);
            margin-top: 0.85rem;
            flex-shrink: 0;
            box-sizing: border-box;
        }}

        /* Picture with Caption Grid */
        .picture-caption-grid {{
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 2.5rem;
            align-items: center;
            flex: 1;
            max-height: 720px;
            height: 100%;
            min-height: 0;
            box-sizing: border-box;
        }}
        .picture-side {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            max-height: 680px;
            min-height: 0;
            width: 100%;
            box-sizing: border-box;
        }}
        .picture-side .slide-embedded-image {{
            max-height: 560px;
            max-width: 100%;
            object-fit: contain;
        }}
        .caption-side {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            justify-content: center;
        }}

        /* Center Media Layout */
        .slide-center-media {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex: 1;
            height: 100%;
            max-height: 720px;
            width: 100%;
            box-sizing: border-box;
        }}
        .slide-center-media .slide-embedded-image {{
            max-height: 620px;
            max-width: 100%;
            object-fit: contain;
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
        .slide-split-text .comparison-card .styled-bullets,
        .slide-split-text .region-col .styled-bullets {{
            gap: 0.45rem;
            margin-top: 0.35rem !important;
        }}
        .slide-split-text .comparison-card .styled-bullets li,
        .slide-split-text .region-col .styled-bullets li {{
            font-size: 0.95rem !important;
            line-height: 1.4 !important;
            padding: 0.55rem 0.85rem;
            border-radius: 8px;
            gap: 0.65rem;
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
        .card-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.85rem;
            width: 100%;
        }}
        .card-icon-container {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: var(--deck-icon-badge-bg);
            border: 1px solid var(--deck-icon-badge-border);
            color: var(--deck-accent);
            box-shadow: var(--deck-icon-badge-glow);
            flex-shrink: 0;
        }}
        .card-icon-container.circle {{
            border-radius: 50%;
        }}
        .card-icon-container.bare {{
            background: transparent;
            border: none;
            box-shadow: none;
            width: auto;
            height: auto;
        }}
        .card-icon-container svg {{
            width: 24px;
            height: 24px;
        }}
        .feature-card.glowing .card-icon-container {{
            color: var(--deck-accent-alt);
            border-color: rgba(214, 14, 181, 0.35);
            background: rgba(214, 14, 181, 0.12);
            box-shadow: 0 0 16px rgba(214, 14, 181, 0.3);
        }}
        .metric-icon-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.65rem;
            color: var(--deck-accent);
        }}
        .metric-icon-badge svg {{
            width: 26px;
            height: 26px;
        }}
        .metric-card.glowing .metric-icon-badge {{
            color: var(--deck-accent-alt);
        }}
        .card-badge {{
            display: inline-block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--deck-accent);
            border: 1px solid var(--deck-accent);
            padding: 3px 10px;
            border-radius: 6px;
            margin-bottom: 0;
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
        .comparison-card .styled-bullets,
        .region-col .styled-bullets {{
            gap: 0.6rem;
            margin-top: 0.5rem !important;
        }}
        .comparison-card .styled-bullets li,
        .region-col .styled-bullets li {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 0.65rem 0.95rem;
            font-size: 1.02rem !important;
            line-height: 1.45 !important;
            box-shadow: none;
            gap: 0.75rem;
        }}
        .comparison-card .styled-bullets li::before,
        .region-col .styled-bullets li::before {{
            width: 7px;
            height: 7px;
            margin-top: 0.38rem;
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

        /* Architecture Slide Layout (Sidebar + Full Canvas) */
        .architecture-slide-layout {{
            display: grid;
            grid-template-columns: 460px 1fr;
            gap: 2.5rem;
            align-items: stretch;
            height: calc(1080px - 220px);
            max-height: 720px;
            box-sizing: border-box;
            width: 100%;
        }}
        .architecture-slide-layout.full-width {{
            grid-template-columns: 1fr;
        }}
        .arch-sidebar {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            justify-content: flex-start;
            height: 100%;
            overflow: hidden;
        }}
        .arch-cards-stack {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            flex: 1;
        }}
        .arch-cards-stack .feature-card {{
            padding: 1.2rem 1.4rem;
            min-height: auto;
        }}
        .arch-cards-stack .card-title {{
            font-size: 1.15rem !important;
            margin-bottom: 0.35rem !important;
        }}
        .arch-cards-stack .card-body {{
            font-size: 0.95rem !important;
            line-height: 1.45 !important;
        }}
        .arch-icon-badge {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.75rem 1.25rem;
            background: rgba(11, 17, 30, 0.65);
            border: 1px solid var(--deck-card-border);
            border-radius: 12px;
            color: var(--deck-ink-muted);
            font-size: 0.95rem;
            font-weight: 500;
        }}
        .arch-icon-badge img {{
            width: 36px;
            height: 36px;
            object-fit: contain;
        }}
        .arch-diagram-canvas {{
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }}
        .arch-diagram-canvas .mermaid-wrapper {{
            width: 100%;
            height: 100%;
            margin-top: 0;
            padding: 1.5rem 2rem;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        .arch-diagram-canvas .mermaid {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .arch-diagram-canvas .mermaid svg {{
            max-width: 100% !important;
            max-height: 600px !important;
            width: auto !important;
            height: auto !important;
        }}
        .arch-svg-diagram-canvas {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.25rem;
            box-sizing: border-box;
        }}
        .arch-svg-diagram-canvas svg {{
            max-width: 100% !important;
            max-height: 580px !important;
            width: 100% !important;
            height: auto !important;
            filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.45));
        }}
        .arch-svg-diagram-canvas .arch-svg-img {{
            max-width: 100%;
            max-height: 580px;
            width: auto;
            height: auto;
            border-radius: 14px;
            object-fit: contain;
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
            background: {"rgba(255, 255, 255, 0.9)" if mode == "light" else "rgba(11, 17, 30, 0.9)"};
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

        /* =========================================================
           Native Architecture Diagram Theme Components
           Strictly bound to theme tokens:
           Aqua (accent): var(--deck-accent) [#54C0E8]
           Pink (accent-alt): var(--deck-accent-alt) [#D60EB5]
           Surface: var(--deck-card-bg) / var(--deck-surface)
           Border: var(--deck-card-border) [#415364]
           Ink: var(--deck-ink) [#FFFFFF] / var(--deck-ink-muted) [#DAE1E9]
        ========================================================= */
        .native-arch-wrapper {{
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 1rem;
            padding: 1.5rem 1.75rem;
            background: linear-gradient(145deg, rgba(11, 17, 30, 0.95) 0%, rgba(1, 28, 72, 0.45) 100%);
            border: 1px solid var(--deck-card-border);
            border-radius: 18px;
            backdrop-filter: blur(12px);
            box-shadow: {card_shadow};
        }}
        .native-arch-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(84, 192, 232, 0.2);
            padding-bottom: 0.6rem;
            margin-bottom: 0.4rem;
        }}
        .native-arch-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .native-arch-title .arch-icon {{
            color: var(--deck-accent);
        }}
        .native-arch-badge {{
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--deck-accent);
            background: rgba(84, 192, 232, 0.12);
            border: 1px solid var(--deck-accent);
            padding: 3px 10px;
            border-radius: 9999px;
        }}

        /* 1. Pipeline Architecture (Slide 2) */
        .arch-pipeline {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            width: 100%;
        }}
        .arch-pipeline-stages {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.85rem;
            align-items: stretch;
            position: relative;
        }}
        .arch-pipeline-stage {{
            background: rgba(15, 26, 46, 0.85);
            border: 1px solid var(--deck-card-border);
            border-radius: 14px;
            padding: 1.1rem 0.9rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            position: relative;
            box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        }}
        .arch-pipeline-stage.glowing {{
            border-color: var(--deck-accent);
            box-shadow: 0 0 20px rgba(84, 192, 232, 0.35);
        }}
        .arch-pipeline-stage .stage-num {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--deck-accent);
            letter-spacing: 0.05em;
        }}
        .arch-pipeline-stage .stage-title {{
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #FFFFFF;
            margin: 0 !important;
        }}
        .arch-pipeline-stage .stage-badge {{
            font-size: 0.72rem;
            color: var(--deck-accent-alt);
            font-weight: 500;
        }}
        .arch-pipeline-stage .stage-desc {{
            font-size: 0.82rem;
            color: var(--deck-ink-muted);
            line-height: 1.35;
            margin: 0;
        }}
        .arch-pipeline-arrow {{
            position: absolute;
            right: -12px;
            top: 50%;
            transform: translateY(-50%);
            z-index: 2;
            color: var(--deck-accent);
            font-size: 1rem;
            background: #0B111E;
            border-radius: 50%;
            width: 22px;
            height: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--deck-accent);
        }}
        .arch-pipeline-trigger {{
            background: rgba(214, 14, 181, 0.08);
            border: 1px dashed var(--deck-accent-alt);
            border-radius: 12px;
            padding: 0.75rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .arch-pipeline-trigger .trigger-badge {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--deck-accent-alt);
            background: rgba(214, 14, 181, 0.15);
            border: 1px solid var(--deck-accent-alt);
            padding: 3px 8px;
            border-radius: 6px;
            white-space: nowrap;
        }}
        .arch-pipeline-trigger .trigger-content {{
            font-size: 0.88rem;
            color: var(--deck-ink-muted);
        }}

        /* 2. Convergence Architecture (Slide 3) */
        .arch-convergence {{
            display: grid;
            grid-template-columns: 1.6fr 0.12fr 1fr;
            gap: 1.25rem;
            align-items: center;
            width: 100%;
        }}
        .arch-tracks-col {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        .arch-track {{
            background: rgba(15, 26, 46, 0.75);
            border: 1px solid var(--deck-card-border);
            border-radius: 14px;
            padding: 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        .arch-track.glowing {{
            border-color: var(--deck-accent-alt);
            box-shadow: 0 0 20px rgba(214, 14, 181, 0.25);
        }}
        .arch-track-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .arch-track-identity {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 1.05rem;
            font-weight: 600;
            color: #FFFFFF;
        }}
        .arch-track-identity img {{
            width: 26px;
            height: 26px;
            object-fit: contain;
        }}
        .arch-track .track-badge {{
            font-size: 0.75rem;
            color: var(--deck-accent);
            border: 1px solid var(--deck-accent);
            padding: 2px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }}
        .arch-track-steps {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.5rem;
        }}
        .arch-track-step {{
            background: rgba(11, 17, 30, 0.6);
            border: 1px solid rgba(84, 192, 232, 0.2);
            border-radius: 8px;
            padding: 0.5rem 0.4rem;
            font-size: 0.8rem;
            color: var(--deck-ink-muted);
            text-align: center;
        }}
        .arch-convergence-arrow {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--deck-accent);
            font-size: 2rem;
        }}
        .arch-hub-card {{
            background: linear-gradient(145deg, rgba(15, 26, 46, 0.95), rgba(1, 28, 72, 0.85));
            border: 2px solid var(--deck-accent);
            box-shadow: 0 0 25px rgba(84, 192, 232, 0.35);
            border-radius: 16px;
            padding: 1.5rem 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }}

        /* 3. Cardinality Architecture (Slide 4) */
        .arch-cardinality {{
            display: grid;
            grid-template-columns: 1fr 0.18fr 1fr 0.18fr 1.15fr;
            gap: 0.85rem;
            align-items: center;
            width: 100%;
        }}
        .arch-card-col {{
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }}
        .arch-card-connector {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            text-align: center;
        }}
        .arch-connector-badge {{
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--deck-accent);
            background: rgba(84, 192, 232, 0.15);
            border: 1px solid var(--deck-accent);
            padding: 3px 8px;
            border-radius: 6px;
            white-space: nowrap;
        }}
        .arch-connector-line {{
            font-size: 1.5rem;
            color: var(--deck-accent);
        }}
        .arch-source-card, .arch-profile-card, .arch-role-card {{
            background: rgba(15, 26, 46, 0.8);
            border: 1px solid var(--deck-card-border);
            border-radius: 14px;
            padding: 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 0.55rem;
        }}
        .arch-profile-card.glowing {{
            border-color: var(--deck-accent);
            box-shadow: 0 0 20px rgba(84, 192, 232, 0.25);
        }}
        .arch-role-card.glowing {{
            border-color: var(--deck-accent-alt);
            box-shadow: 0 0 25px rgba(214, 14, 181, 0.35);
        }}
        .arch-item-chips {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}
        .arch-chip {{
            font-size: 0.8rem;
            background: rgba(11, 17, 30, 0.6);
            border: 1px solid rgba(84, 192, 232, 0.15);
            padding: 4px 8px;
            border-radius: 6px;
            color: var(--deck-ink-muted);
        }}
        .arch-profile-subcard, .arch-role-subcard {{
            background: rgba(11, 17, 30, 0.55);
            border: 1px solid rgba(84, 192, 232, 0.12);
            border-radius: 8px;
            padding: 0.55rem 0.75rem;
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            margin-top: 0.4rem;
        }}
        .arch-profile-subcard strong, .arch-role-subcard strong {{
            font-size: 0.95rem;
            color: #FFFFFF;
        }}
        .subcard-meta {{
            font-size: 0.78rem;
            color: var(--deck-ink-muted);
        }}

        /* 4. Policy Flow / Dynamic ABAC Architecture (Slide 5) */
        .arch-policy-flow {{
            display: grid;
            grid-template-columns: 1fr 0.12fr 1.1fr 0.12fr 1fr 0.12fr 1.1fr;
            gap: 0.75rem;
            align-items: center;
            width: 100%;
        }}
        .arch-flow-col {{
            background: rgba(15, 26, 46, 0.8);
            border: 1px solid var(--deck-card-border);
            border-radius: 14px;
            padding: 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 0.55rem;
        }}
        .arch-flow-col.glowing {{
            border-color: var(--deck-accent);
            box-shadow: 0 0 20px rgba(84, 192, 232, 0.25);
        }}
        .arch-flow-col.role-col.glowing {{
            border-color: var(--deck-accent-alt);
            box-shadow: 0 0 20px rgba(214, 14, 181, 0.25);
        }}
        .arch-flow-arrow {{
            font-size: 1.6rem;
            color: var(--deck-accent);
            text-align: center;
        }}
        .arch-attrs-list {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}
        .arch-attr-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            background: rgba(11, 17, 30, 0.6);
            padding: 5px 8px;
            border-radius: 6px;
            border: 1px solid rgba(84, 192, 232, 0.15);
        }}
        .attr-key {{
            color: #FFFFFF;
            font-weight: 500;
        }}
        .attr-op {{
            color: var(--deck-accent);
            font-weight: 700;
        }}
        .attr-val {{
            color: var(--deck-accent-alt);
            font-weight: 600;
        }}
        .engine-status-badge {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--deck-accent);
            background: rgba(84, 192, 232, 0.15);
            border: 1px solid var(--deck-accent);
            padding: 4px 8px;
            border-radius: 6px;
            text-align: center;
            margin-top: 0.4rem;
        }}

        /* 5. Layered Stack Architecture (Slide 6) */
        .arch-layered-stack {{
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            width: 100%;
        }}
        .arch-layer-card {{
            background: rgba(15, 26, 46, 0.85);
            border: 1px solid var(--deck-card-border);
            border-radius: 14px;
            padding: 1.1rem 1.5rem;
            display: grid;
            grid-template-columns: 90px 1.4fr 2.6fr;
            align-items: center;
            gap: 1.25rem;
        }}
        .arch-layer-card.cyan, .arch-layer-card.glowing {{
            border-color: var(--deck-accent);
            box-shadow: 0 0 20px rgba(84, 192, 232, 0.25);
        }}
        .arch-layer-card.orchid {{
            border-color: var(--deck-accent-alt);
            box-shadow: 0 0 20px rgba(214, 14, 181, 0.25);
        }}
        .arch-layer-card.blue {{
            border-color: #0071CE;
        }}
        .arch-layer-tier {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--deck-accent);
            letter-spacing: 0.05em;
        }}
        .arch-layer-card.orchid .arch-layer-tier {{
            color: var(--deck-accent-alt);
        }}
        .arch-layer-info .card-title {{
            font-size: 1.15rem !important;
            margin: 0.2rem 0 !important;
            color: #FFFFFF;
        }}
        .arch-layer-desc p {{
            font-size: 0.88rem;
            color: var(--deck-ink-muted);
            line-height: 1.4;
            margin: 0;
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
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: false,
            theme: 'dark',
            securityLevel: 'loose',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: 14,
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            themeVariables: {{
                darkMode: true,
                background: '#0B111E',
                primaryColor: '#0F1A2E',
                primaryBorderColor: '#54C0E8',
                primaryTextColor: '#FFFFFF',
                lineColor: '#54C0E8',
                secondaryColor: '#1A2942',
                tertiaryColor: '#111827'
            }}
        }});

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
        }}).then(() => {{
            mermaid.run();
        }});

        Reveal.on('slidechanged', () => {{
            window.dispatchEvent(new Event('resize'));
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
