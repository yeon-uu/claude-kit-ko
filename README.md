# claude-kit-ko

**한국어 사용자를 위한 Claude Code 스킬 + 프로젝트 표준 키트.**
AI 티 안 나는 한국어 글쓰기, 자원 제약 아키텍처 설계, 출처 규율, 공모전 아이디어 검증, 경험블록→JD 매칭 커리어 파이프라인까지 — 바로 복사해서 쓰는 7개 스킬과 문서 표준.

## 왜 만들었나

인기 Claude 스킬들(humanizer 등)은 영어권 전제다. em dash 제거, "delve" 금지 같은 규칙은 한국어 글에 무의미하고, 이력서 스킬은 미국 경력자 시장을 가정한다. 이 키트는 검증된 인기 스킬들의 **구조 규칙만 이식**하고 한국어·한국 취준·공모전 맥락으로 다시 썼다:

- 어미 3연속 반복, 번역투("~를 통해"), 만연체, 포부형 마무리 — 한국어 AI 티의 실제 패턴을 체크리스트화
- 자료조사 출처 등급에 공공데이터포털·KOSIS·국가법령정보센터 등 한국 1차 출처 계층 반영
- 공모전 트랙: 심사기준 배점 역산 → 역대 수상작 차별화 검증 → 레드오션 체크
- 채용공고의 "자격요건/우대사항" 언어 마커 기반 추출 → 경험블록 매핑 → 갭 채움 계획

## 구성

```
skills/        ← ~/.claude/skills/ 에 복사하는 7개 스킬
standards/     ← 프로젝트 문서 표준 4종 (dev 루트 _standards/ 로)
templates/     ← 전역 CLAUDE.md 템플릿 + 커리어 허브 골격
SETUP.md       ← 설치·계층 원칙·모델 전략·새 PC 이전 가이드
```

| 스킬 | 한 줄 |
|---|---|
| **write-human** | Draft→Audit→Revise 프로세스 + 한국어 16개 체크리스트로 AI 티 제거 |
| **research-cited** | 모든 사실 문장 = 출처 링크 / [추정] / [unverified] 셋 중 하나. 반대 증거 의무 탐색 |
| **idea-shaping** | 공모전/상업 분기 → 심사기준 역산 or RAT 검증 → GO/PIVOT/KILL 냉정 판정 |
| **arch-budget** | 서버 티어→메모리 예산 환산, 대안 2~3개 강제 비교, YAGNI 목록, ADR 기록 |
| **design-layout** | 디자인 토큰 파일 고정으로 세션 간 드리프트 방지 + 4/8px·WCAG 수치 규칙 |
| **experience-block** | 프로젝트→키워드/문제/해결/성과(수치 플래그)/STAR 정형 기록 |
| **jd-fit** | JD 요구사항 추출 → 경험 증거 매핑 → 적합성 점수 → 갭별 채움 계획 |

| 표준 문서 | 한 줄 |
|---|---|
| CLAUDE-template.md | 프로젝트 CLAUDE.md 1페이지 템플릿 (상태·목적분류 필수) |
| docs-structure.md | PLAN / DEVLOG / EXPERIENCE / adr 문서 구조 |
| memory-format.md | 에이전트 메모리 정형 포맷 (중복 저장 금지 규칙 포함) |
| backend-guardrails.md | FastAPI+Docker 가드레일 — 다른 스택이면 구조만 유지하고 교체 |

## 퀵스타트

```powershell
git clone https://github.com/<you>/claude-kit-ko
cd claude-kit-ko
Copy-Item -Recurse .\skills\* "$env:USERPROFILE\.claude\skills\"
Copy-Item .\templates\CLAUDE.global.md "$env:USERPROFILE\.claude\CLAUDE.md"   # <> 채우기
```
나머지(표준 문서, 커리어 허브, 계층 원칙)는 [SETUP.md](SETUP.md).

## 설계 원칙

1. **스킬은 판단 위임이 아니라 고정 절차** — 체크리스트·표·점수 공식으로 써서 Sonnet이 실행해도 품질이 유지된다.
2. **계층 중복 금지** — 전역 CLAUDE.md(항상 로드) / 스킬(호출 시) / 표준(참조 시) / 프로젝트 CLAUDE.md(1페이지)의 역할을 나눠 토큰을 아낀다.
3. **냉정 우선** — 응원 대신 약점 먼저. idea-shaping에는 KILL 판정이, jd-fit에는 "지원 비추천" 밴드가 내장돼 있다.
4. **수치는 출처와 함께** — [측정]/[추정]/[내부] 플래그 없는 숫자는 쓰지 않는다.

## 크레딧

이 키트의 스킬은 15개 공개 프로젝트(전부 MIT/Apache-2.0)의 **방법·구조를 참고**해 한국어 맥락으로 **새로 작성**했다. 원문을 복제하지 않았고 저작권이 보호하지 않는 절차·체크리스트 개념만 차용했다. 출처별 라이선스와 참고 부분은 [CREDITS.md](CREDITS.md)에 표로 정리했다.

## 면책

이 프로젝트는 개인이 만든 비공식 키트로, **Anthropic의 공식 제품이 아니며 Anthropic과 제휴·후원 관계가 없다.** "Claude"는 Anthropic의 상표이며, 여기서는 Claude Code와의 호환성을 설명하기 위해 지시적으로만 사용한다.

## 라이선스

MIT — [LICENSE](LICENSE) 참고. 본인 저작물이 부적절하게 반영됐다고 판단하는 저자는 이슈로 알려주면 즉시 반영한다.
