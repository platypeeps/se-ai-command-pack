"""End-to-end installer tests: subprocess runs against temporary roots."""

from __future__ import annotations

import hashlib
import json
import unittest

import yaml
from install_test_support import (
    PACK_ROOT,
    TempDirTestCase,
    install_ok,
    make_home,
    read_provenance,
    read_receipt_targets,
    run_installer,
    tree_paths,
)

from installer.registry import PLATFORM_REGISTRY, SKILL_NAMES

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

MANIFEST = json.loads((PACK_ROOT / "manifest.json").read_text(encoding="utf-8"))
ALL_TARGETS = {row["target"] for row in MANIFEST["files"]}
RECEIPTS = {
    ".se-ai-command-pack/manifest.json",
    ".se-ai-command-pack/provenance.json",
    ".se-ai-command-pack/installed-targets.txt",
}


def manifest_source(platform: str, name: str) -> str:
    target = f"{PLATFORM_REGISTRY[platform].skills_dir}/{name}/SKILL.md"
    row = next(row for row in MANIFEST["files"] if row["target"] == target)
    return row["source"]


def installed_frontmatter(path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} must start with a YAML frontmatter delimiter")
    end = text.find("\n---\n", len("---\n"))
    if end == -1:
        raise AssertionError(f"{path} is missing its closing frontmatter delimiter")
    frontmatter = yaml.safe_load(text[len("---\n") : end])
    if not isinstance(frontmatter, dict):
        raise AssertionError(f"{path} frontmatter must be a mapping")
    return frontmatter


class InstalledFrontmatterTest(TempDirTestCase):
    def test_requires_both_frontmatter_delimiters(self) -> None:
        path = self.base / "SKILL.md"
        path.write_text("name: test\n---\n", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "must start"):
            installed_frontmatter(path)

        path.write_text("---\nname: test\n", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "missing its closing"):
            installed_frontmatter(path)

    def test_requires_mapping_frontmatter(self) -> None:
        path = self.base / "SKILL.md"
        path.write_text("---\n- test\n---\n", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "must be a mapping"):
            installed_frontmatter(path)


class FreshInstallTest(TempDirTestCase):
    def test_all_anchors_full_install(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home))
        self.assertIn("created", result.stdout)
        self.assertEqual(tree_paths(home), ALL_TARGETS | RECEIPTS)
        self.assertEqual(read_receipt_targets(home), ALL_TARGETS | RECEIPTS)
        provenance = read_provenance(home)
        self.assertEqual(provenance["version"], MANIFEST["version"])
        self.assertEqual(provenance["sourceRoot"], str(PACK_ROOT))
        self.assertEqual(set(provenance["files"]), ALL_TARGETS)

    def test_refresh_is_idempotent(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        before = tree_paths(home)
        result = install_ok("--root", str(home))
        self.assertNotIn("created", result.stdout)
        self.assertNotIn("overwritten", result.stdout)
        self.assertIn("unchanged", result.stdout)
        self.assertEqual(tree_paths(home), before)

    def test_missing_anchor_skips_with_hint(self) -> None:
        home = make_home(self.base, anchors=("claude",))
        result = install_ok("--root", str(home))
        self.assertIn("anchor .codex not present", result.stdout)
        self.assertIn("hint: .codex/ not found", result.stdout)
        installed = tree_paths(home)
        self.assertFalse(
            {path for path in installed if path.startswith(".codex/")}
        )
        self.assertTrue(
            {path for path in installed if path.startswith(".claude/")}
        )

    def test_platform_filter_installs_one_platform(self) -> None:
        home = make_home(self.base, anchors=())
        install_ok("--root", str(home), "--platform", "codex")
        installed = tree_paths(home) - RECEIPTS
        self.assertTrue(installed)
        self.assertTrue(
            all(path.startswith(".codex/") for path in installed),
            sorted(installed),
        )

    def test_all_flag_creates_missing_anchors(self) -> None:
        home = make_home(self.base, anchors=())
        install_ok("--root", str(home), "--all")
        self.assertEqual(tree_paths(home), ALL_TARGETS | RECEIPTS)

    def test_every_skill_lands_on_every_platform(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        for name in SKILL_NAMES:
            for platform, info in PLATFORM_REGISTRY.items():
                installed = home / info.skills_dir / name / "SKILL.md"
                self.assertTrue(
                    installed.is_file(),
                    f"{info.skills_dir}/{name}",
                )
                source = PACK_ROOT / manifest_source(platform, name)
                self.assertEqual(installed.read_bytes(), source.read_bytes())

    def test_runtime_metadata_is_claude_only(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        claude_root = home / PLATFORM_REGISTRY["claude"].skills_dir
        research = installed_frontmatter(claude_root / "se-research" / "SKILL.md")
        self.assertEqual(research["context"], "fork")
        self.assertEqual(research["model"], "opus")
        self.assertEqual(research["effort"], "high")
        red_team = installed_frontmatter(claude_root / "se-red-team" / "SKILL.md")
        self.assertTrue(red_team["disable-model-invocation"])
        self.assertEqual(red_team["model"], "opus")
        self.assertEqual(red_team["effort"], "xhigh")
        self.assertNotIn("context", red_team)

        for platform in ("agents", "codex"):
            path = home / PLATFORM_REGISTRY[platform].skills_dir / "se-research" / "SKILL.md"
            self.assertEqual(
                sorted(installed_frontmatter(path)), ["description", "name"]
            )


class ConflictTest(TempDirTestCase):
    def test_conflict_exits_2_and_writes_nothing(self) -> None:
        home = make_home(self.base)
        conflicting = home / ".claude/skills/se-research/SKILL.md"
        conflicting.parent.mkdir(parents=True)
        conflicting.write_text("mine\n", encoding="utf-8")
        result = run_installer("--root", str(home))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Conflicts:", result.stdout)
        self.assertIn("--force", result.stdout)
        # Plan-before-apply: nothing else was written either.
        self.assertEqual(tree_paths(home), {".claude/skills/se-research/SKILL.md"})
        self.assertEqual(conflicting.read_text(encoding="utf-8"), "mine\n")

    def test_force_overwrites_and_backup_keeps_copy(self) -> None:
        home = make_home(self.base)
        conflicting = home / ".claude/skills/se-research/SKILL.md"
        conflicting.parent.mkdir(parents=True)
        conflicting.write_text("mine\n", encoding="utf-8")
        result = install_ok("--root", str(home), "--force", "--backup")
        self.assertIn("overwritten", result.stdout)
        backup = home / ".claude/skills/se-research/SKILL.md.bak"
        self.assertEqual(backup.read_text(encoding="utf-8"), "mine\n")
        source = PACK_ROOT / manifest_source("claude", "se-research")
        self.assertEqual(conflicting.read_bytes(), source.read_bytes())

    def test_installed_user_edit_remains_a_conflict(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        conflicting = home / ".codex/skills/se-research/SKILL.md"
        conflicting.write_text("mine\n", encoding="utf-8")
        provenance_path = home / ".se-ai-command-pack/provenance.json"
        provenance_before = provenance_path.read_bytes()

        result = run_installer("refresh", "--root", str(home))

        self.assertEqual(result.returncode, 2)
        self.assertIn(str(conflicting.relative_to(home)), result.stdout)
        self.assertEqual(conflicting.read_text(encoding="utf-8"), "mine\n")
        self.assertEqual(provenance_path.read_bytes(), provenance_before)

    def test_untrusted_provenance_cannot_authorize_update(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        conflicting = home / ".claude/skills/se-research/SKILL.md"
        prior_content = b"prior installer content\n"
        conflicting.write_bytes(prior_content)
        provenance_path = home / ".se-ai-command-pack/provenance.json"
        provenance_path.write_text("{broken\n", encoding="utf-8")

        result = run_installer("refresh", "--root", str(home))

        self.assertEqual(result.returncode, 2)
        self.assertEqual(conflicting.read_bytes(), prior_content)
        self.assertEqual(provenance_path.read_text(encoding="utf-8"), "{broken\n")


class ReceiptAwareRefreshTest(TempDirTestCase):
    def test_vouched_claude_and_codex_payloads_update_without_force(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        provenance_path = home / ".se-ai-command-pack/provenance.json"
        provenance = read_provenance(home)
        targets: dict[str, bytes] = {}
        for platform in ("claude", "codex"):
            target = (
                f"{PLATFORM_REGISTRY[platform].skills_dir}"
                "/se-research/SKILL.md"
            )
            prior_content = f"prior {platform} installer payload\n".encode()
            (home / target).write_bytes(prior_content)
            provenance["files"][target] = (
                "sha256:" + hashlib.sha256(prior_content).hexdigest()
            )
            targets[target] = prior_content
        provenance_path.write_text(
            json.dumps(provenance, indent=2) + "\n",
            encoding="utf-8",
        )

        dry_run = install_ok(
            "refresh",
            "--root",
            str(home),
            "--platform",
            "claude",
            "--platform",
            "codex",
            "--dry-run",
            "--verbose",
        )
        for target, prior_content in targets.items():
            self.assertIn(f"updated     {target}", dry_run.stdout)
            self.assertEqual((home / target).read_bytes(), prior_content)

        result = install_ok(
            "refresh",
            "--root",
            str(home),
            "--platform",
            "claude",
            "--platform",
            "codex",
            "--verbose",
        )

        refreshed_provenance = read_provenance(home)
        for platform, target in zip(("claude", "codex"), targets, strict=True):
            source = PACK_ROOT / manifest_source(platform, "se-research")
            self.assertEqual((home / target).read_bytes(), source.read_bytes())
            self.assertIn(f"updated     {target}", result.stdout)
            self.assertEqual(
                refreshed_provenance["files"][target],
                "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest(),
            )
        self.assertNotIn("overwritten", result.stdout)
        self.assertFalse(any(path.endswith(".bak") for path in tree_paths(home)))


class ModesAndFlagsTest(TempDirTestCase):
    def test_dry_run_writes_nothing(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home), "--dry-run")
        self.assertIn("mode: dry-run", result.stdout)
        self.assertIn("created", result.stdout)
        self.assertEqual(tree_paths(home), set())

    def test_default_summary_is_aggregate(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home))
        for platform in ("agents", "claude", "codex", "pack"):
            self.assertRegex(
                result.stdout,
                rf"(?m)^{platform}: \d+ files \(created \d+\)$",
            )
        self.assertRegex(
            result.stdout,
            r"(?m)^install complete: \d+ files across \d+ platforms$",
        )
        self.assertNotRegex(result.stdout, r"(?m)^created\s+\.claude/")

    def test_default_summary_aggregates_anchor_skips(self) -> None:
        home = make_home(self.base, anchors=("claude",))
        result = install_ok("--root", str(home))
        self.assertRegex(result.stdout, r"(?m)^claude: \d+ files \(created \d+\)$")
        self.assertRegex(
            result.stdout,
            r"(?m)^skipped codex: \d+ files \(anchor \.codex not present\)$",
        )
        self.assertRegex(
            result.stdout,
            r"(?m)^install complete: \d+ files across 1 platform$",
        )
        self.assertNotRegex(result.stdout, r"(?m)^skipped\s+\.codex/")

    def test_dry_run_summary_names_dry_run_completion(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home), "--dry-run")
        self.assertRegex(
            result.stdout,
            r"(?m)^dry run complete \(no changes written\): \d+ files",
        )
        self.assertEqual(tree_paths(home), set())

    def test_verbose_prints_per_file_lines(self) -> None:
        home = make_home(self.base)
        result = install_ok("--root", str(home), "--verbose")
        self.assertRegex(result.stdout, r"(?m)^created\s+\.claude/")
        self.assertNotIn("install complete:", result.stdout)

    def test_status_count_formatter_keeps_unknown_statuses_visible(self) -> None:
        from install import _format_status_counts

        self.assertEqual(
            _format_status_counts(
                {"zz-future": 2, "created": 3, "unchanged": 1}
            ),
            "created 3, unchanged 1, zz-future 2",
        )

    def test_version_prints_identity(self) -> None:
        result = install_ok("--version")
        self.assertEqual(
            result.stdout.strip(),
            f"se-ai-command-pack {MANIFEST['version']}",
        )

    def test_explicit_install_command(self) -> None:
        home = make_home(self.base)
        result = install_ok("install", "--root", str(home), "--dry-run")
        self.assertIn("mode: dry-run", result.stdout)

    def test_missing_root_errors(self) -> None:
        result = run_installer("--root", str(self.base / "nope"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("install root not found", result.stderr)

    def test_pack_checkout_root_refused(self) -> None:
        result = run_installer("--root", str(PACK_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pack source checkout", result.stderr)

    def test_backup_requires_force_or_remove_command(self) -> None:
        result = run_installer("--root", str(self.base), "--backup")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--backup requires --force", result.stderr)

    def test_root_and_user_are_exclusive(self) -> None:
        result = run_installer("--root", str(self.base), "--user")
        self.assertNotEqual(result.returncode, 0)


class FilteredRefreshReceiptTest(TempDirTestCase):
    def test_platform_filtered_refresh_keeps_other_entries(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        result = install_ok("--root", str(home), "--platform", "claude")
        self.assertIn("kept-in-receipt", result.stdout)
        targets = read_receipt_targets(home)
        codex_entries = {t for t in targets if t.startswith(".codex/")}
        self.assertTrue(codex_entries, "codex entries dropped from receipt")
        provenance = read_provenance(home)
        self.assertTrue(
            {t for t in provenance["files"] if t.startswith(".codex/")},
            "codex entries dropped from provenance",
        )


AGENT_ROWS = [row for row in MANIFEST["files"] if row["kind"] == "agent"]


class AgentInstallTest(TempDirTestCase):
    """Agent rows install, refresh, and remove exactly like skill rows."""

    def test_no_agent_row_targets_the_amp_anchor(self) -> None:
        self.assertTrue(AGENT_ROWS, "expected at least one agent row")
        for row in AGENT_ROWS:
            self.assertFalse(
                row["target"].startswith(".config/agents/"), row["target"]
            )

    def test_agent_round_trip_on_claude_and_codex(self) -> None:
        home = make_home(self.base)
        install_ok("--root", str(home))
        claude_agent = home / ".claude" / "agents" / "se-source-reader.md"
        codex_agent = home / ".codex" / "agents" / "se-source-reader.toml"
        self.assertTrue(claude_agent.is_file())
        self.assertTrue(codex_agent.is_file())

        installed = tree_paths(home)
        self.assertIn(".claude/agents/se-source-reader.md", installed)
        self.assertIn(".codex/agents/se-source-reader.toml", installed)

        receipt = read_receipt_targets(home)
        self.assertIn(".claude/agents/se-source-reader.md", receipt)
        self.assertIn(".codex/agents/se-source-reader.toml", receipt)
        provenance = read_provenance(home)
        self.assertIn(".codex/agents/se-source-reader.toml", set(provenance["files"]))

        # Idempotent refresh leaves the overlays untouched.
        refreshed = install_ok("--root", str(home))
        self.assertIn("unchanged", refreshed.stdout)

        # Remove prunes both overlays.
        install_ok("remove", "--root", str(home))
        self.assertFalse(claude_agent.exists())
        self.assertFalse(codex_agent.exists())

    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_installed_codex_agent_is_valid_toml(self) -> None:
        home = make_home(self.base, anchors=("codex",))
        install_ok("--root", str(home))
        codex_agent = home / ".codex" / "agents" / "se-source-reader.toml"
        parsed = tomllib.loads(codex_agent.read_text(encoding="utf-8"))
        self.assertEqual(parsed["name"], "se-source-reader")
        self.assertIn("developer_instructions", parsed)


if __name__ == "__main__":
    unittest.main()
