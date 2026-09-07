# Slide deck builder

This repo improves how slide decks get built in **NotebookLM** (Google Notebook): a YAML **spec** of structure and content, then one enabled `*-design.md` as the visual **kit** at generation time.

## Caps

NotebookLM paste fields have hard character **caps**. After every edit to a paste target, count characters (`wc -c`) and ship only when every changed field sits under its cap:

| Paste field | Source in this repo | Cap |
| --- | --- | --- |
| Chat system prompt | `System prompt.txt` (whole file) | **9950** |
| Slide tool instructions | `System prompt.txt` from `--- MODE 2` through end of file | **4950** |
| Spec | one `examples/*.yaml` file, pasted whole | **5000** |

When a prompt will not fit, move the meaning into `Schema.yaml`, `Layouts.csv`, or a `styles/*-design.md`. Those files are Notebook sources, not paste fields.

## Sources of truth

Reach the file that owns the change:

- **Spec** shape and field grammar: `Schema.yaml`
- **Layout** names and region counts: `Layouts.csv`
- Visual **kit** (tokens, motif, diagram grammar): `styles/*-design.md`
- NotebookLM chat and slide-tool wording: `System prompt.txt`
- NotebookLM setup and generate-in-one-pass workflow: `README.md`
- Worked specs: `examples/`
