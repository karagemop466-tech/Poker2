"""Self-test: the source-recheck badge must actually mark rows whose document changed.

Builds a throwaway copy of the tree with a synthetic data/verified2026/checks.json and asserts that
each monitor verdict (CHANGED, unchanged, fetch error) reaches the Tournaments table and that the
Sources page reports the run. Without this, a monitor that silently stopped feeding the site would
look identical to a monitor reporting "all clean", which is the failure mode that matters here.

    python3 scripts/check_monitor_badge.py
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = ROOT
tmp = tempfile.mkdtemp(prefix="mon-")
for d in ("scripts", "data", "2026"):
    shutil.copytree(os.path.join(src, d), os.path.join(tmp, d))
sys.path.insert(0, os.path.join(tmp, "data", "sheets"))
sys.path.insert(0, os.path.join(tmp, "data", "verified2026"))
import part1
a, b, c = (part1.SHEETS[n]["url"] for n in (1, 2, 3))
res = [
    dict(key="VSTRUCT01", label="sheet 1", url=a, status=200, hash="1", change="CHANGED"),
    dict(key="VSTRUCT02", label="sheet 2", url=b, status=200, hash="2", change="unchanged"),
    dict(key="VSTRUCT03", label="sheet 3", url=c, status=500, hash=None, change="fetch error"),
]
json.dump(dict(last_run="2026-11-17T06:00:00Z", monitored=3, changed_this_run=1, never_checked=0,
               errors=1, note="fixture", runs=[dict(checked="2026-11-17T06:00:00Z", results=res)]),
          open(os.path.join(tmp, "data", "verified2026", "checks.json"), "w"), indent=1)
subprocess.run([sys.executable, "scripts/build2026.py"], cwd=tmp, check=True, stdout=subprocess.DEVNULL)
h = open(os.path.join(tmp, "2026", "tournaments.html")).read()
s = open(os.path.join(tmp, "2026", "sources.html")).read()
checks = [
    ("changed badge rendered", "source changed" in h),
    ("unchanged badge rendered", ">unchanged<" in h),
    ("fetch-error badge rendered", ">fetch error<" in h),
    ("changed rows tagged for filtering", 'data-changed="1"' in h),
    ("sources page reports the run", "Latest recorded run" in s and "1 changed" in s),
]
bad = [n for n, ok in checks if not ok]
for n, ok in checks:
    print(("ok   " if ok else "FAIL ") + n)
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if bad else 0)
