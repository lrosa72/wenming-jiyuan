#!/usr/bin/env python3
"""验证章节字数 + 检测「不是…是」违规句式"""
import re
import sys
import glob
import os

def count_chinese_chars(text):
    """统计纯汉字数量（不含标点、数字、英文）"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def check_not_shi(text):
    """检测「不是.{0,20}是」模式"""
    pattern = re.compile(r'不是.{0,20}是')
    return pattern.findall(text)

def extract_body(text):
    """提取正文主体：去掉 epigraph、尾诗、元数据块"""
    lines = text.split('\n')
    body_lines = []
    in_metadata = False
    in_epigraph = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('📊 章节元数据'):
            in_metadata = True
            continue
        if in_metadata:
            continue
        if stripped.startswith('> 🎵'):
            in_epigraph = True
            continue
        if in_epigraph:
            if stripped.startswith('>') and not stripped.startswith('> *'):
                continue
            elif stripped == '':
                continue
            elif stripped == '---':
                in_epigraph = False
                continue
            else:
                in_epigraph = False
        if stripped.startswith('# 第'):
            continue
        if stripped.startswith('> *'):
            continue
        body_lines.append(line)
    return '\n'.join(body_lines)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    body = extract_body(content)
    char_count = count_chinese_chars(body)
    not_shi_matches = check_not_shi(body)
    
    chapter_name = os.path.basename(filepath)
    status = "OK" if 2800 <= char_count <= 3200 else "⚠ 字数超标"
    status += " | 0「不是」" if len(not_shi_matches) == 0 else f" | ⚠ {len(not_shi_matches)}处「不是…是」"
    
    print(f"{chapter_name:30s} 汉字: {char_count:>5d}  {status}")
    if not_shi_matches:
        for m in not_shi_matches:
            print(f"    → 违规: {m}")

if __name__ == '__main__':
    base_dir = '/workspace/网文创作/正文存稿'
    files = sorted(glob.glob(os.path.join(base_dir, '第2[1-9]章-*.md')) + 
                   glob.glob(os.path.join(base_dir, '第3[0-5]章-*.md')))
    
    total = 0
    for f in files:
        process_file(f)
