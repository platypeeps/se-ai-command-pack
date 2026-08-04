"""Tests for the skill-surface generator: validation, regen, drift check."""

from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

from install_test_support import PACK_ROOT, TempDirTestCase

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

GENERATOR_PATH = PACK_ROOT / ".github" / "scripts" / "generate-skill-surfaces.py"

spec = importlib.util.spec_from_file_location(
    "generate_skill_surfaces", GENERATOR_PATH
)
assert spec is not None and spec.loader is not None
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

VALID_SKILL = """---
name: {name}
description: Use when testing the generator fixture behavior end to end.
---

# Fixture Skill

Intro paragraph.

## When to use

Text.

## Arguments

Text.

## Workflow

Text.

## Safety rules

Text.

## Final report

Text.
"""

# Golden snapshot of which shared references each skill consumes. Seeded as an
# independent literal, not computed from gen.SHARED_REFERENCES, so a registry
# change (a dropped or added consumer) diverges from this snapshot and fails the
# subTest naming the offending skill. Skills absent here consume no shared
# reference and default to (). Adding a skill needs no new test method: a new
# consumer only edits this dict.
EXPECTED_SHARED_SOURCES: dict[str, tuple[str, ...]] = {
    "se-research": (
        "_shared/references/source-standards.md",
        "_shared/references/verification-protocol.md",
    ),
    "se-brief": ("_shared/references/source-standards.md",),
    "se-meeting-prep": ("_shared/references/source-standards.md",),
    "se-scan": ("_shared/references/source-standards.md",),
    "se-digest": ("_shared/references/source-standards.md",),
    "se-decide": ("_shared/references/source-standards.md",),
    "se-status": ("_shared/references/source-standards.md",),
    "se-fact-check": (
        "_shared/references/source-standards.md",
        "_shared/references/verification-protocol.md",
    ),
    "se-help": ("_shared/references/skill-catalog.md",),
    "se-profile": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-action-inbox": ("_shared/references/source-standards.md",),
    "se-agenda": ("_shared/references/source-standards.md",),
    "se-ask-me": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-author": ("_shared/references/source-standards.md",),
    "se-bookmark-triage": ("_shared/references/source-standards.md",),
    "se-capture": ("_shared/references/source-standards.md",),
    "se-checklist": ("_shared/references/source-standards.md",),
    "se-compare": ("_shared/references/source-standards.md",),
    "se-diagram": ("_shared/references/source-standards.md",),
    "se-distill": ("_shared/references/source-standards.md",),
    "se-evaluate": ("_shared/references/source-standards.md",),
    "se-topic-radar": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-technical-editor": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-explain": ("_shared/references/source-standards.md",),
    "se-feedback": ("_shared/references/source-standards.md",),
    "se-handoff": ("_shared/references/source-standards.md",),
    "se-knowledge-capture": ("_shared/references/source-standards.md",),
    "se-knowledge-gap": ("_shared/references/source-standards.md",),
    "se-learn": ("_shared/references/source-standards.md",),
    "se-literature-map": (
        "_shared/references/source-standards.md",
        "_shared/references/verification-protocol.md",
    ),
    "se-meeting-follow-through": ("_shared/references/source-standards.md",),
    "se-monitor": (
        "_shared/references/source-standards.md",
        "_shared/references/state-schema.md",
    ),
    "se-paper": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
        "_shared/references/verification-protocol.md",
    ),
    "se-plan": ("_shared/references/source-standards.md",),
    "se-postmortem": ("_shared/references/source-standards.md",),
    "se-premortem": ("_shared/references/source-standards.md",),
    "se-presentation": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-proposal": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-publish": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-red-team": ("_shared/references/source-standards.md",),
    "se-retro": ("_shared/references/source-standards.md",),
    "se-weekly-review": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-runbook": ("_shared/references/source-standards.md",),
    "se-socratic-review": ("_shared/references/source-standards.md",),
    "se-sop": ("_shared/references/source-standards.md",),
    "se-stakeholder-map": ("_shared/references/source-standards.md",),
    "se-study-guide": ("_shared/references/source-standards.md",),
    "se-thread-digest": ("_shared/references/source-standards.md",),
    "se-tutorial": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
    ),
    "se-video-notes": ("_shared/references/source-standards.md",),
    "se-watchlist": (
        "_shared/references/personal-profile-contract.md",
        "_shared/references/source-standards.md",
        "_shared/references/state-schema.md",
    ),
}


class RealRepoGeneratorTest(unittest.TestCase):
    def test_canonical_skills_validate(self) -> None:
        gen.validate_skills()

    def test_manifest_matches_generated(self) -> None:
        committed = (PACK_ROOT / "manifest.json").read_text(encoding="utf-8")
        self.assertEqual(committed, gen.regenerated_manifest_text())

    def test_generated_claude_skills_match_runtime_profiles(self) -> None:
        regenerated = gen.regenerated_claude_skill_texts()
        self.assertEqual(len(regenerated), len(gen.SKILL_NAMES))
        for path, expected in regenerated.items():
            self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_claude_frontmatter_applies_reviewed_profiles(self) -> None:
        research = (
            gen.CLAUDE_GENERATED_ROOT / "se-research" / "SKILL.md"
        ).read_text(encoding="utf-8")
        research_metadata, research_body = gen.parse_frontmatter(
            research, "generated research"
        )
        _, canonical_body = gen.parse_frontmatter(
            (gen.SKILLS_ROOT / "se-research" / "SKILL.md").read_text("utf-8"),
            "canonical research",
        )
        self.assertEqual(research_body, canonical_body)
        self.assertEqual(research_metadata["context"], "fork")
        self.assertEqual(research_metadata["model"], "opus")
        self.assertEqual(research_metadata["effort"], "high")
        self.assertNotIn("disable-model-invocation", research_metadata)

        red_team = (
            gen.CLAUDE_GENERATED_ROOT / "se-red-team" / "SKILL.md"
        ).read_text(encoding="utf-8")
        red_team_metadata, _ = gen.parse_frontmatter(red_team, "generated red team")
        self.assertTrue(red_team_metadata["disable-model-invocation"])
        self.assertEqual(red_team_metadata["model"], "opus")
        self.assertEqual(red_team_metadata["effort"], "xhigh")
        self.assertNotIn("context", red_team_metadata)

    def test_manifest_description_matches_bootstrap_default(self) -> None:
        committed = json.loads(
            (PACK_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            committed["description"],
            gen.DEFAULT_MANIFEST_HEADER["description"],
        )

    def test_readme_catalog_matches_generated(self) -> None:
        committed = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(committed, gen.regenerated_readme_text())

    def test_help_catalog_matches_generated(self) -> None:
        committed = gen.HELP_CATALOG_PATH.read_text(encoding="utf-8")
        self.assertEqual(committed, gen.regenerated_help_catalog_text())

    def test_help_catalog_uses_version_family_order_and_frontmatter(self) -> None:
        rendered = gen.regenerated_help_catalog_text()
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        self.assertIn(f"Bundled pack version: `{manifest['version']}`", rendered)
        headings = [f"## {label}" for label in gen.FAMILY_LABELS.values()]
        for earlier, later in zip(headings, headings[1:], strict=False):
            self.assertLess(rendered.index(earlier), rendered.index(later))
        for family, description in gen.FAMILY_DESCRIPTIONS.items():
            self.assertIn(gen.FAMILY_LABELS[family], rendered)
            self.assertIn(description, rendered)
        self.assertIn(
            "Use when the user asks for deep, multi-source research",
            rendered,
        )
        self.assertIn("`se-help`", rendered)

    def test_readme_catalog_uses_family_order_and_frontmatter(self) -> None:
        rendered = gen.regenerated_readme_text()
        self.assertLess(rendered.index("### Understand"), rendered.index("### Decide"))
        self.assertLess(rendered.index("### Decide"), rendered.index("### Create"))
        self.assertLess(rendered.index("### Create"), rendered.index("### Coordinate"))
        self.assertIn("### Operate", rendered)
        self.assertLess(rendered.index("### Operate"), rendered.index("### Improve"))
        self.assertIn("`se-evaluate`", rendered)
        self.assertIn(
            "Use when the user asks for deep, multi-source research",
            rendered,
        )
        self.assertIn(
            "Use when the user wants a defensible recommendation",
            rendered,
        )
        self.assertIn(
            "Use when the user wants an objective-oriented project status",
            rendered,
        )
        self.assertIn(
            "Use when the user supplies claims or a draft",
            rendered,
        )
        self.assertLess(rendered.index("`se-meeting-prep`"), rendered.index("`se-status`"))

    def test_check_mode_passes(self) -> None:
        self.assertEqual(gen.main(["--check"]), 0)

    def test_rows_cover_every_skill_and_platform(self) -> None:
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for name in gen.SKILL_NAMES:
            for platform, info in gen.PLATFORM_REGISTRY.items():
                target = f"{info.skills_dir}/{name}/SKILL.md"
                matches = [row for row in rows if row["target"] == target]
                self.assertEqual(
                    len(matches), 1, f"expected one row for {target}"
                )
                self.assertEqual(matches[0]["platform"], platform)
                self.assertEqual(matches[0]["scope"], "user")
                self.assertEqual(matches[0]["anchor"], info.anchor)
                expected_source = f"templates/skills/{name}/SKILL.md"
                if platform == "claude":
                    expected_source = f"generated/skills/claude/{name}/SKILL.md"
                self.assertEqual(matches[0]["source"], expected_source)

    def test_shared_reference_fanned_into_consumers(self) -> None:
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        targets = {row["target"] for row in manifest["files"]}
        for source, consumers in gen.SHARED_REFERENCES.items():
            basename = Path(source).name
            for consumer in consumers:
                for info in gen.PLATFORM_REGISTRY.values():
                    self.assertIn(
                        f"{info.skills_dir}/{consumer}/references/{basename}",
                        targets,
                    )

    def test_review_skill_bundled_resources_fan_to_every_platform(self) -> None:
        expected = {
            "SKILL.md",
            "references/report-schema.md",
            "references/review-rubric.md",
            "references/session-evidence.md",
            "references/runtime-routing.md",
            "scripts/skill_review.py",
        }
        self.assertEqual(set(gen.skill_payload_files("se-review-skills")), expected)
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for platform, info in gen.PLATFORM_REGISTRY.items():
            for relative in expected:
                target = f"{info.skills_dir}/se-review-skills/{relative}"
                matches = [row for row in rows if row["target"] == target]
                self.assertEqual(len(matches), 1, (platform, target))

    def test_help_catalog_reference_fans_into_help_only(self) -> None:
        source = "_shared/references/skill-catalog.md"
        self.assertEqual(gen.SHARED_REFERENCES[source], ("se-help",))
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for platform, info in gen.PLATFORM_REGISTRY.items():
            target = f"{info.skills_dir}/se-help/references/skill-catalog.md"
            matches = [row for row in rows if row["target"] == target]
            self.assertEqual(len(matches), 1, (platform, target))
            self.assertEqual(
                matches[0]["source"],
                "templates/skills/_shared/references/skill-catalog.md",
            )

    def test_registered_shared_sources_match_snapshot(self) -> None:
        """One registry-driven check replacing the per-skill methods: each
        skill's registered shared sources must match the golden snapshot, and
        every registered reference must fan into a manifest target on every
        platform. Failure output names the offending skill and reference."""
        rows = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))["files"]
        target_counts = Counter(row["target"] for row in rows)
        stale = sorted(set(EXPECTED_SHARED_SOURCES) - set(gen.SKILL_NAMES))
        self.assertEqual(stale, [], f"snapshot names absent from SKILL_NAMES: {stale}")
        for name in gen.SKILL_NAMES:
            with self.subTest(skill=name):
                actual = tuple(
                    sorted(
                        source
                        for source, consumers in gen.SHARED_REFERENCES.items()
                        if name in consumers
                    )
                )
                # Sort the snapshot too so the golden literal is order-free:
                # a maintainer may list a skill's sources in any order.
                expected = tuple(sorted(EXPECTED_SHARED_SOURCES.get(name, ())))
                self.assertEqual(
                    actual,
                    expected,
                    f"{name}: registered shared sources {actual} "
                    f"do not match snapshot {expected}",
                )
                for source in actual:
                    basename = Path(source).name
                    for platform, info in gen.PLATFORM_REGISTRY.items():
                        target = f"{info.skills_dir}/{name}/references/{basename}"
                        # Assert exactly one manifest row per platform target,
                        # preserving the retired per-skill uniqueness coverage.
                        self.assertEqual(
                            target_counts[target],
                            1,
                            f"{name}: shared reference {basename} expected one "
                            f"manifest target for {platform}, got "
                            f"{target_counts[target]}",
                        )

    def test_verification_protocol_preserves_registered_targets(self) -> None:
        source = "_shared/references/verification-protocol.md"
        self.assertEqual(
            gen.SHARED_REFERENCES[source],
            ("se-research", "se-fact-check", "se-literature-map", "se-paper"),
        )
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for platform, info in gen.PLATFORM_REGISTRY.items():
            for consumer in (
                "se-research",
                "se-fact-check",
                "se-literature-map",
                "se-paper",
            ):
                target = (
                    f"{info.skills_dir}/{consumer}/references/"
                    "verification-protocol.md"
                )
                matches = [row for row in rows if row["target"] == target]
                self.assertEqual(len(matches), 1, (platform, consumer))
                self.assertEqual(
                    matches[0]["source"],
                    "templates/skills/_shared/references/"
                    "verification-protocol.md",
                )


class RealRepoAgentTest(unittest.TestCase):
    """Agent artifact kind: committed overlays, rows, and Amp exclusion."""

    def test_committed_agent_overlays_match_canonical(self) -> None:
        regenerated = gen.regenerated_agent_texts()
        self.assertTrue(regenerated, "expected at least one canonical agent")
        for path, expected in regenerated.items():
            self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_agent_rows_only_on_agent_capable_platforms(self) -> None:
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        agent_rows = [r for r in manifest["files"] if r["kind"] == "agent"]
        self.assertTrue(agent_rows)
        platforms = {r["platform"] for r in agent_rows}
        self.assertEqual(platforms, {"claude", "codex"})

    def test_amp_receives_no_agent_rows(self) -> None:
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        for row in manifest["files"]:
            if row["kind"] == "agent":
                self.assertFalse(
                    row["target"].startswith(".config/agents/"),
                    row["target"],
                )

    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_smoke_agent_round_trips_through_both_dialects(self) -> None:
        name = "se-smoke"
        canonical = (gen.AGENTS_ROOT / f"{name}.md").read_text("utf-8")
        _, canonical_body = gen.parse_frontmatter(canonical, "canonical smoke")

        claude = gen.render_claude_agent(name, canonical)
        claude_meta, claude_body = gen.parse_frontmatter(claude, "claude smoke")
        self.assertEqual(claude_meta["name"], name)
        self.assertNotIn("sandbox_mode", claude_meta)
        self.assertEqual(claude_body, canonical_body)

        codex = gen.render_codex_agent(name, canonical)
        parsed = tomllib.loads(codex)
        self.assertEqual(parsed["name"], name)
        self.assertEqual(parsed["developer_instructions"], canonical_body)


class AgentRendererTest(unittest.TestCase):
    """Dialect and escaping guarantees for the agent renderers."""

    CANONICAL = (
        "---\n"
        "name: se-fixture\n"
        "description: Use tabs and quotes to stress the renderer.\n"
        "tools:\n"
        "  - read\n"
        "  - write\n"
        "model: fast\n"
        "sandbox_mode: workspace-write\n"
        "---\n"
        "\n"
        '# Fixture\n'
        "\n"
        'Body has "double quotes", a \\ backslash, a\ttab,\n'
        'and a triple """ quote sequence that must not close early.\n'
    )

    def test_claude_keeps_portable_keys_and_drops_sandbox_mode(self) -> None:
        rendered = gen.render_claude_agent("se-fixture", self.CANONICAL)
        meta, body = gen.parse_frontmatter(rendered, "claude fixture")
        self.assertEqual(
            sorted(meta), ["description", "model", "name", "tools"]
        )
        self.assertEqual(meta["tools"], ["read", "write"])
        self.assertEqual(meta["model"], "fast")
        self.assertNotIn("sandbox_mode", meta)
        _, canonical_body = gen.parse_frontmatter(self.CANONICAL, "canonical")
        self.assertEqual(body, canonical_body)

    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_codex_toml_escapes_and_preserves_body(self) -> None:
        rendered = gen.render_codex_agent("se-fixture", self.CANONICAL)
        parsed = tomllib.loads(rendered)
        self.assertEqual(parsed["name"], "se-fixture")
        self.assertEqual(parsed["model"], "fast")
        self.assertEqual(parsed["sandbox_mode"], "workspace-write")
        self.assertNotIn("tools", parsed)
        _, canonical_body = gen.parse_frontmatter(self.CANONICAL, "canonical")
        self.assertEqual(parsed["developer_instructions"], canonical_body)

    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_codex_omits_absent_optional_hints(self) -> None:
        minimal = (
            "---\n"
            "name: se-min\n"
            "description: No optional hints here.\n"
            "---\n"
            "\n"
            "# Min\n"
        )
        parsed = tomllib.loads(gen.render_codex_agent("se-min", minimal))
        self.assertEqual(sorted(parsed), ["description", "developer_instructions", "name"])


class SandboxGeneratorTest(TempDirTestCase):
    """Generator behavior against a synthetic skills tree."""

    def setUp(self) -> None:
        super().setUp()
        self.skills_root = self.base / "templates" / "skills"
        self.skills_root.mkdir(parents=True)
        self.manifest_path = self.base / "manifest.json"
        self.readme_path = self.base / "README.md"
        self.help_catalog_path = self.base / "skill-catalog.md"
        self.claude_generated_root = (
            self.base / "generated" / "skills" / "claude"
        )
        self.agents_root = self.base / "templates" / "agents"
        self.generated_agents_root = self.base / "generated" / "agents"
        self.readme_path.write_text(
            "# Fixture\n\n## Skills\n\n"
            "<!-- SE_SKILL_CATALOG:START -->\n"
            "old catalog\n"
            "<!-- SE_SKILL_CATALOG:END -->\n\n"
            "Tail.\n",
            encoding="utf-8",
        )
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(
            mock.patch.object(gen, "SKILLS_ROOT", self.skills_root)
        )
        stack.enter_context(
            mock.patch.object(gen, "MANIFEST_PATH", self.manifest_path)
        )
        stack.enter_context(
            mock.patch.object(gen, "README_PATH", self.readme_path)
        )
        stack.enter_context(
            mock.patch.object(gen, "HELP_CATALOG_PATH", self.help_catalog_path)
        )
        stack.enter_context(
            mock.patch.object(
                gen, "CLAUDE_GENERATED_ROOT", self.claude_generated_root
            )
        )
        stack.enter_context(
            mock.patch.object(gen, "AGENTS_ROOT", self.agents_root)
        )
        stack.enter_context(
            mock.patch.object(
                gen, "GENERATED_AGENTS_ROOT", self.generated_agents_root
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "CLAUDE_AGENTS_GENERATED_ROOT",
                self.generated_agents_root / "claude",
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "CODEX_AGENTS_GENERATED_ROOT",
                self.generated_agents_root / "codex",
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "FAMILY_LABELS",
                {"understand": "Understand", "decide": "Decide"},
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "FAMILY_DESCRIPTIONS",
                {
                    "understand": "Understand fixture outcomes.",
                    "decide": "Decide fixture outcomes.",
                },
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "SKILLS",
                (gen.SkillInfo(name="se-test", family="understand"),),
            )
        )
        stack.enter_context(
            mock.patch.object(gen, "SKILL_NAMES", ("se-test",))
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "SKILL_RUNTIME_PROFILES",
                {
                    "se-test": gen.RuntimeProfile(
                        invocation="both",
                        context="inline",
                        model="balanced",
                        effort="medium",
                    )
                },
            )
        )
        stack.enter_context(mock.patch.object(gen, "SHARED_REFERENCES", {}))

    def write_skill(self, name: str = "se-test", text: str | None = None) -> Path:
        skill_dir = self.skills_root / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            text if text is not None else VALID_SKILL.format(name=name),
            encoding="utf-8",
        )
        return skill_md

    def assert_validation_error(self, fragment: str) -> None:
        with self.assertRaises(gen.GenerationError) as caught:
            gen.validate_skills()
        self.assertIn(fragment, str(caught.exception))

    def test_valid_fixture_passes(self) -> None:
        self.write_skill()
        gen.validate_skills()

    def test_missing_skill_dir(self) -> None:
        self.assert_validation_error("has no directory")

    def test_unregistered_skill_dir(self) -> None:
        self.write_skill()
        self.write_skill("se-rogue")
        self.assert_validation_error("not registered")

    def test_missing_frontmatter(self) -> None:
        self.write_skill(text="# No frontmatter\n")
        self.assert_validation_error("missing YAML frontmatter")

    def test_name_mismatch(self) -> None:
        self.write_skill(text=VALID_SKILL.format(name="se-other"))
        self.assert_validation_error("must equal the skill directory name")

    def test_description_prefix(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "Use when testing", "For testing"
        )
        self.write_skill(text=text)
        self.assert_validation_error("must start with 'Use when'")

    def test_description_double_quotes(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "end to end.", 'end to "end".'
        )
        self.write_skill(text=text)
        self.assert_validation_error("double quotes")

    def test_extra_frontmatter_key(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "---\n\n# Fixture",
            "allowed-tools: all\n---\n\n# Fixture",
        )
        self.write_skill(text=text)
        self.assert_validation_error("not allowed")

    def test_missing_section(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "## Safety rules\n\nText.\n\n", ""
        )
        self.write_skill(text=text)
        self.assert_validation_error("missing required section '## Safety rules'")

    def test_out_of_order_sections(self) -> None:
        text = VALID_SKILL.format(name="se-test")
        text = text.replace("## When to use", "## TEMP")
        text = text.replace("## Final report", "## When to use")
        text = text.replace("## TEMP", "## Final report")
        self.write_skill(text=text)
        self.assert_validation_error("out of order")

    def test_banned_phrase(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "Intro paragraph.", "Ask Claude to do it."
        )
        self.write_skill(text=text)
        self.assert_validation_error("framework-neutrality")

    def test_lowercase_paths_are_not_banned(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "Intro paragraph.", "Skills install under `.claude/skills/`."
        )
        self.write_skill(text=text)
        gen.validate_skills()

    def test_unexpected_file_in_skill_dir(self) -> None:
        self.write_skill()
        (self.skills_root / "se-test" / "notes.txt").write_text(
            "x", encoding="utf-8"
        )
        self.assert_validation_error("unexpected file")

    def test_skill_script_is_validated_and_shipped(self) -> None:
        self.write_skill()
        scripts = self.skills_root / "se-test" / "scripts"
        scripts.mkdir()
        (scripts / "inventory.py").write_text("print('ok')\n", encoding="utf-8")
        gen.validate_skills()
        self.assertEqual(
            gen.skill_payload_files("se-test"),
            ["SKILL.md", "scripts/inventory.py"],
        )
        rows = gen.build_rows()
        for platform, info in gen.PLATFORM_REGISTRY.items():
            target = f"{info.skills_dir}/se-test/scripts/inventory.py"
            matches = [row for row in rows if row["target"] == target]
            self.assertEqual(len(matches), 1, (platform, target))

    def test_symlinked_skill_resource_is_rejected(self) -> None:
        self.write_skill()
        scripts = self.skills_root / "se-test" / "scripts"
        scripts.mkdir()
        target = self.base / "outside.py"
        target.write_text("print('outside')\n", encoding="utf-8")
        (scripts / "inventory.py").symlink_to(target)
        self.assert_validation_error("unexpected symlink scripts/inventory.py")

    def test_symlinked_resource_directory_is_rejected_and_not_enumerated(self) -> None:
        self.write_skill()
        external = self.base / "external-scripts"
        external.mkdir()
        (external / "inventory.py").write_text("print('outside')\n", encoding="utf-8")
        (self.skills_root / "se-test" / "scripts").symlink_to(
            external,
            target_is_directory=True,
        )
        self.assertEqual(gen.skill_payload_files("se-test"), ["SKILL.md"])
        self.assert_validation_error("unexpected symlink scripts")

    def test_nested_or_wrong_resource_file_is_rejected(self) -> None:
        self.write_skill()
        nested = self.skills_root / "se-test" / "scripts" / "nested"
        nested.mkdir(parents=True)
        (nested / "inventory.py").write_text("print('no')\n", encoding="utf-8")
        self.assert_validation_error("unexpected directory")

    def test_missing_shared_reference(self) -> None:
        self.write_skill()
        with mock.patch.object(
            gen,
            "SHARED_REFERENCES",
            {"_shared/references/source-standards.md": ("se-test",)},
        ):
            self.assert_validation_error("missing shared reference")

    def test_shared_reference_collision(self) -> None:
        self.write_skill()
        shared = self.skills_root / "_shared" / "references"
        shared.mkdir(parents=True)
        (shared / "source-standards.md").write_text("bar\n", encoding="utf-8")
        own = self.skills_root / "se-test" / "references"
        own.mkdir()
        (own / "source-standards.md").write_text("own\n", encoding="utf-8")
        with mock.patch.object(
            gen,
            "SHARED_REFERENCES",
            {"_shared/references/source-standards.md": ("se-test",)},
        ):
            self.assert_validation_error("collides with the shared reference")

    def test_unregistered_shared_file(self) -> None:
        self.write_skill()
        shared = self.skills_root / "_shared" / "references"
        shared.mkdir(parents=True)
        (shared / "orphan.md").write_text("x\n", encoding="utf-8")
        self.assert_validation_error("not registered in")

    def test_bootstrap_writes_manifest(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "se-ai-command-pack")
        targets = {row["target"] for row in manifest["files"]}
        for info in gen.PLATFORM_REGISTRY.values():
            self.assertIn(f"{info.skills_dir}/se-test/SKILL.md", targets)
        self.assertIn("### Understand", self.readme_path.read_text(encoding="utf-8"))
        self.assertIn(
            "Bundled pack version: `0.1.0`",
            self.help_catalog_path.read_text(encoding="utf-8"),
        )
        generated = self.claude_generated_root / "se-test" / "SKILL.md"
        self.assertTrue(generated.is_file())
        metadata, body = gen.parse_frontmatter(
            generated.read_text(encoding="utf-8"), "generated fixture"
        )
        self.assertEqual(metadata["model"], "sonnet")
        self.assertEqual(metadata["effort"], "medium")
        _, canonical_body = gen.parse_frontmatter(
            self.write_skill().read_text(encoding="utf-8"), "canonical fixture"
        )
        self.assertEqual(body, canonical_body)

    def test_claude_translation_fails_closed(self) -> None:
        canonical = {"name": "se-test", "description": "Use when testing."}
        with self.assertRaisesRegex(gen.GenerationError, "unknown invocation"):
            gen.claude_frontmatter(
                canonical,
                gen.RuntimeProfile("sometimes", "inline", "balanced", "medium"),
            )
        with self.assertRaisesRegex(gen.GenerationError, "unknown context"):
            gen.claude_frontmatter(
                canonical,
                gen.RuntimeProfile("both", "detached", "balanced", "medium"),
            )
        with self.assertRaisesRegex(gen.GenerationError, "unknown portable model"):
            gen.claude_frontmatter(
                canonical,
                gen.RuntimeProfile("both", "inline", "mystery", "medium"),
            )
        with self.assertRaisesRegex(gen.GenerationError, "unsupported effort"):
            gen.claude_frontmatter(
                canonical,
                gen.RuntimeProfile("both", "inline", "balanced", "maximum"),
            )
        with (
            mock.patch.dict(gen.CLAUDE_MODEL_MAP, {"balanced": "unknown"}),
            self.assertRaisesRegex(gen.GenerationError, "unsupported model alias"),
        ):
            gen.claude_frontmatter(
                canonical,
                gen.RuntimeProfile("both", "inline", "balanced", "medium"),
            )

    def test_catalog_groups_skills_and_escapes_pipes(self) -> None:
        first = VALID_SKILL.format(name="se-test").replace(
            "end to end.", "end | to end."
        )
        self.write_skill(text=first)
        self.write_skill(name="se-second")
        with (
            mock.patch.object(
                gen,
                "SKILLS",
                (
                    gen.SkillInfo(name="se-test", family="understand"),
                    gen.SkillInfo(name="se-second", family="decide"),
                ),
            ),
            mock.patch.object(gen, "SKILL_NAMES", ("se-test", "se-second")),
        ):
            rendered = gen.regenerated_readme_text()
        self.assertLess(rendered.index("### Understand"), rendered.index("### Decide"))
        self.assertIn("end \\| to end.", rendered)

    def test_help_catalog_groups_all_families_and_escapes_pipes(self) -> None:
        first = VALID_SKILL.format(name="se-test").replace(
            "end to end.", "end | to end."
        )
        self.write_skill(text=first)
        rendered = gen.regenerated_help_catalog_text()
        self.assertLess(rendered.index("## Understand"), rendered.index("## Decide"))
        self.assertIn("Understand fixture outcomes.", rendered)
        self.assertIn("No bundled skills in this release.", rendered)
        self.assertIn("end \\| to end.", rendered)

    def test_catalog_requires_exactly_one_marker_pair(self) -> None:
        self.write_skill()
        for text in (
            "# Missing markers\n",
            "<!-- SE_SKILL_CATALOG:START -->\n"
            "<!-- SE_SKILL_CATALOG:START -->\n"
            "<!-- SE_SKILL_CATALOG:END -->\n",
        ):
            self.readme_path.write_text(text, encoding="utf-8")
            with self.assertRaises(gen.GenerationError) as caught:
                gen.regenerated_readme_text()
            self.assertIn("catalog markers", str(caught.exception))

    def test_missing_readme_fails_cleanly_before_manifest_write(self) -> None:
        self.write_skill()
        self.readme_path.unlink()
        self.assertEqual(gen.main([]), 1)
        self.assertFalse(self.manifest_path.exists())

    def test_validation_failure_writes_neither_surface(self) -> None:
        self.write_skill()
        self.readme_path.write_text("# Missing markers\n", encoding="utf-8")
        self.assertEqual(gen.main([]), 1)
        self.assertFalse(self.manifest_path.exists())

    def test_readme_write_failure_keeps_manifest_unchanged(self) -> None:
        self.write_skill()
        committed_readme = self.readme_path.read_text(encoding="utf-8")
        calls: list[Path] = []

        def fail_readme(path: Path, content: str) -> None:
            calls.append(path)
            raise SystemExit(f"error: cannot write {path}: read-only fixture")

        with mock.patch.object(gen, "atomic_write_text", side_effect=fail_readme):
            self.assertEqual(gen.main([]), 1)
        self.assertEqual(calls, [self.readme_path])
        self.assertEqual(
            self.readme_path.read_text(encoding="utf-8"), committed_readme
        )
        self.assertFalse(self.manifest_path.exists())

    def test_manifest_write_failure_rolls_back_readme(self) -> None:
        self.write_skill()
        committed_readme = self.readme_path.read_text(encoding="utf-8")
        atomic_write_text = gen.atomic_write_text

        def fail_manifest(path: Path, content: str) -> None:
            if path == self.manifest_path:
                raise SystemExit(f"error: cannot write {path}: read-only fixture")
            atomic_write_text(path, content)

        with mock.patch.object(gen, "atomic_write_text", side_effect=fail_manifest):
            self.assertEqual(gen.main([]), 1)
        self.assertEqual(
            self.readme_path.read_text(encoding="utf-8"), committed_readme
        )
        self.assertFalse(self.help_catalog_path.exists())
        self.assertFalse(self.claude_generated_root.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_help_catalog_write_failure_rolls_back_readme(self) -> None:
        self.write_skill()
        committed_readme = self.readme_path.read_text(encoding="utf-8")
        atomic_write_text = gen.atomic_write_text

        def fail_help_catalog(path: Path, content: str) -> None:
            if path == self.help_catalog_path:
                raise SystemExit(f"error: cannot write {path}: read-only fixture")
            atomic_write_text(path, content)

        with mock.patch.object(
            gen, "atomic_write_text", side_effect=fail_help_catalog
        ):
            self.assertEqual(gen.main([]), 1)
        self.assertEqual(
            self.readme_path.read_text(encoding="utf-8"), committed_readme
        )
        self.assertFalse(self.help_catalog_path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_check_detects_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = []
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_check_detects_readme_catalog_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        committed = self.readme_path.read_text(encoding="utf-8")
        self.readme_path.write_text(
            committed.replace("### Understand", "### Drifted"),
            encoding="utf-8",
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_check_detects_help_catalog_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        committed = self.help_catalog_path.read_text(encoding="utf-8")
        self.help_catalog_path.write_text(
            committed.replace("## Understand", "## Drifted"),
            encoding="utf-8",
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_check_detects_generated_claude_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        generated = self.claude_generated_root / "se-test" / "SKILL.md"
        generated.write_text(
            generated.read_text(encoding="utf-8") + "drift\n",
            encoding="utf-8",
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_generate_removes_unexpected_claude_file(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        unexpected = self.claude_generated_root / "retired" / "SKILL.md"
        unexpected.parent.mkdir(parents=True)
        unexpected.write_text("retired\n", encoding="utf-8")
        self.assertEqual(gen.main(["--check"]), 1)
        self.assertEqual(gen.main([]), 0)
        self.assertFalse(unexpected.exists())

    def write_agent(self, name: str = "se-agent", text: str | None = None) -> Path:
        self.agents_root.mkdir(parents=True, exist_ok=True)
        agent_md = self.agents_root / f"{name}.md"
        agent_md.write_text(
            text
            if text is not None
            else (
                f"---\nname: {name}\n"
                "description: Fixture agent for the generator.\n---\n\n"
                f"# {name}\n\nBody.\n"
            ),
            encoding="utf-8",
        )
        return agent_md

    def test_generate_writes_agent_overlays_and_rows(self) -> None:
        self.write_skill()
        self.write_agent()
        self.assertEqual(gen.main([]), 0)
        self.assertTrue(
            (self.generated_agents_root / "claude" / "se-agent.md").is_file()
        )
        self.assertTrue(
            (self.generated_agents_root / "codex" / "se-agent.toml").is_file()
        )
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        agent_rows = [r for r in manifest["files"] if r["kind"] == "agent"]
        self.assertEqual(
            {r["platform"] for r in agent_rows}, {"claude", "codex"}
        )

    def test_check_detects_agent_drift(self) -> None:
        self.write_skill()
        self.write_agent()
        self.assertEqual(gen.main([]), 0)
        overlay = self.generated_agents_root / "codex" / "se-agent.toml"
        overlay.write_text(
            overlay.read_text(encoding="utf-8") + "\nextra = 1\n",
            encoding="utf-8",
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_generate_removes_unexpected_agent_file(self) -> None:
        self.write_skill()
        self.write_agent()
        self.assertEqual(gen.main([]), 0)
        unexpected = self.generated_agents_root / "codex" / "retired.toml"
        unexpected.write_text('name = "retired"\n', encoding="utf-8")
        self.assertEqual(gen.main(["--check"]), 1)
        self.assertEqual(gen.main([]), 0)
        self.assertFalse(unexpected.exists())

    def test_agent_with_banned_phrase_is_rejected(self) -> None:
        self.write_skill()
        self.write_agent(
            text=(
                "---\nname: se-agent\n"
                "description: Fixture agent for the generator.\n---\n\n"
                "# se-agent\n\nAsk Claude to help.\n"
            )
        )
        with self.assertRaises(gen.GenerationError) as caught:
            gen.validate_agents()
        self.assertIn("framework-neutrality", str(caught.exception))

    def test_header_and_static_rows_preserved(self) -> None:
        self.write_skill()
        self.manifest_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "name": "se-ai-command-pack",
                    "version": "3.2.1",
                    "license": "MIT",
                    "description": "Custom description.",
                    "files": [
                        {
                            "platform": "claude",
                            "kind": "script",
                            "scope": "user",
                            "source": "scripts/se-ai-command-pack-helper.py",
                            "target": ".claude/helper.py",
                            "anchor": ".claude",
                            "install": "if-anchor-exists",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.assertEqual(gen.main([]), 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "3.2.1")
        self.assertEqual(manifest["description"], "Custom description.")
        self.assertEqual(
            manifest["files"][0]["source"],
            "scripts/se-ai-command-pack-helper.py",
        )
        derived = [row for row in manifest["files"] if gen.is_derived_row(row)]
        self.assertGreater(len(derived), 0)

    def test_unknown_header_field_rejected(self) -> None:
        self.write_skill()
        self.manifest_path.write_text(
            json.dumps({"schemaVersion": 1, "requiresTrellis": True, "files": []})
            + "\n",
            encoding="utf-8",
        )
        with self.assertRaises(gen.GenerationError) as caught:
            gen.regenerated_manifest_text()
        self.assertIn("unknown header fields", str(caught.exception))

    def test_generation_error_exits_nonzero(self) -> None:
        # No skill dir written: validate_skills fails inside main.
        self.assertEqual(gen.main([]), 1)


if __name__ == "__main__":
    unittest.main()
