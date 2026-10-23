---
name: spec-wizard
description: Author a presentation specification (spec.yaml) and preview deck from project documentation, scratch, or an existing PowerPoint (.pptx) deck baseline.
---

Author a validated presentation spec (`projects/<project-name>/deck/spec.yaml`) and generate an interactive single-file HTML preview (`projects/<project-name>/deck/preview.html`).

## Workflow

### 1. Project Directory Resolution & Baseline Discovery
The user works from a dedicated project directory: `projects/<project-name>/`.
- **Check context**: Determine if an active project folder exists in `projects/` (or was passed by the user).
- **If no project folder is found**:
  1. Interrogate the user for the project name or topic slug using structured choices.
  2. Create the directory tree:
     ```bash
     mkdir -p projects/<project-name>/deck
     ```
  3. Prompt the user to supply or drop documentation, notes, outlines, briefs, or existing PowerPoint decks into `projects/<project-name>/`.
- **Inspect project files**:
  1. Read all text documents in `projects/<project-name>/` (e.g. `notes.md`, `brief.md`).
  2. **PowerPoint Baseline Discovery**: Check for `.pptx` or `.ppt` files in `projects/<project-name>/`.
     - When discovered, present a structured gate (`ask_question`):
       * `modernize`: "Modernize `<filename>` (Recommended) — extract slide inventory, narrative flow, and presenter notes as baseline to restructure into modern semantic components."
       * `scratch`: "Start fresh — build from notes, brief, or scratch without the existing presentation."
     - If modernizing:
       * Run the inspection engine to parse slides, text hierarchy, layouts, and presenter notes:
         ```bash
         ./venv/bin/python engine/inspect_pptx.py projects/<project-name>/<filename>.pptx
         ```
       * Use the extracted slide inventory as the baseline for modernization.

### 2. Discover Outcome Details (Grilling Round)
Follow the [grilling](../grilling/SKILL.md) skill round loop to systematically settle the presentation contract without unstated assumptions.
Consult [Schema.yaml](../../../Schema.yaml) properties:
- **Title**: Human-readable presentation title.
- **Goal**: Concrete 1-2 sentence statement of what the deck must achieve.
- **Audience**: Primary audience (e.g. Executive Board, Security Architects, DevOps Engineers, Customers).
- **Tone**: Voice and demeanor (e.g. authoritative, visionary, concise, urgent).
- **Length**: Target size (`short`: 5-7 slides, `default`: 8-14 slides, `long`: 15+ slides).
- **Theme / Style**: Visual kit from `styles/` (default: `sailpoint-corporate-2026-design`).
- **Baseline Modernization Focus** (when modernizing an existing deck):
  - Preserved assets: Core technical proofs, data points, or diagrams that must stay.
  - Component elevations: Legacy bullet walls to convert into semantic components (`cards`, `metrics`, `comparison`, `diagram`).
  - Cuts & consolidations: Redundant, outdated, or low-value slides to prune.

Halt at the gate until the user confirms all outcome details.

### 3. Agree on Deck Sections & Story Arc
Before drafting individual slides, present a structured high-level section roadmap / narrative arc:
1. Propose 3 to 5 logical sections (e.g., *Cover & Executive Context*, *Problem & Threat Landscape*, *Architecture & Solution*, *Impact & Metrics*, *Next Steps & Close*).
2. If modernizing, map baseline slides into the target sections, highlighting consolidations.
3. Allocate the target slide count across these sections.
4. Lock the section sequence with the user.

### 4. Tackle Sections One by One
Work through the agreed sections sequentially. For each section:
1. Propose the slide sequence within that section.
2. Select precise layouts from [Layouts.csv](../../../Layouts.csv) (`Title Slide`, `Title and Content`, `Two Content`, `Comparison`, `Section Header`, `Three Columns`, `Four Tiles`, `Picture with Caption`, `Content with Caption`).
3. **Visual Asset Consensus (Gate Before Generation)**:
   - Identify slides where custom imagery adds value (e.g. cover concept, architecture flow, comparison graphic).
   - Propose candidate visual concepts, target slide, and image prompts to the user.
   - Halt at a structured gate (`ask_question`) to agree on the visual plan before generating: approve generation, adjust prompt/concept, or decline images.
   - Run `generate_image` only after explicit user approval. Save generated files to `projects/<project-name>/deck/assets/` and link them in `spec.yaml` (`content.image` or `Picture with Caption`). When declined, express the concept using semantic components (`cards`, `diagram`, `metrics`, `comparison`).
4. Apply semantic content blocks according to [Schema.yaml](../../../Schema.yaml):
   - `image`: single embedded illustration or diagram (`src`, `alt`, `caption`).
   - `bullets`: concise bullet items.
   - `metrics`: stat value, label, subtext, highlight flag.
   - `cards`: titled container cards with badge and icon.
   - `comparison`: side-by-side before/after or contrast blocks.
   - `diagram`: flow or architecture node relationships.
   - `notes`: speaker script and background notes.
5. Update `projects/<project-name>/deck/spec.yaml`.

### 5. Generate & Present HTML Preview
Run the preview engine to create the visual card wireframe deck:
```bash
./venv/bin/python engine/preview.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/preview.html
```

Present the generated [preview.html](file:///Users/fernando.delosrios/Documents/Development/AI/slide-deck-builder/projects/<project-name>/deck/preview.html) to the user.

Display a structured gate (`ask_question`):
1. **Proceed to Build**: Ready to compile into full Reveal.js deck (`/deck-builder`).
2. **Refine Section/Slides**: Iterate on specific slides, wording, or layout assignments.
3. **Change Visual Theme**: Switch the style theme in `spec.yaml`.

## Completion Criterion
`projects/<project-name>/deck/spec.yaml` is fully drafted and validated against `Schema.yaml`, `preview.html` is generated, and the user has approved the preview or initiated `/deck-builder`.

