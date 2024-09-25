import json
import logging
import os
import pathlib
import platform
import re
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from typing import Annotated

from settings import Environment

BASE_PATH = pathlib.Path(__file__).parent
CODE_PATH = BASE_PATH / "input"
RESULT_PATH = BASE_PATH / "result" / datetime.now().strftime("%Y%m%d-%H%M%S")
LOG_PATH = BASE_PATH / "logs"
CSV_PATH = RESULT_PATH / "csv"
JSON_PATH = RESULT_PATH / "json"
TARGET_WORD_PATH = RESULT_PATH / "words"
SEPARATED_WORD_PATH = TARGET_WORD_PATH / "separated"
NEW_CODE_PATH = RESULT_PATH / "output"

ENSURE_PATH_LIST = [
    CODE_PATH,
    LOG_PATH,
    CSV_PATH,
    JSON_PATH,
    NEW_CODE_PATH,
    SEPARATED_WORD_PATH,
]

ALLOWED_ENCODING = Environment.ALLOWED_ENCODING
SLEEP_BEFORE_GETTING_STARTED = Environment.SLEEP_BEFORE_GETTING_STARTED
REPLACE_MAP = Environment.REPLACE_MAP
EXTENSION = Environment.EXTENSION
PROTECTED_KEYWORDS = Environment.PROTECTED_KEYWORDS
KEYWORD_LIST = list(REPLACE_MAP.keys())
REGEX_PATTERN = r"[ \t\n\r\f\v_();}{.-=*~\\<>,\"/\' []+"

# NOTE: global unique text set
unique_text_set = set()


# NOTE: 로그 포맷 설정
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.setLevel(Environment.LOGGING_LEVEL)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


@dataclass
class KeywordMeta:
    """
    키워드 위치 정보를 저장할 데이터 클래스

    NOTE: 텍스트북 정보를 저장하기위해 사용하기도 합니다.
    자료구조가 크게 다르지 않기 때문에 같이 사용하기로 했습니다.
    사용목적이나 기획이 변경되는경우 분리해주세요.
    """

    filepath: Annotated[pathlib.Path, "파일 경로"]
    original_text: Annotated[str, "키워드가 포함된 텍스트 라인"]
    keyword: Annotated[str, "찾은 키워드"]
    line: Annotated[int, "라인 번호"]
    pos: Annotated[int | None, "해당 라인의 키워드 시작 위치"] = None

    def __str__(self):
        """
        CSV 파일에 저장하기 위해 문자열 포맷으로 변환합니다.
        """
        return (
            f"{self.filepath.name}\t"
            f"{self.line}\t"
            f"{self.pos}\t"
            f"{self.keyword}\t"
            f"{self.original_text}"
        )

    def __dict__(self):
        """
        JSON 형식으로 사용할경우 대응하기 위해 딕셔너리 포맷으로 변환합니다.
        """
        return {
            "filename": self.filepath.name,
            "line": self.line,
            "pos": self.pos,
            "keyword": self.keyword,
            "original_text": self.original_text,
        }

    def minify(self):
        """
        원본 텍스트만 확인하기위해 사용합니다.
        """
        return self.original_text


def get_all_paths_with_symlinks(
    directory: pathlib.Path, extensions: list[str]
) -> list[pathlib.Path]:
    all_paths = []
    for root, dirs, files in os.walk(directory, followlinks=True):
        for name in dirs + files:
            full_path = os.path.realpath(os.path.join(root, name))
            path_obj = pathlib.Path(full_path)
            if extensions:  # 확장자 필터링
                if path_obj.is_file() and path_obj.suffix[1:] in extensions:
                    all_paths.append(path_obj)
            else:
                if path_obj.is_file():
                    all_paths.append(path_obj)
    return all_paths


def get_relative_target_path(
    filepath: pathlib.Path,
    target_path: pathlib.Path,
) -> pathlib.Path:
    dir_path = filepath.parent

    try:
        relative_path = dir_path.relative_to(BASE_PATH)
        # NOTE: 결과디렉터리에 생성되는 디렉터리 구조를 단순화하기위해
        # 가장 상위레벨 디렉터리를 제거하기위한 코드 작성
        if len(relative_path.parts) > 1:
            relative_path = pathlib.Path(*relative_path.parts[1:])
    except ValueError:
        # NOTE: subpath가 아닌경우
        match platform.system():
            case "Windows":
                absolute_path = dir_path.absolute()
                # NOTE: 드라이브 경로를 포함하면서 콜론이 포함되어 경로 계산시 에러발생
                colon_removed_path = absolute_path.as_posix().replace(":", "")
                relative_path = f"{target_path.as_posix()}/{colon_removed_path}"
            case _:
                relative_path = f"{target_path.as_posix()}/{dir_path.absolute()}"

    relative_target_path = target_path / relative_path / f"{filepath.name}"
    ensure_path_exists(relative_target_path.parent)
    return relative_target_path


def save_log_as_xlsx(
    keyword_meta_list: Annotated[list[KeywordMeta], "키워드 위치정보 목록"],
):
    """
    xlsx 파일로 키워드 위치 정보를 저장합니다.

    패키지 설치를 안내해야하기 때문에, 기능으로 제공하지 않을 예정이었습니다.
    필요하다면 패키지 설치 후 사용해주세요.
    """
    try:
        # pylint: disable=import-outside-toplevel
        import xlsxwriter
    except ImportError:
        logger.error("🔴 xlsxwriter 패키지가 설치되어 있지 않습니다.")
        logger.info("🟡 패키지 설치후 사용해주세요")
        logger.info("\tpip 사용자 -> pip install xlsxwriter")
        logger.info("\tpoetry 사용자 -> poetry add xlsxwriter")
        return
    if not keyword_meta_list:
        return
    XLSX_PATH = RESULT_PATH / "xlsx"
    ensure_path_exists(XLSX_PATH)

    filepath = keyword_meta_list[0].filepath
    xlsx_path = get_relative_target_path(
        filepath=filepath,
        target_path=XLSX_PATH,
    )

    workbook = xlsxwriter.Workbook(xlsx_path)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({"bold": True})

    worksheet.write("A1", "filename", bold)
    worksheet.write("B1", "line", bold)
    worksheet.write("C1", "pos", bold)
    worksheet.write("D1", "keyword", bold)
    worksheet.write("E1", "original_text", bold)

    for i, keyword_meta in enumerate(keyword_meta_list, start=1):
        worksheet.write(f"A{i}", keyword_meta.filepath.name)
        worksheet.write(f"B{i}", keyword_meta.line)
        worksheet.write(f"C{i}", keyword_meta.pos)
        worksheet.write(f"D{i}", keyword_meta.keyword)
        worksheet.write(f"E{i}", keyword_meta.original_text)

    workbook.close()


def save_log_as_csv(
    keyword_meta_list: Annotated[list[KeywordMeta], "키워드 위치정보 목록"],
):
    """
    키워드 위치 정보를 CSV 파일로 저장합니다.
    """
    if not keyword_meta_list:
        return
    filepath = keyword_meta_list[0].filepath
    csv_path = get_relative_target_path(
        filepath=filepath,
        target_path=CSV_PATH,
    )
    csv_path_with_ext = f"{csv_path}.csv"

    # logger.info(csv_path)
    with open(csv_path_with_ext, mode="w", encoding="utf-8") as c:
        HEADER = "filename\tline\tpos\tkeyword\toriginal_text\n"
        c.write(HEADER)
        sorted_keyword_meta_list_by_line = sorted(
            keyword_meta_list, key=lambda x: (x.line, x.pos)
        )
        for keyword_meta in sorted_keyword_meta_list_by_line:
            c.write(f"{keyword_meta}\n")


def save_log_as_json(
    keyword_meta_list: Annotated[list[KeywordMeta], "키워드 위치정보 목록"],
):
    """
    키워드 위치 정보를 JSON 파일로 저장합니다.
    """
    if not keyword_meta_list:
        return
    filepath = keyword_meta_list[0].filepath
    json_path = get_relative_target_path(
        filepath=filepath,
        target_path=JSON_PATH,
    )
    json_path_with_ext = f"{json_path}.json"
    line_pos_map = _reform_keyword_meta_as_line_pos_map(keyword_meta_list)
    with open(json_path_with_ext, "w", encoding="utf-8") as json_file:
        json.dump(line_pos_map, json_file, ensure_ascii=False, indent=2)


def save_textbook(
    textbook_list: Annotated[list[KeywordMeta], "텍스트북 목록"],
):
    """
    텍스트북 정보를 파일로 저장합니다.
    """
    if not textbook_list:
        return

    filepath = textbook_list[0].filepath
    textbook_path = get_relative_target_path(
        filepath=filepath,
        target_path=SEPARATED_WORD_PATH,
    )
    textbook_path_with_ext = f"{textbook_path}.txt"
    written_text = []
    with open(textbook_path_with_ext, "w", encoding="utf-8") as f:
        for textbook in textbook_list:
            text = textbook.minify()
            unique_text_set.add(text)
            if text in written_text:
                continue
            f.write(f"{text}\n")
            written_text.append(text)
    logger.debug("🟢 각 파일의 텍스트북을 저장했습니다.")
    logger.debug("\t%s", textbook_path)


def save_unique_textbook():
    """
    글로벌 선언된 unique_text_set을 참조하여 텍스트북을 저장합니다.
    """
    if not unique_text_set:
        return
    unique_text_path = TARGET_WORD_PATH / "total.txt"
    with open(unique_text_path, "w", encoding="utf-8") as f:
        for text in unique_text_set:
            f.write(f"{text}\n")
    logger.debug("🟢 전체 텍스트북의 고유값만 추출하여 저장했습니다.")
    logger.debug("\t%s", unique_text_path)


def read_file(
    filepath: Annotated[pathlib.Path, "파일 경로"],
) -> Annotated[str, "파일 내용"]:
    """
    파일을 읽어서 내용을 반환합니다.
    """
    for encoding in ALLOWED_ENCODING:
        with open(filepath, mode="r", encoding=encoding) as f:
            logger.info("🟡 파일 내용 읽음 -> %s ", filepath)
            try:
                return f.read()
            except UnicodeDecodeError:
                logger.debug("🟡 %s 인코딩으로 읽기 실패", encoding)
                continue
    with open(filepath, mode="r", encoding="utf-8", errors="ignore") as f:
        logger.warning("🟡 지원하지 않는 문자열 확인 -> %s ", filepath)
        logger.warning("🟡 기록된 파일과 원본을 대조해주세요")
        return f.read()


def find_similler_words(
    filepath: Annotated[pathlib.Path, "파일 이름, redundant"],
    keyword: Annotated[str, "매칭 대상 키워드"],
    line: Annotated[str, "키워드가 포함된 문자열"],
    line_no: Annotated[int, "키워드가 포함된 라인 번호"],
) -> list[KeywordMeta]:
    """
    정규표현식을 기준으로 매칭하여 분리된 키워드 목록을 반환합니다.

    NOTE:
    단순히 텍스트 목록을 반환하는데 의미를 두기 때문에
    pos를 계산하는 로직은 생략합니다.
    """
    splitted_words = re.split(
        pattern=REGEX_PATTERN,
        string=line,
    )
    textbook_list = []
    for word in splitted_words:
        if not word:
            continue
        if word.find(keyword) != -1:
            logger.debug(
                "\t🟡 %s: %s: %s 키워드와 유사한 단어 %s 를 찾았습니다.",
                filepath.name,
                line_no,
                keyword,
                word,
            )
            textbook_list.append(
                KeywordMeta(
                    filepath=filepath,
                    original_text=word,
                    keyword=keyword,
                    line=line_no,
                    pos=None,
                )
            )
    return textbook_list


def find_keyword(
    filepath: Annotated[pathlib.Path, "파일 이름 (redundant)"],
    text: Annotated[str, "파일 내용"],
    target_keyword: Annotated[str, "찾을 키워드"],
    protected_keywords: Annotated[list[str], "보호할 키워드 리스트"],
) -> Annotated[
    tuple[list[KeywordMeta], list[KeywordMeta]], "키워드 위치, 텍스트북 목록"
]:
    """
    텍스트에서 키워드를 찾아서 위치 정보를 반환합니다.

    이 과정에서 protected_keywords에 포함된 키워드는 무시합니다.
    """
    keywords_ = []
    temp_textbook_list_ = []

    lines = text.split("\n")

    for i, line in enumerate(lines, start=1):
        line_ = line
        if target_keyword not in line_:
            continue
        for protected_keyword in protected_keywords:
            if protected_keyword in line_:
                line_ = line_.replace(protected_keyword, " " * len(protected_keyword))
                logger.debug("🟡 %s 키워드를 보호합니다.", protected_keyword)
                logger.debug("🟡 -> %s", line)
        pos = 0

        temp_textbook_list_.extend(
            find_similler_words(
                filepath=filepath,
                keyword=target_keyword,
                line=line,
                line_no=i,
            )
        )

        while True:
            pos = line_.find(target_keyword, pos)
            if pos == -1:
                break
            keywords_.append(
                KeywordMeta(
                    filepath=filepath,
                    original_text=line,
                    keyword=target_keyword,
                    line=i,
                    pos=pos,
                )
            )
            pos += len(target_keyword)
    return keywords_, temp_textbook_list_


def find_keywords(
    filepath: Annotated[pathlib.Path, "파일 이름 (redundant)"],
    text: Annotated[str, "파일 내용"],
    target_keywords: Annotated[list[str], "찾을 키워드 리스트"],
    protected_keywords: Annotated[list[str], "보호할 키워드 리스트"],
) -> Annotated[
    tuple[list[KeywordMeta], list[KeywordMeta]], "키워드 위치, 텍스트북 목록"
]:
    keywords_ = []
    temp_textbook_list_ = []
    for keyword in target_keywords:
        keywords, textbook_list = find_keyword(
            filepath=filepath,
            text=text,
            target_keyword=keyword,
            protected_keywords=protected_keywords,
        )
        keywords_ += keywords
        temp_textbook_list_ += textbook_list
    return keywords_, temp_textbook_list_


def ensure_path_exists(path: Annotated[pathlib.Path, "디렉터리 경로"]):
    """
    전달된 경로의 디렉터리가 존재하지 않으면 생성합니다.
    """
    if not path.exists():
        path.mkdir(parents=True)


def _reform_keyword_meta_as_line_pos_map(
    keyword_meta_list: Annotated[list[KeywordMeta], "키워드 위치정보 목록"],
):
    """
    키워드 위치 정보를 라인별로 그룹화합니다.
    """
    line_pos_map = {}
    for keyword_meta in keyword_meta_list:
        if keyword_meta.line not in line_pos_map:
            line_pos_map[keyword_meta.line] = {}
        if keyword_meta.keyword not in line_pos_map[keyword_meta.line]:
            line_pos_map[keyword_meta.line][keyword_meta.keyword] = []
        line_pos_map[keyword_meta.line][keyword_meta.keyword].append(keyword_meta.pos)
    return line_pos_map


def _replace_keyword(
    text: Annotated[str, "원본 텍스트"],
    keyword_meta_list: Annotated[list[KeywordMeta], "키워드 위치정보 목록"],
):
    line_pos_map = _reform_keyword_meta_as_line_pos_map(
        keyword_meta_list,
    )
    new_lines = []
    for i, line in enumerate(text.split("\n"), 1):
        if i not in line_pos_map:
            new_lines.append(line)
            continue
        accumulated_pos_delta = 0
        target_pos_list = []
        for keyword, pos_list in line_pos_map[i].items():
            for pos in pos_list:
                target_pos_list.append((keyword, pos))
        sorted_target_pos_list = sorted(target_pos_list, key=lambda x: x[1])
        for keyword, pos in sorted_target_pos_list:
            logger.debug("keyword, pos -> %s, %s", keyword, pos)
            pos += accumulated_pos_delta
            # len(REPLACE_MAP[keyword])는 모두 다름
            new_keyword = REPLACE_MAP[keyword]
            new_keyword_len = len(new_keyword)
            line = line[:pos] + new_keyword + line[pos + len(keyword):]
            accumulated_pos_delta += new_keyword_len - len(keyword)
        new_lines.append(line)
    return "\n".join(new_lines)


def replace_keyword(
    filepath: Annotated[pathlib.Path, "파일 이름"],
    text: Annotated[str, "원본 텍스트"],
    keyword_meta_list: Annotated[list[KeywordMeta], "키워드 위치정보 목록"],
):
    code_path = get_relative_target_path(
        filepath=filepath,
        target_path=NEW_CODE_PATH,
    )
    result = _replace_keyword(text, keyword_meta_list)
    filename = filepath.name
    logger.info("🟡 키워드 치환 -> %s", filename)
    with open(code_path, mode="w", encoding="utf-8") as f:
        logger.info("🟢 파일 저장 -> %s", code_path)
        f.write(result)


if __name__ == "__main__":
    # NOTE: file 형식의 로그가 저장되기 이전에 디렉터리가 존재해야합니다.
    _ = [ensure_path_exists(path) for path in ENSURE_PATH_LIST]

    file_handler = logging.FileHandler(
        LOG_PATH / f'text-replacer-{datetime.now().strftime("%Y%m%d-%H%M%S")}.log',
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("🟢 작업을 수행할 경로는 %s 입니다.", CODE_PATH)

    filepath_list = get_all_paths_with_symlinks(CODE_PATH, EXTENSION)

    for filepath_ in filepath_list:
        logger.info("🟢 작업 목록 확인 -> %s", filepath_)

    for sec in range(SLEEP_BEFORE_GETTING_STARTED):
        logger.info(
            "🟡 %d초 뒤에 작업을 시작합니다.", SLEEP_BEFORE_GETTING_STARTED - sec
        )
        sleep(1)

    for filepath_ in filepath_list:
        filename_ = filepath_.name
        text_ = read_file(filepath_)
        keyword_meta_list_, textbook_list_ = find_keywords(
            filepath=filepath_,
            text=text_,
            target_keywords=KEYWORD_LIST,
            protected_keywords=PROTECTED_KEYWORDS,
        )
        save_textbook(textbook_list_)
        save_unique_textbook()
        save_log_as_csv(keyword_meta_list_)
        save_log_as_json(keyword_meta_list_)
        # NOTE: 엑셀 저장기능이 필요하다면 주석을 해제하세요.
        # save_log_as_xlsx(keyword_meta_list_)
        logger.debug(
            "🟢 %s 파일에서 키워드 %s 개 찾았습니다.",
            filename_,
            len(keyword_meta_list_),
        )
        replace_keyword(
            filepath=filepath_,
            text=text_,
            keyword_meta_list=keyword_meta_list_,
        )

    logger.info("🔴 작업이 완료되었습니다.")
