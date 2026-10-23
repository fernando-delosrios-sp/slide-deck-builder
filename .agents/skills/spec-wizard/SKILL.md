---
name: spec-wizard
description: Guide the creation of a presentation specification (spec.yaml) from project documentation or scratch, using relentless grilling and section-by-section drafting, and generate an interactive lightweight HTML preview card deck.
---

Author a validated presentation spec (`projects/<project-name>/deck/spec.yaml`) and generate an interactive single-file HTML preview (`projects/<project-name>/deck/preview.html`).

## Workflow

### 1. Project Directory Resolution
The user works from a dedicated project directory: `projects/<project-name>/`.
- **Check context**: Determine if an active project folder exists in `projects/` (or was passed by the user).
- **If no project folder is found**:
  1. Interrogate the user for the project name or topic slug using structured choices.
  2. Create the directory tree:
     ```bash
     mkdir -p projects/<project-name>/deck
     ```
  3. Prompt the user to supply or drop relevant documentation, notes, outlines, or briefs into `projects/<project-name>/` (e.g. `notes.md`, `brief.md`, technical whitepapers).
  4. Inspect and read all documents residing in `projects/<project-name>/` before proceeding.

### 2. Discover Outcome Details (Grilling Round)
Follow the [grilling](../grilling/SKILL.md) skill round loop to systematically settle the presentation contract without unstated assumptions.
Consult [Schema.yaml](../../../Schema.yaml) properties:
- **Title**: Human-readable presentation title.
- **Goal**: Concrete 1-2 sentence statement of what the deck must achieve.
- **Audience**: Primary audience (e.g. Executive Board, Security Architects, DevOps Engineers, Customers).
- **Tone**: Voice and demeanor (e.g. authoritative, visionary, concise, urgent).
- **Length**: Target size (`short`: 5-7 slides, `default`: 8-14 slides, `long`: 15+ slides).
- **Theme / Style**: Visual kit from `styles/` (default: `sailpoint-corporate-2026-design`).

Halt at the gate until the user confirms all outcome details.

### 3. Agree on Deck Sections & Story Arc
Before drafting individual slides, present a structured high-level section roadmap / narrative arc:
1. Propose 3 to 5 logical sections (e.g., *Cover & Executive Context*, *Problem & Threat Landscape*, *Architecture & Solution*, *Impact & Metrics*, *Next Steps & Close*).
2. Allocate the target slide count across these sections.
3. Lock the section sequence with the user.

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
`projects/<project-name>/deck/spec.yaml` is fully drafted, `preview.html` is generated, and the user has approved the preview or initiated `/deck-builder`.
