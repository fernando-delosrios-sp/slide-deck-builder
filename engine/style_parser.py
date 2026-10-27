import os
import re
import yaml

# Common high-quality Google Fonts and their fallback stacks
KNOWN_GOOGLE_FONTS = {
    "poppins": ("'Poppins', system-ui, -apple-system, sans-serif", "Poppins:wght@300;400;500;600;700"),
    "inter": ("'Inter', system-ui, -apple-system, sans-serif", "Inter:wght@300;400;500;600;700"),
    "plus jakarta sans": ("'Plus Jakarta Sans', system-ui, -apple-system, sans-serif", "Plus+Jakarta+Sans:wght@300;400;500;600;700"),
    "outfit": ("'Outfit', system-ui, -apple-system, sans-serif", "Outfit:wght@300;400;500;600;700"),
    "roboto": ("'Roboto', system-ui, -apple-system, sans-serif", "Roboto:wght@300;400;500;700"),
    "dm sans": ("'DM Sans', system-ui, -apple-system, sans-serif", "DM+Sans:wght@400;500;700"),
    "space grotesk": ("'Space Grotesk', system-ui, -apple-system, sans-serif", "Space+Grotesk:wght@400;500;600;700"),
    "montserrat": ("'Montserrat', system-ui, -apple-system, sans-serif", "Montserrat:wght@300;400;500;600;700"),
    "geist": ("'Geist', system-ui, -apple-system, sans-serif", "Geist:wght@300;400;500;600;700"),
    "manrope": ("'Manrope', system-ui, -apple-system, sans-serif", "Manrope:wght@300;400;500;600;700")
}

def hex_to_rgb(hex_str):
    if not hex_str or not isinstance(hex_str, str):
        return (0, 0, 0)
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    elif len(hex_str) >= 6:
        hex_str = hex_str[:6]
    else:
        return (0, 0, 0)
    try:
        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
    except Exception:
        return (0, 0, 0)

def relative_luminance(rgb):
    def channel_lum(c):
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

def contrast_ratio(hex1, hex2):
    lum1 = relative_luminance(hex_to_rgb(hex1))
    lum2 = relative_luminance(hex_to_rgb(hex2))
    l_max = max(lum1, lum2)
    l_min = min(lum1, lum2)
    return (l_max + 0.05) / (l_min + 0.05)

def hex_with_alpha(hex_str, alpha_hex="33"):
    if not hex_str or not isinstance(hex_str, str):
        return "#54C0E833"
    clean = hex_str.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join([c*2 for c in clean])
    clean = clean[:6]
    return f"#{clean}{alpha_hex}"

def extract_markdown_sections(body):
    """
    Parses markdown sections (H2) and extracts structured themes like
    Visual Atmosphere, Color Rules, Do's and Don'ts, and Diagram Grammar.
    """
    sections = {}
    current_key = "overview"
    current_lines = []

    for line in body.split("\n"):
        h2_match = re.match(r"^##\s+(?:[0-9]+\.\s*)?([^\n]+)", line)
        if h2_match:
            if current_lines:
                sections[current_key] = "\n".join(current_lines).strip()
                current_lines = []
            heading = h2_match.group(1).strip().lower()
            if "atmosphere" in heading or "overview" in heading or "theme" in heading:
                current_key = "atmosphere"
            elif "color" in heading or "palette" in heading:
                current_key = "colors"
            elif "typography" in heading or "font" in heading:
                current_key = "typography"
            elif "component" in heading:
                current_key = "components"
            elif "do" in heading and "don" in heading:
                current_key = "dos_and_donts"
            elif "diagram" in heading:
                current_key = "diagram_grammar"
            elif "prompt" in heading or "priming" in heading or "agent" in heading:
                current_key = "agent_priming"
            else:
                current_key = re.sub(r"[^a-z0-9_]+", "_", heading).strip("_")
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections

def synthesize_typography(typography_dict, mode="dark"):
    """
    Synthesizes presentation-grade typography scales and Google Fonts import
    from either legacy schema or modern DESIGN.md specifications.
    """
    typo = dict(typography_dict or {})

    # Detect primary font name
    font_name = None
    if "google-fonts" in typo:
        gf = typo["google-fonts"]
        font_name = gf.split(":")[0].replace("+", " ")
    elif "font-family" in typo:
        font_name = typo["font-family"].split(",")[0].replace("'", "").replace('"', "").strip()
    elif "font-sans" in typo:
        font_name = typo["font-sans"].split(",")[0].replace("'", "").replace('"', "").strip()
    elif "display-lg" in typo and isinstance(typo["display-lg"], dict):
        font_name = typo["display-lg"].get("fontFamily", "").split(",")[0].replace("'", "").replace('"', "").strip()
    elif "body" in typo and isinstance(typo["body"], dict):
        font_name = typo["body"].get("fontFamily", "").split(",")[0].replace("'", "").replace('"', "").strip()

    # Map or fallback font family and Google Fonts url
    if font_name and font_name.lower() in KNOWN_GOOGLE_FONTS:
        ff, gf = KNOWN_GOOGLE_FONTS[font_name.lower()]
    elif font_name and ("linear" in font_name.lower() or "sf pro" in font_name.lower()):
        # Map Linear/Apple proprietary system fonts to modern Inter
        ff, gf = KNOWN_GOOGLE_FONTS["inter"]
    elif font_name and ("system" in font_name.lower() or "sans" in font_name.lower()):
        ff = "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
        gf = "Inter:wght@400;500;600;700"
    elif font_name:
        gf_clean = font_name.replace(" ", "+")
        ff = f"'{font_name}', system-ui, -apple-system, sans-serif"
        gf = f"{gf_clean}:wght@300;400;500;600;700"
    else:
        ff, gf = KNOWN_GOOGLE_FONTS["poppins" if mode == "dark" else "plus jakarta sans"]

    if "font-family" not in typo:
        typo["font-family"] = ff
    if "google-fonts" not in typo:
        typo["google-fonts"] = gf

    # Ensure presentation hierarchy roles exist
    if "title-slide" not in typo:
        src = typo.get("display-xl") or typo.get("display-lg") or {}
        typo["title-slide"] = {
            "fontFamily": typo["font-family"],
            "fontSize": src.get("fontSize", "56px"),
            "fontWeight": src.get("fontWeight", 600),
            "lineHeight": src.get("lineHeight", 1.15),
            "letterSpacing": src.get("letterSpacing", "-0.02em")
        }
    if "title-content" not in typo:
        src = typo.get("display-md") or typo.get("headline") or {}
        typo["title-content"] = {
            "fontFamily": typo["font-family"],
            "fontSize": src.get("fontSize", "38px"),
            "fontWeight": src.get("fontWeight", 600),
            "lineHeight": src.get("lineHeight", 1.2),
            "letterSpacing": src.get("letterSpacing", "-0.01em")
        }
    if "subtitle" not in typo:
        src = typo.get("card-title") or typo.get("subhead") or {}
        typo["subtitle"] = {
            "fontFamily": typo["font-family"],
            "fontSize": src.get("fontSize", "22px"),
            "fontWeight": src.get("fontWeight", 400),
            "lineHeight": src.get("lineHeight", 1.4)
        }
    if "body-md" not in typo:
        src = typo.get("body") or typo.get("body-sm") or {}
        typo["body-md"] = {
            "fontFamily": typo["font-family"],
            "fontSize": src.get("fontSize", "16px"),
            "fontWeight": src.get("fontWeight", 400),
            "lineHeight": src.get("lineHeight", 1.5)
        }
    if "bullets" not in typo:
        typo["bullets"] = typo["body-md"]
    if "caption" not in typo:
        typo["caption"] = {
            "fontFamily": typo["font-family"],
            "fontSize": "13px",
            "fontWeight": 300,
            "lineHeight": 1.4
        }

    return typo

def normalize_colors(raw_colors, mode="dark"):
    """
    Normalizes color tokens from any DESIGN.md or legacy schema to presentation tokens.
    Guarantees WCAG AA readable contrast for text, cards, and accents.
    """
    c = dict(raw_colors or {})

    # Background / Canvas
    bg = c.get("background") or c.get("canvas") or c.get("bg") or c.get("surface-0") or ("#000000" if mode == "dark" else "#F0F3F6")

    # Surfaces
    surface = c.get("surface") or c.get("surface-1") or c.get("surface-base") or ("#0B111E" if mode == "dark" else "#F0F3F6")
    surface_soft = c.get("surface-soft") or c.get("surface-2") or c.get("surface-elevated") or ("#111827" if mode == "dark" else "#FFFFFF")

    # Cards
    card_bg = c.get("card-background") or c.get("card-bg") or c.get("surface-1") or surface
    card_border = c.get("card-border") or c.get("border") or c.get("hairline") or c.get("hairline-strong") or c.get("divider") or ("#415364" if mode == "dark" else "#E2E8F0")

    # Accent
    accent = c.get("accent") or c.get("primary") or ("#54C0E8" if mode == "dark" else "#2563EB")
    # If primary is neutral (#000 or #FFF), check if secondary or accent-alt has chromatic color
    if accent.lower() in ["#000000", "#ffffff", "#000", "#fff"]:
        accent = c.get("accent") or c.get("primary-focus") or c.get("brand") or ("#54C0E8" if mode == "dark" else "#2563EB")

    # Secondary Accent
    accent_alt = c.get("accent-alt") or c.get("secondary") or c.get("accent-green") or c.get("primary-hover") or c.get("brand-secure") or ("#D60EB5" if mode == "dark" else "#4F46E5")

    # Text / Ink
    ink = c.get("ink") or c.get("text") or c.get("foreground") or c.get("on-surface") or ("#FFFFFF" if mode == "dark" else "#1D1D1F")
    ink_muted = c.get("ink-muted") or c.get("text-muted") or c.get("ink-subtle") or c.get("secondary-text") or ("#DAE1E9" if mode == "dark" else "#4B5563")

    # Hairline / Divider
    hairline = c.get("hairline") or card_border
    divider = c.get("divider") or hairline

    # Contrast Safety Check: Ensure ink has at least 4.5:1 contrast against bg
    if contrast_ratio(ink, bg) < 4.5:
        ink = "#FFFFFF" if mode == "dark" else "#111827"
    if contrast_ratio(ink_muted, bg) < 2.5:
        ink_muted = "#DAE1E9" if mode == "dark" else "#475569"

    normalized = {
        "primary": ink if mode == "dark" else bg,
        "accent": accent,
        "accent-alt": accent_alt,
        "background": bg,
        "surface": surface,
        "surface-soft": surface_soft,
        "hairline": hairline,
        "divider": divider,
        "ink": ink,
        "ink-muted": ink_muted,
        "card-background": card_bg,
        "card-border": card_border
    }

    # Preserve any extra custom color keys
    for k, v in c.items():
        if k not in normalized:
            normalized[k] = v

    return normalized

def safe_load_yaml_frontmatter(fm_raw):
    try:
        return yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        lines = []
        for line in fm_raw.split("\n"):
            m = re.match(r"^(\s*(?:description|name):\s*)([^\s\"'].*)$", line)
            if m and ":" in m.group(2):
                val = m.group(2).strip().replace('"', '\\"')
                lines.append(f'{m.group(1)}"{val}"')
            else:
                lines.append(line)
        try:
            return yaml.safe_load("\n".join(lines)) or {}
        except Exception:
            return {}

def extract_fm_and_body(content):
    """
    Robust frontmatter extractor handling standard markdown, files with
    leading doc metadata, or multi-delimited frontmatter.
    """
    matches = list(re.finditer(r'(?:^|\n)---\s*(?:\n|$)', content))
    if len(matches) >= 2:
        for i in range(len(matches) - 1):
            start = matches[i].end()
            end = matches[i+1].start()
            candidate_raw = content[start:end].strip()
            if candidate_raw.startswith('---'):
                candidate_raw = candidate_raw[3:].strip()
            if any(k in candidate_raw for k in ['colors:', 'name:', 'version:', 'typography:', 'theme:']):
                body = content[matches[i+1].end():].strip()
                return candidate_raw, body
    # Fallback to single start match
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    return "", content

def parse_style(style_path_or_name, styles_dir="styles"):
    """
    Parses a style specification file in either DESIGN.md format (Google Stitch / VoltAgent)
    or legacy slide deck theme format.
    
    Synthesizes presentation tokens, CSS variables, typography hierarchies, and structured
    markdown guidelines (atmosphere, dos and donts, diagram grammar) for both Python
    compilers and AI drafting agents.
    """
    resolved_path = None
    if os.path.exists(style_path_or_name):
        resolved_path = style_path_or_name
    else:
        # Search candidates
        candidates = [
            os.path.join(styles_dir, style_path_or_name),
            os.path.join(styles_dir, f"{style_path_or_name}.md"),
            os.path.join(styles_dir, f"{style_path_or_name}-design.md"),
            os.path.join(styles_dir, style_path_or_name, "DESIGN.md"),
            os.path.join(style_path_or_name, "DESIGN.md"),
            os.path.join("styles", style_path_or_name)
        ]
        for c in candidates:
            if os.path.exists(c):
                resolved_path = c
                break

        if not resolved_path:
            # Fallback to sailpoint-corporate-2026-design.md
            fallback = os.path.join(styles_dir, "sailpoint-corporate-2026-design.md")
            if os.path.exists(fallback):
                resolved_path = fallback
            else:
                raise FileNotFoundError(f"Style '{style_path_or_name}' not found.")

    with open(resolved_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter
    fm_raw, body = extract_fm_and_body(content)
    if fm_raw:
        data = safe_load_yaml_frontmatter(fm_raw)
    else:
        data = {}
        body = content

    data["body_guidelines"] = body.strip()
    data["file_path"] = resolved_path

    # Extract structured markdown sections (atmosphere, dos and donts, diagram grammar)
    sections = extract_markdown_sections(body)
    data["sections"] = sections
    data["atmosphere"] = sections.get("atmosphere", "")
    data["dos_and_donts"] = sections.get("dos_and_donts", "")
    data["diagram_grammar"] = sections.get("diagram_grammar", "")
    data["agent_priming"] = sections.get("agent_priming", "")

    # Determine mode: explicit frontmatter, markdown declaration, or background luminance
    mode = data.get("mode")
    if not mode:
        mode_match = re.search(r"\*\*Mode:\*\*\s*(light|dark)", body, re.IGNORECASE)
        if mode_match:
            mode = mode_match.group(1).lower()
        else:
            raw_colors = data.get("colors", {})
            bg_candidate = raw_colors.get("background") or raw_colors.get("canvas") or raw_colors.get("bg") or "#000000"
            lum = relative_luminance(hex_to_rgb(bg_candidate))
            mode = "light" if lum > 0.35 else "dark"
    data["mode"] = mode

    # Normalize colors
    normalized_colors = normalize_colors(data.get("colors", {}), mode=mode)
    data["colors"] = normalized_colors

    # Synthesize typography
    normalized_typography = synthesize_typography(data.get("typography", {}), mode=mode)
    data["typography"] = normalized_typography

    # Extract or synthesize presentation tokens
    presentation = data.get("presentation", {})
    accent_color = normalized_colors["accent"]
    accent_alt = normalized_colors["accent-alt"]
    bg_color = normalized_colors["background"]
    surface_color = normalized_colors["surface"]
    card_bg = normalized_colors["card-background"]

    # CSS Variables synthesis
    css_vars = dict(data.get("css_variables", {}))

    # Slide canvas gradient
    if "--deck-bg-gradient" in css_vars:
        bg_gradient = css_vars["--deck-bg-gradient"]
    elif "--theme-bg-gradient" in css_vars:
        bg_gradient = css_vars["--theme-bg-gradient"]
    elif "--sp-bg-gradient" in css_vars:
        bg_gradient = css_vars["--sp-bg-gradient"]
    elif presentation.get("slide-canvas"):
        bg_gradient = presentation["slide-canvas"]
    elif mode == "dark":
        bg_gradient = f"radial-gradient(ellipse at 85% 15%, {hex_with_alpha(accent_color, '26')} 0%, {surface_color} 50%, {bg_color} 100%)"
    else:
        bg_gradient = f"linear-gradient(135deg, {bg_color} 0%, {surface_color} 55%, {normalized_colors['surface-soft']} 100%)"

    css_vars["--deck-bg-gradient"] = bg_gradient
    css_vars["--theme-bg-gradient"] = bg_gradient

    # Card gradient & glow
    if "--theme-card-gradient" not in css_vars and "--sp-card-gradient" not in css_vars:
        if mode == "dark":
            css_vars["--theme-card-gradient"] = f"linear-gradient(145deg, {hex_with_alpha(card_bg, 'F2')} 0%, {surface_color} 100%)"
        else:
            css_vars["--theme-card-gradient"] = f"linear-gradient(145deg, {card_bg} 0%, {surface_color} 100%)"

    if "--theme-glow-accent" not in css_vars and "--sp-glow-aqua" not in css_vars:
        css_vars["--theme-glow-accent"] = f"0 0 24px {hex_with_alpha(accent_color, '35')}"
    if "--theme-glow-alt" not in css_vars and "--sp-glow-pink" not in css_vars:
        css_vars["--theme-glow-alt"] = f"0 0 24px {hex_with_alpha(accent_alt, '35')}"

    data["css_variables"] = css_vars

    # Components & Iconography synthesis
    components = dict(data.get("components", {}))
    iconography = dict(components.get("iconography", {}))
    if not iconography:
        iconography = {
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
    components["iconography"] = iconography
    data["components"] = components

    # Logo resolution
    logo_path = data.get("logo_path")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if logo_path:
        if not os.path.isabs(logo_path):
            logo_path = os.path.join(repo_root, logo_path)
    else:
        assets_dir = data.get("assets_dir")
        if assets_dir:
            assets_full = os.path.join(repo_root, assets_dir) if not os.path.isabs(assets_dir) else assets_dir
            for candidate in ["logo.svg", "logo.png", "logo-white.svg", "media/logo.svg", "media/logo.png", "media/image1.svg"]:
                cand_path = os.path.join(assets_full, candidate)
                if os.path.exists(cand_path):
                    logo_path = cand_path
                    break
    data["logo_path"] = logo_path

    return data
