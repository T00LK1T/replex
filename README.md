# Replex

<image src="docs/image.png" width="400">

> tEXT RePLaCE -> replect -> replex

텍스트에 포함된 특정 키워드 A를 B로 변경하는 프로그램입니다.

## 왜 만들었나요?

요즘은 VSCode, InteliJ 같은 좋은 에디터들이 있고, 왠만하면 제공되는 텍스트 치환기능을 사용할 수 있지만,

별 생각 없이 A를 B로 바꾸는경우 원치 않는 변경사항이 발생할 수 있습니다.

## 원치 않는 변경사항?

특정 단어 substring 을 포함하는 성격의 문자열에 대해 치환을 하는경우가 가장 큰 문제가 될 수 있습니다.

예를들어 `Apple`를 `Banana`로 바꾼다고 하면, `Apple`이라는 단어를 포함하는 `PineApple`도 영향을 받아 `PineBanana`로 바뀌게 됩니다.

그래서 이런 경우를 방지해야하는데, 이 프로그램은 이런 경우를 방지할 수 있는 장치가 구현되어있습니다.

## 사용방법

### 설정

`settings.py` 파일에 존재하는 `Environment` 클래스의 멤버값을 수정하고 사용하시면 됩니다.

| 멤버명 | 설명 | 타입 | 예시 |
| --- | --- | --- | --- |
| LOGGING_LEVEL | 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL) | String | INFO |
| SLEEP_BEFORE_GETTING_STARTED | 시작 전 대기 시간 (초) | Integer | 5 |
| EXTENSION | 치환 대상 파일 확장자 | Array\<String\> | ['c', 'h'] |
| REPLACE_MAP | 치환할 키워드 맵 | Map\<String, String\> | {'apple': 'banana'} |
| PROTECTED_KEYWORDS | 치환 대상에서 제외할 키워드 | Array\<String\> | ['Pineapple'] |

### 실행

`input` 디렉터리에 치환이 필요한 파일을 넣고 `main.py`를 실행하면 됩니다.

**파일을 모두 복제하는게 번거롭다면 심볼릭 링크를 생성하신 뒤 사용하시면 됩니다.**

```bash
python main.py
```

### 실행결과

- `result` 디렉터리의 `{yyyymmdd-hhmmss}` 형식의 디렉터리 안에 실행결과가 저장됩니다.
  - `csv`: 치환대상 파일의 라인번호, 각 라인별 문자열 위치, 해당 라인 텍스트 원문을 csv 파일로 저장합니다.
  - `json`: 치환대상의 라인, 컬럼 번호 정보를 참조할 수 있는 json 파일로 저장합니다.
  - `words`: 치환 대상 단어를 모두 저장합니다.
    - `separated`: 각 파일별로 치환 대상 단어를 저장합니다.
    - `total.txt`: 모든 파일의 치환 대상 단어를 저장합니다.
  - `output`: 치환된 파일을 저장합니다.

### 프로젝트 디렉터리 구조

```bash
.
├── README.md
├── main.py
├── input
│   └── test-project
│       ├── hello_world.c
│       └── hello_world.h
├── result
│   └── 20240904-162305
│       ├── codes
│       │   └── test-project
│       │       ├── hello_world.c
│       │       └── hello_world.h
│       ├── words
│       │   ├── total.txt
│       │   └── separated
│       │       └── test-project
│       │           ├── hello_world.c
│       │           └── hello_world.h
│       ├── csv
│       │   └── test-project
│       │       ├── hello_world.c.csv
│       │       └── hello_world.h.csv
│       └── json
│           └── test-project
│               ├── hello_world.c.json
│               └── hello_world.h.json
├── logs
│   └── text-replacer-20240904-162305.log
├── poetry.lock
└── pyproject.toml
```

<!-- markdownlint-configure-file { "MD033": false } -->