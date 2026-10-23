import os
import re
import yaml

def parse_style(style_path_or_name, styles_dir="styles"):
    """
    Parses a style markdown file (e.g. styles/sailpoint-corporate-2026-design.md).
    Returns a dict containing frontmatter tokens, CSS variables, and markdown guidelines.
    """
    if not os.path.exists(style_path_or_name):
        candidates = [
            os.path.join(styles_dir, style_path_or_name),
            os.path.join(styles_dir, f"{style_path_or_name}.md"),
            os.path.join(styles_dir, f"{style_path_or_name}-design.md")
        ]
        found = False
        for c in candidates:
            if os.path.exists(c):
                style_path_or_name = c
                found = True
                break
        if not found:
            # Fallback to sailpoint-corporate-2026-design.md
            fallback = os.path.join(styles_dir, "sailpoint-corporate-2026-design.md")
            if os.path.exists(fallback):
                style_path_or_name = fallback
            else:
                raise FileNotFoundError(f"Style '{style_path_or_name}' not found.")

    with open(style_path_or_name, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if fm_match:
        fm_raw, body = fm_match.groups()
        data = yaml.safe_load(fm_raw) or {}
    else:
        data = {}
        body = content

    data["body_guidelines"] = body.strip()
    data["file_path"] = style_path_or_name

    # Determine mode: check frontmatter, markdown body, or background luminance
    mode = data.get("mode")
    if not mode:
        mode_match = re.search(r"\*\*Mode:\*\*\s*(light|dark)", body, re.IGNORECASE)
        if mode_match:
            mode = mode_match.group(1).lower()
        else:
            bg_hex = data.get("colors", {}).get("background", "#000000").lstrip("#")
            if len(bg_hex) == 3:
                bg_hex = "".join([c*2 for c in bg_hex])
            try:
                r = int(bg_hex[0:2], 16)
                g = int(bg_hex[2:4], 16)
                b = int(bg_hex[4:6], 16)
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                mode = "light" if lum > 128 else "dark"
            except Exception:
                mode = "dark"
    data["mode"] = mode

    # Determine theme logo if explicitly defined in frontmatter or discovered in assets_dir
    logo_path = data.get("logo_path")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if logo_path:
        if not os.path.isabs(logo_path):
            logo_path = os.path.join(repo_root, logo_path)
    else:
        assets_dir = data.get("assets_dir")
        if assets_dir:
            assets_full = os.path.join(repo_root, assets_dir) if not os.path.isabs(assets_dir) else assets_dir
            # Check standard logo filenames
            for candidate in ["logo.svg", "logo.png", "logo-white.svg", "media/logo.svg", "media/logo.png", "media/image1.svg"]:
                cand_path = os.path.join(assets_full, candidate)
                if os.path.exists(cand_path):
                    logo_path = cand_path
                    break
    data["logo_path"] = logo_path

    return data
