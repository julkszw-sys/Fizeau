#!/usr/bin/env python3
"""
Robust wrapper for apply_rgb_gains_ui_patch.py.

The original patcher used exact anchors with newlines. Current Fizeau sources in this
fork can be compacted/one-line, so exact anchors fail. This wrapper loads the original
patcher, replaces its helper functions with whitespace-flexible versions, then executes it.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "tools" / "apply_rgb_gains_ui_patch.py"

code = PATCHER.read_text(encoding="utf-8")

start = code.index("def insert_after")
end = code.index("# ---- Core ABI / settings")

robust_helpers = """
def _anchor_pattern(anchor):
    # Treat any whitespace in the anchor as flexible whitespace in the source.
    parts = re.split(r'\\s+', anchor.strip())
    return r'\\s+'.join(re.escape(p) for p in parts)

def _find_anchor(s, anchor, path):
    # Fast exact path first.
    idx = s.find(anchor)
    if idx >= 0:
        return idx, idx + len(anchor)

    # Fallback: whitespace-flexible regex.
    pat = _anchor_pattern(anchor)
    m = re.search(pat, s)
    if not m:
        raise SystemExit(f"Anchor not found in {path}: {anchor!r}")
    return m.start(), m.end()

def insert_after(path, anchor, block, marker):
    s = read(path)
    if marker in s:
        return
    a, b = _find_anchor(s, anchor, path)
    s = s[:b] + block + s[b:]
    write(path, s)

def insert_before(path, anchor, block, marker):
    s = read(path)
    if marker in s:
        return
    a, b = _find_anchor(s, anchor, path)
    s = s[:a] + block + s[a:]
    write(path, s)

def replace_once(path, old, new, marker=None):
    s = read(path)
    if marker and marker in s:
        return
    idx = s.find(old)
    if idx >= 0:
        s = s[:idx] + new + s[idx + len(old):]
        write(path, s)
        return

    pat = _anchor_pattern(old)
    m = re.search(pat, s)
    if not m:
        raise SystemExit(f"Text not found in {path}: {old!r}")
    s = s[:m.start()] + new + s[m.end():]
    write(path, s)

"""

patched = code[:start] + robust_helpers + code[end:]
exec(compile(patched, str(PATCHER), "exec"))
