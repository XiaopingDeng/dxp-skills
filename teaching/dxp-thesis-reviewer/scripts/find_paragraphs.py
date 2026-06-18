#!/usr/bin/env python3
"""
段落查找与预览工具 —— 在批注编写前使用，确认关键词在文档中的实际位置。

避免"自以为关键词在段落中，实际却不匹配"的陷阱。
支持精确匹配和模糊匹配预览。

用法:
    # 列出所有段落编号（有内容的段落）
    python scripts/find_paragraphs.py <unpacked_dir/>

    # 搜索含某关键词的段落，显示前120字
    python scripts/find_paragraphs.py <unpacked_dir/> --search "关键词"

    # 模糊搜索（容忍编辑距离 ≤ 2 的字符差异）
    python scripts/find_paragraphs.py <unpacked_dir/> --fuzzy "系统总体架构框图"

    # 显示指定段落的完整文本
    python scripts/find_paragraphs.py <unpacked_dir/> --show 171

    # 显示指定范围段落
    python scripts/find_paragraphs.py <unpacked_dir/> --range 200-210

    # 验证关键词匹配：输出精确的匹配信息（推荐在编写comments.json后使用）
    python scripts/find_paragraphs.py <unpacked_dir/> --verify "要验证的关键词"
"""

import os, sys, argparse
from lxml import etree
from difflib import SequenceMatcher

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def load_paragraphs(unpacked):
    dp = os.path.join(unpacked, 'word', 'document.xml')
    if not os.path.exists(dp):
        print(f"ERROR: {dp} not found. Is the docx unpacked?")
        sys.exit(1)
    dt = etree.parse(dp)
    paras = dt.getroot().findall('.//{%s}p' % W)
    para_texts = [''.join(t.text or '' for t in p.iter('{%s}t' % W)) for p in paras]
    return para_texts


def show_paragraph(para_texts, idx, context_chars=200):
    if idx < 0 or idx >= len(para_texts):
        print(f"Paragraph {idx} out of range (0-{len(para_texts)-1})")
        return
    text = para_texts[idx]
    print(f"--- P{idx} ({len(text)} chars) ---")
    display = text if len(text) <= context_chars else text[:context_chars] + "..."
    print(display)
    print(f"--- end P{idx} ---")


def search_exact(para_texts, keyword):
    matches = [(i, pt) for i, pt in enumerate(para_texts) if keyword in pt]
    return matches


def search_fuzzy(para_texts, keyword, cutoff=0.75):
    """Search using difflib ratio matching (tolerant to minor character differences)."""
    matches = []
    for i, pt in enumerate(para_texts):
        if pt:
            ratio = SequenceMatcher(None, keyword, pt).ratio()
            if ratio > cutoff:
                matches.append((i, pt, ratio))
    matches.sort(key=lambda x: -x[2])
    return matches


def suggest_keyword_candidates(para_texts, paragraph_idx):
    """Suggest good keyword fragments from a paragraph."""
    text = para_texts[paragraph_idx]
    if not text.strip():
        print(f"P{paragraph_idx} is empty.")
        return

    pieces = []
    # Suggest the first 20 chars, a middle 20-char chunk, and a last 20-char chunk
    if len(text) >= 20:
        pieces.append(("开头", text[:25]))
    if len(text) >= 40:
        mid = len(text) // 2
        pieces.append(("中间", text[mid:mid+25]))
    if len(text) >= 20:
        pieces.append(("末尾", text[-25:]))

    print(f"\nP{paragraph_idx} 关键词建议（用于 comments.json 的 keyword 字段）:")
    print(f"  全文共 {len(text)} 字符")
    for label, frag in pieces:
        print(f"  [{label}] \"{frag}\"")
    print()
    print(f"  验证唯一性：python scripts/find_paragraphs.py <unpacked> --search \"你的关键词\"")


def main():
    parser = argparse.ArgumentParser(description='Paragraph finder and preview tool')
    parser.add_argument('unpacked', help='Path to unpacked docx directory')
    parser.add_argument('--search', help='Exact substring search')
    parser.add_argument('--fuzzy', help='Fuzzy search (tolerates character differences)')
    parser.add_argument('--show', type=int, help='Show full text of paragraph at index')
    parser.add_argument('--range', help='Show paragraphs in range, e.g. 200-210')
    parser.add_argument('--verify', help='Verify a keyword and show match details')
    parser.add_argument('--suggest', type=int, help='Suggest keyword candidates from paragraph index')
    parser.add_argument('--list-empty', action='store_true', help='List empty paragraphs')
    args = parser.parse_args()

    para_texts = load_paragraphs(args.unpacked)

    # Default: show stats
    if not any([args.search, args.fuzzy, args.show is not None, args.range,
                args.verify, args.suggest is not None, args.list_empty]):
        non_empty = len([p for p in para_texts if p.strip()])
        print(f"Total paragraphs: {len(para_texts)}, non-empty: {non_empty}")
        print(f"Use --search <keyword> to find paragraphs")
        print(f"Use --fuzzy <keyword> for fuzzy search")
        print(f"Use --show <N> to view paragraph N")
        print(f"Use --range <N-M> to view a range")
        print(f"Use --verify <keyword> to verify a keyword")
        print(f"Use --suggest <N> to get keyword suggestions")
        return

    if args.search:
        matches = search_exact(para_texts, args.search)
        if matches:
            print(f"Found {len(matches)} exact match(es) for \"{args.search}\":")
            for i, pt in matches:
                display = pt[:120] + ("..." if len(pt) > 120 else "")
                print(f"  P{i} ({len(pt)} chars): {display}")
        else:
            print(f"No exact match for \"{args.search}\"")
            # Suggest fuzzy
            fuzzy = search_fuzzy(para_texts, args.search)
            if fuzzy:
                print(f"  Did you mean? (fuzzy matches):")
                for i, pt, ratio in fuzzy[:3]:
                    print(f"    P{i} (ratio={ratio:.2f}): {pt[:80]}...")

    if args.fuzzy:
        matches = search_fuzzy(para_texts, args.fuzzy)
        print(f"Fuzzy search for \"{args.fuzzy}\": {len(matches)} matches")
        for i, pt, ratio in matches[:10]:
            display = pt[:100] + ("..." if len(pt) > 100 else "")
            print(f"  P{i} (ratio={ratio:.3f}): {display}")

    if args.show is not None:
        show_paragraph(para_texts, args.show, context_chars=999999)

    if args.range:
        parts = args.range.split('-')
        start, end = int(parts[0]), int(parts[1])
        for idx in range(start, min(end + 1, len(para_texts))):
            text = para_texts[idx]
            if text.strip():
                display = text[:150] + ("..." if len(text) > 150 else "")
                print(f"P{idx}: {display}")

    if args.verify:
        keyword = args.verify
        matches = search_exact(para_texts, keyword)
        if matches:
            print(f"EXACT MATCH: Found in {len(matches)} paragraph(s):")
            for i, pt in matches:
                # Show context around the keyword
                kw_pos = pt.find(keyword)
                pre = max(0, kw_pos - 20)
                post = min(len(pt), kw_pos + len(keyword) + 20)
                context = pt[pre:post]
                print(f"  P{i}: ...{context}...")
            print(f"\n\u2713 Keyword OK for comments.json")
        else:
            print(f"NO EXACT MATCH for \"{keyword}\"")
            # Try character-by-character analysis
            print(f"\n  Keyword characters: {[hex(ord(c)) for c in keyword]}")
            # Try to find each individual character
            missing_chars = []
            for j, ch in enumerate(keyword):
                found_any = any(ch in pt for pt in para_texts)
                if not found_any:
                    missing_chars.append(f"U+{ord(ch):04X}='{ch}' at pos {j}")
            if missing_chars:
                print(f"  Characters never appearing in document: {missing_chars}")
            # Fuzzy suggestion
            fuzzy = search_fuzzy(para_texts, keyword)
            if fuzzy:
                print(f"  Closest fuzzy matches:")
                for i, pt, ratio in fuzzy[:3]:
                    display = pt[:120] + ("..." if len(pt) > 120 else "")
                    print(f"    P{i} (ratio={ratio:.3f}): {display}")

    if args.suggest is not None:
        suggest_keyword_candidates(para_texts, args.suggest)

    if args.list_empty:
        empty = [(i, pt) for i, pt in enumerate(para_texts) if not pt.strip()]
        print(f"Empty paragraphs: {len(empty)}")
        for i, _ in empty[:20]:
            print(f"  P{i}")


if __name__ == '__main__':
    main()
