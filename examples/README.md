# examples — 실제 산출물·세션 기록

문서로 "좋다"고 주장하는 대신, 이 키트가 실제로 만들어낸 결과를 그대로 둔다.
아래 CLI 출력은 이 리포에서 직접 실행해 붙였다(2026-07).

---

## 1. `kit lint` 가 실제로 잡은 결함 — BOM 혼입

스킬을 늘리다 보면 파일이 서로 다른 에디터로 저장되며 인코딩이 어긋난다.
`interview-prep/SKILL.md` 하나만 UTF-8 **BOM**(`EF BB BF`)으로 저장돼 있었고,
그 탓에 frontmatter 첫 줄 `---`이 `﻿---`로 읽혀 파싱이 깨졌다.
린터가 이걸 에러로 잡았다:

```
$ python -m kit lint
  ok    arch-budget
  ...
  ERROR interview-prep: frontmatter 블록(--- ... ---)이 없거나 닫히지 않았다
  ...
9개 스킬 · 에러 1 · 경고 0
```

BOM을 벗기고 다시 저장한 뒤:

```
$ python -m kit lint
  ok    arch-budget
  ...
  ok    interview-prep
  ...
9개 스킬 · 에러 0 · 경고 0
```

눈으로는 열어봐도 똑같아 보이는 파일이었다. 린터가 없었으면 계속 방치됐을 결함이다.

---

## 2. `kit doctor` — 설치 상태 한눈에

```
$ python -m kit doctor
python      3.13.5
kit         0.1.0
repo        D:\dev\claude-kit-ko
claude dir  C:\Users\dyu87\.claude  있음
스킬        리포 9 · 설치됨 9
CLAUDE.md   있음
lint        통과
```

---

## 3. write-human — before / after

스킬이 실제로 문장을 어떻게 바꾸는지. 왼쪽은 AI 티가 나는 초안, 오른쪽은 Audit 체크리스트를 통과시킨 결과.

### (a) 자기소개서 문단

**Before**
> 이러한 프로젝트를 통해 저는 백엔드 개발 역량을 다양하게 키울 수 있었으며, 협업의 중요성 또한 깨닫게 되었습니다. 앞으로도 지속적인 학습을 통해 더 나은 개발자로 성장해 나가겠습니다.

**After**
> 팀 4명 중 API 서버를 맡았다. 로그인 응답이 느리다는 제보를 받고 프로파일링하니 매 요청마다 권한 테이블을 조인하고 있었다. 캐시로 걷어내 320ms를 90ms로 줄였다. 이때 "느리다"는 체감을 숫자로 바꿔 팀에 공유하는 습관이 생겼다.

(잡은 것: 접속 상투어 "이러한/또한", 번역투 "~를 통해", 포부형 마무리, 모호한 "다양하게" → 구체 수치·마찰로 교체)

### (b) README 소개 문장

**Before**
> 본 프로젝트는 사용자에게 편리하고 직관적인 경험을 제공하는 것을 목표로 하는 혁신적인 서비스입니다.

**After**
> 스터디 모임의 출석·벌금을 자동으로 계산한다. 총무가 매주 엑셀로 하던 정산을 없애려고 만들었다.

(잡은 것: 아첨 형용사 "혁신적인", 3개 묶기 "편리하고 직관적인", 아포리즘 톤 → 무엇을·왜)

### (c) 회고 마무리

**Before**
> 결론적으로 이번 경험은 저에게 매우 값진 시간이었고, 많은 것을 배울 수 있는 소중한 기회였다고 생각합니다.

**After**
> 다시 한다면 인증을 직접 짜지 않고 검증된 라이브러리를 먼저 붙였을 것이다. 3일을 여기서 태웠다.

(잡은 것: 아무 글에나 붙는 막연한 긍정 마무리 → 구체적 다음 행동·후회)

---

## 재현

```powershell
git clone https://github.com/yeon-uu/claude-kit-ko
cd claude-kit-ko
python -m kit lint      # 위 1번 검증
python -m kit doctor    # 위 2번
python -m pytest -q     # 테스트 12개
```

write-human의 before/after는 Claude Code에서 스킬을 켠 뒤
`"이 문단 AI 티 안 나게 다듬어줘: [원문]"` 으로 재현한다.
