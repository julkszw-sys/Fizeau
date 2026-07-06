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

robust_helpers = r