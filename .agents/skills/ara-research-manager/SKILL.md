---
name: ara-research-manager
description: Record research questions, experiments, decisions, failed directions and evidence in the two-level ARA artifact; retrieve focused idea notes and summarize a research Issue at closeout.
---

# Research manager

Read `docs/PROTOCOL.md` for fields and `docs/NOTES.md` for memo boundaries. Paths are relative to the project root.

At task start, list Issues and relevant ideas with `python scripts/ara.py issues` and `ideas --issue N`. Read only needed ideas with `read ID`; revisit their dependencies only when the task needs them. Search failures before proposing a repeated experiment.

Every research Issue has one actually linked GitHub branch, one append-only ExecPlan and one Markdown memo. Record full raw user prompts in that Issue's ExecPlan. The goal can change; dated progress, next steps, decisions, evidence and recovery information are append-only.

Record mature questions, decisions, experiments, dead ends and pivots as ideas. Write only `depends_on` plus one `primary_dependency`, never successors. A new independent direction uses `I000-N00`; failures can inform successors without becoming successful evidence.

Keep shared experiment conditions frozen in the memo's common section. Each idea records its overrides, question, method, results, evidence and limits. Use exact numbers from the available source; record inaccessible raw data explicitly rather than inventing hashes, commands or successful reproduction.

Stage unresolved observations with origin and promotion condition. At every substantive turn/session boundary append events connecting observations, ideas, claims and evidence. A crystallization event names its trigger and rationale; revisions preserve before/after. Never equate user approval or a topic ending with empirical support. Preserve unresolved conflicts.

Before ending Issue work, independently summarize Issue prerequisites; do not mechanically project idea edges. Both `best_ideas` and `promising_ideas` must contain at least one real idea of this Issue, with reasons. They may overlap and contain multiple entries. On failure, preserve the failed outcome and select relatively useful results and justified follow-up potential.

Run `python scripts/ara.py validate`, `python -m unittest discover -s tests`, then `python scripts/ara.py render`. Verify GitHub linkage with `validate --github` when delivering a connected repository. Keep source evidence and provenance; do not silently rewrite old notes or sessions.
