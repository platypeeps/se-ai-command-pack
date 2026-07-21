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


class SkillDocumentationTest(unittest.TestCase):
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
