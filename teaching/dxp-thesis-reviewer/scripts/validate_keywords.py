#!/usr/bin/env python3
"""
预验证所有 keyword 和 sub_keyword 在文档中的匹配情况。

改进说明 (v2.0):
  - 精确匹配失败后自动尝试模糊匹配 (difflib.SequenceMatcher)
  - 失败时提供字符级诊断（显示期望字符与文档实际字符的 Unicode 编码对比）
  - 对每个失败关键词推荐最接近的 3 个候选段落片段
  - 输出可存入注释的 --suggestions 模式

用法:
    python validate_keywords.py <unpacked_dir/> <comments.json>
    python validate_keywords.py <unpacked_dir/> <comments.json> --suggestions

退出码: 失败批注数（精确匹配层面）；--suggestions 模式不计入退出码
"""

import json, os, sys, difflib
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def find_best_fuzzy_matches(keyword, para_texts, top_n=3, cutoff=0.6):
    """Return list of (para_idx, score, context) for fuzzy matches."""
    scored = []
    for i, pt in enumerate(para_texts):
        if not pt.strip():
            continue
        # Use SequenceMatcher ratio on substring sliding windows
        # For long paras, just match ratio of whole para
        ratio = difflib.SequenceMatcher(None, keyword, pt).ratio()
        if ratio >= cutoff:
            scored.append((ratio, i, pt))

        # Also check if keyword is a near-substring
        # For each position in pt, check similarity of a keyword-length window
        if len(keyword) >= 4 and len(pt) > len(keyword):
            for start in range(0, len(pt) - len(keyword) + 1, 2):
                window = pt[start:start + len(keyword)]
                wr = difflib.SequenceMatcher(None, keyword, window).ratio()
                if wr >= cutoff:
                    scored.append((wr, i, pt))
                    break  # one good window per para is enough

    scored.sort(key=lambda x: (-x[0], x[1]))
    deduped = []
    seen_para = set()
    for score, idx, text in scored:
        if idx not in seen_para:
            seen_para.add(idx)
            deduped.append((idx, score, text[:120]))
        if len(deduped) >= top_n:
            break
    return deduped


def diagnostic_compare(expected, actual):
    """Generate character-level diagnostic between expected substring and actual text."""
    lines = []
    lines.append(f'    Expected (len={len(expected)}): {repr(expected[:200])}')
    lines.append(f'    Codes: {[hex(ord(c)) for c in expected[:60]]}')
    lines.append(f'    Actual snippet (len={len(actual)}): {repr(actual[:200])}')
    lines.append(f'    Codes: {[hex(ord(c)) for c in actual[:60]]}')

    # Check for common encoding issues
    if len(expected) >= 2 and len(actual) >= 2:
        common_issues = []
        # Same apparent text but different Unicode forms (e.g., fullwidth vs halfwidth)
        for i, (ec, ac) in enumerate(zip(expected[:20], actual[:20])):
            if ec != ac:
                if ord(ec) > 127 and ord(ec) == ord(ac) + 0xFEE0:
                    common_issues.append(f'  char {i}: fullwidth/halfwidth mismatch')
                break
        if common_issues:
            lines.extend(common_issues)

    return '\n'.join(lines)


def suggest_keywords(context_str, existing_keywords):
    """Suggest additional keywords based on text content."""
    # Extract notable phrases: 2-6 char Chinese tokens with notable characters
    import re
    # Find potential keyword phrases in context
    candidates = set()
    # Look for patterns like "XX系统", "XX模块", "XX设计", "XX算法"
    patterns = [
        (r'[\u4e00-\u9fff]{2,4}(?:系统|模块|设计|算法|模型|方法|技术|方案|功能|结构|流程|策略|原理|分析|研究|实现|测试)'),
        (r'(?:基于|采用|利用|通过|使用)[\u4e00-\u9fff]{2,6}'),
        (r'[\u4e00-\u9fff]{3,8}'),
    ]
    for pat in patterns:
        for m in re.finditer(pat, context_str):
            cand = m.group()
            if cand not in existing_keywords and len(cand) >= 4:
                candidates.add(cand)
    return list(candidates)[:5]


def main():
    suggestions_mode = '--suggestions' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--suggestions']

    if len(args) < 2:
        print("Usage: python validate_keywords.py <unpacked_dir/> <comments.json> [--suggestions]")
        sys.exit(0)

    unpacked, comments_path = args[0], args[1]

    doc_path = os.path.join(unpacked, 'word', 'document.xml')
    if not os.path.exists(doc_path):
        print("ERROR: word/document.xml not found. Is the docx unpacked?")
        sys.exit(1)

    dt = etree.parse(doc_path)
    paras = dt.getroot().findall('.//{%s}p' % W)
    para_texts = [''.join(t.text or '' for t in p.iter('{%s}t' % W)) for p in paras]
    print(f"Loaded {len(paras)} paragraphs ({len([p for p in para_texts if p.strip()])} non-empty)")

    with open(comments_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = data.get('comments', [])
    print(f"Loaded {len(comments)} comments to validate\n")

    # Collect all existing keywords for suggestion dedup
    existing_keywords = {c['keyword'] for c in comments}
    for c in comments:
        if 'sub_keyword' in c:
            existing_keywords.add(c['sub_keyword'])

    ok_count = 0
    fail_count = 0
    suggestion_output = []

    for cmt in comments:
        cid = cmt['id']
        keyword = cmt['keyword']
        occ = cmt.get('occ', 0)
        sub_kw = cmt.get('sub_keyword', None)
        text_preview = cmt['text'][:60]

        # --- Exact matching ---
        matches = [i for i, pt in enumerate(para_texts) if keyword in pt]

        if not matches:
            print(f"  [FAIL id={cid}] keyword NOT FOUND")
            print(f"    keyword: {keyword[:100]}")
            print(f"    comment: {text_preview}...")

            # Fuzzy matching attempt
            fuzzy = find_best_fuzzy_matches(keyword, para_texts, top_n=3)
            if fuzzy:
                print(f"    Top 3 fuzzy matches:")
                for idx, score, snippet in fuzzy:
                    print(f"      P{idx} (score={score:.2f}): {snippet}")
            else:
                # Check if any para contains a significant substring of the keyword
                for sublen in range(len(keyword) - 2, 3, -1):
                    sub_hits = [(i, pt) for i, pt in enumerate(para_texts)
                                if keyword[:sublen] in pt and pt.strip()]
                    if sub_hits:
                        print(f"    No fuzzy match found. However, keyword prefix '{keyword[:sublen]}' found in {len(sub_hits)} paragraphs:")
                        for i, pt in sub_hits[:3]:
                            print(f"      P{i}: {pt[:120]}")
                        break
                else:
                    # Full diagnostic: compare keyword to a nearby paragraph
                    print(f"    No similar text found in document at all.")

            # Character-level diagnostic
            print(f"    Char diagnostic (keyword):")
            print(f"      {repr(keyword[:120])}")
            print(f"      Codes: {[(c, hex(ord(c))) for c in keyword[:30]]}")

            if not suggestions_mode:
                fail_count += 1
            continue

        if len(matches) <= occ:
            print(f"  [FAIL id={cid}] occ={occ} requested but only {len(matches)} match(es)")
            for mi, m_idx in enumerate(matches):
                print(f"    match[{mi}] P{m_idx}: {para_texts[m_idx][:120]}")
            print(f"    comment: {text_preview}...")
            if not suggestions_mode:
                fail_count += 1
            continue

        para_idx = matches[occ]
        matched_text = para_texts[para_idx][:120]
        print(f"  [OK  id={cid}] P{para_idx} ({len(matches)} total, occ={occ})")
        print(f"    para: {matched_text}...")
        print(f"    cmt:  {text_preview}...")

        # Validate sub_keyword if present
        if sub_kw:
            para_full = para_texts[para_idx]
            if sub_kw in para_full:
                sub_pos = para_full.find(sub_kw)
                print(f"    sub_keyword OK at position {sub_pos}: {sub_kw[:80]}")
            else:
                print(f"    sub_keyword NOT FOUND in matched paragraph")
                fuzzy_sub = find_best_fuzzy_matches(sub_kw, [para_full], top_n=2, cutoff=0.5)
                if fuzzy_sub:
                    for idx, score, snippet in fuzzy_sub:
                        print(f"      fuzzy match (score={score:.2f}): {snippet}")
                # Diagnostic for sub_keyword
                print(f"    sub_keyword diagnostic:")
                print(f"      Expected: {repr(sub_kw[:100])}")
                print(f"      Codes: {[hex(ord(c)) for c in sub_kw[:30]]}")
                if not suggestions_mode:
                    fail_count += 1
                continue

        # Suggestions mode: find alternative keywords for this paragraph
        if suggestions_mode:
            para_full = para_texts[para_idx]
            suggest = suggest_keywords(para_full, existing_keywords)
            if suggest:
                print(f"    Suggested additional keywords: {suggest[:3]}")
                suggestion_output.append({
                    'id': cid, 'para_idx': para_idx,
                    'original_keyword': keyword, 'suggestions': suggest[:3],
                })

        ok_count += 1

    print(f"\n{'='*60}")
    print(f"Summary: {ok_count} OK, {fail_count} FAILED (out of {len(comments)})")

    if suggestion_output:
        print(f"\n建议关键词汇总:")
        for s in suggestion_output:
            print(f"  id={s['id']} P{s['para_idx']}: {s['original_keyword']} -> {s['suggestions']}")

    sys.exit(fail_count)


if __name__ == '__main__':
    main()
