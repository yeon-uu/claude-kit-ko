"""스킬 발견·frontmatter 파싱·검증 로직.

CLI(입출력)와 분리해 순수 함수로 두고, 테스트는 이 모듈만 겨눈다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# 스킬 name 규약: 소문자·숫자·하이픈(kebab-case).
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Claude 스킬 description의 실용 길이 범위(문자 수).
# 너무 짧으면 발동 트리거가 부실하고, 너무 길면 항상 로드되는 비용이 커진다.
DESC_MIN = 40
DESC_MAX = 1024


@dataclass
class Frontmatter:
    """SKILL.md 상단 `--- ... ---` 블록 파싱 결과."""

    fields: dict[str, str]
    body: str
    ok: bool  # frontmatter 블록 자체가 존재·정상 종료했는가
    bom: bool = False  # 파일 맨 앞에 UTF-8 BOM이 있었는가


def parse_frontmatter(text: str) -> Frontmatter:
    """단순 `key: value` frontmatter를 파싱한다.

    YAML 전부를 다루지 않는다 — 스킬 frontmatter는 한 줄 스칼라만 쓰므로
    외부 의존성(pyyaml) 없이 첫 콜론 기준으로 나눈다. 값 안의 콜론은 보존된다.
    """
    bom = text.startswith("\ufeff")
    if bom:
        # BOM이 있으면 첫 줄이 '---'로 인식되지 않는다. 벗겨내되 사실은 기록한다.
        text = text[1:]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return Frontmatter(fields={}, body=text, ok=False)

    fields: dict[str, str] = {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()

    if end is None:
        # 닫는 --- 없음 → 손상된 frontmatter.
        return Frontmatter(fields=fields, body=text, ok=False)

    body = "\n".join(lines[end + 1 :]).strip()
    return Frontmatter(fields=fields, body=body, ok=True)


@dataclass
class Skill:
    """디스크의 스킬 하나."""

    name: str  # 디렉터리 이름
    path: Path  # SKILL.md 경로
    frontmatter: Frontmatter


def discover_skills(skills_dir: Path) -> list[Skill]:
    """`skills/*/SKILL.md`를 찾아 이름순으로 반환한다."""
    if not skills_dir.is_dir():
        return []
    found: list[Skill] = []
    for child in sorted(skills_dir.iterdir()):
        skill_file = child / "SKILL.md"
        if child.is_dir() and skill_file.is_file():
            text = skill_file.read_text(encoding="utf-8")
            found.append(
                Skill(
                    name=child.name,
                    path=skill_file,
                    frontmatter=parse_frontmatter(text),
                )
            )
    return found


@dataclass
class LintResult:
    """스킬 하나의 검증 결과."""

    name: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def lint_skill(skill: Skill) -> LintResult:
    """스킬 하나를 규약에 대해 검증한다.

    errors → 배포를 막아야 하는 것. warnings → 손보면 좋은 것.
    """
    result = LintResult(name=skill.name)
    fm = skill.frontmatter

    if fm.bom:
        result.warnings.append("파일 맨 앞에 UTF-8 BOM이 있다 — UTF-8(BOM 없음)로 저장 권장")

    if not fm.ok:
        result.errors.append("frontmatter 블록(--- ... ---)이 없거나 닫히지 않았다")
        return result

    name = fm.fields.get("name")
    desc = fm.fields.get("description")

    if not name:
        result.errors.append("frontmatter에 name이 없다")
    else:
        if name != skill.name:
            result.errors.append(
                f"name('{name}')이 디렉터리('{skill.name}')와 다르다"
            )
        if not NAME_RE.match(name):
            result.errors.append(f"name '{name}'이 kebab-case가 아니다")

    if not desc:
        result.errors.append("frontmatter에 description이 없다")
    else:
        n = len(desc)
        if n < DESC_MIN:
            result.warnings.append(
                f"description이 짧다({n}자) — 발동 트리거가 부실할 수 있다(권장 ≥{DESC_MIN})"
            )
        if n > DESC_MAX:
            result.warnings.append(
                f"description이 길다({n}자) — 항상 로드되는 비용이 크다(권장 ≤{DESC_MAX})"
            )

    if not fm.body:
        result.errors.append("본문이 비어 있다")
    elif not any(line.lstrip().startswith("#") for line in fm.body.splitlines()):
        result.warnings.append("본문에 제목(#) 헤딩이 없다")

    return result


def lint_all(skills_dir: Path) -> list[LintResult]:
    """모든 스킬을 검증해 결과 리스트를 반환한다."""
    return [lint_skill(s) for s in discover_skills(skills_dir)]
