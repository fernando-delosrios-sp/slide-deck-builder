# Slide Deck Builder

Autonomous agent workflow for authoring presentation specifications and compiling high-fidelity slide decks. Visuals are driven by declarative styles, structured layouts, and semantic content schemas.

## Output Targets

1. **Interactive HTML Presentation (Primary)**: Standalone Reveal.js deck (`deck.html`) with dark gradient styling, keyboard navigation, overview mode (`Esc`), speaker notes (`S`), and print-to-PDF (`?print-pdf`).
2. **Native PowerPoint (.pptx)**: Optional export (`deck.pptx`) using `templates/SailPoint PowerPoint Template 2026.pptx` as the master template for SailPoint decks, or tokenized shapes for custom styles.

## Three Pillars (Sources of Truth)

Reach the file that owns the change:

- **Spec grammar & semantic components**: [Schema.yaml](Schema.yaml) defines the YAML contract (`title`, `goal`, `theme`, `slides` array with `bullets`, `cards`, `metrics`, `comparison`, `regions`, `diagram`, and presenter `notes`).
- **Layout definitions & grid templates**: [Layouts.csv](Layouts.csv) defines available slide architectures, CSS grid rules, named slots, and PowerPoint master layout mappings.
- **Visual kits & design tokens**: [styles/](styles/) holds markdown design systems (`*-design.md`). Each declares color tokens, CSS custom properties, typography scales (Google Fonts), spacing, and component bindings. Default premier theme: [styles/sailpoint-corporate-2026-design.md](styles/sailpoint-corporate-2026-design.md).

## Project Directory & Workspace

User presentations live in `projects/<project-name>/`:
- Context documentation, research, and source notes sit at `projects/<project-name>/` (e.g. `notes.md`, `brief.md`).
- Deck assets and outputs reside in `projects/<project-name>/deck/` (`spec.yaml`, `preview.html`, `deck.html`, `deck.pptx`).

## Agent Skills & Commands

- **/spec-wizard** (`.agents/skills/spec-wizard/SKILL.md`): Discovers or initializes `projects/<project-name>/`, uses `grilling` to settle outcome details from `Schema.yaml`, aligns on deck sections first, tackles slides section-by-section, and generates an interactive HTML preview (`preview.html`).
- **/deck-builder** (`.agents/skills/deck-builder/SKILL.md`): Compiles `spec.yaml` into `deck.html` (Reveal.js), opens it for user review, and handles the post-build gate (iteration, PowerPoint export to `deck.pptx`, finalization, or scrap).

## Engine CLI Scripts

All scripts run via the project Python virtual environment (`./venv/bin/python`):

```bash
# Generate lightweight HTML card preview:
./venv/bin/python engine/preview.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/preview.html

# Compile standalone Reveal.js presentation:
./venv/bin/python engine/builder.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.html

# Export to native PowerPoint (.pptx):
./venv/bin/python engine/export_pptx.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pptx
```

## Directory Conventions

- `projects/<project-name>/`: Project workspace holding context docs and `deck/` subfolder.
- `templates/`: Master presentation templates (e.g. `templates/SailPoint PowerPoint Template 2026.pptx`).
- `styles/`: Available visual design kits.
- `assets/themes/`: Static theme assets (e.g. extracted SailPoint SVGs and brand assets).
- `examples/`: Sample specs and reference presentations.
- `archive/notebooklm/`: Archived legacy Google NotebookLM prompts and setup guides.
