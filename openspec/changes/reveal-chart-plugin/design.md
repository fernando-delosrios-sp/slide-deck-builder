## Context

`slide-deck-builder` compiles presentation specifications (`spec.yaml`) into standalone Reveal.js decks (`deck.html`) using Python and Jinja2 templates (`engine/builder.py`, `engine/templates/deck.html`, `engine/templates/deck.css`). Presentations are rendered at 1920x1080 resolution and exported to 1:1 PDF (`engine/export_pdf.py`) and 16:9 PowerPoint decks (`engine/export_pptx.py`) via headless Chrome and `decktape`.

Presently, `spec.yaml` slides support bullets, cards, metrics, comparisons, and SVG architecture diagrams, but quantitative data visualizations (bar, line, pie, doughnut charts) have no native component.

## Goals / Non-Goals

**Goals:**
- Provide a clean, declarative `chart` schema under `slide.content` in `Schema.yaml`.
- Integrate `reveal.js-plugins/chart` and `Chart.js` into `engine/templates/deck.html` with theme-aware defaults (dark/light mode colors, fonts, grid lines, and palette cycles).
- Render chart canvases (`<canvas data-chart="...">`) in `engine/builder.py` with embedded JSON comments containing datasets and options.
- Establish responsive CSS rules in `engine/templates/deck.css` preventing canvas distortion and vertical clipping across full-width and split slide layouts.
- Update `engine/preview.py` to display chart indicator badges on card previews.
- Ensure automated headless PDF and PPTX exports render charts faithfully.
- Document `content.chart` in `AGENTS.md` and `.agents/skills/spec-wizard/SKILL.md` as the preferred method for slide charts.

**Non-Goals:**
- Allowing arbitrary unsanitized Javascript execution within presentation specs.
- Deprecating metrics, cards, or custom SVG architecture diagrams (charts are strictly for quantitative data series).
- Native PPTX chart shape compilation in `export_pptx.py` (the existing DeckTape screenshot pipeline already captures high-DPI canvas charts).

## Decisions

### Decision 1: CDN Integration in `engine/templates/deck.html`
- **Choice**: Link Chart.js (v3.9.1) and `https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js` via CDN scripts in `engine/templates/deck.html`, registering `RevealChart` in `Reveal.initialize({ plugins: [ RevealNotes, RevealChart ], ... })`.
- **Rationale**: Aligns with the current architecture of `deck.html` (which already loads Reveal.js, notes plugin, and Mermaid from CDNs without requiring local node_modules).
- **Alternatives Considered**: Bundling local JS files in `assets/`. Unnecessary overhead and complexity given all other deck runtime dependencies are CDN-linked.

### Decision 2: Declarative YAML Schema in `Schema.yaml`
- **Choice**: Define a structured `chart` object under `slide.content`:
  ```yaml
  chart:
    type: bar # bar | line | pie | doughnut | radar | polarArea
    labels: ["2023", "2024", "2025", "2026"]
    datasets:
      - label: "Adoption Rate (%)"
        data: [25, 48, 72, 94]
        color: "accent" # maps to theme token, hex, or auto-assigned
      - label: "Legacy (%)"
        data: [75, 52, 28, 6]
        color: "accent-alt"
    options:
      stacked: false
      legend: true
  ```
- **Rationale**: Authoring agents (`spec-wizard`) produce structured YAML that is validated against JSON Schema, rather than fragile raw HTML or manual comment blocks.
- **Alternatives Considered**: Raw CSV string inside spec. Rejected because CSV lacks multi-dataset color mappings and option toggles.

### Decision 3: Compilation to RevealChart HTML Comments in `engine/builder.py`
- **Choice**: In `engine/builder.py`, translate the YAML chart specification into:
  ```html
  <div class="slide-chart-wrapper">
    <canvas data-chart="bar">
      <!--
      {
        "data": {
          "labels": ["2023", "2024", "2025", "2026"],
          "datasets": [...]
        },
        "options": {
          "responsive": true,
          "maintainAspectRatio": false,
          ...
        }
      }
      -->
    </canvas>
  </div>
  ```
- **Rationale**: Fully leverages the `reveal.js-plugins/chart` engine while allowing Python to resolve theme color tokens (e.g., `accent` → `#54C0E8`, `accent-alt` → `#D60EB5`).
- **Alternatives Considered**: Direct JS `new Chart()` invocations. Would bypass Reveal's slide change and resize hooks handled automatically by `RevealChart`.

### Decision 4: Theme Palette Injection & Dark/Light Mode Adaptability
- **Choice**: Pass theme color variables from `style_parser.py` into `deck.html` and `Reveal.initialize({ chart: { defaults: { ... } } })`. Set default label colors to `ink_color` / `ink_muted`, grid lines to `card_border`, and auto-cycle dataset background and border colors using theme accents (`accent_color`, `accent_alt`, and complementary harmonized hues).
- **Rationale**: Guarantees WCAG AA readability and consistent brand visual identity across light and dark themes without author intervention.

### Decision 5: Layout Architecture & Overflow Protection
- **Choice**:
  1. **Standalone Chart**: Uses `.slide-content` with `.slide-chart-wrapper` sized to `max-height: 540px; width: 100%;`.
  2. **Split Chart (with bullets or cards)**: Integrates into existing `.slide-split-grid` or creates `.chart-split-grid` (50/50 or 40/60 columns) with `max-height: 520px;`.
  3. `Chart.js` options explicitly enforce `maintainAspectRatio: false` inside the flex/grid wrapper.
- **Rationale**: Prevents vertical slide clipping and preserves presentation geometry on 1920x1080 canvases.

## Risks / Trade-offs

- **[Risk]**: Headless export capture races chart animations, leading to blank or partially rendered charts in PDF/PPTX.
  → *Mitigation*: Configure `animation: false` or short duration when `print-pdf` is present, and leverage `decktape`'s `--load-pause 1000 --pause 500` settings.
- **[Risk]**: Overly dense labels causing axis collision on complex charts.
  → *Mitigation*: Configure Chart.js ticks with `autoSkip: true, maxRotation: 45` by default in `Reveal.initialize`.
- **[Risk]**: Preview cards in `preview.html` cannot easily execute Chart.js scripts in thumbnail grids.
  → *Mitigation*: In `engine/preview.py`, render a clean visual card placeholder badge displaying the chart type, labels, and series count.
