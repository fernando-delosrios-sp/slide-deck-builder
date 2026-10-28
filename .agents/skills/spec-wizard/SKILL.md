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
       * Use the extracted slide inventory and OCR text as the baseline for modernization.
       * **Flattened Deck Gate**: If `inspect_pptx.py` reports a `Flattened Presentation Detected (Picture-Only Slides)`:
         Present a structured gate (`ask_question`) warning the user about the reconstruction effort:
         - `reconstruct`: "Reconstruct Flattened Deck (Recommended) — reconstruct slides into native semantic components from OCR text and redraw diagrams as clean SVGs (requires higher legwork). Whole-slide screenshots will NOT be embedded as thumbnails."
         - `scratch`: "Start fresh — build from notes/brief instead of reconstructing flattened bitmaps."
         - `cancel`: "Pause — provide an editable PowerPoint deck with native vector shapes/text."
       * Record the baseline in `spec.yaml` as `baseline: "../<filename>.pptx"` (enables the coverage gate).
  3. **Mandatory Visual Review (no drafting before this)**: text extraction misses what most baseline slides actually say — screenshots, schemas, worked examples and diagrams live in images.
     - **Open every significant extracted image** in `deck/assets/` with `view_file` (raster ≥150px on both sides; `engine/check_coverage.py` lists them) and write a one-line description of what it shows into `projects/<project-name>/media-notes.md` (e.g. `image29.png — Identity Profile Mappings table: attribute → HR field, sample identity jcooper`).
     - Group-shape diagrams with no extractable text must also be understood visually before being summarised.
     - Drafting may not begin until `media-notes.md` covers every significant image. Never infer an image's content from its filename, slide title, or neighbouring text.
     - **Slide Canvas Rule**: Do NOT embed full-slide canvas screenshots (`assets/imageX.png`) in `content.image`. Embedding whole-slide screenshots into layout frames is prohibited by `check_coverage.py`. Reconstruct the slide into native semantic components (`cards`, `comparison`, `metrics`, `bullets`) using OCR text, and redraw diagrams as clean SVGs or architecture components.

### 2. Discover Outcome Details (Grilling Round)
Follow the [grilling](../grilling/SKILL.md) skill round loop to systematically settle the presentation contract without unstated assumptions.
Consult [Schema.yaml](../../../Schema.yaml) properties:
- **Title**: Human-readable presentation title.
- **Goal**: Concrete 1-2 sentence statement of what the deck must achieve.
- **Audience**: Primary audience (e.g. Executive Board, Security Architects, DevOps Engineers, Customers).
- **Tone**: Voice and demeanor (e.g. authoritative, visionary, concise, urgent).
- **Length**: Target size (`short`: 5-7 slides, `default`: 8-14 slides, `long`: 15+ slides).
- **Presenter & Date**: Authoring team or speaker (e.g. 'Enterprise IAM Architecture Team') and publication date/year (e.g. '2026') for the cover slide metadata.
- **Series / Eyebrow**: Domain or series eyebrow tag (e.g. 'SailPoint IdentityNow Architecture') for the cover badge.
- **Theme / Style**: Visual kit from `styles/` (default: `sailpoint-corporate-2026-design`) or any standard **`DESIGN.md`** kit (e.g. Linear, Vercel, Stripe from `getdesign.md` or `awesome-design-md`, imported via `engine/import_theme.py`).
- **Baseline Modernization Focus** (when modernizing an existing deck):
  - **Fidelity-First Modernization Mandate**: When starting from an existing presentation, the primary goal is **modernizing the existing slides faithfully**. Preserve the original slides' specific technical concepts, data examples, schemas, tables, diagrams, and presenter notes. Modernization means elevating visual design, typography, layout, and theme compliance—**NOT rewriting, over-interpreting, or abstracting away the domain specifics**.
  - **Consensuating Consolidations & Messaging Revisions**: The agent **MUST NOT unilaterally consolidate slides, drop slides, or alter core messaging**. If the agent identifies opportunities to prune, merge, or refine messaging, these recommendations **MUST be explicitly proposed and consensuated with the user** at a structured choice gate (`ask_question`). Without user approval, keep the baseline slides intact.
  - **Media Extraction & Slide Canvas Distinction**: `inspect_pptx.py` automatically extracts all embedded vector graphics (SVGs) and images to `projects/<project-name>/deck/assets/`. Extracted illustrations MUST be prioritized and linked in `spec.yaml` via `content.image`. However, full-slide canvas screenshots (flattened slides) MUST NOT be embedded—they must be reconstructed with native semantic components and SVG diagrams.
  - **Slide Master Backgrounds & Cover Photos**: Master slide decorative graphics, layout backgrounds, and legacy template photos extracted by `inspect_pptx.py` (e.g. split stock photos or template banners) are presentation master template artifacts, NOT content illustrations. They MUST be triaged into `baseline_cuts` (e.g. `reason: "PPTX slide master cover graphic replaced by native theme dark gradient and dedicated generated hero visual"`) and MUST NEVER be embedded as `content.image` on Title Slides.
  - **Strict Diagram Preservation Mandate**: Any baseline slide detected with an architectural, relational, or process diagram (flowcharts, node connections, multi-tier stacks) **MUST** be preserved as a visual diagram in the modernized spec.
  - **Diagram Standard (Prohibition on Embedded Mermaid)**: Embedded Mermaid is prohibited as it renders poorly in presentation slides. Modernized diagrams MUST use **high-fidelity SVGs** (`diagram.svg`, `diagram.src`, or `content.svg`) or native semantic architecture components (`pipeline`, `convergence`, `cardinality`, `policy_flow`, `layered_stack`).
  - **Icon Sizing Rule**: Icons are micro-visual accents (24px–48px). **Never blow up an icon to hero size**. When needing a picture to represent something bigger (e.g. for cover slides, split layouts, or visual metaphors), **generate one** using `generate_image`. Never recycle legacy master slide stock photos as cover heroes.
  - Preserved assets: Core technical proofs, data points, or diagrams that must stay.
  - Component elevations: Legacy bullet walls to convert into semantic components (`cards`, `metrics`, `comparison`, `diagram`, `svg`).

Halt at the gate until the user confirms all outcome details.

### 3. Agree on Deck Sections & Story Arc
Before drafting individual slides, present a structured high-level section roadmap / narrative arc:
1. Propose 3 to 5 logical sections (e.g., *Cover & Executive Context*, *Problem & Threat Landscape*, *Architecture & Solution*, *Impact & Metrics*, *Next Steps & Close*).
2. If modernizing, map baseline slides into the target sections, highlighting consolidations.
3. Allocate the target slide count across these sections.
4. Lock the section sequence with the user.
5. **Coverage ledger gate (per baseline slide, not per section)**: present a table `baseline slide → new slide | carried / merged / cut` covering **every** baseline slide, plus the baseline media each new slide will embed or redraw. Merges (several baseline slides → one) and cuts must each be listed individually and approved by the user at a structured gate. Aggregate approvals ("37→13 slides") do NOT authorize any specific merge or cut. Approved cuts are recorded as `baseline_cuts` (`approved_by_user: true`) in `spec.yaml`; every slide records `baseline_slides: [..]`.

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
   - `image`: single embedded illustration or picture (`src`, `alt`, `caption`). **Icons must remain small (24-48px)**. When a larger visual or cover picture is needed, **generate one** via `generate_image`. Never use an icon as a large picture.
   - `bullets`: concise bullet items.
   - `metrics`: stat value, label, subtext, highlight flag, and optional Lucide icon (`icon: "trending-up"`, `"zap"`). Use `highlight: true` only when an individual metric has standout relevance.
   - `cards`: titled container cards with badge and Lucide icon (`icon: "shield-check"`, `"user-round"`, `"layers"`, `"database"`).
   - `comparison`: side-by-side before/after or contrast blocks.
   - `diagram`: high-fidelity SVG diagram (`svg`, `src`) or native architecture components (`pipeline`, `convergence`, `cardinality`, `policy_flow`, `layered_stack`). **Never use embedded Mermaid**.
     * **SVG Architecture Template (Gold Standard)**: Follow the blueprint from `examples/Identity Model Components and Access Model`:
       - ViewBox: `viewBox="0 0 1000 520"` with `width="100%" height="100%"`.
       - Theme card backdrop: `<rect width="1000" height="520" rx="16" fill="#070C16" stroke="#415364" stroke-width="1.5"/>`.
       - Node styling: Linear gradients (`idGrad`, `accGrad`, `accsGrad`), rounded rects (`rx="10-12"`), and colored strokes.
       - Node anatomy: Bold 11px uppercase category badges (`CORE ENTITY`, `TARGET APPLICATION`), 18px bold title, Lucide glyph/icon in circle badge, 11-12px description bullets.
       - Clean `<path>` connectors with `<marker id="arr">` arrowheads.
       - Architecture Takeaway Banner: Horizontal container at bottom (`y="425"`, `height="65"`) highlighting the core governance principle.
   - `notes`: speaker script and background notes.
   - **Console UI Screenshot Walkthrough Archetype**: When baseline slides show actual UI screens (e.g. IdentityNow console views):
     * Always select `layout: "Picture with Caption"` and `role: "walkthrough"`.
     * Embed high-res screenshot under `content.image.src`.
     * Provide a precise title & subtitle, an executive caption (e.g. `"[Product] Console: [Context] Interface"`), and a 1-2 sentence `content.body` explaining what is configured.
   - **Procedural Sequence & Governance Card Archetypes**:
     * For multi-step administrative workflows (e.g. 4-step setup), use `layout: "Four Tiles"` with numbered card titles (`1. Create Source`, `2. Create Identity Profile`) and functional badges (`Connections`, `Identities`, `Policy`, `Data Import`).
     * For foundational pillars, use `layout: "Three Columns"` with Lucide icons (`user`, `key`, `shield`) and selective `highlight: true` on primary entities.
   - **Title Slide (Cover) Mandatory Anatomy**: Every presentation cover slide (`layout: "Title Slide"`, `role: "cover"`) MUST include:
     * `badge`: Domain or series eyebrow tag (e.g. `SailPoint IdentityNow Architecture`), rendering as a top pill badge and populating `SERIES` in the footer.
     * `title`: Main presentation title.
     * `subtitle`: Architectural or domain scope subtitle.
     * `content.body`: 1–2 sentence executive synopsis or abstract detailing what the deck delivers (prevents empty negative space).
     * `content.presenter`: Authoring team or speaker (e.g. `Enterprise IAM Architecture Team`).
     * `content.date`: Publication year or date (e.g. `'2026'`).
     * `content.image`: High-presence hero visual custom-generated via `generate_image` (e.g. 3D isometric architecture, cybernetic core, glowing nodes). Never recycle legacy master slide stock photos.
   - **Theme Accent & Visual Weight Hierarchy**: When multiple elements on screen have the same weight (e.g. peer cards in a grid representing equal categories, peer steps, or equal metrics), do NOT mix and match accents. Use the most vivid accents (e.g. fuchsia / `accent-alt` glowing border) strictly to highlight items that have more relevance (e.g. standout metrics, critical warnings, winning options, or high-priority items), while using less vivid accents (e.g. electric aqua / `accent`, subtle theme borders) to decorate regular or peer items.
5. **Provenance rule (modernizing)**: slide content must come from the baseline text, notes, or images. Do not add vendor/product names, examples, steps, or claims from general knowledge. If an addition truly helps, list it in the slide's `additions:` so it is shown to the user at the gate; undeclared additions are defects. Worked examples and sample data visible in baseline images (e.g. `E001 / Malory Archer`) are preferred over invented ones.
6. **Keep the original visuals' information**: a baseline image is either embedded (`content.image`), faithfully reproduced as SVG with every label/value preserved and listed in `redrawn_media`, or approved as a `baseline_cuts` media entry. Summarising it into text cards counts as dropping it.
7. Update `projects/<project-name>/deck/spec.yaml`.

### 5. Coverage Gate, Generate & Present HTML Preview
When modernizing, run the coverage gate first and fix every ERROR (never silence it by adding unapproved `baseline_cuts`):
```bash
./venv/bin/python engine/check_coverage.py projects/<project-name>/deck/spec.yaml
```
Show the user the gate's `INFO` lines (declared additions) and any `WARN` lines together with the preview.

Run the preview engine to create the visual card wireframe deck:
```bash
./venv/bin/python engine/preview.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/preview.html
```

Clearly notify the user that drafting is complete and the workflow is paused at a review gate awaiting their confirmation. Explicitly explain the two artifacts:
- **Low-level specification ([spec.yaml](file:///Users/fernando.delosrios/Documents/Development/AI/slide-deck-builder/projects/<project-name>/deck/spec.yaml))**: Declarative semantic definition containing exact content schemas, slot bindings, visual assets, layouts, and presenter notes.
- **High-level visual preview ([preview.html](file:///Users/fernando.delosrios/Documents/Development/AI/slide-deck-builder/projects/<project-name>/deck/preview.html))**: Interactive card-deck wireframe to review overall narrative flow, section balance, and slide architecture before final compilation.

Display a structured gate (`ask_question`) requiring user confirmation before any deck compilation:
1. **Proceed to Build**: Ready to compile into full Reveal.js deck (`/deck-builder`).
2. **Refine Section/Slides**: Iterate on specific slides, wording, or layout assignments.
3. **Change Visual Theme**: Switch the style theme in `spec.yaml`.

## Completion Criterion
`projects/<project-name>/deck/spec.yaml` is fully drafted and validated against `Schema.yaml`, `preview.html` is generated, and the user has approved the preview or initiated `/deck-builder`.

