"""claude-kit-ko — 스킬 설치·검증 CLI.

마크다운 스킬 뭉치를 실제로 돌아가는 도구로 묶는다.
표준 라이브러리만 사용한다(외부 의존성 없음).
"""

# cli 모듈이 이 값을 import하므로 하위 모듈 import보다 먼저 정의한다(순환 방지).
__version__ = "0.1.0"

from .cli import main  # noqa: E402

__all__ = ["main", "__version__"]
