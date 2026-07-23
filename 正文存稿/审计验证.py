#!/usr/bin/env python3
"""审计验证脚本：检查章节字数 + 检测「不是…是」违规句式"""
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
    """提取正文主体：去掉 epigraph、尾诗、元数据块、标题"""
    lines = text.split('\n')
    body_lines = []
    in_metadata = False
    in_tail_poem = False
    in_epigraph = False
    
    for line in lines:
        stripped = line.strip()
        
        # 跳过标题
        if stripped.startswith('# 第'):
            continue
        
        # 跳过 epigraph
        if stripped.startswith('> *') or (stripped.startswith('>') and in_epigraph):
            in_epigraph = True
            continue
        if in_epigraph and stripped == '':
            continue
        if in_epigraph:
            in_epigraph = False
        
        # 元数据块
        if stripped.startswith('📊 章节元数据'):
            in_metadata = True
            continue
        if in_metadata:
            continue
        
        # 尾诗块
        if stripped.startswith('> 🎵'):
            in_tail_poem = True
            continue
        if in_tail_poem:
            if stripped.startswith('>') and not stripped.startswith('> *'):
                continue
            elif stripped == '':
                continue
            elif stripped == '---':
                in_tail_poem = False
                continue
            else:
                in_tail_poem = False
        
        body_lines.append(line)
    
    return '\n'.join(body_lines)

def check_modern_words(text):
    """检测现代口语词"""
    modern_words = [
        '玩意儿', '搞定', '靠谱', '套路', '硬核', '绝了', '牛逼',
        '扯淡', '忽悠', '节奏（抽象名词）', '其实', '简直',
        '直接做', '直接说', '直接走',
    ]
    # 简化版：检测关键禁用词
    keywords = ['玩意儿', '搞定', '靠谱', '套路', '硬核', '牛逼', '扯淡', '忽悠']
    found = []
    for kw in keywords:
        if kw in text:
            # 找到上下文
            idx = text.find(kw)
            start = max(0, idx - 15)
            end = min(len(text), idx + 15)
            found.append(f"    → {kw}: ...{text[start:end]}...")
    return found

def check_historical_labels(text):
    """检测真实历史标签"""
    labels = ['翦商', '商朝', '周朝', '人祭', '天命', '德治', '周文王', '商纣', '周武王']
    found = []
    for label in labels:
        if label in text:
            idx = text.find(label)
            start = max(0, idx - 10)
            end = min(len(text), idx + 10)
            found.append(f"    → {label}: ...{text[start:end]}...")
    return found

def check_real_names(text):
    """检测真实人名/书名/文物名（排除正文中合理的）"""
    # 这里只做粗略检测
    real_names = ['孔子', '老子', '墨子', '孙子兵法', '诗经', '周易', '甲骨文']
    found = []
    for name in real_names:
        if name in text:
            idx = text.find(name)
            start = max(0, idx - 10)
            end = min(len(text), idx + 10)
            found.append(f"    → {name}: ...{text[start:end]}...")
    return found

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    body = extract_body(content)
    char_count = count_chinese_chars(body)
    not_shi_matches = check_not_shi(body)
    modern_words = check_modern_words(body)
    hist_labels = check_historical_labels(body)
    real_names = check_real_names(body)
    
    chapter_name = os.path.basename(filepath)
    
    # 字数状态
    if 2800 <= char_count <= 3200:
        count_status = "OK"
    else:
        count_status = f"⚠ {char_count}"
    
    # 不是...是状态
    if len(not_shi_matches) == 0:
        shi_status = "OK"
    else:
        shi_status = f"⚠ {len(not_shi_matches)}处"
    
    print(f"{chapter_name:30s} 汉字: {char_count:>5d} [{count_status}]  不是…是: [{shi_status}]")
    
    if not_shi_matches:
        for m in not_shi_matches:
            print(f"    → 违规: {m}")
    
    if modern_words:
        for mw in modern_words:
            print(mw)
    
    if hist_labels:
        for hl in hist_labels:
            print(hl)
    
    if real_names:
        for rn in real_names:
            print(rn)

if __name__ == '__main__':
    base_dir = '/workspace/网文创作/正文存稿'
    chapters = range(96, 111)
    files = []
    for ch in chapters:
        files.extend(glob.glob(os.path.join(base_dir, f'第{ch}章-*.md')))
    files = sorted(files)
    
    total_chars = 0
    total_not_shi = 0
    for f in files:
        process_file(f)
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        body = extract_body(content)
        total_chars += count_chinese_chars(body)
        total_not_shi += len(check_not_shi(body))
    
    print(f"\n--- 总计 ---")
    print(f"总汉字数: {total_chars}")
    print(f"总「不是…是」违规: {total_not_shi}")
