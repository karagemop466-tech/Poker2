#!/usr/bin/env bash
# Publish generated audit evidence only, never the hand-transcribed event/rate inputs.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
# Publish only for the main-branch run. Schedule/dispatch checkouts are a detached HEAD, where
# `git branch --show-current` prints nothing - so compare the documented ref env var instead, and
# fall back to allowing the publish when HEAD does resolve to a local main branch (older checkouts).
if [[ "${GITHUB_REF_NAME:-$(git branch --show-current)}" != main ]]; then
  echo 'Report publishing only runs from the main checkout; download the workflow artifact instead.'
  exit 0
fi
if [[ -f /tmp/pristine.failed ]]; then
  echo '::warning::The checked-out plan already had generator drift; report preserved as an artifact, not published over existing pages.'
  exit 0
fi

# The job checks out main at job start; main can move before this script runs (observed
# 2026-11-18: a review branch cut at 15:53 went stale six and a half hours later when the
# source monitor committed at 22:36). Re-apply this run's outputs onto CURRENT origin/main
# instead of the job-start base: the data artefacts (snapshots, change report, schedule diff)
# are this run's fresh evidence and win; the rendered plan/ pages are regenerated from the
# merged tree, never copied from the stale one. If this cannot be done cleanly, fall through
# to the plain commit below - the final push is rejected non-fast-forward rather than revert
# newer work, and the report stays downloadable in Actions.
git fetch -q origin main || true
if git rev-parse --verify -q origin/main >/dev/null && ! git merge-base --is-ancestor origin/main HEAD; then
  echo "::notice::main moved during the run; re-applying this run's outputs onto origin/main before committing"
  rm -rf /tmp/refresh-out && mkdir -p /tmp/refresh-out
  [ -d site-data/snapshots ] && cp -a site-data/snapshots /tmp/refresh-out/snapshots || true
  [ -f site-data/change-report.json ] && cp -a site-data/change-report.json /tmp/refresh-out/change-report.json || true
  [ -f site-data/schedule-diff.json ] && cp -a site-data/schedule-diff.json /tmp/refresh-out/schedule-diff.json || true
  git reset -q --hard origin/main
  git clean -fdq site-data plan
  mkdir -p site-data
  [ -d /tmp/refresh-out/snapshots ] && cp -a /tmp/refresh-out/snapshots site-data/snapshots || true
  [ -f /tmp/refresh-out/change-report.json ] && cp -a /tmp/refresh-out/change-report.json site-data/change-report.json || true
  [ -f /tmp/refresh-out/schedule-diff.json ] && cp -a /tmp/refresh-out/schedule-diff.json site-data/schedule-diff.json || true
  python3 scripts/build-site.py || echo "warning: re-render failed; committing the run's data files only"
fi

# Avoid rebasing generated reports on top of possibly different hand-transcribed inputs.
# If main moved, the push fails safely and the report remains downloadable in Actions.
git config user.name 'source-refresh[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A -- site-data/snapshots site-data/change-report.json site-data/schedule-diff.json plan
if git diff --cached --quiet; then
  echo 'No report changes to publish.'
  exit 0
fi
if [[ -f /tmp/verify.failed ]]; then
  echo '::warning::Generator check needs review. Published reports do not update the transcribed event or hotel data.'
fi
git commit -q -m "refresh $(date -u +%F): publish official-source audit reports"
if ! git push -q origin HEAD:main; then
  echo '::notice::main moved again; rebasing the report commit onto it and retrying once'
  git pull -q --rebase --autostash origin main && git push -q origin HEAD:main
fi
