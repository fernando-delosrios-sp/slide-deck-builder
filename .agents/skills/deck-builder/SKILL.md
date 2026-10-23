---
name: deck-builder
description: Compile a presentation spec (spec.yaml) and design theme into a standalone Reveal.js HTML presentation, with an interactive review gate and PowerPoint (.pptx) export.
---

Compile a presentation spec (`projects/<name>/deck/spec.yaml`) into an interactive Reveal.js presentation (`projects/<name>/deck/deck.html`) and manage post-build review and PowerPoint export.

## Workflow

### 1. Identify & Validate Spec
- Locate the target spec: either user-specified path or in `projects/<project-name>/deck/spec.yaml`.
- Confirm `spec.yaml` adheres to [Schema.yaml](../../../Schema.yaml) and that referenced layout names match [Layouts.csv](../../../Layouts.csv).
- Read the declared `theme` (default: `sailpoint-corporate-2026-design`).

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
- **Print / PDF**: Add `?print-pdf` to the URL or open print dialog to export to PDF.

### 4. Post-Build Review Gate
Immediately prompt the user with a structured decision gate (`ask_question`):
1. **Export to PowerPoint (.pptx)**: Compile into an editable native PowerPoint deck using `templates/SailPoint PowerPoint Template 2026.pptx` (or programmatic master).
2. **Modify / Iterate**: Request changes to specific slides, wording, or layouts.
3. **Keep As-Is / Complete**: Presentation is finalized.
4. **Scrap / Start Over**: Discard and re-draft.

### 5. PowerPoint (.pptx) Export (when requested)
If the user chooses the PowerPoint export option:
```bash
./venv/bin/python engine/export_pptx.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pptx
```
Present the resulting `.pptx` file link: `[deck.pptx](projects/<project-name>/deck/deck.pptx)`.

## Completion Criterion
`deck.html` is compiled and opened for review, the user has chosen their post-build action at the gate, and any requested `.pptx` export is completed.
