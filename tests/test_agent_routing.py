"""Canonical workflow entry-point routing contract for `AGENTS.md`.

The SD pack wraps four Trellis workflows, and the wrapped skill runs the same
workflow without the wrapper's recording and gating steps. `AGENTS.md` is the
one routing document this repository owns, so it is where the canonical route
is stated — outside the Trellis-managed block, which a `trellis update`
overwrites.

The wrapped set used to be derived here, from a same-name pair of
`sd-`/`trellis-` skill directories plus the `sd-` skill's body naming its twin.
Both signals read vendored payload, and the thin conversion took that payload
out of this tree: the `sd-` skills now live wherever the machine keeps the
install, and CI has no install at all. `ROUTED_WORKFLOWS` below is that
derivation's last answer, frozen as a repo-owned list. It still fails when
someone edits the routing section, and it no longer claims to notice an
upstream change this repository can no longer see -- when the pack adds or
renames a wrapper, update the section and this list together.
"""

from __future__ import annotations

import re
import unittest

from install_test_support import PACK_ROOT

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

# The workflows the pack wraps, as the removed derivation last reported them.
# `check` is deliberately absent: `sd-check` has a `trellis-check` sibling it
# does not wrap, which is why the old derivation demanded a body reference to
# the twin and not a same-name pair alone.
ROUTED_WORKFLOWS = frozenset({"continue", "finish-work", "start", "update-spec"})


def routing_section() -> str:
    """The marker-bounded routing section of the checked-in `AGENTS.md`."""
    return section_of(AGENTS_DOC.read_text(encoding="utf-8"))


def section_of(document: str) -> str:
    """The marker-bounded routing section, or an assertion naming what broke.

    Split from the reader so the failure paths below can be exercised against
    synthetic documents. Asserting them against `AGENTS.md` itself would need a
    test that edits a tracked file, and a guard whose failure path never runs is
    indistinguishable from one that cannot fail.
    """
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


def section_bullets() -> list[str]:
    """Every bullet inside the section, matching the grammar or not.

    `route_lines` keeps only what parses, so a bullet the grammar misses is
    invisible to it. Reading the unfiltered bullets is what lets a test notice
    a route written in some other shape.
    """
    return [
        stripped
        for line in routing_section().split("\n")
        if (stripped := line.strip()).startswith("- `")
    ]


def route_lines() -> list[re.Match[str]]:
    return [
        match
        for line in routing_section().split("\n")
        if (match := ROUTE_LINE.match(line.strip())) is not None
    ]


class RoutingSectionPlacementTest(unittest.TestCase):
    def test_section_sits_below_the_trellis_managed_block(self) -> None:
        routing_section()  # raises with the specific placement failure

    def test_no_sd_routing_content_sits_inside_the_managed_block(self) -> None:
        document = AGENTS_DOC.read_text(encoding="utf-8")
        managed = document[: document.index(TRELLIS_END)]
        for token in (SECTION_START, SECTION_END, "/sd:"):
            self.assertNotIn(
                token,
                managed,
                "the SD routing content belongs outside the Trellis block, "
                "which a trellis update overwrites",
            )


class SectionParserTest(unittest.TestCase):
    """The extractor's failure paths, on synthetic documents.

    `test_section_sits_below_the_trellis_managed_block` above passes because
    the real document is well formed; these say what happens when it is not.
    """

    BODY = (
        "\n- `start` — canonical `/sd:start`; bypassed by resolving "
        "`trellis-start` directly\n"
    )

    def document(self, *, order: str = "normal", drop: str = "") -> str:
        section = f"{SECTION_START}{self.BODY}{SECTION_END}\n"
        document = (
            f"# Doc\n{TRELLIS_END}\n{section}"
            if order == "normal"
            else f"# Doc\n{section}{TRELLIS_END}\n"
        )
        return document.replace(drop, "", 1) if drop else document

    def test_a_well_formed_document_parses(self) -> None:
        self.assertIn("`/sd:start`", section_of(self.document()))

    def test_a_missing_marker_is_named(self) -> None:
        for marker in (TRELLIS_END, SECTION_START, SECTION_END):
            with self.subTest(missing=marker):
                with self.assertRaises(AssertionError) as raised:
                    section_of(self.document(drop=marker))
                self.assertIn(marker, str(raised.exception))

    def test_a_duplicated_marker_is_named(self) -> None:
        with self.assertRaises(AssertionError):
            section_of(self.document() + SECTION_START)

    def test_a_section_inside_the_managed_block_is_rejected(self) -> None:
        # The whole point of the placement rule: a trellis update overwrites
        # anything above TRELLIS:END, so a section there is silently lost.
        with self.assertRaises(AssertionError) as raised:
            section_of(self.document(order="above"))
        self.assertIn("after the Trellis block closes", str(raised.exception))


class RoutingSectionContentTest(unittest.TestCase):
    def test_every_route_line_names_one_workflow_consistently(self) -> None:
        for match in route_lines():
            with self.subTest(line=match.group(0)):
                self.assertEqual(match.group("workflow"), match.group("canonical"))
                self.assertEqual(match.group("workflow"), match.group("wrapped"))

    def test_no_bullet_escapes_the_route_grammar(self) -> None:
        # Set equality only sees bullets the grammar parsed. A second bullet
        # routing an already-listed workflow some other way — "- `start` — use
        # `/trellis:start` directly" — leaves the derived set intact and would
        # otherwise pass while contradicting the canonical route.
        escaped = [line for line in section_bullets() if not ROUTE_LINE.match(line)]
        self.assertEqual(
            escaped,
            [],
            "every bullet in the routing section must be a route line in the "
            "documented shape",
        )

    def test_each_workflow_has_exactly_one_route_line(self) -> None:
        listed = [match.group("workflow") for match in route_lines()]
        duplicates = sorted({name for name in listed if listed.count(name) > 1})
        self.assertEqual(duplicates, [], "one canonical route per workflow")

    def test_the_section_names_exactly_the_routed_workflows(self) -> None:
        listed = {match.group("workflow") for match in route_lines()}
        self.assertEqual(
            listed,
            set(ROUTED_WORKFLOWS),
            f"AGENTS.md routes {sorted(listed)}; this module expects "
            f"{sorted(ROUTED_WORKFLOWS)}",
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
