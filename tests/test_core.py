"""core 로직 테스트 — frontmatter 파싱·발견·검증."""

from __future__ import annotations

from pathlib import Path

import pytest

from kit.core import (
    Frontmatter,
    Skill,
    discover_skills,
    lint_all,
    lint_skill,
    parse_frontmatter,
)

VALID = """---
name: demo
description: 이것은 데모 스킬의 설명이다. 발동 트리거를 충분히 담을 만큼 길게 쓴 문장.
---

# demo

본문 내용.
"""


def test_parse_frontmatter_ok():
    fm = parse_frontmatter(VALID)
    assert fm.ok
    assert fm.fields["name"] == "demo"
    assert fm.fields["description"].startswith("이것은")
    assert fm.body.startswith("# demo")


def test_parse_preserves_colon_in_value():
    text = "---\nname: x\ndescription: a: b: c 형태의 값\n---\n\n# x\n"
    fm = parse_frontmatter(text)
    assert fm.fields["description"] == "a: b: c 형태의 값"


def test_parse_no_frontmatter():
    fm = parse_frontmatter("# 그냥 제목\n본문")
    assert not fm.ok


def test_parse_unclosed_frontmatter():
    fm = parse_frontmatter("---\nname: x\n본문에 닫는 구분자가 없음")
    assert not fm.ok


def _skill(text: str, name: str = "demo") -> Skill:
    return Skill(name=name, path=Path(f"{name}/SKILL.md"), frontmatter=parse_frontmatter(text))


def test_lint_valid_passes():
    assert lint_skill(_skill(VALID)).ok


def test_lint_name_mismatch():
    r = lint_skill(_skill(VALID, name="other"))
    assert not r.ok
    assert any("디렉터리" in e for e in r.errors)


def test_lint_missing_description():
    text = "---\nname: demo\n---\n\n# demo\n본문\n"
    r = lint_skill(_skill(text))
    assert any("description" in e for e in r.errors)


def test_lint_short_description_warns():
    text = "---\nname: demo\ndescription: 짧음\n---\n\n# demo\n본문\n"
    r = lint_skill(_skill(text))
    assert r.ok  # 경고지 에러 아님
    assert any("짧다" in w for w in r.warnings)


def test_lint_non_kebab_name():
    text = "---\nname: Demo_Skill\ndescription: " + "가" * 50 + "\n---\n\n# x\n본문\n"
    r = lint_skill(_skill(text, name="Demo_Skill"))
    assert any("kebab" in e for e in r.errors)


def test_lint_empty_body():
    text = "---\nname: demo\ndescription: " + "가" * 50 + "\n---\n"
    r = lint_skill(_skill(text))
    assert any("본문" in e for e in r.errors)


def test_discover_and_lint_real_repo():
    """실제 리포의 스킬이 전부 lint를 통과해야 한다."""
    root = Path(__file__).resolve().parent.parent
    skills = discover_skills(root / "skills")
    assert len(skills) >= 9
    results = lint_all(root / "skills")
    failing = {r.name: r.errors for r in results if not r.ok}
    assert not failing, f"lint 실패 스킬: {failing}"


def test_discover_empty_dir(tmp_path):
    assert discover_skills(tmp_path) == []
