---
name: deck-builder
description: Compile a presentation spec (spec.yaml) and design theme into a standalone Reveal.js HTML presentation, with an interactive review gate and export to PDF and PowerPoint (.pptx).
---

Compile a presentation spec (`projects/<name>/deck/spec.yaml`) into an interactive Reveal.js presentation (`projects/<name>/deck/deck.html`), prompt for satisfaction review, and export to PDF, PowerPoint, both, or none upon approval.

## Workflow

### 1. Identify & Validate Spec
- Locate the target spec: either user-specified path or in `projects/<project-name>/deck/spec.yaml`.
- Confirm `spec.yaml` adheres to [Schema.yaml](../../../Schema.yaml) and that referenced layout names match [Layouts.csv](../../../Layouts.csv).
- Read the declared `theme` (default: `sailpoint-corporate-2026-design`).
- **Coverage gate (modernization specs, i.e. `baseline:` set)**: run `./venv/bin/python engine/check_coverage.py projects/<project-name>/deck/spec.yaml`. Do NOT compile while it reports ERRORs; fix the spec (or take the unresolved cut/merge to the user at a gate). Report remaining WARN/INFO lines (undeclared novel terms, declared additions) to the user with the build.
- **Re-read the `spec-wizard` fidelity rules** (`.agents/skills/spec-wizard/SKILL.md`) when building or iterating on a modernization; skills change between turns, so never rely on an earlier read.

### 2. Compile Reveal.js Deck
Execute the deck builder engine:
```bash
./venv/bin/python engine/builder.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.html
```

### 3. Present HTML Results
Provide the link to the generated presentation:
`[Open Presentation](projects/<project-name>/deck/deck.html)`

Explain keyboard controls:
- **Arrow keys / Space**: Navigate slides.
- **Esc**: Toggle overview tile mode.
- **S**: Open speaker notes view in a dedicated presenter window.
- **Print / PDF**: Direct browser print dialog (`?print-pdf`).

### 4. Satisfaction Review Gate
Immediately prompt the user with a structured decision gate (`ask_question`) to confirm satisfaction:
1. **(Recommended) Happy with Results**: Presentation looks good; proceed to export deliverables.
2. **Needs Refinement**: Request specific adjustments to slides, wording, or layouts.

*If the user requests refinement or reports issues*:
Apply the **Issue Triage Protocol** from `AGENTS.md` before touching code:
- **Palette, contrast, font-family, or glow issue**: Fix in `styles/<theme>-design.md` (or `engine/style_parser.py` if token synthesis failed).
- **Geometry, clipping, card overlapping, or responsive layout issue**: Fix in `engine/builder.py` CSS and verify with `./venv/bin/python engine/test_themes.py`.
- **Content density, bullet volume, or incorrect layout**: Fix in `projects/<project-name>/deck/spec.yaml`.
Re-run `builder.py`, and present the updated `deck.html` until satisfied.

### 5. Export Format Gate (When Happy)
Once the user confirms they are happy with the HTML presentation, prompt with the export choice gate (`ask_question`):
1. **(Recommended) Both PDF and PowerPoint (.pdf + .pptx)**: Compile both 1:1 pixel-perfect PDF and native 16:9 widescreen PowerPoint deck.
2. **PDF Only (.pdf)**: Compile 1:1 standalone presentation PDF using `engine/export_pdf.py`.
3. **PowerPoint Only (.pptx)**: Compile high-fidelity 16:9 widescreen PowerPoint presentation using `engine/export_pptx.py`.
4. **None**: Keep HTML presentation only without compiling exports.

### 6. Deliverable Compilation
Execute the requested exports:
- **PDF Export**:
  ```bash
  ./venv/bin/python engine/export_pdf.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pdf
  ```
  Provide clickable link: `[deck.pdf](projects/<project-name>/deck/deck.pdf)`.

- **PowerPoint Export**:
  ```bash
  ./venv/bin/python engine/export_pptx.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pptx
  ```
  Provide clickable link: `[deck.pptx](projects/<project-name>/deck/deck.pptx)`.

## Completion Criterion
`deck.html` is compiled and opened for review, the user confirms satisfaction, and any requested exports (PDF, PowerPoint, or both) are generated and delivered.

