#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Withforce MES 사양서 - Markdown to Premium PDF 변환
"""

import re
import base64
import urllib.parse
import urllib.request
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def mermaid_to_image_data_url(mermaid_code):
    """Mermaid 코드를 Data URL 형식의 이미지로 변환"""
    try:
        encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        url = f"https://mermaid.ink/img/{encoded}"

        with urllib.request.urlopen(url, timeout=15) as response:
            image_data = response.read()
            b64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/png;base64,{b64_data}"
    except Exception as e:
        print(f"[WARNING] Mermaid 다이어그램 변환 실패: {e}")
        return None


def parse_markdown_to_html(md_content):
    """Markdown을 HTML로 변환"""
    lines = md_content.split('\n')
    html_parts = []

    in_code_block = False
    code_lines = []
    code_language = ''
    in_table = False
    table_headers = None
    table_rows = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # 코드 블록
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_language = line[3:].strip()
                code_lines = []
            else:
                in_code_block = False

                if code_language.lower() == 'mermaid':
                    mermaid_code = '\n'.join(code_lines)
                    image_url = mermaid_to_image_data_url(mermaid_code)

                    if image_url:
                        html_parts.append(f'<div class="diagram-container"><img src="{image_url}" alt="Mermaid Diagram" class="mermaid-diagram"/></div>')
                    else:
                        html_parts.append('<div class="callout warning">⚠ 다이어그램: 원본 마크다운 참조</div>')
                else:
                    html_parts.append(f'<div class="code-block">')
                    if code_language:
                        html_parts.append(f'<div class="code-lang">{code_language.upper()}</div>')
                    html_parts.append(f'<pre><code>{escape_html("\\n".join(code_lines))}</code></pre>')
                    html_parts.append('</div>')

                code_lines = []
                code_language = ''

            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # 테이블 종료 감지
        if in_table and not (line.startswith('|') or re.match(r'^\s*$', line)):
            if table_rows:
                html_parts.append(create_table_html(table_headers, table_rows))
            in_table = False
            table_headers = None
            table_rows = []

        # 테이블 시작
        if line.startswith('|') and not in_table:
            cells = [cell.strip() for cell in line.strip('|').split('|')]

            # 다음 줄이 구분선인지 확인
            if i + 1 < len(lines) and re.match(r'^\|[\s:-]+\|', lines[i + 1]):
                table_headers = cells
                in_table = True
                i += 2  # 헤더와 구분선 건너뛰기
                continue

        # 테이블 데이터 행
        if in_table and line.startswith('|'):
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            table_rows.append(cells)
            i += 1
            continue

        # 제목
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()

            if level == 1:
                html_parts.append(f'<h1 class="heading-1">{escape_html(text)}</h1>')
            elif level == 2:
                html_parts.append(f'<h2 class="heading-2">{escape_html(text)}</h2>')
            elif level == 3:
                html_parts.append(f'<h3 class="heading-3">{escape_html(text)}</h3>')
            elif level == 4:
                html_parts.append(f'<h4 class="heading-4">{escape_html(text)}</h4>')

        # 리스트
        elif re.match(r'^\s*[-*+]\s+', line):
            text = re.sub(r'^\s*[-*+]\s+', '', line)
            html_parts.append(f'<li class="bullet-item">{format_inline(text)}</li>')

        elif re.match(r'^\s*\d+\.\s+', line):
            text = re.sub(r'^\s*\d+\.\s+', '', line)
            html_parts.append(f'<li class="number-item">{format_inline(text)}</li>')

        # 빈 줄
        elif re.match(r'^\s*$', line):
            html_parts.append('<br/>')

        # 일반 텍스트
        else:
            if line.strip():
                html_parts.append(f'<p>{format_inline(line)}</p>')

        i += 1

    # 마지막 테이블 처리
    if in_table and table_rows:
        html_parts.append(create_table_html(table_headers, table_rows))

    return '\n'.join(html_parts)


def create_table_html(headers, rows):
    """테이블 HTML 생성"""
    html = ['<table class="styled-table">']

    # 헤더
    html.append('<thead><tr>')
    for header in headers:
        html.append(f'<th>{escape_html(header)}</th>')
    html.append('</tr></thead>')

    # 데이터 행
    html.append('<tbody>')
    for idx, row in enumerate(rows):
        row_class = 'even' if idx % 2 == 1 else 'odd'
        html.append(f'<tr class="{row_class}">')
        for cell in row:
            html.append(f'<td>{escape_html(cell)}</td>')
        html.append('</tr>')
    html.append('</tbody>')

    html.append('</table>')
    return '\n'.join(html)


def format_inline(text):
    """인라인 포맷팅 적용"""
    # **bold**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # `code`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # *italic*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

    return text


def escape_html(text):
    """HTML 이스케이프"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def create_premium_css():
    """Minimal Datasheet 스타일 CSS (ST 스타일)"""
    return """
    @page {
        size: A4;
        margin: 2.5cm 2cm 2cm 2cm;

        @top-right {
            content: "Withforce MES 사양서 v2.0";
            font-size: 9pt;
            color: #808080;
            font-family: 'Malgun Gothic', sans-serif;
        }

        @bottom-right {
            content: counter(page) " / " counter(pages);
            font-size: 9pt;
            color: #808080;
        }
    }

    body {
        font-family: 'Malgun Gothic', 'Calibri', sans-serif;
        font-size: 10pt;
        line-height: 1.35;
        color: #333;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    /* 표지 스타일 */
    .cover-page {
        page-break-after: always;
        padding-top: 4cm;
    }

    .cover-company {
        font-size: 10pt;
        color: #787878;
        font-weight: 300;
        letter-spacing: 0.3em;
        margin-bottom: 0.5cm;
    }

    .cover-accent-line {
        width: 100%;
        height: 1pt;
        background: #333;
        margin: 0.5cm 0 1.5cm 0;
    }

    .cover-title {
        color: #333;
        font-size: 44pt;
        font-weight: bold;
        margin-bottom: 0.3cm;
    }

    .cover-version {
        color: #666;
        font-size: 19pt;
        font-weight: bold;
        margin-top: 0;
    }

    .cover-doctype {
        font-size: 16pt;
        color: #505050;
        font-weight: 300;
        margin-top: 1.5cm;
        margin-left: 0.1cm;
    }

    .cover-info-table {
        margin-top: 6cm;
        border-collapse: collapse;
        width: 50%;
    }

    .cover-info-table td {
        padding: 0.3cm 0.5cm;
        border: 1px solid #E8E8E8;
        font-size: 9.5pt;
    }

    .cover-info-table .label {
        background: white;
        font-weight: bold;
        color: #333;
        width: 30%;
    }

    .cover-info-table .value {
        color: #444;
    }

    /* 본문 스타일 */
    .content-page {
        page-break-before: always;
    }

    /* 제목 스타일 - Minimal */
    h1.heading-1 {
        color: #333;
        font-size: 21pt;
        font-weight: bold;
        margin: 1.2cm 0 0.8cm 0;
        page-break-after: avoid;
        border-bottom: 1pt solid #333;
        padding-bottom: 0.2cm;
    }

    h2.heading-2 {
        color: #333;
        font-size: 16.5pt;
        font-weight: bold;
        margin: 1cm 0 0.7cm 0;
        page-break-after: avoid;
    }

    h3.heading-3 {
        color: #333;
        font-size: 13pt;
        font-weight: bold;
        margin: 0.8cm 0 0.5cm 0;
        page-break-after: avoid;
    }

    h4.heading-4 {
        color: #333;
        font-size: 11pt;
        font-weight: bold;
        margin: 0.7cm 0 0.4cm 0;
        page-break-after: avoid;
    }

    p {
        margin: 0.3cm 0;
        text-align: justify;
    }

    /* 테이블 스타일 - Minimal */
    table.styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.7cm 0;
        page-break-inside: avoid;
    }

    table.styled-table th {
        background: white;
        color: #333;
        font-weight: bold;
        font-size: 9.5pt;
        padding: 0.35cm 0.4cm;
        text-align: left;
        border: 0.5pt solid #D0D0D0;
        border-bottom: 1pt solid #999;
    }

    table.styled-table td {
        padding: 0.3cm 0.4cm;
        font-size: 9.5pt;
        border: 0.5pt solid #D0D0D0;
        word-break: keep-all;
        overflow-wrap: break-word;
        background: white;
    }

    table.styled-table tr.even td {
        background: white;
    }

    table.styled-table tr.odd td {
        background: white;
    }

    /* 코드 블록 */
    .code-block {
        background: #F5F5F5;
        border-left: 3pt solid #2E74B5;
        padding: 0.3cm 0.5cm;
        margin: 0.5cm 0;
        page-break-inside: avoid;
    }

    .code-lang {
        font-size: 9pt;
        font-weight: bold;
        color: #808080;
        margin-bottom: 0.2cm;
    }

    .code-block pre {
        margin: 0;
        font-family: 'Consolas', monospace;
        font-size: 8.5pt;
        color: #333;
        white-space: pre-wrap;
        word-break: break-all;
    }

    code {
        font-family: 'Consolas', monospace;
        font-size: 9pt;
        color: #E74C3C;
        background: #F0F0F0;
        padding: 0.05cm 0.15cm;
        border-radius: 2pt;
    }

    /* 다이어그램 */
    .diagram-container {
        text-align: center;
        margin: 0.7cm 0;
        page-break-inside: avoid;
    }

    .mermaid-diagram {
        max-width: 100%;
        height: auto;
    }

    /* 리스트 */
    li.bullet-item, li.number-item {
        margin: 0.2cm 0 0.2cm 0.7cm;
    }

    /* 콜아웃 */
    .callout {
        padding: 0.4cm 0.6cm;
        margin: 0.5cm 0;
        border-left: 3pt solid;
    }

    .callout.warning {
        background: #FFF3CD;
        border-color: #FFC107;
        color: #856404;
    }

    /* 페이지 브레이크 */
    .page-break {
        page-break-before: always;
    }

    /* 강조 */
    strong {
        font-weight: bold;
        color: #333;
    }

    em {
        font-style: italic;
    }
    """


def convert_markdown_to_pdf(md_file, pdf_file):
    """Markdown을 Premium PDF로 변환"""

    print(f"[INFO] Markdown 읽기: {md_file}")
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 표지 HTML 생성
    cover_html = """
    <div class="cover-page">
        <div class="cover-company">W I T H F O R C E</div>
        <div class="cover-accent-line"></div>
        <div class="cover-title">MES 시스템 개선안</div>
        <div class="cover-version">Version 2.0</div>
        <div class="cover-doctype">시스템 요구사항 명세서</div>

        <table class="cover-info-table">
            <tr>
                <td class="label">작성일</td>
                <td class="value">2025년 11월 10일</td>
            </tr>
            <tr>
                <td class="label">작성자</td>
                <td class="value">Claude</td>
            </tr>
            <tr>
                <td class="label">문서 분류</td>
                <td class="value">기술 사양서</td>
            </tr>
        </table>
    </div>
    """

    print(f"[INFO] Markdown → HTML 변환 중...")
    content_html = parse_markdown_to_html(md_content)

    # 전체 HTML 구성
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Withforce MES 사양서 v2.0</title>
    </head>
    <body>
        {cover_html}
        <div class="content-page">
            {content_html}
        </div>
    </body>
    </html>
    """

    print(f"[INFO] PDF 생성 중...")
    font_config = FontConfiguration()

    html_doc = HTML(string=full_html)
    css_doc = CSS(string=create_premium_css(), font_config=font_config)

    html_doc.write_pdf(pdf_file, stylesheets=[css_doc], font_config=font_config)

    print(f"[OK] PDF 생성 완료: {pdf_file}")


if __name__ == '__main__':
    md_file = Path(__file__).parent / 'F2X_NeuroHub_MES_사양서_v2.0.md'
    pdf_file = Path(__file__).parent / 'Withforce_MES_사양서_v2.0.pdf'

    if not md_file.exists():
        print(f"[ERROR] 마크다운 파일을 찾을 수 없습니다: {md_file}")
        exit(1)

    print(f"[INFO] Premium Modern Tech PDF 변환 시작...")
    convert_markdown_to_pdf(md_file, pdf_file)
    print(f"[OK] 완료! PDF를 열어보세요: {pdf_file}")
