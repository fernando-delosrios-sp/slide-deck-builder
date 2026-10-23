# Legacy Google NotebookLM Configuration

This directory contains the legacy configuration artifacts used when this repository was focused on Google NotebookLM as the presentation generation target:

- `System prompt.txt`: The previous system prompt subject to NotebookLM chat character caps (9950 characters) and slide tool caps (4950 characters).
- `images/`: Step-by-step setup screenshots for importing schemas, layouts, and styles into NotebookLM sources.

The repository is now driven directly by the agent via `spec-wizard` and `deck-builder` skills, outputting standalone Reveal.js HTML presentations and native PowerPoint `.pptx` decks.
