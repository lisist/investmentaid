import json
import markdown
from pathlib import Path

def build_wiki():
    index_data = []

    for filepath in Path('.').rglob('*.md'):
        html_filepath = filepath.with_suffix('.html')
        url_path = html_filepath.as_posix()
        
        # 파일명에서 확장자(.md)를 제외한 이름만 가져옵니다.
        file_name = filepath.stem 
        
        depth = len(filepath.parts) - 1
        rel_prefix = "../" * depth if depth > 0 else "./"

        # [폴더명] 파일명 형태로 조합
        if depth > 0:
            folder_name = filepath.parts[-2]
            display_title = f"[{folder_name}] {file_name}"
        else:
            display_title = file_name 

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
        except Exception as e:
            print(f"파일 읽기 오류 ({filepath}): {e}")
            continue

        html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])

        # 💡 HTML 템플릿: 모바일 대응 CSS, 방향키 하이라이트 CSS 및 최신 JS 로직 통합
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
    <style>
        .markdown-body {{ box-sizing: border-box; min-width: 200px; max-width: 900px; margin: 0 auto; padding: 45px; }}
        
        /* 검색창 기본 스타일 추가 */
        .search-input {{
            box-sizing: border-box; 
            width: 100%;
            padding: 12px 18px;
            font-size: 16px;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            outline: none;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
            transition: border-color 0.25s, box-shadow 0.25s;
        }}
        .search-input:focus {{
            border-color: #0366d6;
            box-shadow: 0 4px 24px rgba(3, 102, 214, 0.15);
        }}
        .results-list {{
            list-style-type: none;
            padding: 0;
            margin-top: 10px;
            max-height: 350px;
            overflow-y: auto;
            background: white;
            border-radius: 6px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            border: 1px solid #e1e4e8;
            box-sizing: border-box; 
        }}
        .results-list:empty {{ border: none; box-shadow: none; }}
        .results-list li {{ border-bottom: 1px solid #eaecef; }}
        .results-list li:last-child {{ border-bottom: none; }}
        .results-list a {{
            display: block;
            padding: 10px 15px;
            text-decoration: none;
            color: #0366d6;
            font-weight: 600;
            font-size: 15px;
            transition: background-color 0.2s;
        }}
        .results-list a:hover {{ background-color: #f6f8fa; color: #0056b3; }}

        /* 💡 키보드 방향키 하이라이트 스타일 */
        .results-list li.active {{
            background-color: #f1f8ff;
            border-left: 4px solid #0366d6;
        }}
        .results-list li.active a {{
            color: #0056b3;
            padding-left: 11px; 
        }}

        @media (max-width: 767px) {{
            .markdown-body {{ padding: 15px; }}
            .search-input {{ font-size: 14px; padding: 10px 14px; }}
        }}
    </style>
</head>
<body class="markdown-body">
    
    <div style="margin-bottom: 30px; border-bottom: 2px solid #eaecef; padding-bottom: 20px;">
        <input type="text" id="searchInput" placeholder="다른 리서치 노트 검색 (예: 삼성전자)" 
               class="search-input" autocomplete="off">
        <ul id="searchResults" class="results-list"></ul>
    </div>

    {html_body}

    <script src="{rel_prefix}search_index.js"></script>
    <script>
        let currentFocus = -1;

        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const keyword = e.target.value.toLowerCase().trim();
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = ''; 
            currentFocus = -1; 

            if (!keyword) return;

            const filtered = searchData.filter(item => 
                item.title.toLowerCase().includes(keyword)
            );

            filtered.forEach((item, index) => {{
                const li = document.createElement('li');
                const a = document.createElement('a');
                
                a.href = "{rel_prefix}" + item.url; 
                a.textContent = item.title;
                
                li.appendChild(a);
                resultsContainer.appendChild(li);

                // 마우스 진입 시 키보드 포커스와 동기화
                li.addEventListener('mouseenter', () => {{
                    currentFocus = index;
                    addActive(resultsContainer.getElementsByTagName('li'));
                }});
            }});
        }});

        // 한글 씹힘 방지 및 엔터 이동 완벽 적용
        document.getElementById('searchInput').addEventListener('keydown', function(e) {{
            if (e.isComposing || e.keyCode === 229) {{
                if (e.key === "Enter") return;
            }}

            const resultsContainer = document.getElementById('searchResults');
            const items = resultsContainer.getElementsByTagName('li');
            
            if (e.key === "ArrowDown" || e.keyCode === 40) {{
                currentFocus++;
                addActive(items);
                e.preventDefault(); 
            }} else if (e.key === "ArrowUp" || e.keyCode === 38) {{
                currentFocus--;
                addActive(items);
                e.preventDefault();
            }} else if (e.key === "Enter" || e.keyCode === 13) {{
                e.preventDefault();
                if (currentFocus > -1 && items[currentFocus]) {{
                    window.location.href = items[currentFocus].querySelector('a').href;
                }}
            }}
        }});

        function addActive(items) {{
            if (!items || items.length === 0) return false;
            removeActive(items);
            
            if (currentFocus >= items.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = items.length - 1;
            
            items[currentFocus].classList.add("active");
            items[currentFocus].scrollIntoView({{ behavior: "smooth", block: "nearest" }});
        }}

        function removeActive(items) {{
            for (let i = 0; i < items.length; i++) {{
                items[i].classList.remove("active");
            }}
        }}
    </script>
</body>
</html>
"""

        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        index_data.append({
            "title": display_title,
            "url": url_path
        })
        
    with open('search_index.js', 'w', encoding='utf-8') as f:
        f.write("const searchData = ")
        json.dump(index_data, f, ensure_ascii=False, indent=4)
        f.write(";")
    
    print(f"\n✅ 빌드 완료! 총 {len(index_data)}개의 파일이 변환되었습니다.")

if __name__ == "__main__":
    build_wiki()