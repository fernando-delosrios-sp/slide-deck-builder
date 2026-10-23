"""
Icon management system for Slide Deck Builder.
Fetches, caches, and renders Lucide icons as inline SVGs for HTML decks
and rasterized PNGs for PowerPoint (.pptx) decks.
"""

import os
import re
import urllib.request
import urllib.error
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_CACHE_DIR = os.path.join(PROJECT_ROOT, "assets", "icons", "lucide")
PNG_CACHE_DIR = os.path.join(ICON_CACHE_DIR, "png")

# Common aliases mapping to official Lucide icon names
ICON_ALIASES = {
    "security": "shield",
    "cloud-security": "shield-check",
    "lock": "lock",
    "auth": "key-round",
    "authentication": "fingerprint",
    "governance": "scale",
    "policy": "file-check-2",
    "compliance": "clipboard-check",
    "identity": "user-check",
    "user": "user",
    "users": "users",
    "account": "user",
    "accounts": "users",
    "role": "shield-alert",
    "roles": "shield",
    "api": "code-2",
    "database": "database",
    "architecture": "layers",
    "network": "network",
    "speed": "zap",
    "performance": "gauge",
    "analytics": "bar-chart-3",
    "metrics": "trending-up",
    "ai": "sparkles",
    "machine-learning": "cpu",
    "automation": "bot",
    "workflow": "git-branch",
    "integration": "plug",
    "audit": "file-search",
}

def normalize_icon_name(name: str) -> str:
    """Normalize icon name by removing prefixes, extensions, and standardizing format."""
    if not name:
        return ""
    clean = name.strip().lower()
    if clean.startswith("lucide:"):
        clean = clean[7:]
    elif clean.startswith("lucide-"):
        clean = clean[7:]
    if clean.endswith(".svg"):
        clean = clean[:-4]
    clean = clean.replace("_", "-")
    return ICON_ALIASES.get(clean, clean)

def ensure_cache_dirs():
    os.makedirs(ICON_CACHE_DIR, exist_ok=True)
    os.makedirs(PNG_CACHE_DIR, exist_ok=True)

def fetch_lucide_svg(icon_name: str) -> str:
    """
    Fetch Lucide SVG content from local cache, or download from CDN if missing.
    Returns SVG string or empty string if not found.
    """
    clean_name = normalize_icon_name(icon_name)
    if not clean_name:
        return ""

    ensure_cache_dirs()
    cached_path = os.path.join(ICON_CACHE_DIR, f"{clean_name}.svg")

    if os.path.exists(cached_path):
        try:
            with open(cached_path, "r", encoding="utf-8") as f:
                return f.read()
        except OSError:
            pass

    # Try fetching from CDNs
    urls = [
        f"https://unpkg.com/lucide-static@latest/icons/{clean_name}.svg",
        f"https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/{clean_name}.svg",
    ]

    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SlideDeckBuilder/2.0 (LucideIconFetcher)"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    svg_content = resp.read().decode("utf-8")
                    # Save to local cache
                    try:
                        with open(cached_path, "w", encoding="utf-8") as f:
                            f.write(svg_content)
                    except OSError:
                        pass
                    return svg_content
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            continue
        except Exception:
            continue

    return ""

def get_icon_svg(
    icon_name: str,
    stroke_width: str = "1.75",
    stroke_color: str = "currentColor",
    size: str = "24px",
    extra_class: str = ""
) -> str:
    """
    Get customized inline SVG string suitable for direct injection into HTML.
    """
    raw_svg = fetch_lucide_svg(icon_name)
    if not raw_svg:
        return ""

    # Strip XML comments and doc licenses
    svg = re.sub(r"<!--[\s\S]*?-->", "", raw_svg).strip()

    # Normalize svg tag attributes
    clean_name = normalize_icon_name(icon_name)
    cls_str = f"lucide-icon lucide-{clean_name} {extra_class}".strip()

    # Modify stroke-width
    svg = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{stroke_width}"', svg)

    # Modify stroke if not currentColor
    if stroke_color and stroke_color != "currentColor":
        svg = re.sub(r'stroke="currentColor"', f'stroke="{stroke_color}"', svg)

    # Replace width and height with CSS-friendly size or keep viewBox
    svg = re.sub(r'(?<!stroke-)width="[^"]*"', f'width="{size}"', svg)
    svg = re.sub(r'(?<!stroke-)height="[^"]*"', f'height="{size}"', svg)

    # Inject class
    if 'class="' in svg:
        svg = re.sub(r'class="[^"]*"', f'class="{cls_str}"', svg, count=1)
    else:
        svg = re.sub(r'<svg', f'<svg class="{cls_str}"', svg, count=1)

    return svg

def get_icon_png_path(icon_name: str, color_hex: str = "#54C0E8", size: int = 128) -> str:
    """
    Get a high-resolution PNG path for a Lucide icon (used for PowerPoint export).
    Generates and caches the PNG using macOS sips or returns empty string if unavailable.
    """
    clean_name = normalize_icon_name(icon_name)
    if not clean_name:
        return ""

    ensure_cache_dirs()
    safe_color = color_hex.lstrip("#").lower()
    png_path = os.path.join(PNG_CACHE_DIR, f"{clean_name}_{safe_color}_{size}.png")

    if os.path.exists(png_path):
        return png_path

    # Need source SVG
    raw_svg = fetch_lucide_svg(clean_name)
    if not raw_svg:
        return ""

    # Replace currentColor with requested hex color for PNG rasterization
    colored_svg = re.sub(r'stroke="currentColor"', f'stroke="{color_hex}"', raw_svg)
    temp_svg_path = os.path.join(PNG_CACHE_DIR, f"temp_{clean_name}_{safe_color}.svg")

    try:
        with open(temp_svg_path, "w", encoding="utf-8") as f:
            f.write(colored_svg)

        # Use macOS sips to convert to high-res PNG
        res = subprocess.run(
            ["sips", "-s", "format", "png", temp_svg_path, "--out", png_path, "-z", str(size), str(size)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if res.returncode == 0 and os.path.exists(png_path):
            return png_path
    finally:
        if os.path.exists(temp_svg_path):
            try:
                os.remove(temp_svg_path)
            except OSError:
                pass

    return ""


if __name__ == "__main__":
    import sys
    test_icon = sys.argv[1] if len(sys.argv) > 1 else "shield-check"
    print(f"Testing icon fetch for: {test_icon}")
    svg = get_icon_svg(test_icon, stroke_width="1.75", stroke_color="#54C0E8")
    print(f"SVG received (len {len(svg)}):")
    print(svg[:200] + "...")
    png = get_icon_png_path(test_icon, color_hex="#54C0E8")
    print(f"PNG generated at: {png} (exists: {os.path.exists(png) if png else False})")
