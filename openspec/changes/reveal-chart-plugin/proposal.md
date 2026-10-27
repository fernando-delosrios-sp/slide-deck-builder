## Why

Currently, `slide-deck-builder` offers structured slide components for bullets, cards, metrics, comparisons, and architecture diagrams (SVGs), but lacks native, declarative data visualization (bar charts, line charts, pie charts, etc.). Authors presenting quantitative data, metrics trends, or categorical distributions must either embed external static images or construct custom SVG diagrams.

Integrating the `reveal.js-plugins/chart` plugin (powered by Chart.js) establishes a first-class, declarative chart standard in the deck-building engine. This enables animated, theme-aware, responsive charts in the interactive Reveal.js presentation (`deck.html`) that cleanly serialize into 1:1 PDF exports (`deck.pdf`) and widescreen PowerPoint decks (`deck.pptx`).

## What Changes

- **Schema Grammar**: Introduce `chart` under slide `content` in `Schema.yaml`, defining declarative attributes for chart `type` (`bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`), `labels`, `datasets` (with label, data values, colors/accents), and optional layout/axes options.
- **Reveal.js Engine Integration**: In `engine/templates/deck.html`, include Chart.js and the `reveal.js-plugins/chart` plugin script, register `RevealChart` in `Reveal.initialize()`, and inject default theme palettes (fonts, grid lines, text colors) derived from the active `DESIGN.md` theme.
- **HTML Slide Compilation**: In `engine/builder.py`, implement chart rendering that outputs `<canvas data-chart="...">` blocks with embedded configuration comments, wrapped in auto-scaling container elements. Support charts as standalone hero visuals or paired side-by-side with narrative bullets/cards.
- **Deck Stylesheet**: In `engine/templates/deck.css`, add container styles (`.slide-chart-wrapper`, `.slide-chart-container`, canvas constraints) ensuring charts scale responsively without vertical clipping or overflow.
- **Card Preview Support**: In `engine/preview.py`, render a clear visual badge, chart summary, and dataset count on preview cards for quick slide auditing.
- **Authoring Guidelines**: Update `AGENTS.md` and `.agents/skills/spec-wizard/SKILL.md` to recommend `content.chart` as the preferred standard for numerical charts and data visualization.

## Capabilities

### New Capabilities
- `slide-charts`: Declarative chart component in presentation specifications powered by `reveal.js-plugins/chart` and Chart.js, with theme-coordinated styling and export support.

### Modified Capabilities
<!-- None -->

## Impact

- **Schema**: `Schema.yaml` adds `content.chart` definition.
- **Engine Templates**: `engine/templates/deck.html` includes Chart.js and RevealChart CDN scripts and initialization parameters; `engine/templates/deck.css` gains chart container styles.
- **Engine Logic**: `engine/builder.py` and `engine/preview.py` parse `content.chart` and generate HTML canvas elements and preview badges.
- **Documentation & Skills**: `AGENTS.md` and `.agents/skills/spec-wizard/SKILL.md` document the new chart capability and authoring rules.
- **Exports**: `engine/export_pdf.py` and `engine/export_pptx.py` automatically capture rendered canvas charts via headless browser export.
