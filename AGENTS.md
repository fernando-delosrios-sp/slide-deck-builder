# Slide Deck Builder

Autonomous agent workflow for authoring presentation specifications and compiling high-fidelity slide decks. Visuals are driven by declarative styles, structured layouts, and semantic content schemas.

## Output Targets

1. **Interactive HTML Presentation (Primary)**: Standalone Reveal.js deck (`deck.html`) with dark gradient styling, keyboard navigation, overview mode (`Esc`), speaker notes (`S`), and print-to-PDF (`?print-pdf`).
2. **1:1 High-Fidelity PDF Export**: Pixel-perfect standalone PDF presentation (`deck.pdf`) compiled via headless browser (`engine/export_pdf.py`).
3. **PowerPoint (.pptx) Export**: High-fidelity standalone 16:9 widescreen PowerPoint deck (`deck.pptx`) compiled from Reveal.js slides from scratch (`engine/export_pptx.py`), preserving custom layouts, SVGs, and presenter notes.

## Three Pillars (Sources of Truth)

Reach the file that owns the change:

- **Spec grammar & semantic components**: [Schema.yaml](Schema.yaml) defines the YAML contract (`title`, `goal`, `theme`, `slides` array with `bullets`, `cards`, `metrics`, `comparison`, `regions`, `diagram`, `svg`, presenter `notes`, and embedded `image`). Cover slides require `badge`, `subtitle`, `content.body` (1-2 sentence executive abstract), `content.presenter`, `content.date`, and a generated hero `image`.
- **Modernization Fidelity & Consensus Mandate**: When modernizing an existing deck, the first goal is **modernizing the existing slides faithfully**. Preserve original slide topics, technical schema mappings, data examples, tables, and narrative flow. Any proposed consolidation, omission, or major messaging revision **MUST be consensuated with the user** at a structured choice gate before altering slide inventory.
  - **Enforced, not advisory**: every spec slide declares `baseline_slides`; every cut is a user-approved `baseline_cuts` entry; every significant baseline image is embedded, faithfully redrawn (`redrawn_media`), or an approved cut; every fact not in the baseline is declared in `additions`. `engine/check_coverage.py` verifies this and `engine/builder.py` refuses to build a modernization spec that fails it.
  - **Look at the images**: before drafting, open every significant extracted image and record what it shows in `media-notes.md`. Text extraction alone is never a sufficient reading of a baseline slide.
  - **Hidden Slides Policy (Ignore by Default)**: When processing a baseline PowerPoint presentation (`.pptx`), hidden slides (marked with `show="0"` in OpenXML) are automatically ignored by default during inspection (`engine/inspect_pptx.py`) and coverage verification (`engine/check_coverage.py`). Presenters frequently store raw clickstream screenshots, internal notes, or deprecated appendix dumps on hidden slides. Modernization focuses on the visible slide narrative. To explicitly include hidden slides if requested, pass `--include-hidden`.
  - **Flattened decks & slide canvases**: when a baseline deck consists of flattened full-slide bitmaps (detected by `engine/inspect_pptx.py`), OCR text provides the baseline vocabulary. Full-slide canvas images MUST NOT be embedded in `spec.yaml` (`content.image`). Instead, automatically reconstruct the slide using native semantic components (`cards`, `comparison`, `metrics`, `bullets`) and redraw diagrams as clean SVGs (`diagram.svg` or native architecture components). Do NOT pause at an interactive choice gate to prompt the user about whole-slide reconstruction hurdles; perform the reconstruction directly. `engine/check_coverage.py` rejects spec slides that embed full-slide canvases.
  - **No invention**: do not add names, examples, or claims from general knowledge to modernized slides; use what the baseline shows.
  - **Re-read skills each phase**: skill and rule files change during a session; re-read them before each phase instead of trusting an earlier read.
- **Diagram Standard (SVGs over Mermaid)**: Embedded Mermaid is prohibited for slide decks as it produces low-contrast, clipped, and inconsistent visuals. Architectural diagrams MUST be authored as high-fidelity SVGs (`diagram.svg`, `diagram.src`, or `content.svg`) or native semantic architecture components (`pipeline`, `convergence`, `cardinality`, `policy_flow`, `layered_stack`).
  - **Exemplar Modernization Benchmark (`examples/Identity Model Components and Access Model/`)**: Canonical reference for high-fidelity modernization. Follow its architectural blueprint:
    - **SVG Diagram Template**: Use `viewBox="0 0 1000 520"`, dark card backdrop (`#070C16`, `rx="16"`, border `#415364`), theme gradient nodes (e.g. `#0033A1` to `#0B111E`), uppercase bold category badges (11px), node titles (18px), Lucide-styled node icons/glyphs, clean `<path>` connectors with dedicated `<marker>` arrowheads, and a bottom rounded banner (`height="65"`) stating the governing architectural principle.
    - **Arrow & Connector Color Uniformity Mandate**: Arrows and path connectors must have the exact same color across all their parts. An arrow's shaft (`stroke`) and its arrowhead (`marker-end` / `marker-start` `fill`) must match 100%. Creating an arrow with mismatched body and head colors (e.g., magenta line with cyan arrowhead) is strictly prohibited. When creating SVG diagrams, define dedicated markers for each accent color used (e.g. `marker-aqua` with `fill="#54C0E8"`, `marker-pink` with `fill="#D60EB5"`, `marker-green` with `fill="#93D500"`) and pair them strictly with paths sharing that stroke. Enforced automatically as an `ERROR` by `engine/check_coverage.py`.
    - **Zero-Overlap & Corridor Routing Mandate**: Connectors, paths, and arrows must NEVER overlap, cut through, or intersect diagram nodes, cards, or text elements. When routing between non-adjacent or tiered entities, paths must use orthogonal dogleg routing through unobstructed corridors between elements with at least 15px clearance. Connector labels and cardinality badges (`1 .. N`) must be positioned along open path segments and never collide with node borders. Enforced automatically as a build-aborting `ERROR` by `engine/check_coverage.py`.
    - **Container Wrapping & Enclosure Mandate**: Outer diagram card backdrops, column containers, and grouped tiers MUST strictly enclose all child cards, inner rects, and text elements with at least 15px internal bottom padding. The bottom edge (`y + height`) of any child card or text element must NEVER extend beyond or cross the bottom stroke of its parent container. Sizing must be calculated precisely (e.g. parent container `height="400"`, child ends at `y=374`) to prevent bottom edge overflow. Enforced automatically by `engine/check_coverage.py`.
    - **Console Screenshot Walkthroughs**: For baseline UI screenshots, use `layout: "Picture with Caption"`, `role: "walkthrough"`, precise caption (`"[Product] Console: [Context] Interface"`), and a 1-2 sentence `content.body` summarizing what the interface configures.
    - **Procedural & Governance Card Archetypes**: Use `Four Tiles` with numbered card titles (`1. Step Name`, `2. Step Name`) and functional badges (`Connections`, `Policy`, `Data Import`) for sequence slides; use `Three Columns` with Lucide icons (`user`, `key`, `shield`) and uniform peer styling (never apply `highlight: true` to arbitrary peer pillars).
    - **Preserve Real Baseline Data**: Retain original sample identities, usernames, attributes, and correlation rules (e.g. `John Cooper / jcooper`, `Sterling Archer`, `attributes.department: Finance`). Never replace baseline data with generic placeholders.
- **Icon Sizing & Tailored Hero Image Generation**:
  - **Icon Sizing Rule**: Icons are micro-visual accents (24px–48px) and MUST remain small. Never blow up an icon into a hero graphic or large slide picture. Slide master cover background images or legacy stock photos must NOT be reused as cover hero graphics; record them in `baseline_cuts` and generate a bespoke, theme-consistent hero visual instead.
  - **Tailored Hero Visual Mandate**: Every deck must have a tailored hero visual custom-designed for its specific domain, industry, and architectural narrative.
    - **Anti-Repetition Rule (No Generic Sci-Fi Tropes)**: Generating identical, generic sci-fi tropes across decks—such as floating glowing cubes, neon cyan/magenta circuit lines, ungrounded cybernetic cores, or generic glowing padlocks in space—is strictly prohibited.
    - **Domain-Grounded Metaphors**: Ground the visual metaphor in the concrete subject matter of the deck:
      * *Financial Messaging & Banking (e.g. SWIFT)*: Institutional interbank transit corridors, cryptographic transaction validation nodes, high-assurance banking vaults, or structured sovereign financial communications fabric.
      * *Healthcare & Life Sciences*: Clinical data convergence, protected patient health corridors, secure biomedical record pipelines.
      * *Enterprise Identity & Access Governance*: Role materialization hierarchies, entitlement graph topologies, identity lifecycle governance fabrics, zero-trust boundary checkpoints.
      * *Cloud & Infrastructure*: Distributed edge mesh topology, atomic event streams, decoupled container pipelines.
    - **Aesthetic Quality & Lighting**: Direct the generator toward high-end editorial 3D architectural rendering, sophisticated physical-digital hybrid materials (matte dark carbon, brushed titanium, frosted glass, directional laser telemetry), and balanced ambient lighting matching the theme palette rather than blown-out neon light shows.
- **Cover Slide Proportions & Hero Alignment**: To ensure a pixel-perfect 1:1 vertical height alignment between the left-side text column and the right-side hero graphic, `title` and `subtitle` on cover slides (`layout: "Title Slide"`, `role: "cover"`) must remain concise (maximum 2 lines each). Long platform names or series names belong in `badge`, not concatenated into `title` or `subtitle`. The executive abstract belongs in `content.body`.
- **Layout definitions & grid templates**: [Layouts.csv](Layouts.csv) defines available slide architectures, CSS grid rules, and named slots.
- **Visual kits & design tokens**: [styles/](styles/) holds markdown design systems (`*-design.md`). Fully compatible with standard **`DESIGN.md`** files (Google Stitch, getdesign.md, awesome-design-md). Themes specify color palettes (contrast audited for WCAG AA), typography hierarchies, CSS variables, and structured prompt guidelines (`Atmosphere`, `Do's and Don'ts`, `Diagram Grammar`). Default premier theme: [styles/sailpoint-corporate-2026-design.md](styles/sailpoint-corporate-2026-design.md).
- **Theme Accents & Visual Weight Hierarchy**: When multiple elements on screen have the same weight (e.g. peer cards in a grid representing equal categories, peer steps, or equal metrics), do NOT mix and match accents or apply `highlight: true` to arbitrary peer items. Use the most vivid accents (e.g. hot fuchsia / `accent-alt` glowing border) strictly to highlight items that have genuine standout relevance (e.g. standout metrics, critical warnings, winning options, or high-priority items), while using the less vivid accents (e.g. electric aqua / `accent`, subtle theme borders) to decorate regular or peer items.
- **Template Policy (Extraction Only)**: Master PowerPoint templates (`templates/`) are sources of design styles, color tokens, and asset/vector extraction ONLY. They MUST NEVER be used as document templates to populate or create presentation contents. Presentations are compiled cleanly from scratch.

## Project Directory & Workspace

User presentations live in `projects/<project-name>/`:
- Context documentation, research, and source notes sit at `projects/<project-name>/` (e.g. `notes.md`, `brief.md`).
- Deck assets and outputs reside in `projects/<project-name>/deck/` (`spec.yaml`, `preview.html`, `deck.html`, `deck.pdf`, `deck.pptx`).

## Agent Skills & Commands

- **/spec-wizard** (`.agents/skills/spec-wizard/SKILL.md`): Discovers or initializes `projects/<project-name>/`, detects PowerPoint decks to offer modernization baselines, uses `grilling` to settle outcome details from `Schema.yaml`, aligns on deck sections first, tackles slides section-by-section, and automatically compiles both the card preview (`preview.html`) and the full interactive presentation (`deck.html`) for immediate review.
- **/deck-builder** (`.agents/skills/deck-builder/SKILL.md`): Compiles `spec.yaml` into `deck.html` (Reveal.js), opens it for user review, asks whether the user is happy with results or needs refinement, and upon approval offers to export to PDF (`deck.pdf`), PowerPoint (`deck.pptx`), both, or none.


## Engine CLI Scripts

All scripts run via the project Python virtual environment (`./venv/bin/python`):

```bash
# Import and validate a DESIGN.md theme from URL or file (e.g. getdesign.md or GitHub):
./venv/bin/python engine/import_theme.py <url-or-file> --name <theme-name> [--preview]

# Inspect existing PowerPoint deck (extract slide inventory, hierarchy, tables, notes):
./venv/bin/python engine/inspect_pptx.py projects/<project-name>/<file>.pptx

# Generate lightweight HTML card preview:
./venv/bin/python engine/preview.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/preview.html

# Compile standalone Reveal.js presentation:
./venv/bin/python engine/builder.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.html

# Export to 1:1 high-fidelity PDF:
./venv/bin/python engine/export_pdf.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pdf

# Export to 16:9 widescreen PowerPoint deck:
./venv/bin/python engine/export_pptx.py projects/<project-name>/deck/spec.yaml projects/<project-name>/deck/deck.pptx

# Run multi-theme regression & diagnostic test harness:
./venv/bin/python engine/test_themes.py [--full]
```

## Issue Triage & Ownership Protocol (Separation of Concerns)

### Fix Scope Gate (Process vs. Instance)

When the user reports presentation defects, visual flaws, or deck refinement requests, halt at a structured choice gate (`ask_question`) before editing any files:
- **(Recommended) Apply to Build Process & Current Deck**: Fix the root cause in the build process (engine, visual theme, authoring skill, or rules), then re-run the build to update the current deck.
- **Current Deck Only**: Patch `projects/<name>/deck/spec.yaml` directly for this project without changing the underlying build system.
- **Build Process Only**: Update the generator, engine, theme, or authoring rules so future decks avoid the issue; leave the current deck as-is for now.

Once the scope is agreed, reach the layer that owns the issue:

┌─────────────────────────────────────────────────────────────┐
│ Layer 0: Authoring Process (.agents/skills/, AGENTS.md)     │
│          Generation rules, prompts, component guidance      │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Content Instance (projects/<name>/deck/spec.yaml)  │
│          Payload volume, semantic layout choice, wording    │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Visual Kit / Tokens (styles/<theme>-design.md)     │
│          Colors, contrast, font-family, gradients, glows    │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Global Engine (engine/builder.py, CSS rules)       │
│          Grid/Flexbox layouts, clamp() scaling, DOM markup  │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Export Runtime (engine/export_pdf.py, pptx.py)     │
│          Headless Chrome viewport, print CSS, DeckTape      │
└─────────────────────────────────────────────────────────────┘
```

### The 3 Diagnostic Gates:
1. **The Theme-Swap Test (Style vs. Engine)**: If you switch `theme:` in `spec.yaml` to another theme (e.g. `linear` vs `sailpoint`), does the issue persist?
   - If **YES**: It is an **Engine layout bug** (`engine/builder.py`) or a **Content overflow** (`spec.yaml`).
   - If **NO**: It is a **Style Token defect** (`styles/<theme>-design.md`).
2. **The Geometry vs. Palette vs. Process Rule**:
   - Authoring habit, bad generation pattern, icon sizing, or missing component rule? → Fix in Layer 0 (`.agents/skills/`, `AGENTS.md`).
   - Palette, contrast, brand color, font-family, or glow? → Fix in Layer 2 (`styles/<theme>-design.md`). Never hardcode colors in `builder.py`.
   - Grid fraction, column wrap, vertical clipping, or font size scaling? → Fix globally in Layer 3 (`engine/builder.py`).
   - One-off wording or slide-specific density? → Fix in Layer 1 (`spec.yaml`).
3. **Verify with Multi-Theme Test Harness**:
   - After editing `engine/builder.py`, ALWAYS run `./venv/bin/python engine/test_themes.py` to guarantee zero cross-theme regression.

## Directory Conventions

- `projects/<project-name>/`: Project workspace holding context docs and `deck/` subfolder.
- `templates/`: Master presentation templates (e.g. `templates/SailPoint PowerPoint Template 2026.pptx`). Reference files for style extraction only; not used to create contents.
- `styles/`: Available visual design kits.
- `assets/themes/`: Static theme assets (e.g. extracted SailPoint SVGs and brand assets).
- `examples/`: Sample specs and reference presentations.
- `archive/notebooklm/`: Archived legacy Google NotebookLM prompts and setup guides.

