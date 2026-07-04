# SETUP — 설치·적용 가이드

## 1. 전체 구조 — 무엇이 어디로 가는가

```
%USERPROFILE%\.claude\          (Mac/Linux: ~/.claude/)
├── CLAUDE.md          ← templates/CLAUDE.global.md 를 복사해 <> 채우기
└── skills\            ← 이 리포의 skills/ 7개 폴더 복사

<dev 루트>\                      (예: D:\dev, ~/dev)
├── _standards\        ← 이 리포의 standards/ 4파일 복사
├── _career\           ← templates/career-hub/ 복사 (비공개 유지!)
├── _archive\          ← 종료 프로젝트 이동용 (빈 폴더로 시작)
└── <프로젝트들>\
    ├── CLAUDE.md      ← standards/CLAUDE-template.md 로 시작
    └── docs\ (PLAN·DEVLOG·EXPERIENCE·adr)
```

## 2. 설치 절차

1. Claude Code 설치: `npm install -g @anthropic-ai/claude-code` (또는 데스크톱 앱) → 로그인.
2. 전역 지침: `templates/CLAUDE.global.md` → `~/.claude/CLAUDE.md` 복사 후 `<>` 항목 채우기.
3. 스킬: `skills/` 아래 8개 폴더 → `~/.claude/skills/` 복사.
4. 표준: `standards/` → `<dev 루트>/_standards/` 복사.
5. 커리어 허브: `templates/career-hub/` → `<dev 루트>/_career/` 복사. **_career는 절대 공개 레포에 올리지 말 것** (면접용 원본·지원 이력 포함).
6. 검증: 아무 폴더에서 `claude` 실행 → "글 다듬어줘"라고 해보면 write-human이 잡히는지 확인.

Windows 복사 예시 (PowerShell):
```powershell
Copy-Item -Recurse .\skills\* "$env:USERPROFILE\.claude\skills\"
Copy-Item .\templates\CLAUDE.global.md "$env:USERPROFILE\.claude\CLAUDE.md"
Copy-Item -Recurse .\standards "D:\dev\_standards"
Copy-Item -Recurse .\templates\career-hub "D:\dev\_career"
```

## 3. 계층 원칙 — 중복 금지

**위 계층에 이미 있는 내용을 아래 계층에 다시 쓰지 않는다.**

| 계층 | 담는 것 | 로드 시점 |
|---|---|---|
| `~/.claude/CLAUDE.md` | 정체성·작업 방식 6원칙 | 항상 (모든 세션) |
| `~/.claude/skills/` | 호출형 절차·체크리스트 | 해당 작업일 때만 (토큰 절약) |
| `_standards/` | 템플릿·가드레일 | 링크로 참조될 때만 |
| 프로젝트 `CLAUDE.md` | 그 프로젝트에서만 참인 것, 1페이지 | 그 폴더에서 열 때 |
| 프로젝트 `.claude/skills/` | 그 프로젝트 전용 스킬 | 그 폴더 + 해당 작업 |

프로젝트 CLAUDE.md에 "한국어로 소통" 같은 사용자 선호를 쓰지 말 것 — 전역에 이미 있다.

## 4. 스킬 8개 — 용도와 모델 전략

| 스킬 | 언제 발동 | 모델 힌트 |
|---|---|---|
| idea-shaping | 아이디어 구상·공모전 주제·GO/PIVOT/KILL 판정 | 판정은 Opus+ 권장 |
| arch-budget | 아키텍처·기술 선택 (자원 제약 명시) | 대안 발상은 Opus+ 권장 |
| write-human | 사람에게 보여줄 한국어 글 전부 | 체크리스트라 모델 무관 |
| design-layout | 화면 UI 작업 전부 (토큰 고정) | 수치 규칙이라 모델 무관 |
| research-cited | 사실 주장이 들어가는 모든 조사 | 모델 무관 |
| experience-block | 마일스톤 도달 시 경험 기록 | 모델 무관 |
| jd-fit | 채용공고 분석·갭 계획 | 갭 채움 제안은 Opus+ 권장 |
| sprint-plan | 일정·스프린트·역할분배 (마감 역산) | 분배·기간 추정은 Opus+ 권장 |

설계 철학: 스킬은 판단 위임이 아니라 **고정 절차·표·체크리스트**다. 그래서 Sonnet이 작업해도 품질이 유지된다. 권장 모델 배분 — 설계·감사·최종 퇴고는 Opus급, 체크리스트 기반 구현·반복 작업은 Sonnet, 파일 정리·포맷 변환은 Haiku.

## 5. 커스터마이즈 포인트

- **직무가 다르면**: backend-guardrails.md를 자기 스택 가드레일로 교체 (구조는 유지: 일관성 → 단계 → 보안 표 → 인프라 → CI).
- **커리어 허브 위치**: 스킬들은 `_career\`를 참조한다. 위치를 바꾸면 experience-block·jd-fit의 경로와 전역 CLAUDE.md를 함께 수정.
- **서버 기본값**: arch-budget의 기본 티어(t3.small)를 자기 환경으로.
- **개인화 리포 권장**: 이 키트를 fork/복사한 **프라이빗 리포**를 만들어 자기 버전을 관리하면, 새 PC 세팅이 clone 한 번으로 끝난다. `~/.claude`의 실제 파일과 리포 사이는 복사 스크립트(collect/deploy 2모드)로 동기화하는 방식을 추천.

## 6. 새 PC로 옮길 때

1. 이 리포(또는 개인화 프라이빗 리포) clone.
2. §2 절차 반복.
3. 메모리를 옮기려면: `~/.claude/projects/<경로슬러그>/memory/`가 프로젝트 **절대 경로 기반**이므로, 새 PC에서 같은 경로를 쓰면 그대로 복사, 다르면 새 슬러그 폴더에 `memory/`만 복사.
