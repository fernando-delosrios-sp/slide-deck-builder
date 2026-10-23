#!/usr/bin/env python3
import os
import sys
import subprocess

def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
    ]
    for c in candidates:
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None

def export_to_pdf(input_path, output_path=None):
    """
    Exports a presentation to a 1:1 high-fidelity PDF using decktape and headless Chrome.
    Accepts either a spec.yaml or a compiled deck.html.
    """
    input_path = os.path.abspath(input_path)

    if input_path.endswith(".yaml") or input_path.endswith(".yml"):
        spec_dir = os.path.dirname(input_path)
        html_path = os.path.join(spec_dir, "deck.html")
        if not os.path.exists(html_path):
            print(f"deck.html not found at {html_path}. Compiling from spec...")
            builder_py = os.path.join(os.path.dirname(__file__), "builder.py")
            subprocess.run([sys.executable, builder_py, input_path, html_path], check=True)
        if not output_path:
            output_path = os.path.join(spec_dir, "deck.pdf")
    else:
        html_path = input_path
        if not output_path:
            output_path = os.path.splitext(html_path)[0] + ".pdf"

    if not os.path.exists(html_path):
        print(f"Error: HTML presentation not found: {html_path}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    file_url = f"file://{html_path}"
    print(f"Exporting 1:1 PDF from {html_path}...")

    chrome_path = find_chrome()
    cmd = [
        "npx", "--yes", "decktape", "reveal",
        "-s", "1920x1080",
        "--load-pause", "1000",
        "--pause", "500",
        file_url,
        output_path
    ]
    if chrome_path:
        cmd.extend(["--chrome-path", chrome_path])

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Warning: decktape export returned non-zero code. Checking fallback...")
        if chrome_path and not (os.path.exists(output_path) and os.path.getsize(output_path) > 0):
            print("Attempting headless Chrome print-to-pdf fallback...")
            fallback_cmd = [
                chrome_path,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={output_path}",
                f"{file_url}?print-pdf"
            ]
            subprocess.run(fallback_cmd, check=True)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"\nPDF successfully generated (1:1 fidelity): {output_path}")
        return output_path
    else:
        print(f"\nError: Failed to generate PDF output at {output_path}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_pdf.py <spec_file.yaml | deck.html> [output_deck.pdf]")
        sys.exit(1)
    in_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    export_to_pdf(in_arg, out_arg)
