#!/usr/bin/env python3
"""
BibTeX to YAML Converter cho AgIL Lab Publications.
Tự động chuyển đổi file export từ Google Scholar (publications.bib) 
sang định dạng YAML dùng cho website (publications/data/publications.yml).

Chạy: python3 scripts/bib2yaml.py
"""

import os
import re
import json

# =========================================================================
# UTILS: Xử lý Unicode và dọn dẹp chuỗi từ BibTeX
# =========================================================================

# Bảng map các ký tự escape phổ biến trong LaTeX/BibTeX sang Unicode
LATEX_UNICODE_MAP = {
    r"{\'a}": "á", r"{\`a}": "à", r"{\^a}": "â", r"{\~a}": "ã", r"{\.a}": "ȧ",
    r"{\'e}": "é", r"{\`e}": "è", r"{\^e}": "ê", r"{\~e}": "ẽ",
    r"{\'i}": "í", r"{\`i}": "ì", r"{\^i}": "î", r"{\~i}": "ĩ",
    r"{\'o}": "ó", r"{\`o}": "ò", r"{\^o}": "ô", r"{\~o}": "õ", r"{\"o}": "ö",
    r"{\'u}": "ú", r"{\`u}": "ù", r"{\^u}": "û", r"{\~u}": "ũ", r"{\"u}": "ü",
    r"{\'y}": "ý", r"{\`y}": "ỳ", r"{\^y}": "ŷ", r"{\~y}": "ỹ",
    # Viết hoa
    r"{\'A}": "Á", r"{\`A}": "À", r"{\^A}": "Â", r"{\~A}": "Ã",
    r"{\'E}": "É", r"{\`E}": "È", r"{\^E}": "Ê", r"{\~E}": "Ẽ",
    r"{\'I}": "Í", r"{\`I}": "Ì", r"{\^I}": "Î", r"{\~I}": "Ĩ",
    r"{\'O}": "Ó", r"{\`O}": "Ò", r"{\^O}": "Ô", r"{\~O}": "Õ", r"{\"O}": "Ö",
    r"{\'U}": "Ú", r"{\`U}": "Ù", r"{\^U}": "Û", r"{\~U}": "Ũ", r"{\"U}": "Ü",
    r"{\'Y}": "Ý", r"{\`Y}": "Ỳ", r"{\^Y}": "Ŷ", r"{\~Y}": "Ỹ",
    # Các ký tự Việt Nam phổ biến khác (nếu có d/đ)
    r"{\dj}": "đ", r"{\DH}": "Đ"
}

def clean_bibtex_string(text):
    """Làm sạch chuỗi BibTeX: xoá ngoặc {}, escape ký tự LaTeX sang Unicode"""
    if not text:
        return ""
    
    # 1. Thay thế các escape LaTeX bằng ký tự Unicode
    for latex, unicode_char in LATEX_UNICODE_MAP.items():
        text = text.replace(latex, unicode_char)
        # Handle trường hợp không có ngoặc, vd: \'a -> á
        text = text.replace(latex.replace("{", "").replace("}", ""), unicode_char)
    
    # 2. Xoá các dấu ngoặc {} còn sót lại (dùng cho capitalize escape trong bibtex)
    text = text.replace("{", "").replace("}", "")
    
    # 3. Dọn dẹp khoảng trắng thừa
    text = " ".join(text.split())
    return text.strip()

def format_authors(authors_str):
    """Chuyển đổi author format từ BibTeX (A and B and C) sang (A, B, C)"""
    if not authors_str:
        return ""
    
    authors = authors_str.split(" and ")
    formatted_authors = []
    
    for author in authors:
        # Nếu đang ở dạng "Lastname, Firstname", chuyển thành "Firstname Lastname"
        if "," in author:
            parts = author.split(",", 1)
            # Thêm strip() để xoá khoảng trắng thừa
            formatted = f"{parts[1].strip()} {parts[0].strip()}"
            formatted_authors.append(formatted)
        else:
            formatted_authors.append(author.strip())
            
    return ", ".join(formatted_authors)


# =========================================================================
# PARSER: Regex-based BibTeX Parser
# =========================================================================

def parse_bibtex(file_path):
    """
    Parse file BibTeX bằng Regex (tránh dùng thư viện ngoài).
    Trả về list parsed dictionaries.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex bắt từng entry BibTeX: @type{id, ... fields ... }
    # Xử lý các nested braces bằng pattern đơn giản gọn nhẹ:
    # Tìm kiếm "@" theo sau là chữ cái (type), rồi "{" (mở entry), 
    # rồi key, dấu ",", và cuối cùng là các fields kết thúc bằng "}\n" (hoặc kết thúc file)
    
    entries = []
    
    # Bước 1: Split content theo các entry "@" (dùng lookahead hoặc split)
    # Bỏ qua các chuỗi không phải bắt đầu bằng @
    raw_entries = re.split(r'(?=\@[A-Za-z]+\s*\{)', content)
    
    for raw in raw_entries:
        raw = raw.strip()
        if not raw.startswith('@'):
            continue
            
        # Tách loại và ID
        # Ví dụ: @article{nguyen2024aspect,
        first_line_match = re.match(r'\@([A-Za-z]+)\s*\{\s*([^,]+),', raw)
        if not first_line_match:
            continue
            
        # entry_type = first_line_match.group(1).lower()
        # entry_id = first_line_match.group(2)
        
        # Lấy phần nội dung (fields) giữa ngoặc {} ngoài cùng
        # Tìm index của ngoặc đóng cuối cùng phù hợp với ngoặc mở đầu tiên
        content_start = raw.find(',') + 1
        content_end = raw.rfind('}')
        
        if content_start <= 0 or content_end <= 0 or content_start >= content_end:
            continue
            
        fields_str = raw[content_start:content_end]
        
        # Bước 2: Extract từng field. 
        # Cấu trúc: key = {value} hoặc key = "value"
        # Dùng regex để tìm cặp key-value
        # Key: word boundaries, '=', Value: trong {} hoặc ""
        
        # Pattern 1: key = {value}
        pattern_brace = re.compile(r'([a-zA-Z0-9_]+)\s*=\s*\{((?:[^{}]|(?:\{[^{}]*\}))*)\}')
        # Pattern 2: key = "value"
        pattern_quote = re.compile(r'([a-zA-Z0-9_]+)\s*=\s*"([^"]*)"')
        # Pattern 3: key = value (số)
        pattern_num = re.compile(r'([a-zA-Z0-9_]+)\s*=\s*([0-9]+)(?:\s*,|$)')
        
        entry_data = {}
        
        # Find all matches
        for m in pattern_brace.finditer(fields_str):
            entry_data[m.group(1).lower()] = m.group(2)
            
        for m in pattern_quote.finditer(fields_str):
            if m.group(1).lower() not in entry_data: # Đừng overwrite nếu đã bắt bằng pattern_brace
                entry_data[m.group(1).lower()] = m.group(2)
                
        for m in pattern_num.finditer(fields_str):
            if m.group(1).lower() not in entry_data:
                entry_data[m.group(1).lower()] = m.group(2)
                
        if entry_data:
            entries.append(entry_data)
            
    return entries


# =========================================================================
# MAIN PIPELINE
# =========================================================================

def generate_yaml(entries):
    """Convert parsed BibTeX data sang định dạng YAML của website"""
    
    yaml_lines = [
        "# =================================================================",
        "# THƯ VIỆN PUBLICATIONS (AUTO-GENERATED)",
        "# File này được tạo tự động bởi scripts/bib2yaml.py",
        "# VUI LÒNG KHÔNG SỬA TRỰC TIẾP FILE NÀY.",
        "# ",
        "# Hướng dẫn cập nhật:",
        "# 1. Mở file publications.bib",
        "# 2. Paste BibTeX export từ Google Scholar vào file",
        "# 3. Chạy lệnh: python3 scripts/bib2yaml.py",
        "# =================================================================",
        ""
    ]
    
    processed_entries = []
    seen_titles = set()
    
    for entry in entries:
        # Lọc bỏ nếu thiếu thông tin bắt buộc
        if 'title' not in entry or 'author' not in entry:
            print(f"⚠️ Bỏ qua entry do thiếu title hoặc author: {entry.get('title', 'Unknown')}")
            continue
            
        # Clean data
        title = clean_bibtex_string(entry['title'])
        authors = format_authors(clean_bibtex_string(entry['author']))
        
        # Deduplicate dựa trên lowercase title
        title_lower = title.lower().strip()
        if title_lower in seen_titles:
            print(f"ℹ️ Đã loại bỏ duplicate: {title}")
            continue
        seen_titles.add(title_lower)
        
        # Xử lý các trường thông tin khác
        year = entry.get('year', '')
        
        # Journal name prefer: journal -> booktitle (cho conferences) -> publisher
        journal = clean_bibtex_string(entry.get('journal', entry.get('booktitle', entry.get('publisher', ''))))
        
        doi = clean_bibtex_string(entry.get('doi', ''))
        # Nếu format DOI chứ không phải URL đầy đủ, prepend https://doi.org/
        if doi and not doi.startswith('http'):
            # Xoá prefix doi: nếu có
            doi = doi.replace('doi:', '').strip()
            doi = f"https://doi.org/{doi}"
            
        url = clean_bibtex_string(entry.get('url', ''))
        
        # Abstract nếu để hiển thị chi tiết
        abstract = clean_bibtex_string(entry.get('abstract', ''))
        
        # Add vào ds đã xử lý để sort
        processed_entries.append({
            'title': title,
            'authors': authors,
            'year': year,
            'journal': journal,
            'doi': doi,
            'pdf': url,
            'abstract': abstract,
            # Nếu website dùng thumbnail tĩnh hoặc custom:
            'thumbnail': 'example_pub.png', # default thumbnail
            'github_link': '', # custom url nếu có
            'paper_link': doi or url # Map paper_link cho CSS layout hiện tại
        })
        
    # Sort theo năm giảm dần
    def get_year(e):
        try:
            return int(e['year'])
        except ValueError:
            return 0
            
    processed_entries.sort(key=get_year, reverse=True)
    
    # Tạo nội dung YAML dạng thuần tuý tay (để kiểm soát format giống file cũ, không cần lib yaml)
    for pub in processed_entries:
        yaml_lines.append(f"- title: \"{json.dumps(pub['title'])[1:-1]}\"")
        yaml_lines.append(f"  authors: \"{json.dumps(pub['authors'])[1:-1]}\"")
        yaml_lines.append(f"  year: {pub['year'] if pub['year'] else '\"\"'}")
        
        if pub['journal']:
            yaml_lines.append(f"  journal: \"{json.dumps(pub['journal'])[1:-1]}\"")
            
        if pub['abstract']:
            yaml_lines.append(f"  abstract: \"{json.dumps(pub['abstract'])[1:-1]}\"")
            
        if pub['doi']:
            yaml_lines.append(f"  doi: \"{pub['doi']}\"")
            
        if pub['pdf']:
            yaml_lines.append(f"  pdf: \"{pub['pdf']}\"")
            
        yaml_lines.append(f"  thumbnail: \"{pub['thumbnail']}\"")
        yaml_lines.append(f"  paper_link: \"{pub['paper_link']}\"")
        yaml_lines.append(f"  github_link: \"{pub['github_link']}\"")
        yaml_lines.append("")
        
    return "\n".join(yaml_lines)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bib_path = os.path.join(base_dir, 'publications.bib')
    yml_dir = os.path.join(base_dir, 'publications', 'data')
    yml_path = os.path.join(yml_dir, 'publications.yml')
    
    if not os.path.exists(bib_path):
        print(f"❌ Không tìm thấy file `{bib_path}`")
        print("💡 Vui lòng tạo file `publications.bib` với các kết quả xuất từ Google Scholar trước khi chạy tool.")
        return
        
    if not os.path.exists(yml_dir):
        os.makedirs(yml_dir, exist_ok=True)
        
    print(f"⏳ Đang parse `{bib_path}`...")
    entries = parse_bibtex(bib_path)
    print(f"✅ Tìm thấy {len(entries)} publications trong BibTeX.")
    
    yaml_content = generate_yaml(entries)
    
    with open(yml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
        
    print(f"✅ Đã lưu {yml_path}")
    print(f"🎉 Pipeline hoàn tất! F5 website để xem kết quả.")

if __name__ == "__main__":
    main()
