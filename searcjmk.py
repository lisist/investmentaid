import json
from pathlib import Path

def build_search_index():
    index_data = []
    
    for filepath in Path('.').rglob('*.md'):
        html_filepath = filepath.with_suffix('.html').as_posix()
        title = filepath.name 
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('# '):
                        title = line.strip('# \n')
                        break
        except Exception as e:
            print(f"파일을 읽는 중 오류 발생 ({filepath}): {e}")
            continue
        
        index_data.append({
            "title": title,
            "url": html_filepath
        })
        
    # 변경 포인트: json.dump 대신 자바스크립트 변수 형태로 .js 파일에 저장
    with open('search_index.js', 'w', encoding='utf-8') as f:
        f.write("const searchData = ")
        json.dump(index_data, f, ensure_ascii=False, indent=4)
        f.write(";")
    
    print(f"총 {len(index_data)}개의 종목 인덱스가 'search_index.js'에 저장되었습니다.")

if __name__ == "__main__":
    build_search_index()