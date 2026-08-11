"""Canonical workflow entry-point routing contract for `AGENTS.md`.

The SD pack wraps four Trellis workflows, and the wrapped skill runs the same
workflow without the wrapper's recording and gating steps. `AGENTS.md` is the
one routing document this repository owns, so it is where the canonical route
is stated — outside the Trellis-managed block, which a `trellis update`
overwrites.

The wrapped set is derived here rather than listed, on two signals that must
agree: a same-name pair of `sd-`/`trellis-` skill directories, and the `sd-`
skill's body naming its twin. Names alone would admit `sd-check`, which has a
`trellis-check` sibling it does not wrap; the body reference alone would admit
`sd-work-backlog`, which loads `trellis-before-dev` without wrapping it.

Both signals read vendored files, so an upstream refresh that adds, removes, or
renames a wrapped workflow fails this module until `AGENTS.md` is updated. That
alarm is the point: it is the only signal that the routing document has drifted
from the shipped wrapper set. Update the section, never the floor, unless the
removal is the real upstream change.
"""

from __future__ import annotations

import re
import unittest

from install_test_support import PACK_ROOT

SKILLS_DIR = PACK_ROOT / ".agents" / "skills"
AGENTS_DOC = PACK_ROOT / "AGENTS.md"

TRELLIS_END = "<!-- TRELLIS:END -->"
SECTION_START = "<!-- SD-ROUTING:START -->"
SECTION_END = "<!-- SD-ROUTING:END -->"

# One canonical route per workflow. The three names are captured separately so
# a line that routes `finish-work` at `/sd:continue` fails instead of passing
# on shape alone.
ROUTE_LINE = re.compile(
    r"^- `(?P<workflow>[a-z][a-z0-9-]*)` — canonical `/sd:(?P<canonical>[a-z0-9-]+)`; "
    r"bypassed by resolving `trellis-(?P<wrapped>[a-z0-9-]+)` directly$"
)

# The residual bypass: Trellis routes to the wrapped path from files this
# repository cannot edit. A section that lists routes without saying so reads
# as though the bypass had been closed.
BYPASS_SENTENCE = "emits `/trellis:` next actions of its own"

# Measured floor: `continue`, `finish-work`, `start`, `update-spec`. A derived
# set below this means a signal broke, not that the pack shrank — an empty set
# would otherwise satisfy set equality against an emptied section.
MIN_WRAPPED_WORKFLOWS = 4


def wrapped_workflows() -> set[str]:
    """Workflows where an `sd-` skill wraps its same-name `trellis-` twin."""
    found = set()
    for skill in sorted(SKILLS_DIR.glob("sd-*/SKILL.md")):
        workflow = skill.parent.name[len("sd-") :]
        twin = f"trellis-{workflow}"
        if not (SKILLS_DIR / twin / "SKILL.md").is_file():
            continue
        # Not a plain substring test: `trellis-update` occurs inside
        # `trellis-update-spec`, so a hypothetical `sd-update` would match on
        # its neighbour's name. The lookahead demands the reference end where
        # the twin's name ends.
        reference = re.compile(re.escape(twin) + r"(?![a-z0-9-])")
        if reference.search(skill.read_text(encoding="utf-8")):
            found.add(workflow)
    return found


def routing_section() -> str:
    """The marker-bounded routing section, or an assertion naming what broke."""
    document = AGENTS_DOC.read_text(encoding="utf-8")
    for marker in (TRELLIS_END, SECTION_START, SECTION_END):
        if document.count(marker) != 1:
            raise AssertionError(f"AGENTS.md must contain exactly one {marker}")
    start = document.index(SECTION_START)
    end = document.index(SECTION_END)
    if not document.index(TRELLIS_END) < start < end:
        raise AssertionError(
            "the routing section must open after the Trellis block closes and "
            "close after it opens"
        )
    return document[start + len(SECTION_START) : end]


def route_lines() -> list[re.Match[str]]:
    return [
        match
        for line in routing_section().split("\n")
        if (match := ROUTE_LINE.match(line.strip())) is not None
    ]


class RoutingSectionPlacementTest(unittest.TestCase):
    def test_section_sits_below_the_trellis_managed_block(self) -> None:
        routing_section()  # raises with the specific placement failure

    def test_the_trellis_managed_block_was_not_edited(self) -> None:
        document = AGENTS_DOC.read_text(encoding="utf-8")
        managed = document[: document.index(TRELLIS_END)]
        for token in (SECTION_START, SECTION_END, "/sd:"):
            self.assertNotIn(
                token,
                managed,
                "the SD routing content belongs outside the Trellis block, "
                "which a trellis update overwrites",
            )


class WrappedWorkflowDerivationTest(unittest.TestCase):
    def test_derivation_meets_its_floor(self) -> None:
        derived = wrapped_workflows()
        self.assertGreaterEqual(
            len(derived),
            MIN_WRAPPED_WORKFLOWS,
            f"derived {sorted(derived)}; a set below the floor means a signal "
            "broke — check whether the sd-* skills still name their twins",
        )

    def test_a_same_name_pair_alone_is_not_a_wrapper(self) -> None:
        # `sd-check` and `trellis-check` are siblings; `sd-check` wraps nothing.
        # If this stops holding upstream, `check` joins the derived set and the
        # section must name it.
        sd_check = SKILLS_DIR / "sd-check" / "SKILL.md"
        trellis_check = SKILLS_DIR / "trellis-check" / "SKILL.md"
        self.assertTrue(sd_check.is_file() and trellis_check.is_file())
        self.assertEqual(
            "trellis-check" in sd_check.read_text(encoding="utf-8"),
            "check" in wrapped_workflows(),
        )


class RoutingSectionContentTest(unittest.TestCase):
    def test_every_route_line_names_one_workflow_consistently(self) -> None:
        for match in route_lines():
            with self.subTest(line=match.group(0)):
                self.assertEqual(match.group("workflow"), match.group("canonical"))
                self.assertEqual(match.group("workflow"), match.group("wrapped"))

    def test_each_workflow_has_exactly_one_route_line(self) -> None:
        listed = [match.group("workflow") for match in route_lines()]
        duplicates = sorted({name for name in listed if listed.count(name) > 1})
        self.assertEqual(duplicates, [], "one canonical route per workflow")

    def test_the_section_names_exactly_the_derived_workflows(self) -> None:
        listed = {match.group("workflow") for match in route_lines()}
        derived = wrapped_workflows()
        self.assertEqual(
            listed,
            derived,
            f"AGENTS.md routes {sorted(listed)}; .agents/skills/ ships "
            f"{sorted(derived)}",
        )

    def test_the_residual_bypass_is_stated(self) -> None:
        self.assertIn(
            BYPASS_SENTENCE,
            " ".join(routing_section().split()),
            "the section must say Trellis still routes to the wrapped path "
            "from files this repository cannot edit",
        )


if __name__ == "__main__":
    unittest.main()
