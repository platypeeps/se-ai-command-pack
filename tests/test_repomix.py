"""Repository-map configuration and generated-artifact contract tests."""

from __future__ import annotations

import json
import unittest

from install_test_support import PACK_ROOT

CONFIG_PATH = PACK_ROOT / "repomix.config.json"
MAP_PATH = PACK_ROOT / "docs" / "repomix-map.md"

REQUIRED_EXCLUSIONS = {
    "docs/repomix-map.md",
    ".obsidian-kb/**",
    ".sd-ai-command-pack/**",
    ".agents/**",
    ".agent/**",
    ".claude/**",
    ".codebuddy/**",
    ".codex/**",
    ".cursor/**",
    ".devin/**",
    ".factory/**",
    ".gemini/**",
    ".gito/**",
    ".github/agents/**",
    ".github/copilot/**",
    ".github/copilot-instructions.md",
    ".github/hooks/**",
    ".github/prompts/**",
    ".github/skills/**",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".kiro/**",
    ".kilocode/**",
    ".opencode/**",
    ".pi/**",
    ".prism/**",
    ".qoder/**",
    ".reasonix/**",
    ".trae/**",
    ".zcode/**",
    ".trellis/.gitignore",
    ".trellis/.version",
    ".trellis/agents/**",
    ".trellis/config.yaml",
    ".trellis/scripts/**",
    ".trellis/tasks/**",
    ".trellis/workspace/**",
    ".trellis/workflow.md",
    "generated/**",
    "docs/SD_AI_COMMAND_PACK.md",
    "scripts/sd-ai-command-pack-*",
}

EXCLUDED_MAP_HEADERS = {
    "## File: .agents/skills/sd-review-pr/SKILL.md",
    "## File: .github/PULL_REQUEST_TEMPLATE.md",
    "## File: .github/copilot-instructions.md",
    "## File: .gito/config.toml",
    "## File: .prism/rules.json",
    "## File: .trellis/workflow.md",
    "## File: docs/SD_AI_COMMAND_PACK.md",
    "## File: docs/repomix-map.md",
    "## File: generated/skills/claude/se-research/SKILL.md",
    "## File: scripts/sd-ai-command-pack-full-check.sh",
}

REQUIRED_MAP_HEADERS = {
    "## File: .trellis/spec/backend/quality-guidelines.md",
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

    def test_checked_in_map_matches_scope_contract(self) -> None:
        repository_map = MAP_PATH.read_text(encoding="utf-8")

        for header in sorted(EXCLUDED_MAP_HEADERS):
            with self.subTest(excluded=header):
                self.assertNotIn(header, repository_map)
        for header in sorted(REQUIRED_MAP_HEADERS):
            with self.subTest(required=header):
                self.assertIn(header, repository_map)


if __name__ == "__main__":
    unittest.main()
