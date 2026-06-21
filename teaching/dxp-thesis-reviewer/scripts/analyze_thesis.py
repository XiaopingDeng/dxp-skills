#!/usr/bin/env python3
"""
论文综合分析工具 —— Stage 1 核心工具。

一次性输出:
  1. 全文段落文本（含章节标号）
  2. 章节字数统计与比例
  3. 中英文摘要提取与长度对比
  4. 图表编号检查
  5. 简单的跨位置数据一致性扫描（标识符复用检测）
  6. 参考文献年份统计
  7. 结论"幻觉术语"检测（结论中出现但正文从未定义的术语） [v2.1新增]
  8. 情感/口语化词汇密度扫描 [v2.1新增]

用法:
    python scripts/analyze_thesis.py <unpacked_dir/> --output <报告目录>
"""

import os, sys, re, json, argparse
from collections import Counter
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

# 情感/口语化过度修饰词库 —— 本科论文中不宜出现的夸张表达
EMOTIVE_WORDS = [
    '纹丝不动', '像素级', '无可挑剔',
    '无懈可击', '终极基准', '冲破了', '近乎完美', '绝对的',
    '极度', '极其', '极为', '完美', '零误差', '毫无疑问',
    '最先进的', '开创性的', '颠覆性的', '史无前例', '前所未有',
]


def load_para_texts(unpacked):
    dp = os.path.join(unpacked, 'word', 'document.xml')
    dt = etree.parse(dp)
    paras = dt.getroot().findall('.//{%s}p' % W)
    para_texts = [''.join(t.text or '' for t in p.iter('{%s}t' % W)) for p in paras]
    return para_texts


def extract_chapters(para_texts):
    chapter_map = {}  # para_index -> chapter_title
    current_chapter = None
    chapter_para = {}

    for i, t in enumerate(para_texts):
        m = re.match(r'^(第?[1-9一二三四五六七八九十]\s*[章、]|[\d.]+\s+[^\s])', t.strip())
        if m:
            current_chapter = t.strip()[:60]
            chapter_para[i] = current_chapter

    return chapter_para, current_chapter


def count_chapter_chars(para_texts, chapter_start_indices):
    """Count characters per chapter section."""
    chapter_ranges = []
    sorted_indices = sorted(chapter_start_indices.keys())

    for idx in range(len(sorted_indices)):
        start = sorted_indices[idx]
        title = chapter_start_indices[start]
        end = sorted_indices[idx + 1] if idx + 1 < len(sorted_indices) else len(para_texts)
        char_count = sum(len(para_texts[i]) for i in range(start, end))
        chapter_ranges.append((start, title, char_count))

    return chapter_ranges


def find_chinese_abstract(para_texts):
    """Extract Chinese abstract region and English abstract region."""
    ch_abs_start = None
    ch_abs_end = None
    en_abs_start = None
    en_abs_end = None

    for i, t in enumerate(para_texts):
        s = t.strip()
        if re.match(r'^摘\s*要', s) and ch_abs_start is None:
            ch_abs_start = i
        if ch_abs_start is not None and ch_abs_end is None and re.match(r'^关键词', s):
            ch_abs_end = i
        if re.match(r'^ABSTRACT', s, re.IGNORECASE) and en_abs_start is None:
            en_abs_start = i
        if en_abs_start is not None and en_abs_end is None and re.match(r'^Key\s*[Ww]ords', s):
            en_abs_end = i

    return ch_abs_start, ch_abs_end, en_abs_start, en_abs_end


def check_figure_table_positions(para_texts):
    """Detect figure caption and table caption position issues."""
    issues = []
    for i, t in enumerate(para_texts):
        s = t.strip()
        # Figure caption: "图X.X" at start of paragraph
        fig_m = re.match(r'^(图\s*[\d.]+\s+[\S])', s)
        tbl_m = re.match(r'^(表\s*[\d.]+\s+[\S])', s)
        if fig_m:
            # 规范: 图下表上，即图题应在图片下方。
            # 若图片段落(仅含<w:drawing>无<w:t>文本，提取为空)出现在图题之后，
            # 说明图题在图片上方 = 错误。
            next_empty = i + 1 < len(para_texts) and not para_texts[i + 1].strip()
            if next_empty:
                issues.append(('图题可能在上方(应为下方)', i, s[:60]))
        if tbl_m:
            # 规范: 表上图下，即表题应在表格上方。
            # 若表格段落出现在表题之前(前一段为空)，说明表题在表格下方 = 错误。
            prev_empty = i > 0 and not para_texts[i - 1].strip()
            if prev_empty:
                issues.append(('表题可能在下方(应为上方)', i, s[:60]))
    return issues


def scan_identifier_conflicts(para_texts):
    """
    Simple cross-consistency scan: detect identifiers used in different contexts.
    Scans for MCU pin assignments (e.g., "P3.6" appearing with different function descriptions).
    """
    # Collect all uses of common identifiers
    pin_uses = {}  # pin_name -> list of (para_idx, context)
    uart_uses = {}
    baud_uses = {}

    pin_pattern = re.compile(r'P\d+[.]\d+')
    uart_pattern = re.compile(r'UART[1234]')
    baud_pattern = re.compile(r'(\d+)\s*bps')

    for i, t in enumerate(para_texts):
        s = t.strip()
        if not s:
            continue

        # Pin assignments
        for m in pin_pattern.finditer(s):
            pin = m.group()
            # Get context around the pin (30 chars before and after)
            start = max(0, m.start() - 30)
            end = min(len(s), m.end() + 30)
            ctx = s[start:end].replace('\n', ' ')
            if pin not in pin_uses:
                pin_uses[pin] = []
            pin_uses[pin].append((i, ctx))

        # UART uses
        for m in uart_pattern.finditer(s):
            uart = m.group()
            start = max(0, m.start() - 20)
            end = min(len(s), m.end() + 40)
            ctx = s[start:end].replace('\n', ' ')
            if uart not in uart_uses:
                uart_uses[uart] = []
            uart_uses[uart].append((i, ctx))

        # Baud rates
        for m in baud_pattern.finditer(s):
            rate = m.group(1)
            if rate in ('9600', '115200'):
                start = max(0, m.start() - 30)
                end = min(len(s), m.end() + 10)
                ctx = s[start:end].replace('\n', ' ')
                if rate not in baud_uses:
                    baud_uses[rate] = []
                baud_uses[rate].append((i, ctx))

    return pin_uses, uart_uses, baud_uses


def check_references(para_texts):
    """Basic reference check: count refs, check years."""
    ref_start = None
    for i, t in enumerate(para_texts):
        if re.match(r'^参考\s*文\s*献', t.strip()):
            ref_start = i
            break

    if ref_start is None:
        return None, None

    ref_count = 0
    years = []
    ref_text_lines = []

    for i in range(ref_start + 1, len(para_texts)):
        t = para_texts[i].strip()
        if not t:
            continue
        # Check if this line starts a reference entry
        if re.match(r'^\[\d+\]', t):
            ref_count += 1
            ref_text_lines.append(t)
            year_m = re.findall(r'(19\d{2}|20\d{2})', t)
            years.extend(year_m)

    year_counter = Counter(years)

    # Count refs that have at least one year >= 2023 (not total year occurrences)
    recent_refs = 0
    for i in range(ref_start + 1, len(para_texts)):
        t = para_texts[i].strip()
        if re.match(r'^\[\d+\]', t):
            year_m = re.findall(r'(19\d{2}|20\d{2})', t)
            if any(int(y) >= 2023 for y in year_m):
                recent_refs += 1

    ref_info = {
        'total_refs': ref_count,
        'total_years_found': len(years),
        'year_distribution': dict(year_counter.most_common()),
        'recent_3_years': recent_refs,
        'recent_ratio': round(recent_refs / ref_count, 2) if ref_count > 0 else 0,
    }

    return ref_info, ref_count


def detect_hallucination_terms(para_texts):
    """
    Check for technical terms that appear in the conclusion/summary chapter
    but are never defined or explained in the main body chapters.
    This catches AI-generated hallucinations in conclusions.
    """
    # Find conclusion chapter boundaries (look for "总结"/"结论" heading)
    # TOC entries occupy roughly first 100-120 paragraphs. We start searching after
    # that to avoid matching TOC chapter entries. Use body_min_idx = 120 as a safe lower bound.
    body_min_idx = 120

    conclusion_start = None
    conclusion_end = None
    for i in range(body_min_idx, len(para_texts)):
        s = para_texts[i].strip()
        # Match standalone conclusion/展望 chapter heading (short paragraphs < 60 chars are true headings,
        # not long description paragraphs in section 1.4)
        if len(s) < 60 and re.search(r'^(第?[五六6]\s*[章、]|^6[\s.])', s) and ('总结' in s or '结论' in s):
            conclusion_start = i
        if conclusion_start is not None and conclusion_end is None:
            if re.search(r'^(谢\s*辞|致\s*谢|参考\s*文\s*献)', s):
                conclusion_end = i
                break

    if conclusion_start is None:
        return []

    conclusion_end = conclusion_end or len(para_texts)
    body_start = 0  # Everything before conclusion is "body"

    # Collect all noun phrases (3-6 character technical terms) from conclusion
    # These are Chinese technical terms - look for 3+ char compound words in conclusion
    conclusion_text = ''.join(para_texts[conclusion_start:conclusion_end])
    body_text = ''.join(para_texts[body_start:conclusion_start])

    # Find potential technical terms in conclusion (3-8 char sequences ending with specific
    # technical suffixes that suggest a named method/algorithm/protocol — things a student
    # would have defined explicitly if they actually existed in the work)
    # We deliberately use a NARROW suffix set ("算法", "协议") to avoid false positives
    # from normal descriptive phrases like "...控制机制" or "...系统结构".
    term_pattern = re.compile(r'[\u4e00-\u9fff]{3,8}(?:算法|协议|定理|公式|定律)')
    conclusion_terms = set(term_pattern.findall(conclusion_text))
    body_terms = set(term_pattern.findall(body_text))

    hallucinated = []
    for term in conclusion_terms:
        if term not in body_text:
            # Find which paragraph in conclusion contains this term
            for i in range(conclusion_start, conclusion_end):
                if term in para_texts[i]:
                    hallucinated.append((term, i))
                    break

    return hallucinated


def scan_emotive_words(para_texts):
    """
    Scan the full text for emotionally charged / colloquial words
    that are inappropriate in academic writing.
    Returns list of (word, count, paragraph_indices).
    """
    results = []
    for word in EMOTIVE_WORDS:
        found = []
        for i, pt in enumerate(para_texts):
            if word in pt:
                found.append(i)
        if found:
            results.append((word, len(found), found))
    results.sort(key=lambda x: -x[1])  # Sort by frequency descending
    return results


def main():
    parser = argparse.ArgumentParser(description='Comprehensive thesis analysis tool')
    parser.add_argument('unpacked', help='Path to unpacked docx directory')
    parser.add_argument('--output', help='Output directory for analysis results')
    args = parser.parse_args()

    para_texts = load_para_texts(args.unpacked)
    total_chars = sum(len(t) for t in para_texts)
    non_empty = len([t for t in para_texts if t.strip()])

    print(f'=== 论文基本信息 ===')
    print(f'总段落数: {len(para_texts)} (非空: {non_empty})')
    print(f'总字符数: {total_chars}')
    print()

    # Chapter structure
    chapter_start_indices, _ = extract_chapters(para_texts)
    chapter_ranges = count_chapter_chars(para_texts, chapter_start_indices)

    print(f'=== 章节字数统计 ===')
    for pidx, title, chars in chapter_ranges:
        ratio = chars / total_chars * 100
        warn = ' << [WARNING] 占比异常' if ratio > 40 or (ratio < 5 and chars < 3000 and '章' in title and '小' not in title) else ''
        print(f'  P{pidx} {title}: {chars} 字符 ({ratio:.1f}%){warn}')
    print()

    # Abstract extraction
    ch_s, ch_e, en_s, en_e = find_chinese_abstract(para_texts)
    if ch_s is not None:
        ch_abs_text = ''.join(para_texts[ch_s:ch_e]) if ch_e else ''
        en_abs_text = ''.join(para_texts[en_s:en_e]) if en_s and en_e else ''
        print(f'=== 摘要信息 ===')
        print(f'  中文摘要: P{ch_s}-P{ch_e or "?"}, {len(ch_abs_text)} 字符')
        print(f'  英文摘要: P{en_s}-P{en_e or "?"}, {len(en_abs_text)} 字符')
        if ch_abs_text and en_abs_text:
            ratio_cn_en = len(en_abs_text) / len(ch_abs_text) if len(ch_abs_text) > 0 else 0
            print(f'  中英文摘要长度比: {ratio_cn_en:.2f} (正常约0.6-1.0)')
            if ratio_cn_en < 0.4 or ratio_cn_en > 1.5:
                print(f'  [WARNING] 中英文摘要长度差异较大，可能信息不对等')
    print()

    # Figure/table position check
    fig_tbl_issues = check_figure_table_positions(para_texts)
    if fig_tbl_issues:
        print(f'=== 图/表标题位置检查 ({len(fig_tbl_issues)} 处) ===')
        for issue_type, pidx, caption in fig_tbl_issues:
            print(f'  P{pidx}: {issue_type} -> "{caption}"')
        print()
    else:
        print('=== 图/表标题位置检查 ===')
        print('  未发现明显位置异常')
        print()

    # Identifiers scan
    pin_uses, uart_uses, baud_uses = scan_identifier_conflicts(para_texts)
    print(f'=== 标识符复用扫描 ===')
    print(f'  GPIO引脚引用: {len(pin_uses)} 个不同引脚')
    for pin, uses in sorted(pin_uses.items()):
        if len(uses) >= 3:
            print(f'  {pin}: 出现 {len(uses)} 次 - 跨段落分布，请人工核实一致性')
    print(f'  UART引用: {len(uart_uses)} 个')
    for uart, uses in sorted(uart_uses.items()):
        contexts = set(u[1][:40] for u in uses)
        print(f'  {uart}: {len(uses)} 次 (上下文: {", ".join(sorted(contexts)[:3])})')
    for rate, uses in sorted(baud_uses.items()):
        print(f'  波特率 {rate}: {len(uses)} 处引用')
    print()

    # Reference check
    ref_info, ref_count = check_references(para_texts)
    if ref_info:
        print(f'=== 参考文献检查 ===')
        print(f'  总数: {ref_info["total_refs"]}')
        print(f'  年份分布: {ref_info["year_distribution"]}')
        print(f'  近3年文献: {ref_info["recent_3_years"]} ({ref_info["recent_ratio"]*100:.0f}%)')
        if ref_info["recent_ratio"] < 0.3:
            print(f'  [WARNING] 近3年文献占比不足30%')
        print()

    # Hallucination term detection [v2.1新增]
    hallucinated = detect_hallucination_terms(para_texts)
    if hallucinated:
        print(f'=== 结论"幻觉术语"检测 ({len(hallucinated)} 个) ===')
        for term, pidx in hallucinated:
            print(f'  [CRITICAL] "{term}" 出现在 P{pidx}（结论章节），但正文从未定义或使用此术语！')
        print()
    else:
        print('=== 结论"幻觉术语"检测 ===')
        print('  未发现结论独有且正文未定义的术语')
        print()

    # Emotive word density scan [v2.1新增]
    emotive_results = scan_emotive_words(para_texts)
    if emotive_results:
        total_emotive = sum(r[1] for r in emotive_results)
        print(f'=== 情感/口语化词汇密度扫描 (共 {total_emotive} 处，{len(emotive_results)} 个不同词) ===')
        for word, cnt, indices in emotive_results[:10]:
            sample_p = ', '.join(f'P{i}' for i in indices[:5])
            if len(indices) > 5:
                sample_p += f' ... (+{len(indices)-5}处)'
            print(f'  "{word}": {cnt}次 ({sample_p})')
        print()
    else:
        print('=== 情感/口语化词汇密度扫描 ===')
        print('  未检测到过度修饰词')
        print()

    # Output to full text file
    output_dir = args.output or args.unpacked
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, '_full_text.txt'), 'w', encoding='utf-8') as f:
        for i, t in enumerate(para_texts):
            if t.strip():
                f.write(f'[P{i}] {t}\n')

    report = {
        'total_paragraphs': len(para_texts),
        'non_empty_paragraphs': non_empty,
        'total_chars': total_chars,
        'chapters': [(title, chars) for _, title, chars in chapter_ranges],
        'figure_table_issues': [(issue_type, pidx, caption) for issue_type, pidx, caption in fig_tbl_issues],
        'ref_info': ref_info,
        'hallucination_terms': [(term, pidx) for term, pidx in hallucinated],
        'emotive_words': [(word, cnt, indices[:10]) for word, cnt, indices in emotive_results],
    }
    with open(os.path.join(output_dir, '_analysis.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f'完整文本已写入: {os.path.join(output_dir, "_full_text.txt")}')
    print(f'分析报告已写入: {os.path.join(output_dir, "_analysis.json")}')


if __name__ == '__main__':
    main()
