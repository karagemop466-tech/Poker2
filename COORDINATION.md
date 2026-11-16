
Publication record for PR #34 (2026-11-16):

- PR [#34](https://github.com/karagemop466-tech/Poker2/pull/34) merged to `main` at merge commit `c2fc205`, after
  two merge commits on the branch that reconciled `main`'s parallel work (PR #32, #35, #36). Both surfaces' CI was
  green on the PR before merging: `Verify site` (main's, including `scripts/audit.py` and `scripts/check_links.py`)
  and `Plan: generated pages match their data`.
- Deployment verified on `main`: `Deploy static site to GitHub Pages` run 43944718489 and `pages build and
  deployment` run 43944717817 completed successfully; Pages API reports `built`. The new surface is live at
  https://karagemop466-tech.github.io/Poker2/plan/ (root dashboard unchanged).
- Two rendering defects found by reading the deployed page and fixed on this branch: `earliest_plausible_finish`
  is stored as minutes since midnight and was being printed as `1045` instead of `5:25 PM`, and the re-entry
  excerpt duplicated the single-entry excerpt verbatim when both came from the same sentence.
- Follow-ups recorded for the next session: `S-11` (choose one surface to keep), `S-12` (merge the three scheduled
  monitor jobs), `S-02` (27 structure sheets unread), `FG-02` (get the single-entry answer in writing).
