# Slide Deck Builder

This project utilizes NotebookLM as an automated slide deck builder. By providing structured schemas and design assets, we can generate presentations with accurate and foreseeable results.

## Overview

NotebookLM serves two primary purposes in this workflow:
1. **Creating the Deck Spec**: Generating a structured YAML specification for the presentation based on source material.
2. **Creating the Slide Deck**: Compiling the generated specification into a fully formatted slide deck.

The declarative nature of the specification ensures that the final presentation adheres strictly to predefined design rules, resulting in a consistent and high-quality output.

## Core Components

The deck generation process relies on three foundational files:

### 1. Schema (`Schema.yaml`)
This is the blueprint for the presentation. It defines the required structure for the deck, including:
- **Global Properties**: `title`, `goal`, target `style`, and `options` (language, audience, tone, length).
- **Slides Array**: A list of individual slides, each requiring a specific `layout`, semantic `role`, `title`, and `content` (body text, bullets, media regions), along with optional presenter `notes`.

### 2. Layouts (`Layouts.csv`)
This file defines the available per-slide structural layouts. When NotebookLM generates a slide in the spec, it must choose a layout defined here. 
Layouts dictate the grid structure, placeholder styling, background behavior, and spacing.
*Examples include:* Title Slide, Title and Content, Two Content, Comparison, and Picture with Caption.

### 3. Styles (`Styles.csv`)
This file contains the available visual themes for the presentation. The spec selects one global style for the entire deck.
Styles define primary/accent/background colors, typography (Heading and Body fonts), illustration motifs, and the overall design rationale.
*Examples include:* SailPoint Corporate Dark 2026, Cloud Topology, Core Minimalist, and Kinetic Keynote.

## Workflow

1. **Input**: Provide NotebookLM with your source documents (e.g., research notes, articles, or outlines) along with the Schema, Layouts, and Styles definitions.
2. **Spec Generation**: Ask NotebookLM to generate a slide deck specification. It will produce a YAML file adhering to `Schema.yaml`, referencing a single style from `Styles.csv` and appropriate layouts from `Layouts.csv` for each slide.
3. **Compilation**: The resulting YAML spec is parsed and compiled into the final presentation, guaranteeing a predictable and professionally designed slide deck.
