# Archived root-page versions from session arena/7a4b09e2-poker2

These files are the root dashboard pages as merged to main via PRs #18–#23
(session arena/7a4b09e2-poker2, 2026-11-16). During the rebase of the
arena/8234a824-poker2 integration branch onto main, both sessions' root pages
conflicted on the same filenames. Resolution policy (see COORDINATION.md):

- The arena/8234a824-poker2 integration pages are the live root dashboard.
- This folder preserves arena/7a4b09e2-poker2's root pages verbatim so no work is lost.
- All of that session's non-conflicting outputs remain live and untouched:
  `venues/*.html` (its venue pages), `schedule.html`, `single-entry.html`,
  `sources.html`, `data/site/*.json`, `scripts/{build,dataset,audit,recheck_sources}.py`,
  and its CI verification workflow.
