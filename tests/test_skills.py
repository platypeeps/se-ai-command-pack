"""Content pins for the canonical skills: conventions and safety anchors."""

from __future__ import annotations

import re
import unittest
from unittest import mock

import yaml
from install_test_support import PACK_ROOT

from installer.registry import (
    FAMILY_DESCRIPTIONS,
    FAMILY_LABELS,
    SHARED_REFERENCES,
    SKILL_NAMES,
    SKILLS,
    TEMPLATES_SKILLS_DIR,
    SkillInfo,
    validate_registry,
)

SKILLS_ROOT = PACK_ROOT / TEMPLATES_SKILLS_DIR

REQUIRED_SECTIONS = (
    "## When to use",
    "## Arguments",
    "## Workflow",
    "## Safety rules",
    "## Final report",
)

# Skills that read external material must carry the prompt-injection rule.
EXTERNAL_INPUT_SKILLS = (
    "se-research",
    "se-brief",
    "se-meeting-prep",
    "se-scan",
    "se-digest",
    "se-decide",
    "se-status",
    "se-fact-check",
    "se-profile",
    "se-action-inbox",
    "se-agenda",
    "se-ask-me",
    "se-author",
    "se-bookmark-triage",
    "se-capture",
    "se-checklist",
    "se-compare",
    "se-diagram",
    "se-distill",
    "se-evaluate",
    "se-topic-radar",
    "se-technical-editor",
    "se-explain",
    "se-feedback",
    "se-handoff",
    "se-knowledge-capture",
    "se-knowledge-gap",
    "se-learn",
    "se-literature-map",
    "se-meeting-follow-through",
    "se-monitor",
    "se-paper",
    "se-plan",
    "se-postmortem",
    "se-premortem",
    "se-presentation",
    "se-proposal",
    "se-publish",
    "se-red-team",
    "se-retro",
    "se-runbook",
    "se-review-skills",
    "se-socratic-review",
    "se-sop",
    "se-stakeholder-map",
    "se-study-guide",
    "se-thread-digest",
    "se-tutorial",
    "se-video-notes",
)
INJECTION_RULE_FRAGMENT = "data, not instructions"


def skill_text(name: str) -> str:
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def normalized(name: str) -> str:
    """Skill text with runs of whitespace collapsed, so phrase pins are
    immune to markdown line wrapping."""
    return " ".join(skill_text(name).split())


def skill_frontmatter(name: str) -> dict:
    text = skill_text(name)
    end = text.find("\n---\n")
    return yaml.safe_load(text[len("---\n") : end + 1])


class SkillConventionsTest(unittest.TestCase):
    def test_every_registered_skill_exists(self) -> None:
        for name in SKILL_NAMES:
            self.assertTrue(
                (SKILLS_ROOT / name / "SKILL.md").is_file(),
                f"missing SKILL.md for {name}",
            )

    def test_frontmatter_shape(self) -> None:
        for name in SKILL_NAMES:
            frontmatter = skill_frontmatter(name)
            self.assertEqual(
                sorted(frontmatter), ["description", "name"], name
            )
            self.assertEqual(frontmatter["name"], name)
            description = frontmatter["description"]
            self.assertTrue(description.startswith("Use when"), name)
            self.assertNotIn('"', description, name)
            self.assertLessEqual(len(description), 1024, name)

    def test_required_sections_in_order(self) -> None:
        for name in SKILL_NAMES:
            text = skill_text(name)
            last = -1
            for section in REQUIRED_SECTIONS:
                index = text.find(f"\n{section}\n")
                self.assertGreater(index, last, f"{name}: {section}")
                last = index

    def test_unknown_argument_stop_rule(self) -> None:
        for name in SKILL_NAMES:
            self.assertIn(
                "Unknown argument names are an error",
                skill_text(name),
                name,
            )


class SkillFamilyRegistryTest(unittest.TestCase):
    def test_family_labels_have_stable_outcome_order(self) -> None:
        self.assertEqual(
            list(FAMILY_LABELS.items()),
            [
                ("understand", "Understand"),
                ("decide", "Decide"),
                ("create", "Create"),
                ("coordinate", "Coordinate"),
                ("operate", "Operate"),
                ("improve", "Improve"),
            ],
        )

    def test_family_descriptions_match_family_order(self) -> None:
        self.assertEqual(tuple(FAMILY_DESCRIPTIONS), tuple(FAMILY_LABELS))
        self.assertTrue(all(value.strip() for value in FAMILY_DESCRIPTIONS.values()))

    def test_skill_names_are_derived_without_reordering(self) -> None:
        self.assertEqual(SKILL_NAMES, tuple(skill.name for skill in SKILLS))
        self.assertEqual(
            SKILL_NAMES,
            (
                "se-research",
                "se-brief",
                "se-meeting-prep",
                "se-scan",
                "se-digest",
                "se-decide",
                "se-status",
                "se-fact-check",
                "se-help",
                "se-profile",
                "se-action-inbox",
                "se-agenda",
                "se-ask-me",
                "se-author",
                "se-bookmark-triage",
                "se-capture",
                "se-checklist",
                "se-compare",
                "se-diagram",
                "se-distill",
                "se-evaluate",
                "se-topic-radar",
                "se-technical-editor",
                "se-explain",
                "se-feedback",
                "se-handoff",
                "se-knowledge-capture",
                "se-knowledge-gap",
                "se-learn",
                "se-literature-map",
                "se-meeting-follow-through",
                "se-monitor",
                "se-paper",
                "se-plan",
                "se-postmortem",
                "se-premortem",
                "se-presentation",
                "se-proposal",
                "se-publish",
                "se-red-team",
                "se-retro",
                "se-runbook",
                "se-review-skills",
                "se-socratic-review",
                "se-sop",
                "se-stakeholder-map",
                "se-study-guide",
                "se-thread-digest",
                "se-tutorial",
                "se-video-notes",
            ),
        )
        self.assertEqual(
            {skill.name: skill.family for skill in SKILLS},
            {
                "se-research": "understand",
                "se-brief": "coordinate",
                "se-meeting-prep": "coordinate",
                "se-scan": "understand",
                "se-digest": "understand",
                "se-decide": "decide",
                "se-status": "coordinate",
                "se-fact-check": "understand",
                "se-help": "operate",
                "se-profile": "operate",
                "se-action-inbox": "coordinate",
                "se-agenda": "coordinate",
                "se-ask-me": "understand",
                "se-author": "create",
                "se-bookmark-triage": "operate",
                "se-capture": "operate",
                "se-checklist": "operate",
                "se-compare": "understand",
                "se-diagram": "create",
                "se-distill": "understand",
                "se-evaluate": "improve",
                "se-topic-radar": "create",
                "se-technical-editor": "improve",
                "se-explain": "understand",
                "se-feedback": "improve",
                "se-handoff": "coordinate",
                "se-knowledge-capture": "operate",
                "se-knowledge-gap": "understand",
                "se-learn": "understand",
                "se-literature-map": "understand",
                "se-meeting-follow-through": "coordinate",
                "se-monitor": "understand",
                "se-paper": "create",
                "se-plan": "decide",
                "se-postmortem": "improve",
                "se-premortem": "improve",
                "se-presentation": "create",
                "se-proposal": "create",
                "se-publish": "create",
                "se-red-team": "improve",
                "se-retro": "improve",
                "se-runbook": "operate",
                "se-review-skills": "improve",
                "se-socratic-review": "understand",
                "se-sop": "operate",
                "se-stakeholder-map": "coordinate",
                "se-study-guide": "understand",
                "se-thread-digest": "coordinate",
                "se-tutorial": "create",
                "se-video-notes": "understand",
            },
        )

    def assert_invalid_skills(
        self, skills: tuple[SkillInfo, ...], fragment: str
    ) -> None:
        names = tuple(skill.name for skill in skills)
        with (
            mock.patch("installer.registry.SKILLS", skills),
            mock.patch("installer.registry.SKILL_NAMES", names),
            mock.patch("installer.registry.SHARED_REFERENCES", {}),
            self.assertRaises(RuntimeError) as caught,
        ):
            validate_registry()
        self.assertIn(fragment, str(caught.exception))

    def test_registry_rejects_unknown_family(self) -> None:
        self.assert_invalid_skills(
            (SkillInfo("se-test", "unknown"),), "unknown family"
        )

    def test_registry_rejects_empty_name_and_family(self) -> None:
        self.assert_invalid_skills((SkillInfo("", "understand"),), "empty name")
        self.assert_invalid_skills((SkillInfo("se-test", ""),), "empty family")

    def test_registry_rejects_duplicate_skill_membership(self) -> None:
        self.assert_invalid_skills(
            (
                SkillInfo("se-test", "understand"),
                SkillInfo("se-test", "decide"),
            ),
            "duplicate skill name",
        )

    def test_registry_preserves_prefix_validation(self) -> None:
        self.assert_invalid_skills(
            (SkillInfo("test", "understand"),), "missing se- prefix"
        )


class SkillSafetyPinsTest(unittest.TestCase):
    def test_external_input_skills_carry_injection_rule(self) -> None:
        for name in EXTERNAL_INPUT_SKILLS:
            self.assertIn(INJECTION_RULE_FRAGMENT, normalized(name), name)

    def test_shared_reference_consumers_cite_registered_reference(self) -> None:
        for source, consumers in SHARED_REFERENCES.items():
            self.assertTrue(source.startswith("_shared/references/"), source)
            basename = source.rsplit("/", 1)[-1]
            for name in consumers:
                self.assertIn(
                    f"references/{basename}", skill_text(name), name
                )

    def test_research_cites_verification_protocol(self) -> None:
        self.assertIn(
            "references/verification-protocol.md", skill_text("se-research")
        )

    def test_brief_is_read_only(self) -> None:
        self.assertIn("read-only", normalized("se-brief"))

    def test_decide_preserves_uncertainty_and_never_acts(self) -> None:
        text = normalized("se-decide").lower()
        self.assertIn("read-only", text)
        self.assertIn("unknown remains unknown", text)
        self.assertIn("do not invent weights, scores, or numeric precision", text)
        self.assertIn("strongest counterargument", text)
        self.assertIn("conditions would change the recommendation", text)

    def test_decide_has_explicit_sibling_boundaries(self) -> None:
        text = normalized("se-decide")
        for sibling in (
            "se-scan",
            "se-research",
            "se-digest",
            "se-compare",
            "se-plan",
        ):
            self.assertIn(f"`{sibling}`", text)

    def test_decide_final_report_contract(self) -> None:
        text = skill_text("se-decide")
        for field in (
            "**Decision**",
            "**Option comparison**",
            "**Tradeoffs**",
            "**Confidence**",
            "**Reversibility**",
            "**Missing evidence**",
            "**Next action**",
        ):
            self.assertIn(field, text)

    def test_status_preserves_objective_evidence_and_authority(self) -> None:
        text = normalized("se-status").lower()
        self.assertIn("read-only", text)
        self.assertIn("activity is not an outcome", text)
        self.assertIn("no-material-change", text)
        self.assertIn("stale, inaccessible, or contradictory", text)
        self.assertIn("never invent an owner, date", text)

    def test_status_has_explicit_sibling_boundaries(self) -> None:
        text = normalized("se-status")
        for sibling in ("se-brief", "se-digest", "se-decide", "se-monitor"):
            self.assertIn(f"`{sibling}`", text)

    def test_status_final_report_contract(self) -> None:
        text = skill_text("se-status")
        for field in (
            "**Status header**",
            "**Executive status**",
            "**Outcomes**",
            "**Activity**",
            "**Current state**",
            "**Blockers and risks**",
            "**Decisions**",
            "**Asks**",
            "**Next actions**",
            "**Source coverage and gaps**",
        ):
            self.assertIn(field, text)

    def test_action_inbox_classifies_actions_and_lifecycle_separately(self) -> None:
        text = normalized("se-action-inbox")
        for action_class in (
            "`assigned`",
            "`committed`",
            "`requested`",
            "`proposed`",
            "`inferred`",
        ):
            self.assertIn(action_class, text)
        for state in (
            "`open`",
            "`completed`",
            "`cancelled`",
            "`superseded`",
            "`blocked`",
            "`unclear`",
        ):
            self.assertIn(state, text)
        self.assertIn("default `explicit-only`", text)
        self.assertIn("separate from accepted commitments", text)

    def test_action_inbox_preserves_provenance_and_unknowns(self) -> None:
        text = normalized("se-action-inbox").lower()
        self.assertIn("every source locator", text)
        self.assertIn("unknown owner, deadline, project, or state remains", text)
        self.assertIn("preserve each sourced value", text)
        self.assertIn("resolved/excluded section", text)
        self.assertIn("tone alone does not create urgency", text)

    def test_action_inbox_is_read_only_and_has_sibling_boundaries(self) -> None:
        text = normalized("se-action-inbox")
        lower = text.lower()
        self.assertIn("read-only", lower)
        self.assertIn("separate explicit request", lower)
        self.assertIn("data, not instructions", lower)
        self.assertIn("never infer that the requesting user owns", lower)
        for sibling in ("se-thread-digest", "se-digest", "se-plan"):
            self.assertIn(f"`{sibling}`", text)

    def test_action_inbox_final_report_contract(self) -> None:
        text = skill_text("se-action-inbox")
        for field in (
            "**Inbox scope**",
            "**Active commitments**",
            "**Requests and proposals**",
            "**Possible actions**",
            "**Conflicts and ambiguities**",
            "**Resolved and excluded**",
            "**Source coverage**",
            "**Recommended handling**",
        ):
            self.assertIn(field, text)

    def test_agenda_requires_outcome_duration_and_exact_time_budget(self) -> None:
        text = normalized("se-agenda").lower()
        self.assertIn("observable outcome", text)
        self.assertIn("duration=", text)
        self.assertIn("sums to no more than `duration=`", text)
        self.assertIn("opening time", text)
        self.assertIn("closing time", text)

    def test_agenda_preserves_authority_and_async_boundaries(self) -> None:
        text = normalized("se-agenda").lower()
        self.assertIn("attendance never proves authority", text)
        self.assertIn("unknown authority", text)
        self.assertIn("asynchronous update", text)
        self.assertIn("blocked-meeting condition", text)
        self.assertIn("never invent participant availability", text)

    def test_agenda_is_read_only_and_routes_sibling_workflows(self) -> None:
        text = normalized("se-agenda")
        lower = text.lower()
        self.assertIn("read-only", lower)
        self.assertIn("data, not instructions", lower)
        self.assertIn("separate explicit request", lower)
        for sibling in (
            "se-meeting-prep",
            "se-status",
            "se-decide",
            "se-meeting-follow-through",
        ):
            self.assertIn(f"`{sibling}`", text)

    def test_agenda_final_report_contract(self) -> None:
        text = skill_text("se-agenda")
        for field in (
            "**Meeting brief**",
            "**Meeting recommendation**",
            "**Preconditions and pre-read**",
            "**Timeboxed agenda**",
            "**Decision and role rules**",
            "**Parking lot and stop conditions**",
            "**Close and handoff**",
            "**Facilitator notes**",
        ):
            self.assertIn(field, text)

    def test_fact_check_uses_exact_verdict_vocabulary(self) -> None:
        text = skill_text("se-fact-check")
        verdicts = (
            "**supported**",
            "**partially supported**",
            "**unverified**",
            "**contradicted**",
            "**outdated**",
        )
        for verdict in verdicts:
            self.assertIn(verdict, text)
        self.assertIn("Assign exactly one verdict", text)

    def test_fact_check_is_claim_led_and_read_only(self) -> None:
        text = normalized("se-fact-check").lower()
        self.assertIn("inventory", text)
        self.assertIn("before verification begins", text)
        self.assertIn("read-only", text)
        self.assertIn("data, not instructions", text)
        self.assertIn("smallest corrected wording", text)
        self.assertIn("never edit or replace", text)

    def test_fact_check_has_explicit_sibling_boundaries(self) -> None:
        text = normalized("se-fact-check")
        for sibling in ("se-research", "se-digest"):
            self.assertIn(f"`{sibling}`", text)

    def test_fact_check_final_report_contract(self) -> None:
        text = skill_text("se-fact-check")
        for field in (
            "**Audit scope**",
            "**Verdict summary**",
            "**Claim ledger**",
            "**Minimal corrections**",
            "**Non-fact-checkable items**",
            "**Evidence gaps and conflicts**",
            "**Methodology**",
        ):
            self.assertIn(field, text)

    def test_meeting_prep_excludes_sensitive_data(self) -> None:
        text = normalized("se-meeting-prep")
        self.assertIn("sensitive personal data", text)
        self.assertIn("stop and ask", text)

    def test_help_modes_and_shared_response_envelope(self) -> None:
        text = skill_text("se-help")
        normalized_text = normalized("se-help")
        for mode in ("list", "explain", "compare", "recommend", "examples", "tour"):
            self.assertIn(mode, normalized_text)
        fields = (
            "**Pack and availability**",
            "**Answer**",
            "**Why it fits**",
            "**Required context**",
            "**Expected output**",
            "**Side effects and boundaries**",
            "**Related skills**",
            "**Next invocation**",
        )
        positions = [text.index(field) for field in fields]
        self.assertEqual(positions, sorted(positions))

    def test_help_preserves_availability_and_version_boundaries(self) -> None:
        text = normalized("se-help").lower()
        for label in (
            "available now",
            "included in the installed pack but not discoverable now",
            "source/package-local only",
            "external",
            "unknown",
        ):
            self.assertIn(label, text)
        self.assertIn("bundled catalog version", text)
        self.assertIn("installed pack version", text)
        self.assertIn("python3 install.py status --user", text)
        self.assertIn("do not guess", text)

    def test_help_routes_without_execution(self) -> None:
        text = normalized("se-help").lower()
        self.assertIn("read-only", text)
        self.assertIn("smallest-fit", text)
        self.assertIn("at most one clarifying question", text)
        self.assertIn("at most three skills", text)
        self.assertIn("separate explicit request", text)
        self.assertIn("never execute", text)
        self.assertIn("platform-native invocation", text)
        self.assertNotIn("/sd:", text)

    def test_help_references_and_examples_use_registered_skills(self) -> None:
        text = skill_text("se-help")
        self.assertIn("references/skill-catalog.md", text)
        self.assertIn("references/examples.md", text)
        examples = (
            SKILLS_ROOT / "se-help" / "references" / "examples.md"
        ).read_text(encoding="utf-8")
        named = set(re.findall(r"\bse-[a-z0-9-]+\b", examples))
        self.assertTrue(named)
        self.assertEqual(named - set(SKILL_NAMES), set())

    def test_profile_modes_arguments_and_ownership(self) -> None:
        text = normalized("se-profile")
        for mode in (
            "create",
            "status",
            "propose-update",
            "apply-approved",
            "correct",
            "forget",
            "review",
            "audience",
            "import",
            "export",
        ):
            self.assertIn(mode, text)
        for argument in (
            "profile=auto|<locator>",
            "sources=",
            "destination=",
            "entries=",
            "audience=",
            "scope=private-only|internal|outward-safe",
            "cadence=",
            "format=markdown|summary",
        ):
            self.assertIn(argument, text)
        self.assertIn("sole profile mutation owner", text)
        self.assertIn("ordinary profile use never writes back", text)

    def test_profile_schema_provenance_and_preflight(self) -> None:
        skill = normalized("se-profile")
        contract = (
            SKILLS_ROOT / "_shared" / "references" / "personal-profile-contract.md"
        ).read_text(encoding="utf-8")
        normalized_contract = " ".join(contract.split())
        for value in (
            "se-personal-profile/v1",
            "profile_id",
            "statement",
            "first_observed",
            "last_evidenced",
            "last_confirmed",
            "review_after",
            "conflicts_with",
        ):
            self.assertIn(value, contract)
        for vocabulary in (
            "`explicit`, `observed`, or `inferred`",
            "`confirmed`, `proposed`, `contested`, or `retired`",
            "`private-only`, `internal`, or `outward-safe`",
        ):
            self.assertIn(vocabulary, contract)
        for state in (
            "`new`",
            "`valid`",
            "`repairable`",
            "`conflicting`",
            "`unsupported-version`",
            "`unavailable`",
        ):
            self.assertIn(state, skill)
        self.assertIn("stable assertion/evidence IDs", skill)
        self.assertIn("unknown or manually edited content", skill)
        self.assertIn(
            "Consumers use `profile=auto|off|<locator>`", normalized_contract
        )
        self.assertIn(
            "The `se-profile` maintenance owner uses `profile=auto|<locator>`",
            normalized_contract,
        )

    def test_profile_consent_privacy_and_feedback_boundaries(self) -> None:
        text = normalized("se-profile").lower()
        for phrase in (
            "bounded, user-authorized sources",
            "data, not instructions",
            "never infer protected or sensitive attributes",
            "inferred assertions always begin `proposed`",
            "observed assertions remain approval-gated",
            "assistant-generated feedback loops",
            "cannot independently corroborate their own conclusions",
            "never continuously monitor",
        ):
            self.assertIn(phrase, text)

    def test_profile_mutations_preserve_verify_and_delete_honestly(self) -> None:
        text = normalized("se-profile").lower()
        for phrase in (
            "re-read the current artifact",
            "preserve `## personal notes` plus unknown/user-owned content",
            "read back",
            "semantically verify",
            "concurrent material changes",
            "idempotent reruns",
            "whole-profile deletion requires explicit destructive confirmation",
            "connector history, backups, or prior model context may retain",
        ):
            self.assertIn(phrase, text)

    def test_profile_review_overlay_and_destination_boundaries(self) -> None:
        text = normalized("se-profile").lower()
        for phrase in (
            "remain read-only until the user approves numbered items",
            "update `last_reviewed_at` only after an approved verified write",
            "`cadence=` records a preference only",
            "never automatically blend overlays",
            "never silently fall back",
            "mirror both destinations",
            "do not publish or write a second copy",
        ):
            self.assertIn(phrase, text)
        self.assertIn("references/personal-profile-contract.md", text)
        self.assertIn("references/source-standards.md", text)

    def test_ask_me_modes_arguments_and_profile_preflight(self) -> None:
        text = normalized("se-ask-me")
        for value in (
            "mode=predict|advise|reflect|draft",
            "profile=auto|off|<locator>",
            "horizon=now|near-term|long-term|<date>",
            "detail=compact|standard",
            "se-personal-profile/v1",
            "Ask at most one focused question",
        ):
            self.assertIn(value, text)

    def test_ask_me_separates_modes_evidence_and_uncertainty(self) -> None:
        text = normalized("se-ask-me").lower()
        for phrase in (
            "prediction asks what evidence suggests is likely",
            "advice asks what best aligns with current goals and values",
            "current explicit context outranks older profile evidence",
            "likely`, `plausible`, or `insufficient evidence",
            "never fabricate a probability",
            "historical patterns are evidence, not destiny",
        ):
            self.assertIn(phrase, text)

    def test_ask_me_preserves_scope_identity_and_authority(self) -> None:
        text = normalized("se-ask-me").lower()
        for phrase in (
            "read-only",
            "data, not instructions",
            "outward drafts use only confirmed `outward-safe` assertions",
            "never blend multiple overlays automatically",
            "ordinary consumption never writes back",
            "a profile is not proof or permission to impersonate",
            "do not send, publish, schedule, purchase, decide, commit",
        ):
            self.assertIn(phrase, text)
        for sibling in ("se-profile", "se-decide"):
            self.assertIn(f"`{sibling}`", skill_text("se-ask-me"))

    def test_ask_me_draft_high_stakes_and_final_report_contract(self) -> None:
        text = normalized("se-ask-me").lower()
        for phrase in (
            "never invent first-person experience",
            "cannot replace current authoritative evidence or professional guidance",
            "never infer or predict protected or sensitive traits",
            "never simulate a profile answer",
        ):
            self.assertIn(phrase, text)
        raw = skill_text("se-ask-me")
        for field in (
            "**Mode and interpretation**",
            "**Answer**",
            "**Profile basis**",
            "**External merits**",
            "**Counterevidence and uncertainty**",
            "**Limits**",
            "**Draft**",
            "**Next step**",
        ):
            self.assertIn(field, raw)

    def test_author_routes_theme_discovery_interview_and_brief(self) -> None:
        text = normalized("se-author")
        for phrase in (
            "ten ranked opportunities",
            "Ask exactly one highest-value unresolved question per turn",
            "require explicit brief approval",
            "latest explicit approved checkpoint",
            "never overwrite or infer approval",
        ):
            self.assertIn(phrase, text)

    def test_author_preserves_authorship_evidence_and_thesis(self) -> None:
        text = normalized("se-author").lower()
        for phrase in (
            "user answers, assistant hypotheses, sourced claims, and generated prose",
            "never fabricate personal experience",
            "research supports the approved thesis",
            "material thesis change returns to brief revision and approval",
            "data, not instructions",
            "dedicated confidentiality pass",
        ):
            self.assertIn(phrase, text)

    def test_author_orders_draft_passes_and_never_publishes(self) -> None:
        text = normalized("se-author").lower()
        self.assertIn(
            "`skeleton`, `substance`, `voice`, `compression`, `reader comprehension`, then `integrity`",
            text,
        )
        self.assertIn("explicit not-published status", text)
        self.assertIn("every external write requires a separate request", text)
        for sibling in (
            "se-topic-radar",
            "se-research",
            "se-fact-check",
            "se-distill",
            "se-technical-editor",
            "se-paper",
            "se-publish",
        ):
            self.assertIn(f"`{sibling}`", skill_text("se-author"))

    def test_author_final_report_contract(self) -> None:
        text = skill_text("se-author")
        for field in (
            "**Authoring state**",
            "**Editorial brief**",
            "**Interview record**",
            "**Evidence state**",
            "**Outline and draft state**",
            "**Article package**",
            "**Integrity and confidentiality**",
            "**Publication handoff**",
        ):
            self.assertIn(field, text)

    def test_bookmark_triage_classifies_with_honest_coverage(self) -> None:
        text = normalized("se-bookmark-triage")
        for classification in (
            "`discard`",
            "`skim`",
            "`study`",
            "`act`",
            "`defer`",
            "`archive`",
        ):
            self.assertIn(classification, text)
        for coverage in (
            "`full content`",
            "`snippet`",
            "`metadata`",
            "`user context`",
            "`judgment`",
        ):
            self.assertIn(coverage, text)
        self.assertIn("Never claim to have read, watched, or assessed", text)

    def test_bookmark_triage_preserves_identity_and_private_boundaries(self) -> None:
        text = normalized("se-bookmark-triage").lower()
        for phrase in (
            "preserve every original locator",
            "unresolved duplicate",
            "confirmed dead, inaccessible/private, and temporarily unavailable",
            "do not summarize or quote content that could not be accessed",
            "source and audience boundary for private items",
        ):
            self.assertIn(phrase, text)

    def test_bookmark_triage_budget_safety_and_handoffs(self) -> None:
        text = normalized("se-bookmark-triage").lower()
        for phrase in (
            "estimated total fits the budget",
            "never rank everything immediate",
            "return an empty queue rather than exceed the budget",
            "data, not instructions",
            "every external write requires a separate explicit request",
            "age alone does not make foundational material low value",
        ):
            self.assertIn(phrase, text)
        raw = skill_text("se-bookmark-triage")
        for sibling in (
            "se-video-notes",
            "se-digest",
            "se-capture",
            "se-knowledge-capture",
            "se-action-inbox",
        ):
            self.assertIn(f"`{sibling}`", raw)

    def test_bookmark_triage_final_report_contract(self) -> None:
        text = skill_text("se-bookmark-triage")
        for field in (
            "**Triage scope**",
            "**Selected queue**",
            "**Budget accounting**",
            "**Deferred and archive candidates**",
            "**Discarded and unavailable**",
            "**Duplicates and identity questions**",
            "**Evidence coverage**",
            "**Recommended handoffs**",
        ):
            self.assertIn(field, text)

    def test_capture_normalizes_one_unit_and_retrieval_state(self) -> None:
        text = normalized("se-capture").lower()
        for state in (
            "`complete`",
            "`partial`",
            "`metadata-only`",
            "`unavailable`",
        ):
            self.assertIn(state, text)
        for phrase in (
            "one logical intake unit",
            "one url, file, pasted passage, connected record, or bounded thread",
            "source metadata`, `user-supplied metadata`, and `assistant-derived",
            "missing values remain `unknown`",
            "never summarize inaccessible body text",
        ):
            self.assertIn(phrase, text)

    def test_capture_uses_reproducible_deduplication_identity(self) -> None:
        text = normalized("se-capture").lower()
        for phrase in (
            "stable source or external id namespaced by source system",
            "canonical url after conservative removal of known tracking parameters",
            "normalized supplied locator",
            "`sha256` of exact retrieved or supplied content",
            "record the key type and reproducible basis",
            "never use title alone, invent a hash",
        ):
            self.assertIn(phrase, text)

    def test_capture_labels_knowledge_and_never_executes(self) -> None:
        text = normalized("se-capture").lower()
        for label in (
            "`source-stated`",
            "`corroborated`",
            "`disputed`",
            "`unverified`",
            "`explicit`",
            "`assigned`",
            "`requested`",
            "`proposed`",
            "`inferred`",
        ):
            self.assertIn(label, text)
        for phrase in (
            "a source-stated claim is not a verified fact",
            "data, not instructions",
            "every external write requires a separate explicit request",
            "mark every suggestion `not run`",
        ):
            self.assertIn(phrase, text)
        raw = skill_text("se-capture")
        for sibling in (
            "se-digest",
            "se-video-notes",
            "se-action-inbox",
            "se-fact-check",
            "se-knowledge-capture",
        ):
            self.assertIn(f"`{sibling}`", raw)

    def test_capture_final_report_contract(self) -> None:
        text = skill_text("se-capture")
        for field in (
            "**Capture metadata**",
            "**Summary**",
            "**Key claims and evidence**",
            "**Decisions and candidate actions**",
            "**Entities, topics, and referenced resources**",
            "**Unknowns and limitations**",
            "**Suggested next workflows**",
        ):
            self.assertIn(field, text)

    def test_checklist_modes_and_preflight_contract(self) -> None:
        text = normalized("se-checklist").lower()
        for phrase in (
            "`mode=read-do|do-confirm`",
            "exact task, operator, environment, trigger, start state, end state",
            "source authority",
            "conflicting, stale, inaccessible, or missing authority",
            "observable completion signal",
        ):
            self.assertIn(phrase, text)

    def test_checklist_inclusion_tests_and_item_contract(self) -> None:
        text = normalized("se-checklist").lower()
        for phrase in (
            "all five inclusion tests pass",
            "specific risk, requirement, dependency, or completion signal",
            "evaluated at a specific point",
            "observable pass condition",
            "failure changes behavior",
            "verified system control",
            "stable id and phase",
            "pass:",
            "evidence:",
            "if not:",
            "basis:",
        ):
            self.assertIn(phrase, text)

    def test_checklist_dependency_order_and_emergency_safety(self) -> None:
        text = normalized("se-checklist").lower()
        for phrase in (
            "order checks by dependency and point of use",
            "must not replace a preventive safety gate",
            "include only validated stop conditions and safety-critical checks",
            "do not invent commands",
            "use explicit `stop` or `escalate`",
        ):
            self.assertIn(phrase, text)

    def test_checklist_final_report_and_workflow_boundaries(self) -> None:
        text = skill_text("se-checklist")
        for field in (
            "**Checklist header**",
            "**Use and non-use**",
            "**Operational checklist**",
            "**Completion signal**",
            "**Source gaps and proposed checks**",
            "**Author notes**",
            "**Review metadata**",
            "**Limits**",
        ):
            self.assertIn(field, text)
        lowered = text.lower()
        for phrase in (
            "read-only",
            "data, not instructions",
            "no certification is claimed",
        ):
            self.assertIn(phrase, lowered)
        for sibling in ("se-runbook", "se-sop", "se-retro"):
            self.assertIn(f"`{sibling}`", text)

    def test_diagram_selects_form_by_relationship(self) -> None:
        text = normalized("se-diagram").lower()
        for form in (
            "`flow` for transformations and decision paths",
            "`sequence` for ordered or concurrent interactions",
            "`architecture` for components, boundaries, and dependencies",
            "`state` for allowed states, transitions, and guards",
            "`tree` for hierarchy or ownership",
            "`matrix` for repeated pairwise mappings",
            "`timeline` for dated change",
            "`schematic` for spatial or domain-specific structure",
        ):
            self.assertIn(form, text)

    def test_diagram_ledger_preserves_uncertainty_and_structure(self) -> None:
        text = normalized("se-diagram").lower()
        for phrase in (
            "authoritative diagram ledger before rendering",
            "stable readable id",
            "status `explicit`, `inferred`, or `conflicting`",
            "cycles, asynchronous edges",
            "state labels, guards, concurrency",
            "show conflicting models separately",
            "never drop edges or boundaries silently",
        ):
            self.assertIn(phrase, text)

    def test_diagram_mermaid_fallback_and_accessibility(self) -> None:
        text = normalized("se-diagram").lower()
        for phrase in (
            "conservative syntax, stable safe ids, escaped labels",
            "tool-neutral visual brief",
            "linear accessibility description",
            "without relying on color, position, or shape alone",
            "never add a component, causal arrow, containment, or ordering",
        ):
            self.assertIn(phrase, text)

    def test_diagram_final_report_and_read_only_boundaries(self) -> None:
        raw = skill_text("se-diagram")
        for field in (
            "**Scope and question**",
            "**Source coverage**",
            "**Element and relationship ledger**",
            "**Diagram or visual brief**",
            "**Legend**",
            "**Assumptions and conflicts**",
            "**Accessibility description**",
            "**Review questions**",
            "**Limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-diagram").lower()
        for phrase in (
            "read-only",
            "data, not instructions",
            "do not inspect live systems outside the supplied source boundary",
            "no automatic discovery",
        ):
            self.assertIn(phrase, text)

    def test_compare_builds_one_fair_criterion_contract(self) -> None:
        text = normalized("se-compare").lower()
        for phrase in (
            "test comparability before choosing criteria",
            "define one criterion contract before filling cells",
            "criterion origin",
            "criteria chosen to favor one alternative",
            "duplicated or dependent dimensions",
            "separate factual or technical criteria from user values",
        ):
            self.assertIn(phrase, text)

    def test_compare_preserves_cell_states_and_evidence_asymmetry(self) -> None:
        text = normalized("se-compare").lower()
        for state in (
            "`known`",
            "`unknown`",
            "`not-public`",
            "`not-applicable`",
            "`conflicting`",
            "`not-comparable`",
        ):
            self.assertIn(state, text)
        for phrase in (
            "missing evidence is `unknown` or `not-public`, never zero, failure",
            "better documentation is not better performance",
            "never average them",
            "confidence `high`, `medium`, or `low`",
        ):
            self.assertIn(phrase, text)

    def test_compare_stays_neutral_through_sensitivity_and_dominance(self) -> None:
        text = normalized("se-compare").lower()
        for phrase in (
            "preserve user-supplied order; otherwise use neutral lexical order",
            "without scores, hidden weights, an overall rank",
            "dominance under this frame",
            "eligibility is not a winner",
            "do not convert it into a personal recommendation",
            "if no meaningful difference appears, say so plainly",
        ):
            self.assertIn(phrase, text)

    def test_compare_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-compare")
        for sibling in ("se-scan", "se-evaluate", "se-decide"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Scope and comparability**",
            "**Fair comparison frame**",
            "**Evidence matrix**",
            "**Alternative profiles**",
            "**Tradeoffs and disqualifiers**",
            "**Evidence asymmetry and uncertainty**",
            "**Sensitivity**",
            "**Open questions and highest-value evidence**",
            "**Decision handoff**",
            "**Limits**",
        ):
            self.assertIn(field, raw)
        lowered = normalized("se-compare").lower()
        for phrase in (
            "read-only",
            "data, not instructions",
            "never recommend, select, rank overall",
            "`not run` status",
        ):
            self.assertIn(phrase, lowered)

    def test_distill_measures_budget_and_rejects_false_precision(self) -> None:
        text = normalized("se-distill").lower()
        for phrase in (
            "choose one size measure",
            "output size / input size",
            "minimum useful artifact",
            "never claim that 80% of semantic or informational value was objectively measured",
            "operational prioritization goal",
        ):
            self.assertIn(phrase, text)

    def test_distill_uses_traceable_importance_map_and_invariants(self) -> None:
        text = normalized("se-distill").lower()
        for phrase in (
            "build a traceable importance map before drafting",
            "stable id",
            "rank items by consequence",
            "non-negotiable invariant set",
            "technical mode also preserves exact code, formulas, notation, units",
            "every non-negotiable item must appear",
        ):
            self.assertIn(phrase, text)

    def test_distill_uses_smallest_safe_escape_and_loss_ledger(self) -> None:
        text = normalized("se-distill").lower()
        for phrase in (
            "return the smallest safe result",
            "smallest relaxation that would fit",
            "do not silently trade correctness for 10%",
            "build the loss ledger",
            "individually name every omitted or compressed point that could change a decision",
            "consult-the-source list",
        ):
            self.assertIn(phrase, text)

    def test_distill_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-distill")
        for sibling in ("se-digest", "se-research", "se-compare"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Scope and measurement**",
            "**Distilled artifact**",
            "**Importance map coverage**",
            "**Conflicts and contested points**",
            "**Loss ledger**",
            "**Target safety**",
            "**Consult the source**",
            "**Limits**",
        ):
            self.assertIn(field, raw)
        lowered = normalized("se-distill").lower()
        for phrase in (
            "read-only",
            "data, not instructions",
            "preserve attribution",
            "do not add external research unless the user separately approves",
        ):
            self.assertIn(phrase, lowered)

    def test_evaluate_audits_rubric_before_applying_it(self) -> None:
        text = normalized("se-evaluate").lower()
        for phrase in (
            "audit every criterion before applying it",
            "criteria that encode the desired answer",
            "double-counted or dependent criteria",
            "protected or sensitive trait proxies",
            "require rubric revision or explicit acceptance",
            "audit bias before applying the rubric",
        ):
            self.assertIn(phrase, text)

    def test_evaluate_maps_evidence_to_distinct_criterion_states(self) -> None:
        text = normalized("se-evaluate").lower()
        for state in (
            "`met`",
            "`partially-met`",
            "`failed`",
            "`missing-evidence`",
            "`not-evaluable`",
            "`not-applicable`",
        ):
            self.assertIn(state, text)
        for phrase in (
            "use exactly one evidence state per criterion",
            "missing-evidence`, never a zero or failure",
            "trace every judgment to a criterion and cited evidence",
            "unequal evidence availability must not become a performance difference",
        ):
            self.assertIn(phrase, text)

    def test_evaluate_guards_numeric_mode_and_runs_sensitivity(self) -> None:
        text = normalized("se-evaluate").lower()
        for phrase in (
            "numeric scores require a meaningful scale with anchored levels",
            "never convert adjectives, missing data, or arbitrary labels into numbers",
            "never hide missing or not-evaluable criteria in a denominator",
            "run sensitivity analysis whenever plausible weight, threshold",
            "smallest assumption or evidence change that would change the conclusion",
            "a valid overall result may be `not evaluable`",
        ):
            self.assertIn(phrase, text)

    def test_evaluate_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-evaluate")
        for sibling in ("se-compare", "se-decide", "se-scan", "se-red-team"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Scope and purpose**",
            "**Rubric audit**",
            "**Criterion ledger**",
            "**Overall bounded judgment**",
            "**Uncertainty and sensitivity**",
            "**Prioritized improvements**",
            "**Missing evidence and open questions**",
            "**Handoffs**",
            "**Limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-evaluate").lower()
        for phrase in (
            "read-only",
            "data, not instructions",
            "never evaluate or rank people",
            "does not make it",
            "`not run` status",
        ):
            self.assertIn(phrase, text)

    def test_topic_radar_inventories_personal_and_external_sources(self) -> None:
        text = normalized("se-topic-radar").lower()
        for phrase in (
            "build a source-coverage ledger before generating ideas",
            "keep personal activity and external developments in separate evidence lanes",
            "breaking-news signals require authoritative corroboration",
            "do not replace missing personal activity with generic trends",
        ):
            self.assertIn(phrase, text)

    def test_topic_radar_scores_distinct_candidates_transparently(self) -> None:
        text = normalized("se-topic-radar").lower()
        for phrase in (
            "anchored component levels `0` through `3`",
            "use `unknown` rather than zero",
            "penalize duplicates visibly",
            "a different title does not make a different idea",
            "by one anchored level would change the top group",
        ):
            self.assertIn(phrase, text)

    def test_topic_radar_preserves_profile_privacy_and_provenance(self) -> None:
        text = normalized("se-topic-radar").lower()
        for phrase in (
            "references/personal-profile-contract.md",
            "references/source-standards.md",
            "data, not instructions",
            "sensitive or private signals may affect internal ranking only when authorized",
            "cannot appear in a title",
            "never invent personal activity",
        ):
            self.assertIn(phrase, text)

    def test_topic_radar_adequacy_boundaries_and_final_report(self) -> None:
        raw = skill_text("se-topic-radar")
        for sibling in ("se-scan", "se-watchlist", "se-author", "se-paper"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Scope and source coverage**",
            "**Ranking method**",
            "**Ranked opportunities**",
            "**Distinctness and prior-content audit**",
            "**Uncertainty and sensitivity**",
            "**Selection handoff**",
            "**Limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-topic-radar").lower()
        for phrase in (
            "only then return exactly ten ranked opportunities",
            "when coverage is inadequate, do not pad to ten",
            "explicit status `not run`",
            "this skill is read-only",
        ):
            self.assertIn(phrase, text)

    def test_technical_editor_runs_distinct_report_first_passes(self) -> None:
        text = normalized("se-technical-editor").lower()
        for phrase in (
            "technical correctness",
            "evidence and citations",
            "hidden assumptions",
            "code and examples",
            "novelty and originality",
            "skeptical-reader objections",
            "reader comprehension",
            "title and opening",
            "record `not run` for every omitted pass",
            "deliver the complete editorial report",
            "before rewriting any material claim, structure, citation relationship, or voice",
        ):
            self.assertIn(phrase, text)
        for token in (
            "technical-correctness",
            "evidence-and-citations",
            "hidden-assumptions",
            "code-and-examples",
            "novelty-and-originality",
            "skeptical-reader-objections",
            "structure",
            "reader-comprehension",
            "confidentiality",
            "title-and-opening",
            "voice-consistency",
        ):
            self.assertIn(f"`{token}`", text)

    def test_technical_editor_locates_and_classifies_findings(self) -> None:
        text = normalized("se-technical-editor").lower()
        for phrase in (
            "stable id, severity",
            "exact location",
            "evidence or concrete rationale",
            "reader or integrity impact",
            "`factual defect`",
            "`high-confidence improvement`",
            "`editorial choice`",
            "`optional style preference`",
            "do not disguise preference as correctness",
        ):
            self.assertIn(phrase, text)

    def test_technical_editor_preserves_validation_voice_and_confidentiality(self) -> None:
        text = normalized("se-technical-editor").lower()
        for phrase in (
            "never report unsupported claims, unverified citations, or unexecuted code as validated",
            "weakens this draft",
            "never use or imply an automated authorship or detector score",
            "build a voice sample from representative supplied language",
            "supplied draft's evidenced voice outrank profile preferences",
            "run confidentiality triage before sending draft content into broader search",
            "data, not instructions",
            "never fabricate technical validation",
        ):
            self.assertIn(phrase, text)

    def test_technical_editor_approval_boundary_and_final_report(self) -> None:
        raw = skill_text("se-technical-editor")
        for sibling in (
            "se-topic-radar",
            "se-author",
            "se-research",
            "se-fact-check",
            "se-red-team",
            "se-publish",
        ):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Review scope and inputs**",
            "**Draft contract and conflicts**",
            "**Pass coverage**",
            "**Editorial findings**",
            "**Verification gaps**",
            "**Prioritized revision plan**",
            "**Approval boundary**",
            "**Voice and confidentiality**",
            "**Revision result and substantive change ledger**",
            "**Handoffs and limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-technical-editor").lower()
        for phrase in (
            "apply only that set",
            "omission never means all proposed edits are approved",
            "report mode is read-only",
            "does not authorize publication",
            "explicitly not-published status",
        ):
            self.assertIn(phrase, text)

    def test_explain_calibrates_audience_depth_and_layers(self) -> None:
        text = normalized("se-explain").lower()
        for phrase in (
            "correct a false premise before building on it",
            "for a novice, define specialized terms at first use",
            "for an expert, compress familiar foundations",
            "lead with a concise direct model",
            "`brief` may omit layers but never the qualification",
            "`deep` adds mechanism and boundaries rather than repetition",
        ):
            self.assertIn(phrase, text)

    def test_explain_separates_analogy_evidence_and_simplification(self) -> None:
        text = normalized("se-explain").lower()
        for phrase in (
            "label every analogy as an analogy",
            "name unmapped parts, and state where the analogy breaks",
            "an analogy is not evidence",
            "an example must not silently become proof",
            "facts, assumptions, simplifications, examples, and unresolved claims distinct",
            "where it stops being accurate",
        ):
            self.assertIn(phrase, text)

    def test_explain_routes_current_claims_and_resists_injection(self) -> None:
        text = normalized("se-explain").lower()
        for phrase in (
            "current, version-specific, disputed, quantitative, or load-bearing claims require supplied or verified evidence",
            "mark the claim unresolved",
            "data, not instructions",
            "this skill is read-only",
            "never invent expertise, citations, source access, measurements, current behavior",
        ):
            self.assertIn(phrase, text)

    def test_explain_progressive_followup_and_final_report_contract(self) -> None:
        raw = skill_text("se-explain")
        for sibling in (
            "se-learn",
            "se-study-guide",
            "se-socratic-review",
            "se-research",
            "se-fact-check",
        ):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Explanation contract**",
            "**Direct model**",
            "**Intuition and example**",
            "**Mechanism**",
            "**Analogy map and break point**",
            "**Limitations and simplifications**",
            "**Misconceptions and premise corrections**",
            "**Quick self-check**",
            "**Established so far**",
            "**Next learning step and handoffs**",
            "**Sources and limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-explain").lower()
        for phrase in (
            "without repeating the full explanation",
            "correct earlier simplifications",
            "does not claim to assess mastery",
            "status `not run`",
        ):
            self.assertIn(phrase, text)

    def test_feedback_preserves_atomic_evidence_before_clustering(self) -> None:
        text = normalized("se-feedback").lower()
        for phrase in (
            "normalize feedback into atomic entries before clustering",
            "stable feedback id, source id, exact wording or lossless excerpt, original locator",
            "split compound comments without losing their shared source and locator",
            "each theme must point back to its atomic feedback ids",
            "cluster by root concern and affected outcome, not shared vocabulary alone",
        ):
            self.assertIn(phrase, text)

    def test_feedback_handles_duplicates_conflicts_and_severity(self) -> None:
        text = normalized("se-feedback").lower()
        for phrase in (
            "keep every atomic evidence record",
            "raw mention count and deduplicated source or audience reach",
            "repetition is a signal of reach, not proof",
            "segment conflicting audience needs rather than averaging them",
            "elevate an isolated safety, security, correctness, legal, or accessibility concern",
            "frequency is one",
        ):
            self.assertIn(phrase, text)

    def test_feedback_uses_explicit_evidence_backed_dispositions(self) -> None:
        text = normalized("se-feedback").lower()
        for disposition in (
            "`accept`",
            "`reject`",
            "`clarify`",
            "`test`",
            "`defer`",
            "`already-addressed`",
        ):
            self.assertIn(disposition, text)
        for phrase in (
            "exactly one provisional disposition",
            "validation action, and condition that would change the disposition",
            "use `already-addressed` only when dated artifact or change evidence shows",
            "use `reject` for an evidenced mismatch or harmful proposal",
        ):
            self.assertIn(phrase, text)

    def test_feedback_read_only_safety_and_final_report_contract(self) -> None:
        raw = skill_text("se-feedback")
        for sibling in ("se-technical-editor", "se-fact-check"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Scope and source coverage**",
            "**Atomic feedback ledger**",
            "**Theme map**",
            "**Contradictions, minority views, and severe exceptions**",
            "**Disposition ledger**",
            "**Unresolved feedback**",
            "**Decision-ready summary**",
            "**Actions and limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-feedback").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "never reply to contributors, resolve review threads, modify the reviewed artifact",
            "never invent sources, comments, locators, authors, roles, dates, audiences",
            "all `not run`",
        ):
            self.assertIn(phrase, text)

    def test_handoff_reconstructs_dated_state_without_inventing_context(self) -> None:
        text = normalized("se-handoff").lower()
        for phrase in (
            "state the as-of cutoff",
            "verified fact, recorded decision, assumption, or unresolved question",
            "current, stale, unavailable, or contradictory",
            "identify the authoritative source only when the evidence establishes one",
            "never invent missing state to make the packet look complete",
        ):
            self.assertIn(phrase, text)

    def test_handoff_preserves_only_load_bearing_operational_detail(self) -> None:
        text = normalized("se-handoff").lower()
        for phrase in (
            "preserve exact identifiers, paths, urls, error strings, versions, commits, task references, and commands",
            "only when they are necessary to continue safely",
            "the first next action must be independently executable",
            "name every prerequisite, stop condition, and required authority",
            "shorter than the source context",
        ):
            self.assertIn(phrase, text)

    def test_handoff_minimizes_sensitive_data_and_never_acts(self) -> None:
        text = normalized("se-handoff").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "omit the value and note the omission",
            "irrelevant private or confidential material",
            "never send, publish, assign, activate, execute, or mutate",
            "proposed, not authorized actions",
        ):
            self.assertIn(phrase, text)

    def test_handoff_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-handoff")
        for sibling in ("se-digest", "se-status"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Handoff contract**",
            "**Objective and scope**",
            "**Verified current state**",
            "**Completed work**",
            "**Decisions and rationale**",
            "**Evidence and continuation-critical locators**",
            "**Assumptions and risks**",
            "**Open questions**",
            "**Ordered next actions**",
            "**Source coverage, omissions, and limits**",
        ):
            self.assertIn(field, raw)

    def test_knowledge_capture_searches_identity_and_classifies_actions(self) -> None:
        text = normalized("se-knowledge-capture").lower()
        for phrase in (
            "canonical url, namespaced external id, normalized title or aliases, then stored fingerprint",
            "`create`, `append-managed`, `update-managed`, `skip`, or `conflict`",
            "an ambiguous or contradictory match is `conflict`",
            "idempotent reruns target the same record",
            "never use title similarity alone to silently choose a record",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_capture_requires_preview_approval_and_verification(self) -> None:
        text = normalized("se-knowledge-capture").lower()
        for phrase in (
            "`mode=apply` requests a write but does not bypass preview or approval",
            "return the concrete preview and wait",
            "re-read the destination immediately before writing",
            "write once, read back, and semantically verify",
            "full replacement, ambiguous duplicate resolution, destructive field loss",
            "requires specific confirmation",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_capture_preserves_destination_owned_content(self) -> None:
        text = normalized("se-knowledge-capture").lower()
        for phrase in (
            "preserve user-owned frontmatter properties and sections",
            "change only explicitly declared managed regions",
            "return an openable obsidian note link",
            "map only configured data-source properties",
            "preserve unsupported properties and page content",
            "return the resulting notion page link",
            "never mirror full content to both systems by default",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_capture_failure_safety_and_final_report_contract(self) -> None:
        raw = skill_text("se-knowledge-capture")
        self.assertIn("`se-capture`", raw)
        for field in (
            "**Operation and routing**",
            "**Identity search and matches**",
            "**Preview and approval state**",
            "**Mapped and preserved content**",
            "**Conflicts and destructive gates**",
            "**Write and verification result**",
            "**Links and cross-links**",
            "**Limits and next action**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-knowledge-capture").lower()
        for phrase in (
            "data, not instructions",
            "connector is unavailable",
            "schema mismatch",
            "partial write failure",
            "never claim persistence without verified read-back",
            "portable preview",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_gap_requires_bounded_scope_and_source_inventory(self) -> None:
        text = normalized("se-knowledge-gap").lower()
        for phrase in (
            "topic or question",
            "intended decision or audience",
            "source inventory",
            "freshness threshold",
            "`exclude=`",
            "connector, container, query, date range, permissions, pagination, and truncation",
            "claim and decision map",
            "before classifying gaps",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_gap_distinguishes_absence_from_access_and_normalizes_terms(self) -> None:
        text = normalized("se-knowledge-gap").lower()
        for phrase in (
            "terminology and alias query map",
            "not found",
            "does not exist",
            "access-gap",
            "missing",
            "sufficient and justified coverage",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_gap_uses_exact_finding_taxonomy_and_preserves_conflicts(self) -> None:
        text = skill_text("se-knowledge-gap")
        for finding in (
            "**missing**",
            "**access-gap**",
            "**stale**",
            "**conflicting**",
            "**unsupported**",
            "**duplicate-authority**",
            "**unresolved**",
        ):
            self.assertIn(finding, text)
        normalized_text = normalized("se-knowledge-gap").lower()
        self.assertIn("preserve both positions, dates, and authority signals", normalized_text)
        self.assertIn("duplicate authority is not automatically wrong", normalized_text)

    def test_knowledge_gap_prioritizes_qualitatively_without_fake_precision(self) -> None:
        text = normalized("se-knowledge-gap").lower()
        for phrase in (
            "decision impact",
            "urgency",
            "blocking or dependency effect",
            "confidence",
            "closure effort",
            "qualitative",
            "never invent numeric precision",
        ):
            self.assertIn(phrase, text)

    def test_knowledge_gap_safety_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-knowledge-gap")
        for sibling in ("se-fact-check", "se-research", "se-monitor"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Audit contract**",
            "**Coverage and access ledger**",
            "**Terminology and query map**",
            "**Claim and decision map**",
            "**Prioritized findings**",
            "**Closure plan**",
            "**Follow-up workflow status**",
            "**Limits and unresolved coverage**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-knowledge-gap").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "minimize sensitive",
            "preserve audience and source boundaries",
            "not run",
            "unavailable",
            "never rewrite source material",
            "never expand into unlimited research",
        ):
            self.assertIn(phrase, text)

    def test_learn_defines_mastery_and_diagnoses_baseline_evidence(self) -> None:
        text = normalized("se-learn").lower()
        for phrase in (
            "capability goal",
            "observable mastery signals",
            "self-reported familiarity",
            "demonstrated ability",
            "representative explanation, application, or transfer task",
            "diagnostic opt-out",
            "weaker baseline",
            "never infer ability from title, role, credentials, or confidence",
        ):
            self.assertIn(phrase, text)

    def test_learn_sequences_complete_stages_and_spaced_review(self) -> None:
        text = normalized("se-learn").lower()
        for phrase in (
            "dependency map",
            "measurable learning outcome",
            "worked example",
            "retrieval practice",
            "application exercise",
            "transfer or project task",
            "checkpoint",
            "spaced review",
            "prerequisite",
        ):
            self.assertIn(phrase, text)

    def test_learn_adapts_from_exact_checkpoint_states_without_lowering_goal(self) -> None:
        raw = skill_text("se-learn")
        for state in (
            "**secure**",
            "**partial**",
            "**misconception**",
            "**procedure-without-understanding**",
            "**not demonstrated**",
        ):
            self.assertIn(state, raw)
        text = normalized("se-learn").lower()
        for phrase in (
            "revisit a prerequisite",
            "change representation",
            "add retrieval or application practice",
            "increase difficulty",
            "early mastery",
            "never silently lower",
            "explicit approval",
        ):
            self.assertIn(phrase, text)

    def test_learn_handles_time_and_resource_limits_honestly(self) -> None:
        text = normalized("se-learn").lower()
        for phrase in (
            "reduce scope, extend the horizon, or label a foundation-only path",
            "workload assumptions",
            "inaccessible materials",
            "equivalent capability requirements",
            "never invent access",
            "does not guarantee mastery by a date",
            "never issue a grade or credential",
        ):
            self.assertIn(phrase, text)

    def test_learn_safety_handoffs_and_final_report_contract(self) -> None:
        raw = skill_text("se-learn")
        for sibling in ("se-explain", "se-study-guide", "se-socratic-review"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Goal and mastery contract**",
            "**Baseline evidence**",
            "**Dependency map**",
            "**Staged learning path**",
            "**Session and review rhythm**",
            "**Checkpoint and adaptation rules**",
            "**Resource gaps and alternatives**",
            "**Next session and handoffs**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-learn").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "not run",
            "unavailable",
            "never enroll, purchase, schedule",
            "never claim mastery",
        ):
            self.assertIn(phrase, text)

    def test_socratic_review_enforces_one_question_and_commitment(self) -> None:
        text = normalized("se-socratic-review").lower()
        for phrase in (
            "ask exactly one assessable question per turn",
            "do not hide multiple demands inside one question",
            "require a committed answer or reasoning before explanation",
            "stop, skip, reveal, or request a hint",
            "record any hint, reveal, or leading repair as contaminated evidence",
        ):
            self.assertIn(phrase, text)

    def test_socratic_review_classifies_and_adapts_from_evidence(self) -> None:
        raw = skill_text("se-socratic-review")
        for response_class in (
            "**correct-reasoning**",
            "**correct-guess**",
            "**partial-model**",
            "**procedure-without-understanding**",
            "**misconception**",
            "**not-assessed**",
        ):
            self.assertIn(response_class, raw)
        text = normalized("se-socratic-review").lower()
        for phrase in (
            "increase transfer or difficulty only after correct reasoning",
            "probe the explanation at the same level after a correct guess",
            "narrow the demand, change representation, or probe a prerequisite",
            "ask for mechanism, variation, or debugging evidence",
            "never silently lower the target level",
        ):
            self.assertIn(phrase, text)

    def test_socratic_review_repairs_misconceptions_and_stops_honestly(self) -> None:
        text = normalized("se-socratic-review").lower()
        for phrase in (
            "validate the question and source before attributing the error",
            "give the smallest source-backed correction",
            "ask a new non-identical repair check",
            "test transfer before marking the misconception repaired",
            "stop immediately on user request",
            "report every area not tested",
            "never infer intelligence, personality, or general ability",
        ):
            self.assertIn(phrase, text)

    def test_socratic_review_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-socratic-review")
        self.assertIn("references/source-standards.md", raw)
        for sibling in ("`se-explain`", "`se-learn`", "`se-study-guide`"):
            self.assertIn(sibling, raw)
        for field in (
            "**Review contract**",
            "**Question and response ledger**",
            "**Demonstrated capabilities**",
            "**Misconception and repair ledger**",
            "**Adaptation record**",
            "**Help contamination and confidence**",
            "**Unknown and not-tested areas**",
            "**Next practice and handoffs**",
            "**Limits and actions not performed**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-socratic-review").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "unknown argument names are an error",
            "never issue a grade, credential, ranking, or psychological assessment",
        ):
            self.assertIn(phrase, text)

    def test_literature_map_defines_search_protocol_and_coverage_boundary(self) -> None:
        text = normalized("se-literature-map").lower()
        for phrase in (
            "databases and sources",
            "queries and query synonyms",
            "date range",
            "disciplines",
            "source types",
            "languages",
            "`languages=`",
            "inclusion and exclusion rules",
            "stopping condition",
            "never claim exhaustive coverage",
            "missing databases",
        ):
            self.assertIn(phrase, text)

    def test_literature_map_inventories_work_identity_access_and_method(self) -> None:
        text = normalized("se-literature-map").lower()
        for phrase in (
            "doi or stable locator",
            "title, authors, date, venue or type",
            "access state",
            "method, contribution, evidence base, and source quality",
            "abstract-only",
            "secondary description",
            "never infer full-text conclusions from metadata",
        ):
            self.assertIn(phrase, text)

    def test_literature_map_uses_exact_verified_relationship_vocabulary(self) -> None:
        raw = skill_text("se-literature-map")
        for relationship in (
            "**builds-on**",
            "**critiques**",
            "**replicates**",
            "**contradicts**",
            "**applies**",
            "**independent-parallel**",
        ):
            self.assertIn(relationship, raw)
        text = normalized("se-literature-map").lower()
        for phrase in (
            "source locator and confidence",
            "verify the relationship",
            "never infer intellectual influence solely from co-occurrence, citation count, or memory",
            "citation mismatch",
        ):
            self.assertIn(phrase, text)

    def test_literature_map_preserves_clusters_disputes_and_evidence_distinctions(self) -> None:
        text = normalized("se-literature-map").lower()
        for phrase in (
            "question, theory or school, method, evidence base, or response relationship",
            "overlapping membership",
            "interpretive judgment",
            "influence or prominence",
            "methodological strength",
            "current evidentiary support",
            "recent work",
            "agreements, disputes, gaps, and open questions",
        ):
            self.assertIn(phrase, text)

    def test_literature_map_safety_handoffs_and_final_report_contract(self) -> None:
        raw = skill_text("se-literature-map")
        for sibling in ("se-research", "se-paper"):
            self.assertIn(f"`{sibling}`", raw)
        for field in (
            "**Scope and search protocol**",
            "**Coverage and access limits**",
            "**Work inventory**",
            "**Cluster and method map**",
            "**Relationship ledger**",
            "**Agreement, dispute, and gap map**",
            "**Purpose-specific reading sequence**",
            "**Handoffs and limits**",
        ):
            self.assertIn(field, raw)
        text = normalized("se-literature-map").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "not run",
            "unavailable",
            "never invent a citation",
            "never write the paper",
            "preserve competing schools",
        ):
            self.assertIn(phrase, text)

    def test_meeting_follow_through_reconciles_expected_and_actual_outcomes(self) -> None:
        raw = skill_text("se-meeting-follow-through")
        for state in (
            "**achieved**",
            "**changed**",
            "**deferred**",
            "**unaddressed**",
            "**unclear**",
        ):
            self.assertIn(state, raw)
        text = normalized("se-meeting-follow-through").lower()
        for phrase in (
            "expected-outcomes ledger",
            "exactly one",
            "without prep context",
            "expected-versus-actual reconciliation is unavailable",
            "derive only explicitly evidenced actual outcomes",
        ):
            self.assertIn(phrase, text)

    def test_meeting_follow_through_separates_decisions_and_commitments(self) -> None:
        text = normalized("se-meeting-follow-through").lower()
        for phrase in (
            "a **decision** requires explicit agreement or an authorized decision",
            "a **proposal** is discussed or suggested",
            "a **commitment** requires explicit acceptance by the named owner",
            "a **candidate action** is useful follow-through",
            "never promote a proposal into a decision",
            "suggested owner or date into an agreed commitment",
        ):
            self.assertIn(phrase, text)

    def test_meeting_follow_through_preserves_record_gaps_and_sensitivity(self) -> None:
        text = normalized("se-meeting-follow-through").lower()
        for phrase in (
            "`complete`, `partial`, `summary-only`, `unavailable`, or `unknown`",
            "never imply complete transcript coverage",
            "label the item `disputed`",
            "keep restricted personnel, legal, health, security, or confidential discussion",
            "minimum safe restricted locator",
            "preserve missing coverage and conflicts",
        ):
            self.assertIn(phrase, text)

    def test_meeting_follow_through_is_read_only_and_routes_siblings(self) -> None:
        raw = skill_text("se-meeting-follow-through")
        for sibling in (
            "se-meeting-prep",
            "se-agenda",
            "se-thread-digest",
            "se-handoff",
            "se-knowledge-capture",
        ):
            self.assertIn(f"`{sibling}`", raw)
        text = normalized("se-meeting-follow-through").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "separate explicit request",
            "connector availability does not grant write authority",
            "all external actions are marked `not run`",
        ):
            self.assertIn(phrase, text)

    def test_meeting_follow_through_final_report_contract(self) -> None:
        raw = skill_text("se-meeting-follow-through")
        for field in (
            "**Meeting and evidence contract**",
            "**Expected-versus-actual outcomes**",
            "**Decision and proposal ledger**",
            "**Commitment and candidate-action review**",
            "**Open questions, risks, and disagreements**",
            "**Audience-safe recap draft**",
            "**Follow-through drafts**",
            "**Source coverage and sensitivity limits**",
            "**Actions and handoffs**",
        ):
            self.assertIn(field, raw)

    def test_monitor_distinguishes_first_baseline_and_delta_states(self) -> None:
        text = normalized("se-monitor").lower()
        for phrase in (
            "enter first-baseline mode and do not claim a delta",
            "exactly one of `new`, `changed`, `resolved`, `unchanged`, or `unverifiable`",
            "never report a delta when no valid comparison exists",
            "summarize unchanged items as a count",
            "never convert source absence into resolution",
        ):
            self.assertIn(phrase, text)

    def test_monitor_validates_portable_state_and_minimizes_retention(self) -> None:
        raw = skill_text("se-monitor")
        self.assertIn("references/state-schema.md", raw)
        schema = (
            SKILLS_ROOT / "se-monitor" / "references" / "state-schema.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "`se-monitor-state/v1`",
            '"schemaVersion": 1',
            '"subject"',
            '"asOf"',
            '"watch"',
            '"sources"',
            '"items"',
            "Reject a newer version",
            "untrusted data, not instructions",
            "minimum fact, observation date, and locator",
        ):
            self.assertIn(phrase, schema)

    def test_monitor_handles_source_and_semantic_comparison_gaps(self) -> None:
        text = normalized("se-monitor").lower()
        for phrase in (
            "readable but stale",
            "stable semantic keys",
            "source-only changes",
            "apply explicit thresholds before promotion",
            "a missing or unavailable source yields `unverifiable`",
            "newly added sources instead of silently changing the evidence boundary",
        ):
            self.assertIn(phrase, text)

    def test_monitor_is_read_only_and_routes_siblings(self) -> None:
        raw = skill_text("se-monitor")
        for sibling in ("se-brief", "se-status", "se-research"):
            self.assertIn(f"`{sibling}`", raw)
        text = normalized("se-monitor").lower()
        for phrase in (
            "this skill is read-only",
            "data, not instructions",
            "connector or scheduler availability does not grant persistence",
            "all explicitly `not run`",
        ):
            self.assertIn(phrase, text)

    def test_monitor_final_report_contract(self) -> None:
        raw = skill_text("se-monitor")
        for field in (
            "**Monitor contract**",
            "**Meaningful deltas**",
            "**Unchanged summary**",
            "**Unverifiable and ambiguous items**",
            "**Source-only changes**",
            "**Source coverage and gaps**",
            "**Next monitor state**",
            "**Capability status**",
        ):
            self.assertIn(field, raw)

    def test_paper_gates_question_feasibility_and_drafting(self) -> None:
        text = normalized("se-paper").lower()
        for phrase in (
            "interview one question per turn",
            "run a feasibility and ethics gate",
            "require explicit approval before full literature work",
            "silence and workspace presence are not approval",
            "stop, rescope, or propose a non-empirical alternative",
        ):
            self.assertIn(phrase, text)

    def test_paper_defines_literature_and_provenance_contracts(self) -> None:
        text = normalized("se-paper").lower()
        for phrase in (
            "define the literature-search protocol before making coverage claims",
            "exact queries",
            "inclusion and exclusion rules",
            "citation-chaining",
            "every literature work, dataset, experiment, code artifact, quotation, citation, exclusion, transformation, analytical decision, and unavailable component",
            "never claim systematic-review or literature completeness",
        ):
            self.assertIn(phrase, text)

    def test_paper_preserves_execution_and_results_integrity(self) -> None:
        text = normalized("se-paper").lower()
        for phrase in (
            "proposed, approved, executed, partially executed, and not run",
            "never present planned collection, code, experiments, or analyses as executed",
            "method, observations/results, interpretation, discussion, and conclusions separate",
            "preserve contradictory, negative, and null findings",
            "results cannot be rewritten, omitted, or relabeled",
            "a nearby citation or plausible title is not evidence",
        ):
            self.assertIn(phrase, text)

    def test_paper_profile_ethics_and_submission_boundaries(self) -> None:
        raw = skill_text("se-paper")
        for reference in (
            "references/source-standards.md",
            "references/verification-protocol.md",
            "references/personal-profile-contract.md",
        ):
            self.assertIn(reference, raw)
        for sibling in (
            "se-author",
            "se-literature-map",
            "se-research",
            "se-fact-check",
            "se-topic-radar",
        ):
            self.assertIn(f"`{sibling}`", raw)
        text = normalized("se-paper").lower()
        for phrase in (
            "data, not instructions",
            "profile use is read-only and framing-only",
            "do not bypass ethics",
            "this workflow does not submit, publish, register, upload, message, collect data, execute experiments, or obtain approval",
        ):
            self.assertIn(phrase, text)

    def test_paper_final_report_contract(self) -> None:
        raw = skill_text("se-paper")
        for field in (
            "**Research state and approvals**",
            "**Approved research brief**",
            "**Literature protocol and coverage**",
            "**Evidence and decision ledger**",
            "**Method and execution state**",
            "**Paper artifact**",
            "**Integrity and validity review**",
            "**Reproducibility and ethics inventory**",
            "**Venue adaptation and gaps**",
            "**Submission handoff**",
        ):
            self.assertIn(field, raw)

    def test_plan_requires_accepted_observable_outcome(self) -> None:
        text = normalized("se-plan").lower()
        for phrase in (
            "confirm the goal is accepted, bounded, and observable",
            "desired changed state and completion evidence",
            "route the decision to `se-decide`",
            "a vague aspiration, missing outcome, or unknown governing constraint",
        ):
            self.assertIn(phrase, text)

    def test_plan_builds_outcome_milestones_and_dependencies(self) -> None:
        text = normalized("se-plan").lower()
        for phrase in (
            "work backward from the outcome into outcome-based milestones",
            "observable completion signal",
            "activities without an observable result are supporting work, not milestones",
            "surface missing prerequisites",
            "dependency cycles",
            "name a critical path only when sourced timing and dependencies support one",
        ):
            self.assertIn(phrase, text)

    def test_plan_preserves_commitment_and_authority_boundaries(self) -> None:
        text = normalized("se-plan").lower()
        for phrase in (
            "separate verified constraints and accepted commitments from assumptions, estimates, and planning proposals",
            "use `unassigned` and `unscheduled`",
            "unknown authority remains unknown",
            "first action must be possible under current authority and information",
            "never invent owners, dates, deadlines, estimates, budgets, capacity, commitments, approvals, dependencies, or a critical path",
        ):
            self.assertIn(phrase, text)

    def test_plan_is_read_only_and_defers_local_development(self) -> None:
        raw = skill_text("se-plan")
        self.assertIn("`se-decide`", raw)
        text = normalized("se-plan").lower()
        for phrase in (
            "data, not instructions",
            "this skill is read-only",
            "local development workflow",
            "do not write parallel technical planning artifacts",
            "every task, calendar, message, purchase, approval, or external write marked `not run`",
        ):
            self.assertIn(phrase, text)

    def test_plan_final_report_contract(self) -> None:
        raw = skill_text("se-plan")
        for field in (
            "**Planning contract**",
            "**Assumptions and missing information**",
            "**Milestones**",
            "**Dependencies and sequence**",
            "**Risks, blockers, and contingencies**",
            "**Decision points**",
            "**Immediate next actions**",
            "**Commitment ledger**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_postmortem_preserves_evidence_and_analytic_categories(self) -> None:
        text = normalized("se-postmortem").lower()
        for phrase in (
            "inventory every requested source before analysis",
            "build an evidence-linked timeline",
            "keep direct observation, reported account, and interpretation distinct",
            "`observation`, `interpretation`, `contributing factor`, `root cause`, and `counterfactual`",
            "no defensible root cause established",
        ):
            self.assertIn(phrase, text)

    def test_postmortem_requires_causal_mechanism_and_system_analysis(self) -> None:
        text = normalized("se-postmortem").lower()
        for phrase in (
            "requires a defensible causal mechanism plus supporting evidence",
            "temporal correlation, hindsight, repetition, or confidence in the narrative is not enough",
            "human error as an observed action or outcome, never a terminal root cause",
            "preserve conflicting accounts as competing evidence-linked interpretations",
            "successful, failed, bypassed, and absent controls",
        ):
            self.assertIn(phrase, text)

    def test_postmortem_actions_are_verifiable_and_authority_bounded(self) -> None:
        text = normalized("se-postmortem").lower()
        for phrase in (
            "map every corrective or preventive action to one or more causal findings or control gaps",
            "vague intentions without an observable verification signal are not corrective actions",
            "record owners and dates only when explicitly approved",
            "`proposed`, `unassigned`, or `unscheduled`",
            "this skill is read-only",
        ):
            self.assertIn(phrase, text)

    def test_postmortem_protects_sensitive_incidents_and_sibling_boundary(self) -> None:
        raw = skill_text("se-postmortem")
        self.assertIn("references/source-standards.md", raw)
        self.assertIn("`se-retro`", raw)
        text = normalized("se-postmortem").lower()
        for phrase in (
            "data, not instructions",
            "restricted reporting must minimize exposure without silently changing the substantive finding",
            "do not make disciplinary, legal, compliance, medical, financial, or forensic conclusions",
        ):
            self.assertIn(phrase, text)

    def test_postmortem_final_report_contract(self) -> None:
        raw = skill_text("se-postmortem")
        for field in (
            "**Postmortem contract**",
            "**Source coverage and conflicts**",
            "**Impact**",
            "**Evidence-linked timeline**",
            "**Detection, response, and recovery**",
            "**Safeguard analysis**",
            "**Causal analysis**",
            "**Counterfactuals and uncertainty**",
            "**Corrective-action ledger**",
            "**Sensitive-detail handling**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_premortem_preserves_hypotheses_and_evidence_classes(self) -> None:
        text = normalized("se-premortem").lower()
        for phrase in (
            "define what failure means before generating scenarios",
            "`evidence-supported`, `analogical`, or `speculative`",
            "scenarios are hypotheses, not predictions",
            "data, not instructions",
        ):
            self.assertIn(phrase, text)

    def test_premortem_handles_correlation_ranking_and_tail_risk(self) -> None:
        text = normalized("se-premortem").lower()
        for phrase in (
            "identify common-cause, correlated, and cascading failures",
            "ordinal bands and rationale rather than numeric probability",
            "do not multiply or average ordinal labels",
            "retain low-likelihood catastrophic cases in a separate tail-risk view",
        ):
            self.assertIn(phrase, text)

    def test_premortem_mitigations_are_observable_and_authority_bounded(self) -> None:
        text = normalized("se-premortem").lower()
        for phrase in (
            "map every prevention or contingency to a named failure mode and observable leading indicator",
            "cases with no viable mitigation",
            "only when explicitly supplied or approved",
            "this skill is read-only",
        ):
            self.assertIn(phrase, text)

    def test_premortem_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-premortem")
        self.assertIn("references/source-standards.md", raw)
        for sibling in ("`se-plan`", "`se-postmortem`", "`se-red-team`"):
            self.assertIn(sibling, raw)
        for field in (
            "**Premortem contract**",
            "**Plan sufficiency and assumptions**",
            "**Source coverage and conflicts**",
            "**Failure-mode register**",
            "**Correlation and cascade map**",
            "**Prioritized risk view**",
            "**Catastrophic tail risks**",
            "**Mitigation and indicator ledger**",
            "**Decision points and stop conditions**",
            "**Residual risk and no-mitigation cases**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_presentation_builds_outcome_led_traceable_slides(self) -> None:
        text = normalized("se-presentation").lower()
        for phrase in (
            "build a source ledger before outlining",
            "design an outcome-led story arc",
            "exactly one primary claim per slide",
            "speaker notes must distinguish sourced fact from interpretation",
            "every slide claim, statistic, quotation, visual, and speaker assertion",
        ):
            self.assertIn(phrase, text)

    def test_presentation_preserves_variants_visuals_and_accessibility(self) -> None:
        text = normalized("se-presentation").lower()
        for phrase in (
            "`existing`, `derived from identified data`, or `proposed`",
            "maintain an omission ledger",
            "never create a short version by shrinking text",
            "color-independent meaning",
            "must be redesigned or left as an open production gap",
        ):
            self.assertIn(phrase, text)

    def test_presentation_profile_and_execution_authority_are_bounded(self) -> None:
        raw = skill_text("se-presentation")
        self.assertIn("references/source-standards.md", raw)
        self.assertIn("references/personal-profile-contract.md", raw)
        text = normalized("se-presentation").lower()
        for phrase in (
            "data, not instructions",
            "profile use is optional, read-only, and preference-only",
            "this skill is read-only",
            "actual deck production belongs to presentation tooling",
        ):
            self.assertIn(phrase, text)

    def test_presentation_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-presentation")
        for sibling in (
            "`se-author`",
            "`se-proposal`",
            "`se-diagram`",
            "`se-publish`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Presentation contract**",
            "**Source coverage and evidence ledger**",
            "**Feasibility and tradeoffs**",
            "**Story arc and timing**",
            "**Slide specification**",
            "**Variant and omission ledger**",
            "**Citation and visual integrity**",
            "**Accessibility review**",
            "**Production handoff**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_proposal_gates_authority_interview_and_brief_approval(self) -> None:
        text = normalized("se-proposal").lower()
        for phrase in (
            "audience interest is not decision authority",
            "interview one question per turn",
            "require explicit approval of this brief before drafting the full proposal",
            "silence, workspace presence, or prior interest is not approval",
            "weak evidence requires a smaller claim, not stronger prose",
        ):
            self.assertIn(phrase, text)

    def test_proposal_preserves_claim_and_estimate_classes(self) -> None:
        text = normalized("se-proposal").lower()
        for phrase in (
            "`observed evidence`, `estimate`, `assumption`, or `advocacy`",
            "record the method, inputs, range, time basis, sensitivity",
            "precise-looking numbers do not create evidence",
            "do not present estimates as observations",
        ):
            self.assertIn(phrase, text)

    def test_proposal_compares_real_alternatives_and_rejected_framing(self) -> None:
        text = normalized("se-proposal").lower()
        for phrase in (
            "at least one credible alternative plus a do-nothing baseline",
            "do not weaken an alternative",
            "when stakeholders optimize for incompatible outcomes",
            "triggers interview or rescoping, not cosmetic rewriting",
            "acceptance of the document does not approve the intervention",
        ):
            self.assertIn(phrase, text)

    def test_proposal_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-proposal")
        self.assertIn("references/source-standards.md", raw)
        self.assertIn("references/personal-profile-contract.md", raw)
        for sibling in ("`se-decide`", "`se-red-team`", "`se-plan`"):
            self.assertIn(sibling, raw)
        for field in (
            "**Proposal contract**",
            "**Interview and stakeholder record**",
            "**Evidence and claim ledger**",
            "**Approved proposal brief**",
            "**Decision-ready proposal**",
            "**Alternatives and do-nothing analysis**",
            "**Investment and benefit basis**",
            "**Risks, objections, and rejection conditions**",
            "**Commitment and approval ledger**",
            "**Planning handoff**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_publish_preserves_source_approval_and_claim_fidelity(self) -> None:
        text = normalized("se-publish").lower()
        for phrase in (
            "an already approved source artifact is required",
            "build a source ledger before adaptation",
            "every load-bearing claim",
            "evidence wins when brevity, persuasion, or destination style conflicts",
            "unsupported promotional claims cannot be introduced during transformation",
        ):
            self.assertIn(phrase, text)

    def test_publish_applies_destination_and_adaptation_contracts(self) -> None:
        text = normalized("se-publish").lower()
        for phrase in (
            "apply the destination contract",
            "**slack message**",
            "**slack canvas**",
            "**notion page**",
            "**memo**",
            "**announcement**",
            "**briefing**",
            "**youtube outline**",
            "maintain an adaptation ledger",
            "`unchanged`, `compressed`, `reordered`, `retitled`, `terminology-changed`",
            "if a tight limit cannot be met without changing meaning or safety",
        ):
            self.assertIn(phrase, text)

    def test_publish_bounds_profile_audience_and_write_authority(self) -> None:
        raw = skill_text("se-publish")
        self.assertIn("references/source-standards.md", raw)
        self.assertIn("references/personal-profile-contract.md", raw)
        text = normalized("se-publish").lower()
        for phrase in (
            "a broader audience, public channel, incompatible objective",
            "profile use is optional, read-only, and preference-only",
            "this skill is read-only",
            "a request to send or publish does not execute here",
            "only after a fresh preview",
        ):
            self.assertIn(phrase, text)

    def test_publish_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-publish")
        for sibling in (
            "`se-digest`",
            "`se-author`",
            "`se-presentation`",
            "`se-knowledge-capture`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Publication contract**",
            "**Source coverage and claim ledger**",
            "**Audience and destination fit**",
            "**Destination draft and preview**",
            "**Adaptation and omission ledger**",
            "**Citation integrity**",
            "**Sensitivity and accessibility review**",
            "**Open approvals and conflicts**",
            "**Connector-ready handoff**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_red_team_steelmans_and_covers_relevant_lanes(self) -> None:
        text = normalized("se-red-team").lower()
        for phrase in (
            "steelman the artifact first",
            "select only relevant adversarial lanes and disclose coverage",
            "scenarios are tests or hypotheses, not event predictions",
            "strongest counterargument, not a convenient weak version",
        ):
            self.assertIn(phrase, text)

    def test_red_team_preserves_finding_classes_and_evidence(self) -> None:
        text = normalized("se-red-team").lower()
        for phrase in (
            "assign exactly one finding class",
            "`demonstrated-defect`",
            "`plausible-risk`",
            "`speculative-case`",
            "`value-disagreement`",
            "severity cannot outrun the demonstrated consequence and evidence",
            "do not invent adversaries, motives, vulnerabilities",
        ):
            self.assertIn(phrase, text)

    def test_red_team_minimizes_sensitive_detail_and_accepts_no_findings(self) -> None:
        text = normalized("se-red-team").lower()
        for phrase in (
            "minimize sensitive security and privacy detail",
            "omit secrets, live targets, weaponized sequences",
            "no-material-findings result",
            "never manufacture criticism",
            "this skill is read-only",
        ):
            self.assertIn(phrase, text)

    def test_red_team_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-red-team")
        self.assertIn("references/source-standards.md", raw)
        for sibling in (
            "`se-fact-check`",
            "`se-evaluate`",
            "`se-premortem`",
            "`se-postmortem`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Red-team contract**",
            "**Steelman and success model**",
            "**Evidence and assertion ledger**",
            "**Adversarial coverage map**",
            "**Classified finding register**",
            "**Counterargument and reversal analysis**",
            "**Security and privacy handling**",
            "**Responses and closure evidence**",
            "**No-findings and residual-risk statement**",
            "**Decision handoff**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_retro_orders_evidence_before_analysis_and_separates_claims(self) -> None:
        text = normalized("se-retro").lower()
        self.assertLess(
            text.index("inventory the evidence before analysis"),
            text.index("compare intended and actual outcomes only after the timeline"),
        )
        for phrase in (
            "build a factual timeline before interpreting causes",
            "verified fact",
            "participant perspective",
            "assistant inference",
            "preserve conflicting perspectives as attributed accounts",
        ):
            self.assertIn(phrase, text)

    def test_retro_is_non_blaming_and_bounded_under_uncertainty(self) -> None:
        text = normalized("se-retro").lower()
        for phrase in (
            "focus on systems and observable choices, not personal blame",
            "no defensible root cause was established",
            "do not identify an individual as the cause or infer intent",
            "do not promote correlation, chronology, hindsight",
            "proposed follow-ups are not commitments",
        ):
            self.assertIn(phrase, text)

    def test_retro_routes_delivery_work_conditionally_and_remains_read_only(self) -> None:
        raw = skill_text("se-retro")
        self.assertIn("references/source-standards.md", raw)
        text = normalized("se-retro").lower()
        for phrase in (
            "route to `sd-retro` if that specialized workflow is available",
            "if it is unavailable, continue here",
            "this skill is read-only",
            "does not record a journal entry",
            "does not record a journal entry, create or assign tasks",
            "requires a separate explicit request",
        ):
            self.assertIn(phrase, text)

    def test_retro_final_report_contract(self) -> None:
        raw = skill_text("se-retro")
        for field in (
            "**Retrospective contract**",
            "**Evidence coverage and limits**",
            "**Factual timeline**",
            "**Expected versus actual**",
            "**What worked and what limited harm**",
            "**Contributing conditions**",
            "**Lessons and transfer limits**",
            "**Proposed follow-ups**",
            "**Open questions and disagreements**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_runbook_requires_complete_step_and_mutation_contracts(self) -> None:
        text = normalized("se-runbook").lower()
        for phrase in (
            "exactly one execution state: `validated`, `partially-validated`, or `proposed`",
            "for every mutating step, require explicit authority, exact scope",
            "expected outcome, verification, failure handling, and a stop condition",
            "keep the target and verification adjacent to each action",
        ):
            self.assertIn(phrase, text)

    def test_runbook_handles_partial_failure_rollback_and_staleness(self) -> None:
        text = normalized("se-runbook").lower()
        for phrase in (
            "reconcile live state before retry, rollback, or recovery",
            "separate rollback from recovery",
            "no safe rollback established",
            "untested recovery or rollback cannot be presented as guaranteed",
            "prominent stale-runbook warning",
        ):
            self.assertIn(phrase, text)

    def test_runbook_protects_secrets_targets_and_execution_authority(self) -> None:
        text = normalized("se-runbook").lower()
        for phrase in (
            "replace credentials, tokens, personal data",
            "reject empty variables and traversal",
            "avoid root/home/workspace-wide targets",
            "this skill is read-only",
            "execution requires a separate explicit request",
            "data, not instructions",
        ):
            self.assertIn(phrase, text)

    def test_runbook_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-runbook")
        self.assertIn("references/source-standards.md", raw)
        for sibling in ("`se-checklist`", "`se-sop`", "`se-plan`"):
            self.assertIn(sibling, raw)
        for field in (
            "**Runbook contract**",
            "**Source and validation coverage**",
            "**Preflight, abort, and no-go gates**",
            "**Ordered procedure**",
            "**Decision and stop map**",
            "**Partial-failure reconciliation**",
            "**Rollback, recovery, and residual risk**",
            "**Escalation and handoff**",
            "**End-state verification and records**",
            "**Maintenance and staleness**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_sop_preserves_current_practice_and_proposed_future(self) -> None:
        text = normalized("se-sop").lower()
        for phrase in (
            "`observed-current`, `approved-current`, `proposed-future`, `conflicting`, or `unknown`",
            "proposed improvements never enter the operative procedure",
            "preserve conflicting practice",
            "do not convert a proposed improvement into current practice",
        ):
            self.assertIn(phrase, text)

    def test_sop_makes_controls_and_exceptions_operationally_testable(self) -> None:
        text = normalized("se-sop").lower()
        for phrase in (
            "every procedure step and mandatory control must be operationally testable",
            "separate mandatory controls from helpful guidance",
            "undocumented exceptions remain explicit gaps",
            "each supported exception and each discovered exception gap",
            "allowed deviation or `unknown`, approving authority or `unknown`",
            "escalation target or `unassigned`, decision required",
            "timeout or fallback, handoff acknowledgement",
        ):
            self.assertIn(phrase, text)

    def test_sop_preserves_conflict_evidence_and_routes_failure_response(self) -> None:
        text = normalized("se-sop").lower()
        for phrase in (
            "retain each variant's underlying observed or approved state",
            "local correction is limited to restoring an expected routine precondition or output",
            "diagnosis, rollback, restore, or recovery belongs in `se-runbook`",
            "active incident response belongs in the applicable incident-command process",
        ):
            self.assertIn(phrase, text)

    def test_sop_evidences_compliance_and_document_control(self) -> None:
        text = normalized("se-sop").lower()
        for phrase in (
            "jurisdiction, version, effective date, applicable scope",
            "label it `unverified requirement`",
            "version, effective date, review cadence",
            "changing a date does not make a stale procedure current",
        ):
            self.assertIn(phrase, text)

    def test_sop_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-sop")
        self.assertIn("references/source-standards.md", raw)
        for sibling in ("`se-runbook`", "`se-checklist`", "`se-plan`"):
            self.assertIn(sibling, raw)
        for field in (
            "**SOP contract**",
            "**Source and provenance register**",
            "**Document control**",
            "**Roles and responsibilities**",
            "**Inputs and prerequisites**",
            "**Routine procedure**",
            "**Mandatory controls**",
            "**Helpful guidance**",
            "**Exceptions and escalation**",
            "**Outputs, records, and completion**",
            "**Proposed future state**",
            "**Compliance and authority gaps**",
            "**Maintenance and staleness**",
            "**Sibling handoffs**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_stakeholder_map_preserves_provenance_and_role_complexity(self) -> None:
        text = normalized("se-stakeholder-map").lower()
        for phrase in (
            "`observed`, `user-judgment`, `assistant-inference`, `conflicting`, or `unknown`",
            "every assistant inference must carry a validation question and validation action",
            "formal authority and informal influence remain separate",
            "one person with multiple roles receives role-specific entries",
            "never treat a group as monolithic",
        ):
            self.assertIn(phrase, text)

    def test_stakeholder_map_limits_profiling_and_manipulation(self) -> None:
        text = normalized("se-stakeholder-map").lower()
        for phrase in (
            "do not infer private motives",
            "protected or sensitive traits",
            "behavior or process evidence",
            "no personality, psychographic, or vulnerability profile",
            "never recommend deception, coercion, covert persuasion, or exploiting vulnerabilities",
        ):
            self.assertIn(phrase, text)

    def test_stakeholder_map_surfaces_gaps_conflicts_and_staleness(self) -> None:
        text = normalized("se-stakeholder-map").lower()
        for phrase in (
            "missing stakeholder means an access or coverage gap, not evidence of irrelevance",
            "conflicting incentives",
            "organizational change",
            "as-of cutoff",
            "revalidation trigger",
        ):
            self.assertIn(phrase, text)

    def test_stakeholder_map_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-stakeholder-map")
        self.assertIn("references/source-standards.md", raw)
        for sibling in (
            "`se-agenda`",
            "`se-plan`",
            "`se-handoff`",
            "`se-feedback`",
            "`se-profile`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Mapping contract**",
            "**Source coverage and limits**",
            "**Stakeholder register**",
            "**Authority and influence view**",
            "**Roles, dependencies, and tensions**",
            "**Observed positions and concerns**",
            "**Inferences and validation plan**",
            "**Missing-stakeholder and access gaps**",
            "**Engagement sequence and information needs**",
            "**Conflicting incentives and decision risks**",
            "**Privacy and sensitivity review**",
            "**Staleness and revalidation**",
            "**Sibling handoffs**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_study_guide_covers_sources_and_preserves_conflicts(self) -> None:
        text = normalized("se-study-guide").lower()
        for phrase in (
            "read every accessible source in full",
            "unreadable, partial, or omitted regions",
            "source concept ledger",
            "preserve each definition with its source, context, and scope",
            "never silently choose one conflicting definition",
        ):
            self.assertIn(phrase, text)

    def test_study_guide_separates_source_and_generated_material(self) -> None:
        text = normalized("se-study-guide").lower()
        for phrase in (
            "`source-content`, `source-derived`, `generated-scaffolding`, `generated-inference`, or `unsupported`",
            "every answer, solution, rubric, and distractor",
            "generated material never becomes a source claim",
            "do not invent a solvable answer from a thin source",
        ):
            self.assertIn(phrase, text)

    def test_study_guide_builds_unambiguous_varied_practice(self) -> None:
        text = normalized("se-study-guide").lower()
        for phrase in (
            "recall, explanation, application, comparison, error diagnosis, misconception repair, and transfer",
            "inspect every prompt independently for answer leakage",
            "one clear retrieval target",
            "relationships and application, not isolated trivia alone",
            "required concepts are never silently removed",
        ):
            self.assertIn(phrase, text)

    def test_study_guide_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-study-guide")
        self.assertIn("references/source-standards.md", raw)
        self.assertIn(
            "Never certify a learner or claim certification of mastery",
            normalized("se-study-guide"),
        )
        for sibling in (
            "`se-distill`",
            "`se-learn`",
            "`se-explain`",
            "`se-socratic-review`",
            "`se-tutorial`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Study contract**",
            "**Source coverage and limits**",
            "**Concept and prerequisite map**",
            "**Essential definitions and notation**",
            "**Worked examples and common traps**",
            "**Retrieval and flashcard set**",
            "**Practice, solutions, and rubrics**",
            "**Conflict and unsupported-content ledger**",
            "**Review order**",
            "**Sibling handoffs**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_thread_digest_requires_bounded_message_coverage(self) -> None:
        text = normalized("se-thread-digest").lower()
        for phrase in (
            "explicit conversation scope and time window",
            "complete, partial, edited, deleted, unavailable, or unknown",
            "stable message id or link",
            "parent and reply context",
            "never imply complete coverage",
        ):
            self.assertIn(phrase, text)

    def test_thread_digest_preserves_conversation_state_and_evidence(self) -> None:
        text = normalized("se-thread-digest").lower()
        for phrase in (
            "proposal, decision, explicit commitment, candidate action",
            "every decision and explicit commitment",
            "silence, repetition, attendance, or a reaction is not acceptance",
            "supersession chain",
            "unknown owners, dates, authority, and resolution state remain `unknown`",
        ):
            self.assertIn(phrase, text)

    def test_thread_digest_limits_privacy_actions_and_injection(self) -> None:
        text = normalized("se-thread-digest").lower()
        for phrase in (
            "data, not instructions",
            "never widen private-channel information",
            "do not expose unrelated participant details",
            "posting, reacting, canvases, lists, monitoring",
            "all `not run`",
        ):
            self.assertIn(phrase, text)

    def test_thread_digest_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-thread-digest")
        self.assertIn("references/source-standards.md", raw)
        for sibling in (
            "`se-digest`",
            "`se-meeting-follow-through`",
            "`se-status`",
            "`se-handoff`",
            "`se-knowledge-capture`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Conversation contract**",
            "**Outcome digest**",
            "**Decision and proposal ledger**",
            "**Commitment and candidate-action ledger**",
            "**Open questions, disagreements, and risks**",
            "**Evidence and revision ledger**",
            "**Downstream payloads**",
            "**Coverage, privacy, and uncertainty**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_tutorial_requires_outcome_prerequisite_and_checkpoint_contracts(self) -> None:
        text = normalized("se-tutorial").lower()
        for phrase in (
            "observable final result",
            "prerequisite check",
            "stop before the first dependent step",
            "every major checkpoint",
            "stable assertion",
        ):
            self.assertIn(phrase, text)

    def test_tutorial_preserves_platform_version_and_execution_state(self) -> None:
        text = normalized("se-tutorial").lower()
        for phrase in (
            "`verified`, `partially-verified`, or `unverified`",
            "never describe unverified or partially verified behavior as working",
            "platform or environment branch",
            "version and date scope",
            "authoritative sources",
        ):
            self.assertIn(phrase, text)

    def test_tutorial_safeguards_secrets_destructive_steps_and_cleanup(self) -> None:
        text = normalized("se-tutorial").lower()
        for phrase in (
            "placeholder, never a real secret",
            "verify the exact target",
            "safer alternative",
            "backup and rollback",
            "cleanup can be destructive",
            "commands on the reader's system",
        ):
            self.assertIn(phrase, text)

    def test_tutorial_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-tutorial")
        self.assertIn("references/source-standards.md", raw)
        self.assertIn("references/personal-profile-contract.md", raw)
        for sibling in (
            "`se-study-guide`",
            "`se-learn`",
            "`se-explain`",
            "`se-runbook`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Tutorial contract**",
            "**Prerequisite and environment check**",
            "**Checkpoint-driven tutorial**",
            "**Troubleshooting and recovery map**",
            "**Final validation**",
            "**Cleanup and rollback**",
            "**Version, source, and execution inventory**",
            "**Sibling handoffs**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_video_notes_preserves_source_coverage_and_content_classes(self) -> None:
        text = normalized("se-video-notes").lower()
        for phrase in (
            "`complete-transcript`, `partial-transcript`, `metadata-only`, or `unavailable`",
            "metadata, transcript-grounded creator content, and assistant analysis",
            "read every accessible transcript region",
            "caption source and quality",
            "never imply that the video was watched",
        ):
            self.assertIn(phrase, text)

    def test_video_notes_requires_timestamp_and_quote_fidelity(self) -> None:
        text = normalized("se-video-notes").lower()
        for phrase in (
            "known timestamp map and basis",
            "never create timestamps from untimed prose",
            "do not convert transcript offsets",
            "exact, short, and traceable",
            "edits, inserted ads, or alternate cuts",
        ):
            self.assertIn(phrase, text)

    def test_video_notes_handles_missing_captions_and_compare_asymmetry(self) -> None:
        text = normalized("se-video-notes").lower()
        for phrase in (
            "no usable captions or transcript representation is available",
            "no guessed summary",
            "questions and checklist for manual viewing",
            "agreements, conflicts, method or evidence differences, and unique contributions",
            "evidence asymmetry, not a negative judgment",
            "do not merge or align multilingual captions",
        ):
            self.assertIn(phrase, text)

    def test_video_notes_boundaries_and_final_report_contract(self) -> None:
        raw = skill_text("se-video-notes")
        self.assertIn("references/source-standards.md", raw)
        for sibling in (
            "`se-fact-check`",
            "`se-capture`",
            "`se-knowledge-capture`",
        ):
            self.assertIn(sibling, raw)
        for field in (
            "**Video-note contract**",
            "**Source inventory and coverage**",
            "**Timestamped notes**",
            "**Claims and verification queue**",
            "**Comparison view**",
            "**Limitations and manual-viewing aid**",
            "**Portable Markdown artifact**",
            "**Downstream handoffs**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)

    def test_review_skills_enforces_scope_evidence_and_template_boundaries(self) -> None:
        text = normalized("se-review-skills").lower()
        for phrase in (
            "candidate signals into findings",
            "file/line or reproducible-command evidence",
            "for the se pack, review and change only `templates/skills/**`",
            "for the sd pack, review and change only `templates/**`",
            "installed copies, registries, manifests, generators",
            "first-party issue without a template remedy is non-selectable",
        ):
            self.assertIn(phrase, text)

    def test_review_skills_preserves_capabilities_and_bounded_delegation(self) -> None:
        text = normalized("se-review-skills").lower()
        for phrase in (
            "build a capability ledger for every skill",
            "use subagents only for independently testable work",
            "cap fan-out, prohibit recursive delegation",
            "parent verify and deduplicate",
            "give independent validators raw artifacts, not conclusions",
            "portable model profile",
        ):
            self.assertIn(phrase, text)

    def test_review_skills_routes_tasks_and_applies_from_stable_snapshots(self) -> None:
        text = normalized("se-review-skills").lower()
        for phrase in (
            "preserve its json and `snapshotid`",
            "reconcile active and archived trellis tasks",
            "at most one planning task per affected skill and snapshot",
            "route verified sd and se work to their respective upstream trellis checkouts",
            "cross-repository selections create handoffs and stop",
            "require `task=` or `apply=`",
        ):
            self.assertIn(phrase, text)

    def test_review_skills_resources_and_final_report_contract(self) -> None:
        raw = skill_text("se-review-skills")
        skill_root = SKILLS_ROOT / "se-review-skills"
        for relative in (
            "references/review-rubric.md",
            "references/runtime-routing.md",
            "references/report-schema.md",
            "scripts/skill_review.py",
        ):
            self.assertIn(relative, raw)
            self.assertTrue((skill_root / relative).is_file(), relative)
        for field in (
            "**Review contract**",
            "**Coverage and limits**",
            "**Package-wide findings**",
            "**Family and skill findings**",
            "**Runtime recommendations**",
            "**Repository selectors**",
            "**Task/application state**",
            "**Execution boundary**",
        ):
            self.assertIn(field, raw)
        for sibling in ("`se-help`", "`sd-audit-repo`", "`sd-review-local`"):
            self.assertIn(sibling, raw)


class SkillDocumentationTest(unittest.TestCase):
    def test_thread_digest_docs_distinguish_thread_and_document_synthesis(self) -> None:
        operator = " ".join(
            (PACK_ROOT / "docs/SE_AI_COMMAND_PACK.md")
            .read_text(encoding="utf-8")
            .split()
        )
        self.assertIn(
            "bounded thread outcome reconstruction with `se-thread-digest`, "
            "generic multi-document synthesis with `se-digest`",
            operator,
        )

    def test_technical_editor_docs_use_canonical_pass_names(self) -> None:
        readme = " ".join(
            (PACK_ROOT / "README.md").read_text(encoding="utf-8").split()
        )
        operator = " ".join(
            (PACK_ROOT / "docs/SE_AI_COMMAND_PACK.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for phrase in (
            "technical correctness",
            "evidence and citations",
            "hidden assumptions",
            "code and examples",
            "novelty and originality",
            "skeptical-reader objections",
            "structure",
            "reader comprehension",
            "confidentiality",
            "title and opening",
            "voice consistency",
        ):
            self.assertIn(phrase, readme)
            self.assertIn(phrase, operator)

    def test_readme_lists_every_skill(self) -> None:
        readme = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
        for name in SKILL_NAMES:
            self.assertIn(f"`{name}`", readme)

    def test_changelog_mentions_every_skill(self) -> None:
        changelog = (PACK_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        for name in SKILL_NAMES:
            self.assertIn(name, changelog)


if __name__ == "__main__":
    unittest.main()
