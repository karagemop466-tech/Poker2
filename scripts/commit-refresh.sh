#!/usr/bin/env bash
# Publish generated audit evidence only, never the hand-transcribed event/rate inputs.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
if [[ $(git branch --show-current) != main ]]; then
  echo 'Report publishing only runs from the main checkout; download the workflow artifact instead.'
  exit 0
fi
if [[ -f /tmp/pristine.failed ]]; then
  echo '::warning::The checked-out plan already had generator drift; report preserved as an artifact, not published over existing pages.'
  exit 0
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
git commit -m "refresh $(date -u +%F): publish official-source audit reports"
git push origin HEAD:main
