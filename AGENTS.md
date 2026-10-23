# Slide Deck Builder

Autonomous agent workflow for authoring presentation specifications and compiling high-fidelity slide decks. Visuals are driven by declarative styles, structured layouts, and semantic content schemas.

## Output Targets

1. **Interactive HTML Presentation (Primary)**: Standalone Reveal.js deck (`deck.html`) with dark gradient styling, keyboard navigation, overview mode (`Esc`), speaker notes (`S`), and print-to-PDF (`?print-pdf`).
2. **1:1 High-Fidelity PDF Export**: Pixel-perfect standalone PDF presentation (`deck.pdf`) compiled via headless browser (`engine/export_pdf.py`).

## Three Pillars (Sources of Truth)

Reach the file that owns the change:

- **Spec grammar & semantic components**: [Schema.yaml](Schema.yaml) defines the YAML contract (`title`, `goal`, `theme`, `slides` array with `bullets`, `cards`, `metrics`, `comparison`, `regions`, `diagram`, `svg`, presenter `notes`, and embedded `image`).
- **Modernization Fidelity & Consensus Mandate**: When modernizing an existing deck, the first goal is **modernizing the existing slides faithfully**. Preserve original slide topics, technical schema mappings, data examples, tables, and narrative flow. Any proposed consolidation, omission, or major messaging revision **MUST be consensuated with the user** at a structured choice gate before altering slide inventory.
  - **Enforced, not advisory**: every spec slide declares `baseline_slides`; every cut is a user-approved `baseline_cuts` entry; every significant baseline image is embedded, faithfully redrawn (`redrawn_media`), or an approved cut; every fact not in the baseline is declared in `additions`. `engine/check_coverage.py` verifies this and `engine/builder.py` refuses to build a modernization spec that fails it.
  - **Look at the images**: before drafting, open every significant extracted image and record what it shows in `media-notes.md`. Text extraction alone is never a sufficient reading of a baseline slide.
  - **Flattened decks & slide canvases**: when a baseline deck consists of flattened full-slide bitmaps (detected by `engine/inspect_pptx.py`), OCR text provides the baseline vocabulary. Full-slide canvas images MUST NOT be embedded in `spec.yaml` (`content.image`). Instead, reconstruct the slide using native semantic components (`cards`, `comparison`, `metrics`, `bullets`) and redraw diagrams as clean SVGs (`diagram.svg` or native architecture components). `engine/check_coverage.py` rejects spec slides that embed full-slide canvases.
  - **No invention**: do not add names, examples, or claims from general knowledge to modernized slides; use what the baseline shows.
  - **Re-read skills each phase**: skill and rule files change during a session; re-read them before each phase instead of trusting an earlier read.
- **Diagram Standard (SVGs over Mermaid)**: Embedded Mermaid is prohibited for slide decks as it produces low-contrast, clipped, and inconsistent visuals. Architectural diagrams MUST be authored as high-fidelity SVGs (`diagram.svg`, `diagram.src`, or `content.svg`) or native semantic architecture components (`pipeline`, `convergence`, `cardinality`, `policy_flow`, `layered_stack`).
- **Icon Sizing & Image Generation**: Icons are micro-visual accents (24px–48px) and MUST remain small. Never blow up an icon into a hero graphic or large slide picture. When needing a picture to represent something bigger (e.g. cover slide or hero visual), **generate one** using `generate_image`.
- **Layout definitions & grid templates**: [Layouts.csv](Layouts.csv) defines available slide architectures, CSS grid rules, and named slots.
- **Visual kits & design tokens**: [styles/](styles/) holds markdown design systems (`*-design.md`). Each declares color tokens, CSS custom properties, typography scales (Google Fonts), spacing, and component bindings. Default premier theme: [styles/sailpoint-corporate-2026-design.md](styles/sailpoint-corporate-2026-design.md).

## Project Directory & Workspace

User presentations live in `projects/<project-name>/`:
- Context documentation, research, and source notes sit at `projects/<project-name>/` (e.g. `notes.md`, `brief.md`).
- Deck assets and outputs reside in `projects/<project-name>/deck/` (`spec.yaml`, `preview.html`, `deck.html`, `deck.pdf`).

## Agent Skills & Commands

- **/spec-wizard** (`.agents/skills/spec-wizard/SKILL.md`): Discovers or initializes `projects/<project-name>/`, detects PowerPoint decks to offer modernization baselines, uses `grilling` to settle outcome details from `Schema.yaml`, aligns on deck sections first, tackles slides section-by-section, and generates an interactive HTML preview (`preview.html`).
- **/deck-builder** (`.agents/skills/deck-builder/SKILL.md`): Compiles `spec.yaml` into `deck.html` (Reveal.js), opens it for user review, and handles the post-build gate (iteration, 1:1 PDF export to `deck.pdf`, finalization, or scrap).

## Engine CLI Scripts

All scripts run via the project Python virtual environment (`./venv/bin/python`):

```bash
# Inspect existing PowerPoint deck (extract slide inventory, hierarchy, tables, notes):
./venv/bin/python engine/inspect_pptx.py projects/<project-name>/<file>.pptx

# Generate lightweight HTML card preview:
./venv/bin/python engine/preview.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/preview.html

# Compile standalone Reveal.js presentation:
./venv/bin/python engine/builder.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.html

# Export to 1:1 high-fidelity PDF:
./venv/bin/python engine/export_pdf.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pdf
```

## Directory Conventions

- `projects/<project-name>/`: Project workspace holding context docs and `deck/` subfolder.
- `templates/`: Master presentation templates (e.g. `templates/SailPoint PowerPoint Template 2026.pptx`).
- `styles/`: Available visual design kits.
- `assets/themes/`: Static theme assets (e.g. extracted SailPoint SVGs and brand assets).
- `examples/`: Sample specs and reference presentations.
- `archive/notebooklm/`: Archived legacy Google NotebookLM prompts and setup guides.
