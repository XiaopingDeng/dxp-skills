#!/usr/bin/env python3
"""
在正式写入批注前，预验证所有 keyword→段落映射是否正确。

为什么需要这个脚本：
    中文论文中，同一个短语可能在多个段落出现，或者在 Bash/终端编码环境下
    匹配失败（GBK vs UTF-8）。在跑完 batch_comment.py 之前提前验证，
    可以避免"批注挂错段落"或"部分批注丢失"的问题。

用法:
    python validate_keywords.py <unpacked_dir/> <comments.json>

输出:
    - 每个批注的匹配状态（OK / 关键词不存在 / occ 超出范围）
    - 对于每个 OK，打印匹配到的段落前 120 字符供人工核对
    - 统计：总数 / 成功 / 失败
"""

import json, os, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def main():
    if len(sys.argv) < 3:
        print("Usage: python validate_keywords.py <unpacked_dir/> <comments.json>")
        print("  Returns exit code = number of failed matches")
        sys.exit(0)

    unpacked = sys.argv[1]
    comments_path = sys.argv[2]

    # Load document text
    doc_path = os.path.join(unpacked, 'word', 'document.xml')
    if not os.path.exists(doc_path):
        print("ERROR: word/document.xml not found. Is the docx unpacked?")
        sys.exit(1)

    dt = etree.parse(doc_path)
    paras = dt.getroot().findall('.//{%s}p' % W)
    para_texts = [''.join(t.text or '' for t in p.iter('{%s}t' % W)) for p in paras]
    print(f"Loaded {len(paras)} paragraphs ({len([p for p in para_texts if p.strip()])} non-empty)")

    # Load comments
    with open(comments_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = data.get('comments', [])
    print(f"Loaded {len(comments)} comments to validate\n")

    ok_count = 0
    fail_count = 0

    for cmt in comments:
        cid = cmt['id']
        keyword = cmt['keyword']
        occ = cmt.get('occ', 0)
        text_preview = cmt['text'][:60]

        matches = [i for i, pt in enumerate(para_texts) if keyword in pt]

        if not matches:
            print(f"  [FAIL id={cid}] keyword NOT FOUND in any paragraph")
            print(f"    keyword: {keyword[:100]}")
            print(f"    comment: {text_preview}...")
            fail_count += 1
            continue

        if len(matches) <= occ:
            print(f"  [FAIL id={cid}] occ={occ} requested but only {len(matches)} match(es)")
            for mi, m_idx in enumerate(matches):
                print(f"    match[{mi}] P{m_idx}: {para_texts[m_idx][:120]}")
            print(f"    comment: {text_preview}...")
            fail_count += 1
            continue

        matched_para = para_texts[matches[occ]][:120]
        print(f"  [OK  id={cid}] P{matches[occ]} ({len(matches)} total matches, using occ={occ})")
        print(f"    para: {matched_para}...")
        print(f"    cmt:  {text_preview}...")
        ok_count += 1

    print(f"\n{'='*60}")
    print(f"Summary: {ok_count} OK, {fail_count} FAILED (out of {len(comments)})")

    sys.exit(fail_count)


if __name__ == '__main__':
    main()
