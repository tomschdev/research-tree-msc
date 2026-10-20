# Research tree

This repo follows `workflow/methodology.md`. The research lives in `research-tree/`;
everything that maintains it lives in `workflow/`.

- A question is `question.md`; it is concluded when `conclusion.md` sits beside it.
  Children nest in its `questions/` folder.
- Create questions and conclusions with `python3 workflow/manage_research_tree.py`
  (or the `/research-tree` skill) — never by hand. It owns ids, letters and timestamps.
- Run `python3 workflow/validate_research_tree.py` after editing any question or
  conclusion, and `python3 workflow/render_research_tree.py` to regenerate the diagram.
- The directory name is the id (`2b-<slug>`); `path` (e.g. `1a2b`) locates it in the tree.
  To reparent, edit `parent` — the edit hook runs `workflow/sync_research_tree_paths.py`,
  which moves the folder and recomputes `path` and id prefixes down the subtree.
- Do not hand-edit `path`, `opened`, `updated`, `concluded`, or `research-tree/tree.*`.
- Large artefacts: external storage with pointers. Datasets, recordings, transcripts and
  other large or sensitive files (e.g. POPIA/ethics-governed case-study data) never enter
  git; they live in external storage, and the question's `data/` holds a pointer file
  (location, description, checksum) in their place.
