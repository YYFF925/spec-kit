"""Fixed Chinese role annotations on generated Spec Kit skill descriptions.

``spec-kit init`` prepends a short role label (e.g. ``（2.需求定义）``) to the
description of each known core skill so skill lists and pickers surface its
responsibility and recommended order at a glance. The original description
must survive verbatim after the label, re-generation must never stack
labels, and skills outside the mapping must keep their description untouched.
"""

from pathlib import Path

import yaml

from specify_cli._skill_annotations import (
    SKILL_ANNOTATIONS,
    annotate_skill_description,
)
from specify_cli.agents import CommandRegistrar
from specify_cli.integrations import get_integration
from specify_cli.integrations.manifest import IntegrationManifest

SPECIFY_DESCRIPTION = (
    "Create or update the feature specification from a natural language "
    "feature description."
)


class TestAnnotateSkillDescription:
    def test_known_skill_gets_label_and_keeps_description(self):
        result = annotate_skill_description("speckit-specify", SPECIFY_DESCRIPTION)
        assert result == f"（2.需求定义） {SPECIFY_DESCRIPTION}"

    def test_every_mapped_skill_uses_its_own_label(self):
        for skill_name, note in SKILL_ANNOTATIONS.items():
            result = annotate_skill_description(skill_name, "Do things.")
            assert result == f"（{note}） Do things."

    def test_legacy_dotted_name_is_annotated(self):
        result = annotate_skill_description("speckit.plan", "Generate plans.")
        assert result == "（5.实现规划） Generate plans."

    def test_re_annotation_does_not_stack(self):
        once = annotate_skill_description("speckit-plan", "Execute the planning workflow.")
        twice = annotate_skill_description("speckit-plan", once)
        assert once == twice == "（5.实现规划） Execute the planning workflow."

    def test_unknown_skill_unchanged(self):
        description = "Some extension command description."
        assert (
            annotate_skill_description("speckit-hint-ext-build-context", description)
            == description
        )

    def test_empty_description_unchanged(self):
        assert annotate_skill_description("speckit-plan", "") == ""

    def test_core_command_templates_are_all_mapped(self):
        commands_dir = Path(__file__).resolve().parent.parent / "templates" / "commands"
        cores = {
            f"speckit-{path.stem}"
            for path in commands_dir.iterdir()
            if path.is_file() and path.suffix == ".md"
        }
        missing = cores - SKILL_ANNOTATIONS.keys()
        assert not missing, f"core skills missing Chinese annotations: {sorted(missing)}"

    def test_bundled_extension_commands_are_mapped(self):
        assert SKILL_ANNOTATIONS["speckit-github-taskstoissues"] == "转为Issue"
        result = annotate_skill_description(
            "speckit.github.taskstoissues",
            "Convert tasks into GitHub issues.",
        )
        assert result == "（转为Issue） Convert tasks into GitHub issues."

    def test_core_labels_follow_full_path_order(self):
        expected = [
            ("speckit-constitution", "1.项目原则"),
            ("speckit-specify", "2.需求定义"),
            ("speckit-clarify", "3.需求澄清"),
            ("speckit-coldread", "4.冷读测试"),
            ("speckit-plan", "5.实现规划"),
            ("speckit-checklist", "6.需求质检"),
            ("speckit-tasks", "7.任务拆分"),
            ("speckit-analyze", "8.一致性分析"),
            ("speckit-implement", "9.代码实现"),
            ("speckit-converge", "10.查漏补缺"),
        ]
        for skill_name, note in expected:
            assert SKILL_ANNOTATIONS[skill_name] == note

    def test_stale_unnumbered_label_is_replaced(self):
        result = annotate_skill_description(
            "speckit-plan",
            "（实现规划） Generate plans.",
        )
        assert result == "（5.实现规划） Generate plans."


class TestSkillGeneratorsAnnotate:
    def test_build_skill_frontmatter_annotates_known_skill(self):
        fm = CommandRegistrar.build_skill_frontmatter(
            "codex", "speckit-plan", "Execute plans.", "templates/commands/plan.md"
        )
        assert fm["description"] == "（5.实现规划） Execute plans."

    def test_build_skill_frontmatter_leaves_unknown_skill_unchanged(self):
        fm = CommandRegistrar.build_skill_frontmatter(
            "codex", "speckit-myfeature", "Custom.", "commands/myfeature.md"
        )
        assert fm["description"] == "Custom."

    def test_skills_setup_annotates_core_skills(self, tmp_path):
        integration = get_integration("agy")
        created = integration.setup(tmp_path, IntegrationManifest("agy", tmp_path))
        skill_files = [f for f in created if f.name == "SKILL.md"]
        assert skill_files

        for skill_file in skill_files:
            fm = yaml.safe_load(
                skill_file.read_text(encoding="utf-8").split("---", 2)[1]
            )
            note = SKILL_ANNOTATIONS.get(fm["name"])
            if note is None:
                assert not fm["description"].startswith("（"), skill_file
            else:
                assert fm["description"].startswith(f"（{note}） "), skill_file

    def test_hermes_setup_annotates_core_skills(self, tmp_path, monkeypatch):
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: home)

        integration = get_integration("hermes")
        created = integration.setup(
            tmp_path, IntegrationManifest("hermes", tmp_path)
        )
        skill_files = [f for f in created if f.name == "SKILL.md"]
        assert skill_files

        for skill_file in skill_files:
            fm = yaml.safe_load(
                skill_file.read_text(encoding="utf-8").split("---", 2)[1]
            )
            note = SKILL_ANNOTATIONS.get(fm["name"])
            if note is not None:
                assert fm["description"].startswith(f"（{note}） "), skill_file

    def test_generic_skills_mode_annotates(self, tmp_path):
        from specify_cli.integrations.generic import GenericIntegration

        template = tmp_path / "plan.md"
        template.write_text(
            "---\n"
            "description: Generate plans.\n"
            "---\n"
            "Body\n",
            encoding="utf-8",
        )
        skill_name, content = GenericIntegration()._build_skill_content(
            template, "sh", tmp_path
        )
        assert skill_name == "speckit-plan"
        fm = yaml.safe_load(content.split("---", 2)[1])
        assert fm["description"] == "（5.实现规划） Generate plans."
