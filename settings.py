class Environment:
    # NOTE: INFO, DEBUG, WARNING, ERROR, CRITICAL
    LOGGING_LEVEL = "INFO"
    """
    필요한경우 이 클래스의 내용을 수정하여 사용합니다.
    """
    # 시작전 대기시간
    SLEEP_BEFORE_GETTING_STARTED = 1

    # 처리대상파일 확장자
    EXTENSION = [
        "c",
        "h",
    ]

    # # 변경되면 안되는 텍스트 목록
    # PROTECTED_KEYWORDS = []

    # # 변경해야할 텍스트의 before, after 목록
    # REPLACE_MAP = {
    #     "EGIS": "HELLO",
    #     "Egis": "Hello",
    #     "egis": "hello",
    # }

    PROTECTED_KEYWORDS = [
    "Register",
    "REGISTER",
    "register",
    # 여기 변경되지 말아야할 키워드 추가
    ]

    # 변경해야할 텍스트의 before, after 목록
    REPLACE_MAP = {
    "egis": "ㄱㄴㄷㄹㅁ",
    "Egis": "1234567890123",
    "EGIS": "abcdefghi",
    # 여기 변경되어야할 before: after 추가
    }

    ALLOWED_ENCODING = [
        "utf-8",
        "cp949",
        "euc-kr",
    ]
