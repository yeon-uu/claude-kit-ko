"""kit CLI — lint / list / install / doctor.

repo 루트는 이 패키지의 부모로 추론한다(별도 설치 없이 리포에서 바로 실행).
`--repo`로 재정의할 수 있다.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__
from .core import discover_skills, lint_all


def repo_root(override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def default_claude_dir() -> Path:
    return Path.home() / ".claude"


# ── lint ─────────────────────────────────────────────────────────────────────
def cmd_lint(args: argparse.Namespace) -> int:
    skills_dir = repo_root(args.repo) / "skills"
    results = lint_all(skills_dir)
    if not results:
        print(f"검증할 스킬이 없다: {skills_dir}", file=sys.stderr)
        return 1

    n_err = n_warn = 0
    for r in results:
        if r.ok and not r.warnings:
            print(f"  ok    {r.name}")
        for e in r.errors:
            n_err += 1
            print(f"  ERROR {r.name}: {e}")
        for w in r.warnings:
            n_warn += 1
            print(f"  warn  {r.name}: {w}")

    print(f"\n{len(results)}개 스킬 · 에러 {n_err} · 경고 {n_warn}")
    return 1 if n_err else 0


# ── list ─────────────────────────────────────────────────────────────────────
def cmd_list(args: argparse.Namespace) -> int:
    skills = discover_skills(repo_root(args.repo) / "skills")
    if not skills:
        print("스킬 없음", file=sys.stderr)
        return 1
    width = max(len(s.name) for s in skills)
    for s in skills:
        desc = s.frontmatter.fields.get("description", "(description 없음)")
        one_line = desc.split(". ")[0][:80]
        print(f"  {s.name.ljust(width)}  {one_line}")
    print(f"\n{len(skills)}개 스킬")
    return 0


# ── install ──────────────────────────────────────────────────────────────────
def cmd_install(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    dest = Path(args.dest).expanduser() if args.dest else default_claude_dir()
    dry = args.dry_run

    src_skills = root / "skills"
    skills = discover_skills(src_skills)
    if not skills:
        print(f"스킬을 찾지 못함: {src_skills}", file=sys.stderr)
        return 1

    tag = "[dry-run] " if dry else ""
    print(f"{tag}대상: {dest}")

    dest_skills = dest / "skills"
    for s in skills:
        target = dest_skills / s.name
        if target.exists() and not args.force:
            print(f"  skip  {s.name} (이미 있음 — 덮으려면 --force)")
            continue
        action = "덮어씀" if target.exists() else "복사"
        print(f"  {action}  skills/{s.name}")
        if not dry:
            dest_skills.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(s.path.parent, target)

    # 전역 CLAUDE.md는 사용자의 개인 지침이 들어있을 수 있어 절대 조용히 덮지 않는다.
    global_tpl = root / "templates" / "CLAUDE.global.md"
    global_dest = dest / "CLAUDE.md"
    if global_tpl.is_file():
        if global_dest.exists() and not args.force:
            print(f"  skip  CLAUDE.md (이미 있음 — 개인 지침 보호, 덮으려면 --force)")
        else:
            action = "덮어씀" if global_dest.exists() else "복사"
            print(f"  {action}  CLAUDE.md  ← templates/CLAUDE.global.md (<> 채우기 필요)")
            if not dry:
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(global_tpl, global_dest)

    if dry:
        print("\n실제로 적용하려면 --dry-run 없이 다시 실행.")
    else:
        print("\n완료. `kit doctor`로 확인.")
    return 0


# ── doctor ───────────────────────────────────────────────────────────────────
def cmd_doctor(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    dest = Path(args.dest).expanduser() if args.dest else default_claude_dir()

    print(f"python      {sys.version.split()[0]}")
    print(f"kit         {__version__}")
    print(f"repo        {root}")
    print(f"claude dir  {dest}  {'있음' if dest.is_dir() else '없음'}")

    repo_skills = {s.name for s in discover_skills(root / "skills")}
    installed = set()
    dest_skills = dest / "skills"
    if dest_skills.is_dir():
        installed = {
            p.name for p in dest_skills.iterdir() if (p / "SKILL.md").is_file()
        }
    print(f"스킬        리포 {len(repo_skills)} · 설치됨 {len(installed & repo_skills)}")
    missing = sorted(repo_skills - installed)
    if missing:
        print(f"  미설치: {', '.join(missing)}  → `kit install`")

    global_dest = dest / "CLAUDE.md"
    print(f"CLAUDE.md   {'있음' if global_dest.is_file() else '없음'}")

    results = lint_all(root / "skills")
    n_err = sum(len(r.errors) for r in results)
    print(f"lint        {'통과' if n_err == 0 else f'에러 {n_err}개 — `kit lint`'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kit",
        description="claude-kit-ko — 스킬 설치·검증 CLI",
    )
    p.add_argument("--version", action="version", version=f"kit {__version__}")
    p.add_argument("--repo", help="리포 루트 재정의(기본: kit 패키지의 부모)")

    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("lint", help="SKILL.md 규약 검증").set_defaults(func=cmd_lint)
    sub.add_parser("list", help="스킬 목록·요약").set_defaults(func=cmd_list)

    pi = sub.add_parser("install", help="스킬을 ~/.claude 로 복사")
    pi.add_argument("--dest", help="대상 디렉터리(기본: ~/.claude)")
    pi.add_argument("--dry-run", action="store_true", help="실제 복사 없이 계획만 출력")
    pi.add_argument("--force", action="store_true", help="기존 항목 덮어쓰기")
    pi.set_defaults(func=cmd_install)

    pd = sub.add_parser("doctor", help="설치 상태 점검")
    pd.add_argument("--dest", help="대상 디렉터리(기본: ~/.claude)")
    pd.set_defaults(func=cmd_doctor)

    return p


def _force_utf8_output() -> None:
    """윈도우 기본 콘솔(cp949)에서 한글·em dash 출력이 깨지거나 크래시하지 않도록."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass  # 리다이렉트·파이프 등 재설정 불가 스트림은 그대로 둔다


def main(argv: list[str] | None = None) -> int:
    _force_utf8_output()
    args = build_parser().parse_args(argv)
    return args.func(args)
