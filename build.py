import json
import markdown
from pathlib import Path

def build_wiki():
    index_data = []

    for filepath in Path('.').rglob('*.md'):
        html_filepath = filepath.with_suffix('.html')
        url_path = html_filepath.as_posix()
        
        # 파일명에서 확장자(.md)를 제외한 이름만 가져옵니다. (예: "01-비즈니스모델-버핏시각")
        file_name = filepath.stem 
        
        depth = len(filepath.parts) - 1
        rel_prefix = "../" * depth if depth > 0 else "./"

        # 💡 문서 내용을 무시하고 오직 [폴더명] 파일명 형태로만 조합합니다.
        if depth > 0:
            folder_name = filepath.parts[-2]
            display_title = f"[{folder_name}] {file_name}"
        else:
            display_title = file_name # 최상위 폴더 파일인 경우

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
        except Exception as e:
            print(f"파일 읽기 오류 ({filepath}): {e}")
            continue

        html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])

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
        @media (max-width: 767px) {{
            .markdown-body {{ padding: 15px; }}
            #searchInput {{ font-size: 14px !important; padding: 10px !important; }}
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

        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 검색 인덱스에도 새로 만든 직관적인 이름을 저장합니다.
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