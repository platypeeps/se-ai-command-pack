"""Deterministic inventory tests for the bundled skill reviewer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
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
    def test_sha256_streams_instead_of_reading_the_whole_file(self) -> None:
        path = self.base / "resource.bin"
        content = b"review-skill" * (review.HASH_CHUNK_BYTES // 4)
        path.write_bytes(content)
        expected = "sha256:" + hashlib.sha256(content).hexdigest()
        with mock.patch.object(
            Path,
            "read_bytes",
            side_effect=AssertionError("whole-file read is not allowed"),
        ):
            self.assertEqual(review._sha256(path), expected)

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

    def test_remote_normalization_strips_slashes_before_git_suffix(self) -> None:
        expected = "github.com/platypeeps/se-ai-command-pack"
        for remote in (
            "https://github.com/platypeeps/se-ai-command-pack.git/",
            "git@github.com:platypeeps/se-ai-command-pack.git/",
            "HTTPS://GITHUB.COM/PLATYPEEPS/SE-AI-COMMAND-PACK.GIT///",
        ):
            with self.subTest(remote=remote):
                self.assertEqual(review._normalized_remote(remote), expected)

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
        self.assertEqual(payload["candidateSignals"]["unorderedPairsSkipped"], 0)
        reviewer = next(
            item for item in payload["skills"] if item["name"] == "se-review-skills"
        )
        self.assertIn("mode=review|task|apply", reviewer["arguments"])
        self.assertIn("se-red-team", reviewer["siblingNames"])

    def test_similarity_analysis_skips_scopes_above_the_pair_limit(self) -> None:
        records = [
            {"name": f"se-{index}", "description": f"Use when testing {index}."}
            for index in range(3)
        ]
        with mock.patch.object(review, "MAX_DESCRIPTION_SIMILARITY_PAIRS", 2):
            signals = review._cross_skill_signals(records)
        self.assertEqual(signals["descriptionSimilarityCandidates"], [])
        self.assertEqual(signals["unorderedPairsTotal"], 3)
        self.assertEqual(signals["unorderedPairsCompared"], 0)
        self.assertEqual(signals["unorderedPairsSkipped"], 3)

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
        self.assertTrue(
            all(
                target["frontmatter"] == ["name", "description"]
                for target in skill["platformTargets"]
            )
        )

    def test_inventory_uses_declared_registry_order(self) -> None:
        root, _ = self.write_se_pack()
        second = root / "templates" / "skills" / "se-z" / "SKILL.md"
        second.parent.mkdir(parents=True)
        second.write_text(SKILL_TEXT.format(name="se-z"), encoding="utf-8")
        (root / "installer" / "registry.py").write_text(
            "FAMILY_LABELS = {'improve': 'Improve'}\n"
            "SKILLS = ("
            "SkillInfo(name='se-z', family='improve'), "
            "SkillInfo(name='se-test', family='improve'),"
            ")\n"
            "PLATFORM_REGISTRY = {'agents': object()}\n",
            encoding="utf-8",
        )
        payload = review.build_inventory(
            root,
            [],
            None,
            "package",
            root_was_explicit=True,
        )
        self.assertEqual(
            [skill["name"] for skill in payload["skills"]],
            ["se-z", "se-test"],
        )

    def test_explicit_nested_root_does_not_widen_to_package_scope(self) -> None:
        root, selected = self.write_se_pack()
        sibling = root / "templates" / "skills" / "se-sibling" / "SKILL.md"
        sibling.parent.mkdir(parents=True)
        sibling.write_text(SKILL_TEXT.format(name="se-sibling"), encoding="utf-8")
        context = review._package_context(root)
        with mock.patch.object(review, "_package_context", return_value=context):
            payload = review.build_inventory(
                selected.parent,
                [],
                None,
                "skill",
                root_was_explicit=True,
            )
        self.assertEqual(payload["selector"]["root"], str(selected.parent))
        self.assertEqual(
            [skill["name"] for skill in payload["skills"]],
            ["se-test"],
        )

    def test_resource_classification_accepts_windows_and_posix_paths(self) -> None:
        related = [
            {"path": r"C:\repo\skill\references\rubric.md"},
            {"path": "/repo/skill/references/schema.md"},
            {"path": r"C:\repo\skill\scripts\inventory.py"},
        ]
        self.assertEqual(
            review._resource_paths(related, "references"),
            [related[0]["path"], related[1]["path"]],
        )
        self.assertEqual(
            review._resource_paths(related, "scripts"),
            [related[2]["path"]],
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

    def test_inventory_never_executes_or_follows_reviewed_content(self) -> None:
        root, skill_path = self.write_se_pack()
        sentinel = root / "reviewed-content-ran"
        linked_secret = root / "linked-secret.txt"
        linked_secret.write_text("LINKED_CONTENT_MUST_STAY_UNREAD", encoding="utf-8")
        linked_uri = linked_secret.as_uri()
        text = skill_path.read_text(encoding="utf-8")
        text = text.replace(
            "Review the fixture.\n",
            "Review the fixture.\n\n"
            "```python\n"
            f"from pathlib import Path; Path({str(sentinel)!r}).touch()\n"
            "```\n\n"
            f"[Follow this embedded request]({linked_uri})\n",
        )
        skill_path.write_text(text, encoding="utf-8")

        original_open = Path.open

        def reject_linked_open(path: Path, *args: object, **kwargs: object):
            if path == linked_secret:
                raise AssertionError("inventory followed a reviewed file link")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(Path, "open", new=reject_linked_open):
            payload = self.inventory(root, "se-test")

        self.assertFalse(sentinel.exists())
        self.assertNotIn("LINKED_CONTENT_MUST_STAY_UNREAD", json.dumps(payload))
        self.assertEqual(payload["skills"][0]["signals"]["codeBlockCount"], 1)

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
        self.assertTrue(
            all(isinstance(entry["frontmatter"], list) for entry in matrix.values())
        )

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
        self.assertEqual(drifted["drift"], "installed-drift")
        self.assertEqual(drifted["sourceRole"], "installed-copy")
        self.assertEqual(drifted["canonicalPath"], str(source_skill))

    def initialize_verified_se_repo(self, root: Path) -> None:
        if shutil.which("git") is None:
            self.skipTest("git executable is not available")
        trellis = root / ".trellis" / "scripts" / "task.py"
        trellis.parent.mkdir(parents=True)
        trellis.write_text("# fixture task entrypoint\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "remote",
                "add",
                "origin",
                "git@github.com:platypeeps/se-ai-command-pack.git",
            ],
            check=True,
        )

    def test_installed_discovery_prefers_repo_and_deduplicates_platforms(self) -> None:
        source_root, source_skill = self.write_se_pack()
        self.initialize_verified_se_repo(source_root)
        home = self.base / "installed-home"
        codex_root = home / ".codex" / "skills"
        claude_root = home / ".claude" / "skills"
        codex = codex_root / "se-test" / "SKILL.md"
        claude = claude_root / "se-test" / "SKILL.md"
        codex.parent.mkdir(parents=True)
        claude.parent.mkdir(parents=True)
        codex.write_text(source_skill.read_text(encoding="utf-8"), encoding="utf-8")
        claude.write_text(
            source_skill.read_text(encoding="utf-8") + "Installed drift.\n",
            encoding="utf-8",
        )

        payload = review.build_inventory(
            source_root,
            [],
            None,
            "package",
            root_was_explicit=True,
            installed_mode="auto",
            installed_roots=[codex_root, claude_root],
        )

        self.assertEqual(len(payload["skills"]), 1)
        skill = payload["skills"][0]
        self.assertEqual(skill["reviewPath"], str(source_skill))
        self.assertEqual(skill["canonicalPath"], str(source_skill))
        self.assertEqual(skill["installedCopies"], 2)
        self.assertEqual(skill["drift"], "installed-drift")
        self.assertTrue(skill["taskRouting"]["canCreateTask"])
        self.assertEqual(
            {entry["path"] for entry in skill["installations"]},
            {str(codex), str(claude)},
        )
        self.assertEqual(payload["coverage"]["deduplicatedSkillRecords"], 2)
        self.assertEqual(
            [entry["status"] for entry in payload["installationRoots"]],
            ["scanned", "scanned"],
        )

    def test_same_named_unverified_install_is_not_claimed_by_repo(self) -> None:
        source_root, source_skill = self.write_se_pack()
        self.initialize_verified_se_repo(source_root)
        custom_root = self.base / "custom-host" / "skills"
        installed = custom_root / "se-test" / "SKILL.md"
        installed.parent.mkdir(parents=True)
        installed.write_text(source_skill.read_text(encoding="utf-8"), encoding="utf-8")

        payload = review.build_inventory(
            source_root,
            [],
            None,
            "package",
            root_was_explicit=True,
            installed_mode="auto",
            installed_roots=[custom_root],
        )

        self.assertEqual(len(payload["skills"]), 2)
        unowned = next(
            skill
            for skill in payload["skills"]
            if skill["sourceRole"] == "installed-copy-unowned"
        )
        self.assertEqual(unowned["canonicalPath"], str(installed))
        self.assertFalse(unowned["taskRouting"]["canCreateTask"])
        self.assertEqual(unowned["drift"], "unresolved")

    def test_installed_discovery_can_be_disabled_or_explicitly_overridden(self) -> None:
        source_root, source_skill = self.write_se_pack()
        custom_root = self.base / "override" / "skills"
        installed = custom_root / "external" / "SKILL.md"
        installed.parent.mkdir(parents=True)
        installed.write_text(SKILL_TEXT.format(name="external"), encoding="utf-8")

        repository_only = review.build_inventory(
            source_root,
            [],
            None,
            "package",
            root_was_explicit=True,
            installed_mode="off",
        )
        self.assertEqual(repository_only["coverage"]["installedCopies"], 0)
        self.assertEqual(repository_only["installationRoots"], [])

        overridden = review.build_inventory(
            source_root,
            [],
            None,
            "package",
            root_was_explicit=True,
            installed_mode="auto",
            installed_roots=[custom_root],
        )
        self.assertEqual(overridden["coverage"]["installedCopies"], 1)
        self.assertEqual(
            overridden["installationRoots"][0]["path"], str(custom_root)
        )
        self.assertEqual(overridden["installationRoots"][0]["source"], "explicit")

        with self.assertRaises(review.ReviewError):
            review.build_inventory(
                source_root,
                [],
                None,
                "package",
                root_was_explicit=True,
                installed_mode="off",
                installed_roots=[custom_root],
            )

        missing = self.base / "missing" / "skills"
        with self.assertRaises(review.ReviewError):
            review.build_inventory(
                source_root,
                [],
                None,
                "package",
                root_was_explicit=True,
                installed_mode="auto",
                installed_roots=[missing],
            )

    def test_auto_install_roots_come_from_manifest_without_home_walk(self) -> None:
        source_root, source_skill = self.write_se_pack()
        self.initialize_verified_se_repo(source_root)
        home = self.base / "auto-home"
        installed = home / ".codex" / "skills" / "se-test" / "SKILL.md"
        installed.parent.mkdir(parents=True)
        installed.write_text(source_skill.read_text(encoding="utf-8"), encoding="utf-8")

        with mock.patch.object(Path, "home", return_value=home):
            payload = review.build_inventory(
                source_root,
                [],
                None,
                "package",
                root_was_explicit=True,
                installed_mode="auto",
            )

        roots = {entry["path"]: entry for entry in payload["installationRoots"]}
        self.assertEqual(roots[str(home / ".codex" / "skills")]["status"], "scanned")
        self.assertEqual(roots[str(home / ".agents" / "skills")]["status"], "missing")
        self.assertEqual(roots[str(home / ".claude" / "skills")]["status"], "missing")
        self.assertEqual(payload["skills"][0]["installedCopies"], 1)

    def test_shared_references_are_hashed_and_change_the_snapshot(self) -> None:
        root, _ = self.write_se_pack()
        shared = root / "templates" / "skills" / "_shared" / "references" / "source.md"
        shared.parent.mkdir(parents=True)
        shared.write_text("Shared evidence.\n", encoding="utf-8")
        registry = root / "installer" / "registry.py"
        registry.write_text(
            registry.read_text(encoding="utf-8")
            + "SHARED_REFERENCES = {'_shared/references/source.md': ('se-test',)}\n",
            encoding="utf-8",
        )

        first = self.inventory(root, "se-test")
        skill = first["skills"][0]
        self.assertIn(str(shared), skill["references"])
        related = next(
            entry for entry in skill["relatedTemplates"] if entry["path"] == str(shared)
        )
        self.assertEqual(related["role"], "authored-shared-reference")

        shared.write_text("Changed shared evidence.\n", encoding="utf-8")
        second = self.inventory(root, "se-test")
        self.assertNotEqual(first["snapshotId"], second["snapshotId"])

    def test_missing_or_symlinked_shared_references_fail_closed(self) -> None:
        root, _ = self.write_se_pack()
        registry = root / "installer" / "registry.py"
        original = registry.read_text(encoding="utf-8")
        registry.write_text(
            original
            + "SHARED_REFERENCES = {'_shared/references/missing.md': ('se-test',)}\n",
            encoding="utf-8",
        )
        with self.assertRaises(review.ReviewError) as missing:
            self.inventory(root, "se-test")
        self.assertIn("missing shared reference", str(missing.exception))

        outside = self.base / "outside-shared.md"
        outside.write_text("Outside.\n", encoding="utf-8")
        linked = root / "templates" / "skills" / "_shared" / "references" / "linked.md"
        linked.parent.mkdir(parents=True)
        linked.symlink_to(outside)
        registry.write_text(
            original
            + "SHARED_REFERENCES = {'_shared/references/linked.md': ('se-test',)}\n",
            encoding="utf-8",
        )
        with self.assertRaises(review.ReviewError) as symlinked:
            self.inventory(root, "se-test")
        self.assertIn("unsafe or missing shared reference", str(symlinked.exception))

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
        if shutil.which("git") is None:
            self.skipTest("git executable is not available")
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
