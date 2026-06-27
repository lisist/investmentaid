import json
import markdown
from pathlib import Path

def build_wiki():
    index_data = []

    # 1. 루트 폴더부터 모든 .md 파일을 재귀적으로 찾습니다.
    for filepath in Path('.').rglob('*.md'):
        
        # HTML 파일 저장 경로 및 URL 설정
        html_filepath = filepath.with_suffix('.html')
        url_path = html_filepath.as_posix()
        title = filepath.name
        
        # 현재 파일의 폴더 깊이(depth) 계산 
        # (예: 최상위 폴더면 depth=0, '태광/노트.md'면 depth=1)
        depth = len(filepath.parts) - 1
        rel_prefix = "../" * depth if depth > 0 else "./"

        # 2. 마크다운 파일 내용 읽기 및 제목 추출
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
            
            # 첫 번째 H1 태그를 제목으로 추출
            for line in md_text.splitlines():
                if line.startswith('# '):
                    title = line.strip('# \n')
                    break
        except Exception as e:
            print(f"파일 읽기 오류 ({filepath}): {e}")
            continue

        # 3. 마크다운을 순수 HTML 요소로 변환
        html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])

        # 4. 검색창과 스타일이 포함된 통합 HTML 템플릿에 본문 삽입
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
    <style>
        .markdown-body {{ 
            box-sizing: border-box; 
            min-width: 200px; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 45px; 
        }}
        /* 📱 모바일 화면 최적화: 여백을 대폭 줄여 가독성 확보 */
        @media (max-width: 767px) {{
            .markdown-body {{ 
                padding: 15px; 
            }}
            #searchInput {{
                font-size: 14px !important;
                padding: 10px !important;
            }}
        }}
    </style>
</head>
<body class="markdown-body">
    
    <div style="margin-bottom: 30px; border-bottom: 2px solid #eaecef; padding-bottom: 20px;">
        <input type="text" id="searchInput" placeholder="다른 리서치 노트 검색 (예: 태광, 삼성전자)" 
               style="width: 100%; padding: 12px; font-size: 16px; border: 1px solid #d1d5da; border-radius: 6px; outline: none; box-sizing: border-box;">
        <ul id="searchResults" style="list-style-type: none; padding: 0; margin-top: 10px;"></ul>
    </div>

    {html_body}

    <script src="{rel_prefix}search_index.js"></script>
    <script>
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const keyword = e.target.value.toLowerCase().trim();
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = ''; 

            if (!keyword) return;

            const filtered = searchData.filter(item => 
                item.title.toLowerCase().includes(keyword)
            );

            filtered.forEach(item => {{
                const li = document.createElement('li');
                li.style.padding = '10px';
                li.style.borderBottom = '1px solid #eaecef';
                
                const a = document.createElement('a');
                a.href = "{rel_prefix}" + item.url; 
                a.textContent = item.title;
                a.style.textDecoration = 'none';
                a.style.color = '#0366d6'; 
                a.style.fontWeight = '600';
                
                li.appendChild(a);
                resultsContainer.appendChild(li);
            }});
        }});
    </script>
</body>
</html>
"""

        # 5. 완성된 HTML 파일 저장
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"변환 완료: {html_filepath}")

        # 6. 검색 인덱스에 데이터 추가 (검색은 새로 만든 html 파일들만 타겟팅합니다)
        index_data.append({
            "title": title,
            "url": url_path
        })
        
    # 7. 검색을 위한 자바스크립트 변수 파일 저장
    with open('search_index.js', 'w', encoding='utf-8') as f:
        f.write("const searchData = ")
        json.dump(index_data, f, ensure_ascii=False, indent=4)
        f.write(";")
    
    print(f"\n✅ 빌드 완료! 총 {len(index_data)}개의 HTML 파일과 1개의 검색 엔진(search_index.js)이 생성되었습니다.")

if __name__ == "__main__":
    build_wiki()