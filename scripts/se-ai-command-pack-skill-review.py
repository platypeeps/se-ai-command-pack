#!/usr/bin/env python3
"""Run the canonical bundled skill-review inventory helper from this checkout."""

from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "templates"
    / "skills"
    / "se-review-skills"
    / "scripts"
    / "skill_review.py"
)

runpy.run_path(str(SCRIPT), run_name="__main__")
