## 1. Schema & Engine Templates

- [ ] 1.1 Add the `chart` semantic component definition to `Schema.yaml` under `content`, specifying supported chart types (`bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`), categorical labels, dataset arrays (label, data, color, fill), and display options. Verify schema parsing with YAML validator.
- [ ] 1.2 Update `engine/templates/deck.html` to include Chart.js and `reveal.js-plugins/chart` scripts via CDN, register `RevealChart` in `Reveal.initialize()`, and configure theme-aware default styling (fonts, grid colors, ink labels, and PDF animation overrides). Verify Jinja2 template renders without syntax errors.
- [ ] 1.3 Add responsive chart container rules in `engine/templates/deck.css` (`.slide-chart-wrapper`, `.slide-chart-container`, canvas max-height, and split grid adjustments) ensuring responsive scaling and zero vertical clipping.

## 2. Builder & Preview Implementation

- [ ] 2.1 Implement chart rendering helper in `engine/builder.py` that serializes `content.chart` specifications into `<canvas data-chart="...">` blocks with embedded JSON configuration comments and maps theme color tokens (`accent`, `accent-alt`, `surface-soft`) to dataset colors.
- [ ] 2.2 Integrate chart rendering into `engine/builder.py` slide layout branches, supporting both standalone full-width chart slides and split layouts (chart alongside bullets, narrative body, or cards). Verify by compiling a test deck to HTML.
- [ ] 2.3 Update `engine/preview.py` and preview templates to detect `content.chart` and display a chart indicator badge with type and dataset count on preview cards. Verify preview generation output.

## 3. Export Verification & Authoring Guidelines

- [ ] 3.1 Create an example deck featuring diverse chart types (`bar`, `line`, `doughnut`) in `examples/` or `projects/` and build it with `engine/builder.py`.
- [ ] 3.2 Test headless PDF export (`engine/export_pdf.py`) and PPTX export (`engine/export_pptx.py`) on the chart presentation to verify canvas charts render cleanly without clipping or blank frames.
- [ ] 3.3 Update `AGENTS.md` and `.agents/skills/spec-wizard/SKILL.md` to define `content.chart` as the preferred mechanism for numerical data visualizations.
- [ ] 3.4 Run `./venv/bin/python engine/test_themes.py` to confirm zero regression across all themes.
