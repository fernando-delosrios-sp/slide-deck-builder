# Slide Deck Builder

An autonomous presentation generation pipeline. Author structured presentation specifications (`spec.yaml`), preview them with lightweight interactive card wireframes, and compile them into standalone **Reveal.js HTML decks** and editable **PowerPoint (`.pptx`) presentations**.

---

## Workspace Structure: `projects/<project-name>/`

All presentation projects reside in dedicated directories under `projects/`:
```
projects/
└── my-presentation/
    ├── context.md               # Context documentation, research, whitepapers, notes
    ├── legacy-deck.pptx         # Optional existing PowerPoint deck to modernize
    └── deck/
        ├── spec.yaml            # Specification contract adhering to Schema.yaml
        ├── preview.html         # Lightweight visual card wireframe preview
        ├── deck.html            # Standalone Reveal.js presentation
        └── deck.pptx            # Native editable PowerPoint deck
```

If `/spec-wizard` cannot find an active project from context, it interrogates you, creates the folder tree, and suggests adding context files before drafting.

---

## Architecture: The Three Pillars

Presentations are generated strictly from declarative specifications and reusable design systems:

1. **Schema ([Schema.yaml](Schema.yaml))**:
   The blueprint for presentations. Defines the required structure:
   - Metadata: `title`, `goal`, `theme`, `options` (audience, tone, language).
   - Slides array: `layout`, semantic `role`, `title`, `subtitle`, `badge`, and rich content components (`bullets`, `cards`, `metrics`, `comparison`, `regions`, `diagram`, and presenter `notes`).

2. **Layouts ([Layouts.csv](Layouts.csv))**:
   Defines available slide architectures:
   - Structure: `Title Slide`, `Title and Content`, `Two Content`, `Comparison`, `Section Header`, `Three Columns`, `Four Tiles`, `Title Only`, `Blank`, `Agenda`.
   - Grid definitions: CSS Grid templates, named container slots, and PowerPoint master layout mappings.

3. **Design System ([styles/](styles/))**:
   Theme markdown files (`*-design.md`) containing color tokens, CSS custom properties, typography scales (Google Fonts), spacing rules, and diagram grammars.
   - **Default Premier Theme**: [styles/sailpoint-corporate-2026-design.md](styles/sailpoint-corporate-2026-design.md) — SailPoint 2026 dark mode standard featuring deep cobalt gradients, glowing aqua (`#54C0E8`) and magenta (`#D60EB5`) accents, Poppins typography, and official monoline vector tech icons.

---

## Agent Workflow & Skills

Use dedicated agent skills to build and compile presentations:

### 1. `/spec-wizard` — Author & Preview
- Locates or initializes `projects/<project-name>/` and context docs.
- **PowerPoint Baseline Discovery**: Scans for existing `.pptx` decks and offers an interactive gate to modernize them as a structured baseline.
- **Content & Notes Extraction**: Runs `engine/inspect_pptx.py` to extract slide inventory, text hierarchy, tables, and speaker notes.
- Uses `grilling` to interview you on outcome details from [Schema.yaml](Schema.yaml) (title, goal, audience, length, tone, theme) and modernization targets (what to preserve, convert to semantic cards/metrics/diagrams, or prune).
- Agrees on high-level deck sections and story arc first, then drafts slide by slide.
- Automatically renders a lightweight visual HTML card preview (`projects/<project-name>/deck/preview.html`).

### 2. `/deck-builder` — Compile & Review
- Compiles the specification into an interactive **Reveal.js** presentation (`projects/<project-name>/deck/deck.html`).
  - **Features**: Keyboard navigation, slide overview mode (`Esc`), speaker notes window (`S`), and browser print-to-PDF (`?print-pdf`).
- Presents an interactive decision gate:
  - **Export to PowerPoint (.pptx)**: Generates a native editable `.pptx` using `templates/SailPoint PowerPoint Template 2026.pptx` (or programmatic master).
  - **Modify / Iterate**: Adjust slide copy or layouts.
  - **Keep As-Is / Complete**: Finalize presentation.
  - **Scrap / Start Over**: Discard.

---

## CLI Engine Usage

All engine scripts run via the project Python virtual environment:

```bash
# 1. Inspect existing PowerPoint deck (extract slide inventory, hierarchy, tables, notes):
./venv/bin/python engine/inspect_pptx.py projects/<project-name>/<file>.pptx

# 2. Generate lightweight HTML card preview:
./venv/bin/python engine/preview.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/preview.html

# 3. Compile standalone Reveal.js presentation:
./venv/bin/python engine/builder.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.html

# 4. Export to native PowerPoint (.pptx):
./venv/bin/python engine/export_pptx.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pptx
```

---

## Templates & Legacy Archive

- **PowerPoint Master Templates**: Stored in `templates/` (e.g. `templates/SailPoint PowerPoint Template 2026.pptx`).
- **Legacy NotebookLM Configuration**: Archived in [archive/notebooklm/](archive/notebooklm/).
