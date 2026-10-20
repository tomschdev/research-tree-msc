# Research-tree methodology

Research is recursive question answering. A top-level question is decomposed into
sub-questions until each can be settled by one bounded piece of evidence; findings
are then synthesised back up the tree. The tree is the substance a paper is
condensed from.

```
answer(q):
  if one bounded piece of evidence settles q:      # base case
      gather it (literature or activity) → conclude q
  else:                                            # recursive case
      pose sub-questions; answer each
      synthesise their findings → conclude q
```

A child's finding may supersede its parent. The parent is left intact and
concluded `bypassed`; the child answers in its place.

## Repository layout

```
<root>/
  research-tree/                         # the research
    tree.mmd, tree.md                    # generated diagram — do not edit
    questions/
      1a-<slug>/                         # the root question (exactly one), path 1a
        question.md                      # posed
        conclusion.md                    # present = concluded
        notes/ experiments/ data/ refs.bib   # activities (free-form)
        questions/                       # children — same shape, recursively
          2a-<slug>/ …                   # path 1a2a
          2b-<slug>/ …                   # path 1a2b
  workflow/                              # everything that maintains the tree
    methodology.md                       # this file
    candidate-conclusion-definitions.yaml
    validate_research_tree.py            # rules 1–9
    sync_research_tree_paths.py          # follows `parent` changes; recomputes `path` and ids
    render_research_tree.py              # mermaid diagram
    manage_research_tree.py              # pose / conclude / reword / touch (owns ids, letters, timestamps)
    on_edit_hook.py                      # Claude Code PostToolUse hook
    check_hook.py                        # Claude Code SessionStart/UserPromptSubmit hook: validates,
                                         #   so edits made outside Claude (e.g. vim) surface early
```

- **The nesting is the tree.** A question's children live in its `questions/` folder.
- **The directory name is the id**: `<depth><letter>-<slug>`. Depth is the nesting
  level (root = 1); the letter orders siblings (a, b, …); the slug is kebab-case.
  Ids are unique across the tree.
- **`path` locates the question**: the `<depth><letter>` segments from the root down to
  the question, concatenated — `1a` for the root, `1a2b3a` for the first child of the
  root's second child. Its last segment is the id's prefix. `path` is derived; tooling
  owns it.
- Bypass moves nothing. Reparenting is editing `parent`: `sync_research_tree_paths.py`
  (run by the edit hook) moves the folder under the new parent with `git mv`, then
  recomputes `path` and the id prefix for the moved subtree, rewriting every reference
  to a renamed id (`parent`, `bypassed_by`, `## Synthesis` lines). Questions already in
  place keep their letter; the moved question takes the next free letter among its new
  siblings.
- Evidence shared across subtrees is referenced by repo-root-relative path.
- Large data, models and results stay out of git. Each repo records its policy
  (git-lfs, DVC, or external storage with pointers in `data/`) in its `CLAUDE.md`.

## Candidate conclusion definitions

`workflow/candidate-conclusion-definitions.yaml` defines every conclusion a question
may reach. Each entry has `always-available` (may conclude any question without being
listed), `requires` (what `conclusion.md` must contain), `message` and `style`. Add a
new conclusion type there; the tooling reads it generically.

A question with no `conclusion.md` is **open**. `open` is not a conclusion.

## `question.md` — posed, then frozen

```yaml
---
id: 3b-eratosthenes-shadow               # == directory name
path: 1a2a3b                             # set by tooling: parent's path + <depth><letter>
question: Do simultaneous noon shadows differ in angle between two latitudes?
parent: 2a-local-curvature-observation   # == enclosing question; ~ on the root
candidate-conclusions: [supported, refuted]
candidate-conclusion-definitions-path: ./workflow/candidate-conclusion-definitions.yaml
opened: 2026-10-01T09:00:00Z             # set by tooling
updated: 2026-10-01T09:30:00Z            # set by tooling
---

## Rationale
Why answering this matters to the parent, and what each candidate conclusion
means for this question.
```

While a question is open its wording may be refined with `reword` (the id and slug
stay); once concluded it is frozen (rule 5).

Fields appear in this order. `candidate-conclusions` lists ≥2 defined ids that are not
`always-available`.

## `conclusion.md` — the result

```yaml
---
id: 3b-eratosthenes-shadow
candidate-conclusion-definitions-path: ./workflow/candidate-conclusion-definitions.yaml
conclusion: supported                    # a candidate, or an always-available id
basis: activity                          # literature | activity | synthesis
concluded: 2026-10-12T12:00:00Z          # set by tooling
reason: ~                                # when the definition requires it
bypassed_by: ~                           # child id, when conclusion = bypassed
---

## Finding
Claim, evidence (paths, citations), confidence, limitations.

## Synthesis
- relied on: <child-id> — why
- discounted: <child-id> — why
```

`basis` records the kind of work that produced the conclusion: `literature` (existing
work settles it — related work), `activity` (an experiment, derivation, proof or
analysis you ran — contribution), or `synthesis` (combines the children's findings).
The `## Synthesis` section is where conflicting children are resolved: the parent says
which evidence it trusted and why.

## Rules

Enforced by `workflow/validate_research_tree.py`. Rule 5 is checked against git
history and skipped outside a git repo.

1. `research-tree/questions/` holds exactly one directory (the root). Every directory
   directly inside any `questions/` folder holds a `question.md`.
2. Directory names match `<depth><letter>-<slug>`; ids are unique across the tree.
   `path` is the parent's `path` plus `<depth><letter>`; the depth equals the nesting
   depth; letters are unique among siblings; the id's prefix equals the last segment.
3. `question.md` has all fields in order; `id` equals the directory name; `parent`
   equals the enclosing question (`~` on the root); the definitions path is
   `./workflow/candidate-conclusion-definitions.yaml`; `candidate-conclusions` holds ≥2
   defined, non-always-available ids; `opened` ≤ `updated`, both ISO-8601.
4. `conclusion.md` has `id` equal to the directory name and the same definitions path;
   `conclusion` is a candidate or always-available; every field its definition
   `requires` is present (`finding` = non-empty `## Finding`); `concluded` is ISO-8601
   and not before `opened`.
5. `question.md` is frozen once `conclusion.md` is committed: its content may not differ
   from that commit, except `id`, `parent` and `path` (reparenting). A wrong question is
   bypassed or abandoned, not edited.
6. A question cannot be concluded (other than `bypassed`) while any effective child is
   open. Effective children are the children, with each bypassed child replaced by its
   `bypassed_by`, recursively.
7. `bypassed_by` names a child of the question.
8. `basis` is one of `literature | activity | synthesis`, and is `synthesis` exactly
   when the question has effective children.
9. A `synthesis` conclusion's `## Synthesis` names every effective child as
   `relied on` or `discounted`.

## Branching

No rules. A branch is a divergent state of the research; how branches combine is
decided at merge time. The tree on any branch is that branch's state.

## Commands

```bash
python3 workflow/validate_research_tree.py        # exit 1 on any violation
python3 workflow/render_research_tree.py          # research-tree/tree.mmd + tree.md
python3 workflow/sync_research_tree_paths.py      # move questions whose parent changed; recompute path + ids
python3 workflow/render_research_tree.py --svg    # + tree.svg (mmdc, else npx mermaid-cli)
python3 workflow/manage_research_tree.py pose --parent <id|~> --slug <slug> --question "<text>" --candidates a,b
python3 workflow/manage_research_tree.py conclude <id> --conclusion <id> [--basis B] [--reason R] [--bypassed-by C]
python3 workflow/manage_research_tree.py reword <id> --question "<text>"   # open questions only
```
