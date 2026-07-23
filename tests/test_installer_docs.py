"""Contract tests for the user-facing installer documentation."""

from __future__ import annotations

import unittest
from pathlib import Path

from install_test_support import PACK_ROOT


def markdown_section(path: Path, heading: str) -> str:
    """Return one normalized level-two Markdown section."""
    text = path.read_text(encoding="utf-8")
    marker = f"## {heading}\n"
    if text.count(marker) != 1:
        raise AssertionError(f"{path} must contain exactly one {marker.strip()!r}")
    start = text.index(marker) + len(marker)
    end = text.find("\n## ", start)
    if end == -1:
        end = len(text)
    return " ".join(text[start:end].split())


class InstallerDocumentationContractTest(unittest.TestCase):
    def assert_refresh_contract(self, section: str) -> None:
        for phrase in (
            "normal refresh",
            "prior provenance hash",
            "preservation semantics",
            "remain `preserved`",
            "`updated`",
        ):
            self.assertIn(phrase, section)
        self.assertNotIn("prior install receipt", section.lower())

    def test_readme_install_section_uses_canonical_refresh_contract(self) -> None:
        section = markdown_section(PACK_ROOT / "README.md", "Install")
        self.assert_refresh_contract(section)

    def test_operator_receipts_section_uses_canonical_refresh_contract(self) -> None:
        section = markdown_section(
            PACK_ROOT / "docs" / "SE_AI_COMMAND_PACK.md",
            "Receipts (`<root>/.se-ai-command-pack/`)",
        )
        self.assertIn("`provenance.json`", section)
        self.assert_refresh_contract(section)


if __name__ == "__main__":
    unittest.main()
