"""Fixed role annotations prefixed to known Spec Kit skill descriptions.

Every skill generator prepends a short Chinese role label to the
description of a known core skill (``speckit-specify`` etc.) so skill
lists and pickers surface each skill's responsibility at a glance. Core
SDD labels carry a workflow-order number (``1.项目原则``) so pickers
sort in the recommended run order. The original description is preserved
verbatim after the label; skills outside the mapping keep their
description untouched.
"""

import re

SKILL_ANNOTATIONS = {
    # Core SDD commands (templates/commands), numbered in recommended
    # full-path order: constitution → specify → clarify → coldread →
    # plan → checklist → tasks → analyze → implement → converge.
    "speckit-constitution": "1.项目原则",
    "speckit-specify": "2.需求定义",
    "speckit-clarify": "3.需求澄清",
    "speckit-coldread": "4.冷读测试",
    "speckit-plan": "5.实现规划",
    "speckit-checklist": "6.需求质检",
    "speckit-tasks": "7.任务拆分",
    "speckit-analyze": "8.一致性分析",
    "speckit-implement": "9.代码实现",
    "speckit-converge": "10.查漏补缺",
    # Bundled extension commands. Independent of the core SDD sequence,
    # so they are numbered inside their own workflow.
    "speckit-github-taskstoissues": "转为Issue",
    "speckit-bug-assess": "1.缺陷评估",
    "speckit-bug-fix": "2.缺陷修复",
    "speckit-bug-test": "3.缺陷验证",
    "speckit-assess-intake": "1.想法收录",
    "speckit-assess-research": "2.想法调研",
    "speckit-assess-define": "3.问题定义",
    "speckit-assess-shape": "4.方案塑形",
    "speckit-assess-decide": "5.投资决策",
    "speckit-git-feature": "功能分支",
    "speckit-git-validate": "分支校验",
    "speckit-git-remote": "远程探测",
    "speckit-git-initialize": "仓库初始化",
    "speckit-git-commit": "自动提交",
    "speckit-agent-context-update": "上下文刷新",
}

# Matches a previously applied annotation, with or without a workflow
# number, so re-init replaces a stale label instead of stacking one.
_ANNOTATION_PREFIX = re.compile(r"^（(?:\d+\.)?[^）]+） ")


def annotate_skill_description(skill_name: str, description: str) -> str:
    """Prepend the fixed role annotation for *skill_name* to *description*.

    Legacy dotted skill names (``speckit.specify``) are normalized to the
    modern hyphenated form before lookup. A description that already
    carries this skill's current annotation is returned unchanged.
    An older annotation (unnumbered, or a previous number) is stripped
    and replaced so re-init and upgrade never stack duplicates.
    """
    if not description:
        return description
    note = SKILL_ANNOTATIONS.get(skill_name.replace(".", "-"))
    if note is None:
        return description
    prefix = f"（{note}）"
    if description.startswith(prefix):
        return description
    stripped = _ANNOTATION_PREFIX.sub("", description, count=1)
    return f"{prefix} {stripped}"
