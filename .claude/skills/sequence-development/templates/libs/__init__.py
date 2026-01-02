"""
Libs Package - Internal Dependencies

이 폴더에는 시퀀스 실행에 필요한 내부 라이브러리를 포함합니다.
pip로 설치할 수 없는 커스텀 프로토콜, 유틸리티 등을 여기에 배치합니다.

사용법:
    드라이버에서 다음과 같이 import:

    ```python
    import sys
    from pathlib import Path

    _libs_path = Path(__file__).parent.parent / "libs"
    if str(_libs_path) not in sys.path:
        sys.path.insert(0, str(_libs_path))

    from my_protocol import MyClient
    ```
"""
