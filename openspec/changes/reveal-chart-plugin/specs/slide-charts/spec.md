## Purpose

Provides declarative data visualization components in slide presentations using the Reveal.js Chart plugin and Chart.js, rendering responsive, theme-aware animated charts across HTML, PDF, and PPTX formats.

## ADDED Requirements

### Requirement: Declarative Chart Specification
The presentation specification SHALL allow authors to declare a `chart` component within slide `content` specifying chart type (`bar`, `line`, `pie`, `doughnut`, `radar`, `polarArea`), categorical labels, numerical datasets, and optional display configurations.

#### Scenario: Author specifies a multi-series bar chart
- **WHEN** a slide definition includes `content.chart` with `type: bar`, `labels: ["Q1", "Q2", "Q3", "Q4"]`, and two numerical datasets
- **THEN** the engine validates the schema and renders an HTML chart canvas configured with the specified categories and data series.

#### Scenario: Author specifies a line chart with custom options
- **WHEN** a slide definition includes `content.chart` with `type: line` and optional curve or legend settings
- **THEN** the engine includes the custom display options in the embedded chart configuration comment.

### Requirement: Theme Palette Integration
The presentation engine SHALL automatically style chart elements (datasets, grid lines, tick labels, tooltips, and legends) using active theme tokens from the selected `DESIGN.md` theme when explicit dataset colors are omitted.

#### Scenario: Chart renders in dark mode theme
- **WHEN** a chart slide is compiled using a dark-mode theme
- **THEN** chart axis tick marks and label text render in theme ink colors, grid lines render in subtle muted border tones, and data series use theme accent and accent-alt colors.

#### Scenario: Chart renders in light mode theme
- **WHEN** a chart slide is compiled using a light-mode theme
- **THEN** chart axis ticks and labels render in dark ink colors and data series draw from the light-mode palette tokens.

### Requirement: Dual Slide Layout Compositions
The presentation engine SHALL support rendering charts as standalone slide visual centerpieces or side-by-side alongside narrative bullet points or feature cards without vertical overflow.

#### Scenario: Standalone full-width chart slide
- **WHEN** a slide contains `content.chart` without accompanying bullets or cards
- **THEN** the engine renders the chart canvas in an auto-scaling, centered container that occupies the slide body.

#### Scenario: Split layout with narrative bullets and chart
- **WHEN** a slide defines both `content.bullets` and `content.chart`
- **THEN** the engine renders a two-column grid with bullets on the left and the chart canvas on the right, constrained to prevent vertical overflow.

### Requirement: Headless PDF and PPTX Export Compatibility
Presentation charts SHALL render and settle before headless browser slide capture, ensuring exported PDF and PPTX slides contain fully visualized charts identical to the interactive Reveal.js presentation.

#### Scenario: Exporting a presentation containing charts to PDF
- **WHEN** an author runs `engine/export_pdf.py` on a presentation with chart slides
- **THEN** the resulting PDF presentation renders each chart with complete labels, plotted data, and legends.

#### Scenario: Exporting a presentation containing charts to PPTX
- **WHEN** an author runs `engine/export_pptx.py` on a presentation with chart slides
- **THEN** the exported PowerPoint slides capture the rendered chart visuals at 16:9 widescreen resolution.

### Requirement: Card Preview Presentation
The lightweight card preview generator SHALL detect chart slides and display a visual indicator and dataset summary on the corresponding preview card.

#### Scenario: Generating slide preview for a chart slide
- **WHEN** `engine/preview.py` processes a slide containing `content.chart`
- **THEN** the generated preview card displays a chart badge indicating the chart type and number of datasets.
