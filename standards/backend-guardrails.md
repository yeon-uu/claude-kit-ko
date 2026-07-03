# backend-guardrails — FastAPI + Docker 공통 가드레일

모든 백엔드 프로젝트에 공통 적용. 프로젝트 CLAUDE.md에는 이 파일 링크만 넣고 내용을 복제하지 않는다.

## 1. 파일 간 일관성 — 바이브코딩 최다 사고 지점

AI가 파일 단위로 생성하면 파일 간 불일치가 생긴다. 생성·수정 후 반드시 대조:
- SQLAlchemy 모델 필드명 == Pydantic 스키마 == 프론트 JS 필드명
- `config.py` 환경변수명 == `docker-compose.yml` == `.env.example` 키
- 라우터 URL 경로 == 프론트 fetch URL / 서비스 리턴 타입 == 라우터 기대 타입

## 2. 한 번에 1개씩

기능 전체가 아니라 **모델 → 스키마 → 서비스 → 라우터 → 프론트 연동** 순으로, 한 단계 동작 확인 후 다음. 과잉 생성(미사용 관리자 페이지·통계 API) 금지.

## 3. async 일관성

비동기 스택에서는 모든 DB 접근·httpx 호출이 `async def` + `await`. 한 함수 안에서 동일 DB 세션 사용(세션 분리 금지). sync 함수 안 await 금지.

## 4. 보안 — 생성 시점에 적용 (사후 추가 금지)

| 항목 | 규칙 |
|---|---|
| 리소스 소유권 | 접근 시 `resource.user_id == current_user.id` 검증 (OWASP A01) |
| 쿼리 | ORM이라도 raw SQL은 반드시 파라미터화 |
| XSS | 외부 입력·LLM 출력은 저장 전 `html.escape()`, 프론트는 `textContent`만 — `innerHTML` 금지 |
| Rate limit | 비용 나가는 엔드포인트(LLM 호출 등)에 slowapi 등으로 제한 |
| 시크릿 | 코드·**설정 파일(.mcp.json, compose 포함)** 하드코딩 금지. 환경변수로만. JWT secret 최소 256-bit. 같은 키를 여러 파일에 복제 금지 |
| CORS | FastAPI `CORSMiddleware` 한 곳에서만. 와일드카드(*) 금지 |
| 에러 응답 | 500에 스택 트레이스·내부 정보 노출 금지 |
| HTTPS | 공개 배포 시 Nginx에서 HTTP→HTTPS 리다이렉트 |

## 5. Docker

- 컨테이너 간 DB 연결은 `localhost:5432`가 아니라 서비스명(`db:5432`).
- `depends_on`만으로 불충분 → healthcheck + `condition: service_healthy`.
- 환경변수 진실 소스는 `.env.example` — 코드 기본값과 충돌하지 않게 통일.

## 6. 트랜잭션 무결성

연쇄 상태 변경(예: 완료 처리 → 보상 지급)은 한 트랜잭션으로 묶고, UNIQUE 위반 등 IntegrityError는 409로 응답.

## 7. SSE / 스트리밍

- Nginx `proxy_buffering off` 필수 (없으면 한 번에 몰아서 도착).
- 응답 헤더: `text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`.
- 프론트 `EventSource`는 에러 핸들링 + 타임아웃 처리, 스트림 중단 시 에러 이벤트 전송.

## 8. 외부 API는 실패한다고 가정

공공 API·LLM 호출은 타임아웃 + 실패 시 fallback을 설계 단계에 포함 (Design for Failure).

## 9. CI 최소선

첫 커밋부터 GitHub Actions에 ruff + pytest. 포매터·린터는 사람 손이 아니라 CI가 잡게 한다.
