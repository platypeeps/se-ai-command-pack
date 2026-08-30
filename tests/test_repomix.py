"""Repository-map configuration and generated-artifact contract tests."""

from __future__ import annotations

import json
import unittest

from install_test_support import PACK_ROOT

CONFIG_PATH = PACK_ROOT / "repomix.config.json"
MAP_PATH = PACK_ROOT / "docs" / "repomix-map.md"
# Generated locally by `make repomix`, not tracked. Every read is behind
# skipUnless(MAP_PATH.exists()); tests/test_test_hermeticity.py enforces the
# declaration.
HERMETICITY_UNTRACKED_PATHS = ("docs/repomix-map.md",)
REFRESH_SCRIPT_PATH = PACK_ROOT / ".github" / "scripts" / "update-repomix"

REQUIRED_EXCLUSIONS = {
    "docs/repomix-map.md",
    ".obsidian-kb/**",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".prism/**",
    "generated/**",
}

EXCLUDED_MAP_HEADERS = {
    "## File: .github/PULL_REQUEST_TEMPLATE.md",
    "## File: .prism/rules.json",
    "## File: docs/repomix-map.md",
    "## File: generated/skills/claude/se-research/SKILL.md",
}

REQUIRED_MAP_HEADERS = {
    "## File: docs/spec/backend/quality-guidelines.md",
    "## File: README.md",
    "## File: installer/manifest.py",
    "## File: templates/skills/se-research/SKILL.md",
    "## File: tests/test_repomix.py",
}


class RepomixContractTest(unittest.TestCase):
    def test_config_declares_required_output_and_exclusions(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(config["output"]["filePath"], "docs/repomix-map.md")
        self.assertEqual(config["output"]["style"], "markdown")
        self.assertTrue(config["output"]["compress"])
        self.assertFalse(config["output"]["git"]["sortByChanges"])
        exclusions = set(config["ignore"]["customPatterns"])
        self.assertEqual(REQUIRED_EXCLUSIONS - exclusions, set())

    def test_refresh_script_disables_npm_lifecycle_scripts(self) -> None:
        script = REFRESH_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("export NPM_CONFIG_IGNORE_SCRIPTS=true", script)
        # The export has to precede the fetch it constrains: npm reads its
        # configuration from the environment at invocation time, so an export
        # placed after `exec npx` would never apply.
        self.assertLess(
            script.index("export NPM_CONFIG_IGNORE_SCRIPTS=true"),
            script.index("exec npx"),
        )

    @unittest.skipUnless(
        MAP_PATH.exists(),
        "docs/repomix-map.md is gitignored and generated on demand (policy A-025); "
        "run `make repomix` to validate its scope contract locally",
    )
    def test_generated_map_matches_scope_contract_when_present(self) -> None:
        repository_map = MAP_PATH.read_text(encoding="utf-8")

        for header in sorted(EXCLUDED_MAP_HEADERS):
            with self.subTest(excluded=header):
                self.assertNotIn(header, repository_map)
        for header in sorted(REQUIRED_MAP_HEADERS):
            with self.subTest(required=header):
                self.assertIn(header, repository_map)


if __name__ == "__main__":
    unittest.main()
