#!/usr/bin/env python3
"""
Robust wrapper for apply_rgb_gains_ui_patch.py, with color.cpp repair.

Why this exists:
- Fizeau source files in the current fork are heavily compacted into long lines.
- The original patcher used exact multiline anchors.
- A whitespace-flexible anchor can accidentally insert gains_matrix() inside whitepoint().
- This wrapper applies the original patch, then moves gains_matrix() to file scope before whitepoint().
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
    parts = re.split(r'\\s+', anchor.strip())
    return r'\\s+'.join(re.escape(p) for p in parts)

def _find_anchor(s, anchor, path):
    idx = s.find(anchor)
    if idx >= 0:
        return idx, idx + len(anchor)

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

# ---- Repair color.cpp -----------------------------------------------------
color_path = ROOT / "common/src/color.cpp"
s = color_path.read_text(encoding="utf-8")

gains_block = """ColorMatrix gains_matrix(ColorGains gains) {
    gains.r = std::clamp(gains.r, MIN_GAIN, MAX_GAIN);
    gains.g = std::clamp(gains.g, MIN_GAIN, MAX_GAIN);
    gains.b = std::clamp(gains.b, MIN_GAIN, MAX_GAIN);

    return {
        gains.r, 0.0f,    0.0f,
        0.0f,    gains.g, 0.0f,
        0.0f,    0.0f,    gains.b,
    };
}

"""

# Remove every inserted copy of gains_matrix(), whether at file scope or inside whitepoint().
s = s.replace(gains_block, "")

# Insert exactly once before whitepoint(), at namespace/file scope.
m = re.search(r"std::tuple\s*<\s*float\s*,\s*float\s*,\s*float\s*>\s+whitepoint\s*\(\s*Temperature\s+temperature\s*\)\s*\{", s)
if not m:
    raise SystemExit("Could not find whitepoint() in common/src/color.cpp for gains_matrix insertion")

s = s[:m.start()] + gains_block + s[m.start():]
color_path.write_text(s, encoding="utf-8")

print("RGB gains + simple UI patch applied; color.cpp gains_matrix placement repaired.")
