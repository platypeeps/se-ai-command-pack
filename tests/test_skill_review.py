"""Deterministic inventory tests for the bundled skill reviewer."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

from install_test_support import PACK_ROOT, TempDirTestCase

from installer.registry import SKILL_NAMES

SCRIPT_PATH = (
    PACK_ROOT
    / "templates"
    / "skills"
    / "se-review-skills"
    / "scripts"
    / "skill_review.py"
)
SPEC = importlib.util.spec_from_file_location("skill_review", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
review = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = review
previous_dont_write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    SPEC.loader.exec_module(review)
finally:
    sys.dont_write_bytecode = previous_dont_write_bytecode

SKILL_TEXT = """---
name: {name}
description: Use when fixture skill {name} needs deterministic review.
---

# Fixture

## When to use

Use it.

## Arguments

Arguments.

## Workflow

Review the fixture.

## Safety rules

Remain read-only.

## Final report

Report findings.
"""


class SkillReviewInventoryTest(TempDirTestCase):
    def test_test_loader_does_not_write_into_the_skill_payload(self) -> None:
        self.assertFalse((SCRIPT_PATH.parent / "__pycache__").exists())

    def test_git_probe_fails_closed_when_git_is_missing_or_times_out(self) -> None:
        failures = (
            OSError("git is unavailable"),
            subprocess.TimeoutExpired(["git", "status"], review.GIT_TIMEOUT_SECONDS),
        )
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                with mock.patch.object(review.subprocess, "run", side_effect=failure):
                    self.assertIsNone(review._run_git(self.base, "status"))

    def write_se_pack(self) -> tuple[Path, Path]:
        root = self.base / "se-pack"
        skill = root / "templates" / "skills" / "se-test" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(SKILL_TEXT.format(name="se-test"), encoding="utf-8")
        registry = root / "installer" / "registry.py"
        registry.parent.mkdir()
        registry.write_text(
            "FAMILY_LABELS = {'improve': 'Improve'}\n"
            "SKILLS = (SkillInfo(name='se-test', family='improve'),)\n"
            "PLATFORM_REGISTRY = {'agents': object(), 'claude': object(), "
            "'codex': object()}\n",
            encoding="utf-8",
        )
        rows = [
            {
                "platform": platform,
                "source": "templates/skills/se-test/SKILL.md",
                "target": f".{platform}/skills/se-test/SKILL.md",
            }
            for platform in ("agents", "claude", "codex")
        ]
        (root / "manifest.json").write_text(
            json.dumps(
                {
                    "name": "se-ai-command-pack",
                    "version": "1.2.3",
                    "files": rows,
                }
            ),
            encoding="utf-8",
        )
        return root, skill

    def write_sd_pack(self) -> tuple[Path, Path]:
        root = self.base / "sd-pack"
        skill = root / "templates" / ".agents" / "skills" / "sd-test" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(SKILL_TEXT.format(name="sd-test"), encoding="utf-8")
        authored = root / "templates" / ".commands" / "sd-test.md"
        authored.parent.mkdir(parents=True)
        authored.write_text("Neutral command.\n", encoding="utf-8")
        adapters = {
            "claude": root / "templates" / ".claude" / "commands" / "sd" / "test.md",
            "gemini": root / "templates" / ".gemini" / "commands" / "sd" / "test.toml",
            "github": root / "templates" / ".github" / "prompts" / "sd-test.prompt.md",
        }
        for platform, path in adapters.items():
            path.parent.mkdir(parents=True)
            path.write_text(f"{platform} adapter.\n", encoding="utf-8")
        registry = root / "installer" / "registry.py"
        registry.parent.mkdir()
        registry.write_text(
            "COMMAND_REGISTRY = (CommandInfo('sd-test', 'test', 'verify'),)\n"
            "PLATFORM_REGISTRY = {'shared': object(), 'claude': object(), "
            "'gemini': object(), 'github': object()}\n",
            encoding="utf-8",
        )
        sources = {
            "shared": "templates/.commands/sd-test.md",
            "claude": "templates/.claude/commands/sd/test.md",
            "gemini": "templates/.gemini/commands/sd/test.toml",
            "github": "templates/.github/prompts/sd-test.prompt.md",
        }
        rows = [
            {
                "platform": platform,
                "source": source,
                "target": f".{platform}/command",
            }
            for platform, source in sources.items()
        ]
        rows.append(
            {
                "platform": "shared",
                "source": "templates/.agents/skills/sd-test/SKILL.md",
                "target": ".agents/skills/sd-test/SKILL.md",
            }
        )
        (root / "manifest.json").write_text(
            json.dumps(
                {
                    "name": "sd-ai-command-pack",
                    "version": "4.5.6",
                    "files": rows,
                }
            ),
            encoding="utf-8",
        )
        return root, skill

    def inventory(self, root: Path, *skills: str) -> dict:
        return review.build_inventory(
            root,
            list(skills),
            None,
            "skill" if len(skills) == 1 else "repo",
            root_was_explicit=True,
        )

    def test_current_package_inventory_compares_every_skill_pair(self) -> None:
        payload = review.build_inventory(
            PACK_ROOT,
            [],
            None,
            "package",
            root_was_explicit=True,
        )
        skill_count = len(SKILL_NAMES)
        self.assertEqual(payload["coverage"]["selectedSkills"], skill_count)
        self.assertEqual(
            payload["candidateSignals"]["unorderedPairsCompared"],
            skill_count * (skill_count - 1) // 2,
        )
        reviewer = next(
            item for item in payload["skills"] if item["name"] == "se-review-skills"
        )
        self.assertIn("mode=review|task|apply", reviewer["arguments"])
        self.assertIn("se-red-team", reviewer["siblingNames"])

    def test_se_inventory_is_stable_and_template_bounded(self) -> None:
        root, _ = self.write_se_pack()
        first = self.inventory(root, "se-test")
        second = self.inventory(root, "se-test")
        self.assertEqual(first["snapshotId"], second["snapshotId"])
        repository = first["repositories"][0]
        self.assertEqual(repository["package"], "se-ai-command-pack")
        self.assertEqual(
            repository["allowedTemplateRoot"],
            str(root / "templates" / "skills"),
        )
        skill = first["skills"][0]
        self.assertEqual(skill["family"], "improve")
        self.assertEqual(skill["canonicalHash"], skill["observedHash"])
        self.assertEqual(skill["arguments"], [])
        self.assertEqual(skill["siblingNames"], [])
        self.assertEqual(skill["sourceRole"], "authored-template")
        self.assertTrue(skill["changeable"])
        self.assertEqual(
            [target["target"] for target in skill["platformTargets"]],
            ["agents", "claude", "codex"],
        )

    def test_inventory_surfaces_embedded_script_candidate_facts(self) -> None:
        root, skill_path = self.write_se_pack()
        text = skill_path.read_text(encoding="utf-8")
        text = text.replace(
            "Review the fixture.\n",
            "Review the fixture.\n\n"
            "```bash\n"
            "find templates -name SKILL.md\n"
            "jq -S . manifest.json\n"
            "```\n",
        )
        skill_path.write_text(text, encoding="utf-8")
        skill = self.inventory(root, "se-test")["skills"][0]
        self.assertEqual(skill["signals"]["codeBlockCount"], 1)
        candidate = skill["signals"]["scriptCandidateSignals"][0]
        self.assertEqual(candidate["language"], "bash")
        self.assertEqual(
            candidate["candidateKinds"],
            [
                "path-resolution-or-inventory",
                "stable-command-orchestration",
                "structured-parsing",
            ],
        )

    def test_sd_inventory_distinguishes_authored_and_adapter_templates(self) -> None:
        root, _ = self.write_sd_pack()
        payload = self.inventory(root, "sd-test")
        repository = payload["repositories"][0]
        self.assertEqual(repository["package"], "sd-ai-command-pack")
        self.assertEqual(repository["allowedTemplateRoot"], str(root / "templates"))
        skill = payload["skills"][0]
        self.assertEqual(skill["family"], "verify")
        roles = {entry["role"] for entry in skill["relatedTemplates"]}
        self.assertEqual(roles, {"authored-template", "generated-template-adapter"})
        matrix = {entry["target"]: entry for entry in skill["platformTargets"]}
        self.assertEqual(matrix["gemini"]["commandFormat"], "toml")
        self.assertEqual(matrix["claude"]["content"], "adapted")
        self.assertEqual(matrix["shared"]["content"], "shared")

    def test_installed_copy_maps_to_source_and_reports_drift(self) -> None:
        source_root, source_skill = self.write_se_pack()
        install_root = self.base / "home"
        observed = install_root / ".codex" / "skills" / "se-test" / "SKILL.md"
        observed.parent.mkdir(parents=True)
        observed.write_text(source_skill.read_text(encoding="utf-8"), encoding="utf-8")
        receipt = install_root / ".se-ai-command-pack" / "provenance.json"
        receipt.parent.mkdir()
        receipt.write_text(
            json.dumps({"sourceRoot": str(source_root)}), encoding="utf-8"
        )
        payload = self.inventory(install_root, str(observed))
        skill = payload["skills"][0]
        self.assertEqual(skill["canonicalPath"], str(source_skill))
        self.assertEqual(skill["sourceRole"], "installed-copy")
        self.assertEqual(skill["drift"], "canonical-match")

        observed.write_text(
            source_skill.read_text(encoding="utf-8") + "Local override.\n",
            encoding="utf-8",
        )
        drifted = self.inventory(install_root, str(observed))["skills"][0]
        self.assertEqual(drifted["drift"], "local-override")
        self.assertEqual(drifted["sourceRole"], "local-override")

    def test_unbounded_generic_multiple_roots_are_rejected(self) -> None:
        root = self.base / "generic"
        for relative, name in (
            (".agents/skills/one", "one"),
            (".codex/skills/two", "two"),
        ):
            path = root / relative / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(SKILL_TEXT.format(name=name), encoding="utf-8")
        with self.assertRaises(review.ReviewError) as caught:
            review.build_inventory(
                root,
                [],
                None,
                None,
                root_was_explicit=False,
            )
        self.assertIn("multiple unrelated skill roots", str(caught.exception))

    def test_home_or_filesystem_root_is_rejected_before_discovery(self) -> None:
        for root in (Path.home(), Path(Path.home().anchor)):
            with self.assertRaises(review.ReviewError) as caught:
                review.build_inventory(
                    root,
                    [],
                    None,
                    None,
                    root_was_explicit=True,
                )
            self.assertIn("refusing unbounded", str(caught.exception))

    def test_explicit_root_rejects_skill_path_escape(self) -> None:
        root, _ = self.write_se_pack()
        outside = self.base / "outside" / "escaped" / "SKILL.md"
        outside.parent.mkdir(parents=True)
        outside.write_text(SKILL_TEXT.format(name="escaped"), encoding="utf-8")
        with self.assertRaises(review.ReviewError) as caught:
            review.build_inventory(
                root,
                [str(outside)],
                None,
                "skill",
                root_was_explicit=True,
            )
        self.assertIn("escapes the bounded root", str(caught.exception))

    def test_empty_root_and_malformed_skill_fail_cleanly(self) -> None:
        empty = self.base / "empty"
        empty.mkdir()
        with self.assertRaises(review.ReviewError) as caught:
            review.build_inventory(
                empty,
                [],
                None,
                "repo",
                root_was_explicit=True,
            )
        self.assertIn("no skills found", str(caught.exception))

        malformed = empty / "skills" / "broken" / "SKILL.md"
        malformed.parent.mkdir(parents=True)
        malformed.write_text("# no metadata\n", encoding="utf-8")
        with self.assertRaises(review.ReviewError) as caught:
            review.build_inventory(
                empty,
                [str(malformed)],
                None,
                "skill",
                root_was_explicit=True,
            )
        self.assertIn("missing frontmatter opening", str(caught.exception))

    def test_symlinked_skill_path_is_rejected(self) -> None:
        root, skill = self.write_se_pack()
        linked = self.base / "linked-skill.md"
        linked.symlink_to(skill)
        with self.assertRaises(review.ReviewError) as caught:
            self.inventory(root, str(linked))
        self.assertIn("symlink boundary", str(caught.exception))

    def test_family_scope_requires_declared_family(self) -> None:
        root, _ = self.write_se_pack()
        with self.assertRaises(review.ReviewError) as caught:
            review.build_inventory(
                root,
                [],
                None,
                "family",
                root_was_explicit=True,
            )
        self.assertIn("requires --family", str(caught.exception))

    def test_first_party_identity_with_wrong_remote_is_unresolved(self) -> None:
        root, _ = self.write_se_pack()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "remote",
                "add",
                "origin",
                "git@github.com:example/not-the-pack.git",
            ],
            check=True,
        )
        payload = self.inventory(root, "se-test")
        self.assertEqual(payload["repositories"][0]["ownerKind"], "unresolved")
        self.assertFalse(payload["skills"][0]["taskRouting"]["canCreateTask"])

    def test_installed_mapping_cannot_escape_first_party_templates(self) -> None:
        source_root, _ = self.write_se_pack()
        outside = source_root / "outside" / "se-test" / "SKILL.md"
        outside.parent.mkdir(parents=True)
        outside.write_text(SKILL_TEXT.format(name="se-test"), encoding="utf-8")
        manifest = json.loads((source_root / "manifest.json").read_text("utf-8"))
        manifest["files"] = [
            {
                "platform": "codex",
                "source": "outside/se-test/SKILL.md",
                "target": ".codex/skills/se-test/SKILL.md",
            }
        ]
        (source_root / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        install_root = self.base / "escaped-home"
        observed = install_root / ".codex" / "skills" / "se-test" / "SKILL.md"
        observed.parent.mkdir(parents=True)
        observed.write_text(outside.read_text("utf-8"), encoding="utf-8")
        receipt = install_root / ".se-ai-command-pack" / "provenance.json"
        receipt.parent.mkdir()
        receipt.write_text(
            json.dumps({"sourceRoot": str(source_root)}), encoding="utf-8"
        )
        payload = self.inventory(install_root, str(observed))
        skill = payload["skills"][0]
        self.assertNotEqual(skill["canonicalPath"], str(outside))
        self.assertFalse(skill["taskRouting"]["canCreateTask"])


if __name__ == "__main__":
    import unittest

    unittest.main()
