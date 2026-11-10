"""Fixed role annotations prefixed to known Spec Kit skill descriptions.

Every skill generator prepends a short Chinese role label to the
description of a known core skill (``speckit-specify`` etc.) so skill
lists and pickers surface each skill's responsibility at a glance. The
original description is preserved verbatim after the label; skills
outside the mapping keep their description untouched.
"""

SKILL_ANNOTATIONS = {
    "speckit-constitution": "项目原则",
    "speckit-specify": "需求定义",
    "speckit-clarify": "需求澄清",
    "speckit-coldread": "冷读测试",
    "speckit-plan": "实现规划",
    "speckit-tasks": "任务拆分",
    "speckit-analyze": "一致性分析",
    "speckit-checklist": "需求质检",
    "speckit-implement": "代码实现",
    "speckit-taskstoissues": "转为Issue",
    "speckit-converge": "查漏补缺",
}


def annotate_skill_description(skill_name: str, description: str) -> str:
    """Prepend the fixed role annotation for *skill_name* to *description*.

    Legacy dotted skill names (``speckit.specify``) are normalized to the
    modern hyphenated form before lookup. A description that already
    carries its annotation is returned unchanged so re-init and upgrade
    can never stack duplicates.
    """
    if not description:
        return description
    note = SKILL_ANNOTATIONS.get(skill_name.replace(".", "-"))
    if note is None:
        return description
    prefix = f"（{note}）"
    if description.startswith(prefix):
        return description
    return f"{prefix} {description}"
