#!/usr/bin/env python3
"""Build the offline study site from the markdown sources.

Usage:
    python3 build.py          # build index.html
    python3 build.py --test   # also run every solution against its tests

Source format
-------------
LeetCode (sources/leetcode/*.md):
    ### 88. Merge Sorted Array
    difficulty: Easy
    <markdown body: **Problem.** ... **Idea.** ... ```python ...``` ...>
    ```test            (optional, hidden from the site, run with --test)
    assert ...
    ```

HackerRank (sources/hackerrank/*.md):
    ## Subdomain
    ### Problem name
    <markdown body>
    ```stdin / ```stdout   (optional sample, hidden, run with --test)

```python blocks are complete programs (executed in tests); ```py blocks are snippets.
The solution part of a problem starts at the first line beginning with **Idea
(everything before it is the problem description, shown in practice mode).
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).parent))
from lists import TOP_150, TOP_100_LIKED, HACKERRANK_PYTHON, LC_SLUG_OVERRIDES, HR_SLUGS  # noqa: E402

ROOT = Path(__file__).parent
SRC = ROOT / "sources"
OUT = ROOT

FENCE_RE = re.compile(r"^```(\w[\w-]*)?\s*\n(.*?)^```\s*$", re.S | re.M)


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "x"


def split_hidden(body):
    """Remove ```test / ```stdin / ```stdout blocks; return (visible_body, hidden dict)."""
    hidden = {"test": [], "stdin": None, "stdout": None}

    def repl(m):
        lang = (m.group(1) or "").lower()
        if lang == "test":
            hidden["test"].append(m.group(2))
            return ""
        if lang in ("stdin", "stdout"):
            hidden[lang] = m.group(2)
            return ""
        return m.group(0)

    visible = FENCE_RE.sub(repl, body)
    return visible.strip() + "\n", hidden


def code_blocks(body):
    return [(m.group(1) or "", m.group(2)) for m in FENCE_RE.finditer(body)]


MD = markdown.Markdown(
    extensions=["fenced_code", "codehilite", "tables", "sane_lists"],
    extension_configs={"codehilite": {"css_class": "hl", "guess_lang": False}},
)


LIST_LINE = re.compile(r"^\s*(\d+\.|[-*]) ")


def fix_lists(body):
    """Markdown needs a blank line before a list that follows a paragraph line; add it (outside code fences)."""
    out, in_fence, prev = [], False, ""
    for line in body.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and LIST_LINE.match(line) and prev.strip() and not LIST_LINE.match(prev) \
                and not prev.startswith("    "):
            out.append("")
        out.append(line)
        prev = line if not in_fence or line.startswith("```") else prev
    return "\n".join(out)


def render(body):
    body = fix_lists(body)
    MD.reset()
    idx = body.find("\n**Idea")
    if body.startswith("**Idea"):
        idx = 0
    if idx == -1:
        return MD.convert(body), ""
    problem, solution = body[:idx], body[idx:]
    MD.reset()
    p_html = MD.convert(problem)
    MD.reset()
    s_html = MD.convert(solution)
    return p_html, s_html


# ---------------------------------------------------------------- parsing

def parse_leetcode():
    problems = {}
    for f in sorted((SRC / "leetcode").glob("*.md")):
        text = f.read_text()
        parts = re.split(r"^### (\d+)\. (.+)$", text, flags=re.M)
        for i in range(1, len(parts), 3):
            num, title, body = int(parts[i]), parts[i + 1].strip(), parts[i + 2]
            m = re.match(r"\s*difficulty:\s*(\w+)\s*\n", body)
            if not m:
                raise SystemExit(f"{f.name}: problem {num} has no difficulty line")
            body = body[m.end():]
            if num in problems:
                raise SystemExit(f"duplicate LeetCode problem {num} ({f.name})")
            visible, hidden = split_hidden(body)
            problems[num] = {
                "num": num, "title": title, "difficulty": m.group(1),
                "body": visible, "hidden": hidden, "file": f.name,
            }
    return problems


def parse_hackerrank():
    sections = {}
    for f in sorted((SRC / "hackerrank").glob("*.md")):
        text = f.read_text()
        for sec in re.split(r"^## ", text, flags=re.M)[1:]:
            name, rest = sec.split("\n", 1)
            name = name.strip()
            parts = re.split(r"^### (.+)$", rest, flags=re.M)
            items = sections.setdefault(name, {})
            for i in range(1, len(parts), 2):
                title, body = parts[i].strip(), parts[i + 1]
                visible, hidden = split_hidden(body)
                items[title] = {"title": title, "body": visible, "hidden": hidden, "file": f.name}
    return sections


# ---------------------------------------------------------------- tests

PRELUDE = '''
import sys, math, heapq, bisect, random, collections, itertools, functools, string, re
from typing import *
from collections import *
from functools import *
from itertools import *
from heapq import *
from bisect import *
from math import inf
sys.setrecursionlimit(100000)

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val; self.next = next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val; self.left = left; self.right = right

class Node:
    def __init__(self, val=0, *args, **kw):
        self.val = val
        self.next = kw.get("next"); self.random = kw.get("random")
        self.left = kw.get("left"); self.right = kw.get("right")
        self.neighbors = kw.get("neighbors") if kw.get("neighbors") is not None else []
        if args:
            # Node(val, left, right, next) for tree-with-next, Node(val, neighbors) for graphs
            if isinstance(args[0], list):
                self.neighbors = args[0]
            else:
                self.left = args[0] if len(args) > 0 else None
                self.right = args[1] if len(args) > 1 else None
                self.next = args[2] if len(args) > 2 else None

def build_list(vals):
    dummy = ListNode(); cur = dummy
    for v in vals:
        cur.next = ListNode(v); cur = cur.next
    return dummy.next

def to_list(head):
    out = []
    while head:
        out.append(head.val); head = head.next
    return out

def build_tree(vals):
    if not vals or vals[0] is None:
        return None
    nodes = [None if v is None else TreeNode(v) for v in vals]
    kids = nodes[::-1]; root = kids.pop()
    q = [root]; i = 0
    it = iter(nodes[1:])
    from collections import deque
    dq = deque([root])
    vals_it = iter(vals[1:])
    while dq:
        node = dq.popleft()
        try:
            lv = next(vals_it)
        except StopIteration:
            break
        if lv is not None:
            node.left = TreeNode(lv); dq.append(node.left)
        try:
            rv = next(vals_it)
        except StopIteration:
            break
        if rv is not None:
            node.right = TreeNode(rv); dq.append(node.right)
    return root

def tree_to_list(root):
    from collections import deque
    out = []; dq = deque([root])
    while dq:
        n = dq.popleft()
        if n is None:
            out.append(None); continue
        out.append(n.val); dq.append(n.left); dq.append(n.right)
    while out and out[-1] is None:
        out.pop()
    return out

def find(root, val):
    if not root: return None
    if root.val == val: return root
    return find(root.left, val) or find(root.right, val)
'''


def run_leetcode_tests(problems):
    failures = []
    ran = 0
    for num, p in sorted(problems.items()):
        blocks = [c for lang, c in code_blocks(p["body"]) if lang == "python"]
        if not blocks:
            failures.append(f"LC {num}: no ```python block")
            continue
        for bi, code in enumerate(blocks):
            g = {"__name__": "lc_test"}
            try:
                exec(PRELUDE, g)
                exec(compile(code, f"LC{num}-block{bi}", "exec"), g)
            except Exception as e:
                failures.append(f"LC {num} block {bi}: definition error {type(e).__name__}: {e}")
                continue
            for t in p["hidden"]["test"]:
                try:
                    exec(compile(t, f"LC{num}-test", "exec"), g)
                    ran += 1
                except AssertionError as e:
                    failures.append(f"LC {num} block {bi}: assertion failed {e}")
                except Exception as e:
                    failures.append(f"LC {num} block {bi}: test error {type(e).__name__}: {e}")
        if not p["hidden"]["test"]:
            failures.append(f"LC {num}: (warning) no tests")
    return ran, failures


def norm(out):
    return "\n".join(line.rstrip() for line in out.strip().splitlines())


def run_hackerrank_tests(sections):
    failures = []
    ran = 0
    for sec, items in sections.items():
        for title, p in items.items():
            blocks = [c for lang, c in code_blocks(p["body"]) if lang == "python"]
            if not blocks:
                failures.append(f"HR {sec} / {title}: no ```python block")
                continue
            for code in blocks:
                try:
                    compile(code, title, "exec")
                except SyntaxError as e:
                    failures.append(f"HR {title}: syntax error {e}")
            stdin, stdout = p["hidden"]["stdin"], p["hidden"]["stdout"]
            if stdin is None:
                continue
            with tempfile.TemporaryDirectory() as d:
                prog = Path(d) / "prog.py"
                prog.write_text(blocks[0])
                outp = Path(d) / "out.txt"
                env = dict(os.environ, OUTPUT_PATH=str(outp))
                r = subprocess.run([sys.executable, str(prog)], input=stdin, capture_output=True,
                                   text=True, timeout=20, cwd=d, env=env)
                got = r.stdout
                if outp.exists():
                    got += outp.read_text()
            ran += 1
            if r.returncode != 0:
                failures.append(f"HR {title}: crashed\n{r.stderr[-600:]}")
            elif stdout is not None and norm(got) != norm(stdout):
                failures.append(f"HR {title}: output mismatch\n--- expected\n{stdout}\n--- got\n{got}")
    return ran, failures


# ---------------------------------------------------------------- site data

def build_data(lc, hr):
    in_lists = {}
    for key, lst in (("top150", TOP_150), ("top100", TOP_100_LIKED)):
        for _, ids in lst:
            for i in ids:
                in_lists.setdefault(i, []).append(key)

    missing = [i for i in in_lists if i not in lc]
    extra = [i for i in lc if i not in in_lists]

    lc_out = {}
    for num, p in lc.items():
        prob, sol = render(p["body"])
        lc_out[num] = {
            "num": num, "title": p["title"], "difficulty": p["difficulty"],
            "slug": LC_SLUG_OVERRIDES.get(num, slugify(p["title"])), "lists": in_lists.get(num, []),
            "problem": prob, "solution": sol,
        }

    hr_sections = []
    hr_missing = []
    hr_slug_iter = iter(HR_SLUGS)
    for sec, names in HACKERRANK_PYTHON:
        items = hr.get(sec, {})
        probs = []
        for n in names:
            hr_slug = next(hr_slug_iter)
            p = items.get(n)
            if p is None:
                hr_missing.append(f"{sec} / {n}")
                continue
            prob, sol = render(p["body"])
            probs.append({"title": n, "slug": slugify(n), "url": f"https://www.hackerrank.com/challenges/{hr_slug}/problem", "problem": prob, "solution": sol})
        hr_sections.append({"name": sec, "slug": slugify(sec), "problems": probs})
    hr_extra = [f"{s} / {t}" for s, items in hr.items() for t in items
                if not any(s == sec and t in names for sec, names in HACKERRANK_PYTHON)]

    data = {
        "leetcode": {
            "lists": {
                "top150": {"name": "Top Interview 150", "sections": [{"name": n, "slug": slugify(n), "ids": ids} for n, ids in TOP_150]},
                "top100": {"name": "Top 100 Liked", "sections": [{"name": n, "slug": slugify(n), "ids": ids} for n, ids in TOP_100_LIKED]},
            },
            "problems": lc_out,
        },
        "hackerrank": {"name": "Python", "sections": hr_sections},
    }
    return data, missing, extra, hr_missing, hr_extra


def main():
    lc = parse_leetcode()
    hr = parse_hackerrank()
    data, missing, extra, hr_missing, hr_extra = build_data(lc, hr)

    print(f"LeetCode problems written: {len(lc)} (needed {len(lc) + len(missing) - len(extra)})")
    print(f"HackerRank problems written: {sum(len(s['problems']) for s in data['hackerrank']['sections'])} / 115")
    if missing:
        print("LeetCode missing:", sorted(missing))
    if extra:
        print("LeetCode extra (not in any list):", sorted(extra))
    if hr_missing:
        print("HackerRank missing:", hr_missing)
    if hr_extra:
        print("HackerRank names not matched to the list:", hr_extra)

    if "--test" in sys.argv:
        ran, fails = run_leetcode_tests(lc)
        print(f"\nLeetCode test blocks run: {ran}")
        ran2, fails2 = run_hackerrank_tests(hr)
        print(f"HackerRank samples run: {ran2}")
        real = [f for f in fails + fails2 if "(warning)" not in f]
        warns = [f for f in fails + fails2 if "(warning)" in f]
        for f in real:
            print("FAIL:", f)
        if warns:
            print(f"{len(warns)} warnings:", ", ".join(w.split(':')[0] for w in warns))
        print("ALL TESTS PASSED" if not real else f"{len(real)} FAILURES")

    template = (ROOT / "template.html").read_text()
    from pygments.formatters import HtmlFormatter
    css_light = HtmlFormatter(style="friendly").get_style_defs(".hl")
    css_dark = HtmlFormatter(style="monokai").get_style_defs(".dark .hl")
    page = (template
            .replace("/*PYGMENTS_LIGHT*/", css_light)
            .replace("/*PYGMENTS_DARK*/", css_dark)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page)
    print(f"\nWrote {OUT / 'index.html'} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
