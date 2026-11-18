# m32/tools — the plan generator

`plan.html` is **generated**, not hand-edited, so it cannot drift from the requirements.

```
plan.html  =  plan.preamble.md            (delivered M1–M3.1 summary + abstract; plan-authored)
            +  requirements.md             (THE SOURCE OF TRUTH for every M3.2 number and rule)
            +  plan.appendix.md            (plan-authored decisions, prerequisites, execution table)
```

rendered to the release-plan gist's HTML style (`tools/plan.css`).

## Use

```sh
python3 m32/tools/build_plan.py          # regenerate m32/plan.html
python3 m32/tools/build_plan.py --check  # exit 1 if the committed plan.html is stale (for CI)
```

Edit a **source** (`requirements.md`, `plan.preamble.md`, `plan.appendix.md`, or `tools/plan.css`),
then regenerate. Never edit `plan.html` directly — `--check` will fail the next build if you do.

## Why

A plan review (blis-design PR #34) found that the hand-kept `plan.html` had drifted from
`requirements.md` — a stale coverage ceiling, an un-chosen date rule, stale counts. Generating the
M3.2 body straight from `requirements.md` makes those impossible: the numbers and rules are rendered
from the one source every time. Only the delivered-milestone summary (which is history, not M3.2) and
the plan-level decisions/execution (which carry no source numbers) live in the two plan-authored files.

`build_plan.py` is pure standard library (no third-party markdown dependency, per X21) and supports
only the markdown subset the three sources use: ATX headings, paragraphs, `-`/`*` lists (one nesting
level, wrapped continuations), GFM tables, blockquotes, and inline `**bold**` / `*italic*` /
`` `code` `` / `[text](url)`.
