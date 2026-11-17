#!/usr/bin/env bash
# Decide what to do with the refresh run: nothing, a direct snapshot commit, or a review PR.
#
#   all states ok/new            -> commit snapshots + report to the current branch (no review needed)
#   any changed/drifted/error    -> open a pull request so a human re-reads the sheet and re-runs
#                                   scripts/build-events.py before the site repeats an old number
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
git config user.name  "source-refresh[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

FILES=(site-data/snapshots site-data/change-report.json site-data/schedule-diff.json)
ADD=()
for f in "${FILES[@]}"; do [[ -e "$f" ]] && ADD+=("$f"); done
if [ "${#ADD[@]}" -eq 0 ]; then
  echo "nothing to commit: no snapshots were written"; exit 0
fi

if git diff --quiet -- "${ADD[@]}" && [ -z "$(git status --porcelain -- "${ADD[@]}")" ]; then
  echo "no snapshot changes since the last run"; exit 0
fi

NEEDS=$(python3 - <<'PY'
import json, os
p = "site-data/change-report.json"
n = 0
if os.path.exists(p):
    r = json.load(open(p))
    n = r.get("needs_attention", 0)
    if any(s.get("state") in ("drifted",) for s in r.get("sources", [])):
        n += 1
if os.path.exists("site-data/schedule-diff.json"):
    d = json.load(open("site-data/schedule-diff.json"))
    if d.get("state") not in (None, "ok"):
        n += 1
print(n)
PY
)

if [ -f /tmp/verify.failed ]; then
  NEEDS=$((NEEDS + 1))
fi

STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git add -- "${ADD[@]}"

if [ "$NEEDS" -gt 0 ]; then
  BRANCH="refresh/${STAMP//[:]/}"
  git checkout -q -b "$BRANCH"
  git commit -q -m "refresh ${STAMP}: ${NEEDS} source(s) need review"
  git push -q -u origin "$BRANCH"
  {
    echo "## Source refresh needs a decision"
    echo
    echo "Automated re-read of the official pages found something the planner depends on."
    echo "Nothing in \`site-data/events.json\` or \`site-data/hotels.json\` was edited: those files are"
    echo "transcribed from the cited documents by \`scripts/build-events.py\`, so a human has to confirm the new text."
    echo
    echo '```'
    python3 - <<'PY'
import json, os
r = json.load(open("site-data/change-report.json")) if os.path.exists("site-data/change-report.json") else {"sources": []}
for s in r.get("sources", []):
    if s.get("state") in ("ok", "new"):
        continue
    print(f"- {s['state']:9} {s['id']}: {s.get('url','')}")
    for d in s.get("value_diffs") or []:
        print(f"          {d[0]}: {d[1]} -> {d[2]}")
    if s.get("error"):
        print(f"          error: {s['error']}")
if os.path.exists("site-data/schedule-diff.json"):
    d = json.load(open("site-data/schedule-diff.json"))
    if d.get("state") != "ok":
        c = d.get("counts", {})
        print(f"- schedule  {d['state']}: +{c.get('added',0)} -{c.get('removed',0)} ~{c.get('modified',0)} renamed {c.get('renamed', d.get('renamed', 0))}")
PY
    echo '```'
    if [ -f /tmp/verify.failed ]; then
      echo
      echo "### Generator check output"
      echo '```'
      cat /tmp/verify.log
      echo '```'
    fi
    echo
    echo "Next: read the changed official document, update the transcription in"
    echo "\`scripts/build-events.py\`, run \`python3 scripts/build-events.py && python3 scripts/build-schedule.py && python3 scripts/build-site.py\`,"
    echo "then merge. The site keeps showing the last verified values with their old check date until then."
  } > /tmp/pr-body.md
  gh pr create --title "Source refresh ${STAMP}: review ${NEEDS} change(s)" --body-file /tmp/pr-body.md --base main || {
    echo "gh pr create failed; branch is pushed and ready for a manual PR: $BRANCH"; exit 1; }
  echo "opened PR for ${NEEDS} source(s) needing review"
else
  git commit -q -m "refresh ${STAMP}: official sources unchanged (snapshots only)"
  BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
  # main can move while this job runs; rebase onto it and retry rather than failing the run.
  for i in 1 2 3; do
    git pull --rebase --autostash origin "$BRANCH_NAME" && git push -q origin HEAD:"$BRANCH_NAME" && exit 0
    echo "push attempt $i failed; retrying after rebase"
    sleep 5
  done
  echo "could not push the snapshot commit after 3 attempts" >&2
  exit 1
fi
