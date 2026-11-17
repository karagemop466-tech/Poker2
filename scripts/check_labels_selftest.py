#!/usr/bin/env python3
"""Self-test for scripts/check_labels.py.

A gate that cannot fail is decoration. This injects each defect the gate was written for into a
throwaway copy of one page, runs the gate against it, and asserts it fails - then restores the file
and asserts it passes again. If someone weakens a rule in check_labels.py, this job goes red.

    python3 scripts/check_labels_selftest.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CASES = [
    # (page, how to plant the defect, what the defect is)
    ("tournaments.html",
     lambda s: s.replace("fee unconfirmed</span>", "62.50&times;", 1),
     "a guarantee ratio printed where the house fee is blank"),
    ("plan/flagged.html",
     lambda s: s.replace("actions/workflows/plan-refresh.yml",
                         "actions/workflows/daily-refresh.yml"),
     "a citation of a workflow file that does not exist"),
    ("rules.html",
     lambda s: s.replace(">structure sheet</a>", ">schedule</a>", 1),
     "a structure-sheet PDF labelled 'schedule'"),
]


def run_gate(root):
    return subprocess.run([sys.executable, os.path.join(root, "scripts", "check_labels.py"), "--quiet"],
                          capture_output=True, text=True, cwd=root)


def main():
    tmp = tempfile.mkdtemp(prefix="labelcheck-")
    for name in ("scripts", ".github"):
        src = os.path.join(ROOT, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(tmp, name))
    # the pages the gate reads, at their real relative paths
    for rel in ("tournaments.html", "rules.html", os.path.join("plan", "flagged.html")):
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True) if os.path.dirname(rel) else None
        shutil.copy(os.path.join(ROOT, rel), dst)

    ok = True
    base = run_gate(tmp)
    if base.returncode != 0:
        print("FAIL: the gate rejects the unmodified pages")
        print(base.stdout[:800])
        return 1
    print("ok   clean tree passes")

    for rel, mutate, what in CASES:
        path = os.path.join(tmp, rel)
        original = open(path, encoding="utf8").read()
        mutated = mutate(original)
        if mutated == original:
            print("FAIL: self-test could not plant the defect on %s (%s)" % (rel, what))
            ok = False
            continue
        open(path, "w", encoding="utf8").write(mutated)
        r = run_gate(tmp)
        if r.returncode == 0:
            print("FAIL: gate did not catch %s" % what)
            ok = False
        else:
            print("ok   caught %s" % what)
        open(path, "w", encoding="utf8").write(original)

    r = run_gate(tmp)
    if r.returncode != 0:
        print("FAIL: gate does not pass after restoring the pages")
        ok = False
    shutil.rmtree(tmp, ignore_errors=True)
    print("label-gate selftest %s" % ("ok" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
