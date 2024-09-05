import chardet
from tests.text import KOREAN

def make_cp_949_text_file():
    with open('cp949.txt', 'w', encoding='cp949') as f:
        f.write(KOREAN)

def make_euc_kr_text_file():
    with open('euc-kr.txt', 'w', encoding='euc-kr') as f:
        f.write(KOREAN)


def check_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

if __name__ == '__main__':
    # make_cp_949_text_file()
    # make_euc_kr_text_file()
    encoding_1 = check_encoding('cp949.txt')
    print(f'File encoding: {encoding_1}')
    encoding_2 = check_encoding('euc-kr.txt')
    print(f'File encoding: {encoding_2}')
