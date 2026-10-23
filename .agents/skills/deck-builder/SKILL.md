---
name: deck-builder
description: Compile a presentation spec (spec.yaml) and design theme into a standalone Reveal.js HTML presentation, with an interactive review gate and 1:1 high-fidelity PDF export.
---

Compile a presentation spec (`projects/<name>/deck/spec.yaml`) into an interactive Reveal.js presentation (`projects/<name>/deck/deck.html`) and manage post-build review and 1:1 PDF export.

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

### 3. Present Results
Provide the link to the generated presentation:
`[Open Presentation](projects/<project-name>/deck/deck.html)`

Explain keyboard controls:
- **Arrow keys / Space**: Navigate slides.
- **Esc**: Toggle overview tile mode.
- **S**: Open speaker notes view in a dedicated window.
- **Print / PDF**: Export directly using `engine/export_pdf.py` or print dialog.

### 4. Post-Build Review Gate
Immediately prompt the user with a structured decision gate (`ask_question`):
1. **Export to 1:1 PDF (.pdf)**: Compile into a pixel-perfect standalone PDF presentation (`deck.pdf`) using `engine/export_pdf.py`.
2. **Modify / Iterate**: Request changes to specific slides, wording, or layouts.
3. **Keep As-Is / Complete**: Presentation is finalized.
4. **Scrap / Start Over**: Discard and re-draft.

### 5. High-Fidelity PDF Export (when requested)
If the user chooses the PDF export option:
```bash
./venv/bin/python engine/export_pdf.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pdf
```
Present the resulting `.pdf` file link: `[deck.pdf](projects/<project-name>/deck/deck.pdf)`.

## Completion Criterion
`deck.html` is compiled and opened for review, the user has chosen their post-build action at the gate, and any requested `.pdf` export is completed.
