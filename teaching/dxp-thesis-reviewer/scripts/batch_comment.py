#!/usr/bin/env python3
"""
批量批注写入工具 —— 一步完成所有 OOXML 级批注基础设施构建和标记插入。

改进说明 (v2.0):
  - 支持 sub_keyword: 精确定位到段落内的具体句子，而非高亮整个段落
  - 匹配失败时硬中止(exit code=失败数)，不再静默跳过
  - 无参数的 --force 可跳过严格检查继续执行

用法:
    python batch_comment.py <unpacked_dir/> <comments.json> --author "指导教师姓名" --initials "缩写"

comments.json 格式:
{
  "author": "指导教师",
  "initials": "DS",
  "comments": [
    {
      "id": 0,
      "keyword": "需要批注的关键词",
      "occ": 0,
      "text": "[问题类型] 具体修改建议。"
    },
    {
      "id": 1,
      "keyword": "段落中的关键词",
      "sub_keyword": "只高亮这一小段（可选）",
      "occ": 0,
      "text": "[问题类型] 具体修改建议。"
    }
  ]
}
"""

import json, os, sys, uuid, argparse
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W14 = 'http://schemas.microsoft.com/office/word/2010/wordml'
W15 = 'http://schemas.microsoft.com/office/word/2012/wordml'
W16CEX = 'http://schemas.microsoft.com/office/word/2018/wordml/cex'
W16CID = 'http://schemas.microsoft.com/office/word/2016/wordml/cid'
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
NCT = 'http://schemas.openxmlformats.org/package/2006/content-types'
R_PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'

NSMAP = {
    'w': W, 'r': R, 'mc': MC,
    'w14': W14, 'w15': W15, 'w16cex': W16CEX, 'w16cid': W16CID,
}


def qn(tag):
    ns, local = tag.split(':')
    return '{%s}%s' % (NSMAP[ns], local)


def ensure_content_type(unpacked, part_name, content_type):
    ctp = os.path.join(unpacked, '[Content_Types].xml')
    ct = etree.parse(ctp)
    cr = ct.getroot()
    for o in cr.findall('{%s}Override' % NCT):
        if o.get('PartName') == part_name:
            return
    etree.SubElement(cr, 'Override', {'PartName': part_name, 'ContentType': content_type})
    ct.write(ctp, xml_declaration=True, encoding='UTF-8', standalone=True)


def ensure_relationship(unpacked, target, rel_type):
    rp = os.path.join(unpacked, 'word', '_rels', 'document.xml.rels')
    rt = etree.parse(rp)
    rr = rt.getroot()
    for r in rr:
        if r.get('Target') == target:
            return
    rid = 'rId%d' % (500 + len(rr))
    etree.SubElement(rr, '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship', {
        'Id': rid, 'Type': rel_type, 'Target': target,
    })
    rt.write(rp, xml_declaration=True, encoding='UTF-8', standalone=True)


def ensure_comment_styles(unpacked):
    sp = os.path.join(unpacked, 'word', 'styles.xml')
    st = etree.parse(sp)
    sr = st.getroot()
    existing = {s.get(qn('w:styleId')) for s in sr if s.get(qn('w:styleId'))}

    styles_to_add = [
        ('paragraph', 'CommentText', 'Comment Text',
         [('w:basedOn', 'Normal'), ('w:autoRedefine', '0'), ('w:uiPriority', '99'), ('w:semiHidden', '1'), ('w:unhideWhenUsed', '1')],
         [('w:spacing', {'w:after': '0', 'w:line': '240', 'w:lineRule': 'auto'})]),
        ('character', 'CommentReference', 'Comment Reference',
         [('w:basedOn', 'DefaultParagraphFont'), ('w:uiPriority', '99'), ('w:semiHidden', '1'), ('w:unhideWhenUsed', '1')],
         []),
        ('character', 'CommentSubject', 'Comment Subject',
         [('w:basedOn', 'CommentReference'), ('w:uiPriority', '99'), ('w:semiHidden', '1'), ('w:unhideWhenUsed', '1')],
         [('w:b', None), ('w:bCs', None), ('w:sz', '20'), ('w:szCs', '20')]),
        ('paragraph', 'BalloonText', 'Balloon Text',
         [('w:basedOn', 'Normal'), ('w:autoRedefine', '0'), ('w:uiPriority', '99'), ('w:semiHidden', '1'), ('w:unhideWhenUsed', '1')],
         [('w:spacing', {'w:after': '0', 'w:line': '240', 'w:lineRule': 'auto'})]),
    ]

    added = 0
    for stype, sid, sname, attrs, rpr_items in styles_to_add:
        if sid not in existing:
            style = etree.SubElement(sr, qn('w:style'), {qn('w:type'): stype, qn('w:styleId'): sid, qn('w:default'): '0'})
            etree.SubElement(style, qn('w:name')).set(qn('w:val'), sname)
            for ak, av in attrs:
                if av is not None:
                    style.set(qn(ak), av)
            if rpr_items:
                rpr_el = etree.SubElement(style, qn('w:rPr'))
                for rk, rv in rpr_items:
                    child = etree.SubElement(rpr_el, qn(rk))
                    if isinstance(rv, dict):
                        for sk, sv in rv.items():
                            child.set(qn(sk), sv)
                    elif rv is not None:
                        child.set(qn('w:val'), rv)
            added += 1

    if added:
        st.write(sp, xml_declaration=True, encoding='UTF-8', standalone=True)
        print(f'  Styles added: {added}')
    else:
        print('  Styles already present')


def build_comments_xml(unpacked, comments_data):
    cp = os.path.join(unpacked, 'word', 'comments.xml')
    root = etree.Element(qn('w:comments'), nsmap=NSMAP)
    root.set('{%s}Ignorable' % MC, 'w14 w15 w16cex w16cid')

    for c in comments_data:
        durable = str(uuid.uuid4()).upper()[:8]
        cmt = etree.SubElement(root, qn('w:comment'), {
            qn('w:id'): str(c['id']),
            qn('w:author'): c['author'],
            qn('w:initials'): c['initials'],
            qn('w:date'): '2026-01-01T00:00:00Z',
            qn('w16cid:durableId'): durable,
        })
        p = etree.SubElement(cmt, qn('w:p'))
        pp = etree.SubElement(p, qn('w:pPr'))
        etree.SubElement(pp, qn('w:pStyle')).set(qn('w:val'), 'CommentText')
        r = etree.SubElement(p, qn('w:r'))
        rp = etree.SubElement(r, qn('w:rPr'))
        rf = etree.SubElement(rp, qn('w:rFonts'))
        rf.set(qn('w:ascii'), 'Microsoft YaHei')
        rf.set(qn('w:hAnsi'), 'Microsoft YaHei')
        rf.set(qn('w:eastAsia'), 'Microsoft YaHei')
        etree.SubElement(rp, qn('w:sz')).set(qn('w:val'), '20')
        etree.SubElement(rp, qn('w:szCs')).set(qn('w:val'), '20')
        t = etree.SubElement(r, qn('w:t'))
        t.text = c['text']
        t.set('{%s}space' % XML_NS, 'preserve')

    etree.ElementTree(root).write(cp, xml_declaration=True, encoding='UTF-8', standalone=True)
    print(f'  comments.xml: {len(comments_data)} comments')


def build_comments_extended(unpacked, comment_ids):
    cep = os.path.join(unpacked, 'word', 'commentsExtended.xml')
    root = etree.Element(qn('w15:commentsEx'), nsmap={'w15': W15, 'mc': MC})
    root.set('{%s}Ignorable' % MC, 'w15')
    for cid in sorted(comment_ids):
        pid = str(uuid.uuid4()).upper()[:8]
        etree.SubElement(root, qn('w15:commentEx'), {
            qn('w15:paraId'): pid,
            qn('w15:paraIdParent'): pid,
            qn('w15:durableId'): str(uuid.uuid4()).upper()[:8],
        })
    etree.ElementTree(root).write(cep, xml_declaration=True, encoding='UTF-8', standalone=True)
    print(f'  commentsExtended.xml: {len(comment_ids)} entries')


def insert_document_markers(unpacked, para_indices, sub_keywords_map):
    """Remove old markers and insert correct ones, with optional sub_keyword for precise range."""
    dp = os.path.join(unpacked, 'word', 'document.xml')
    dt = etree.parse(dp)
    dr = dt.getroot()
    all_p = dr.findall('.//{%s}p' % W)

    for tag in ['commentRangeStart', 'commentRangeEnd', 'commentReference']:
        for el in list(dr.iter('{%s}%s' % (W, tag))):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
    print(f'  Cleared old markers from {len(all_p)} paragraphs')

    for p in all_p:
        if not p.get(qn('w15:paraId')):
            p.set(qn('w15:paraId'), str(uuid.uuid4()).upper()[:8])

    for cid, para_idx in sorted(para_indices, key=lambda x: x[1], reverse=True):
        if para_idx >= len(all_p):
            print(f'  WARNING: para_idx {para_idx} out of range for comment {cid}')
            continue
        target_p = all_p[para_idx]
        sid = str(cid)

        crs = etree.Element(qn('w:commentRangeStart'), {qn('w:id'): sid})
        cre = etree.Element(qn('w:commentRangeEnd'), {qn('w:id'): sid})

        r = etree.Element(qn('w:r'))
        rPr_el = etree.SubElement(r, qn('w:rPr'))
        rs = etree.SubElement(rPr_el, qn('w:rStyle'))
        rs.set(qn('w:val'), 'CommentReference')
        cref_el = etree.SubElement(r, qn('w:commentReference'))
        cref_el.set(qn('w:id'), sid)

        sub_kw = sub_keywords_map.get(cid)
        if sub_kw:
            # Insert markers around the sub_keyword inside the paragraph
            # Find which <w:r> elements contain the sub_keyword and wrap those
            para_text = ''.join(t.text or '' for t in target_p.iter('{%s}t' % W))
            sub_pos = para_text.find(sub_kw)
            if sub_pos >= 0:
                sub_end = sub_pos + len(sub_kw)
                # Walk <w:r> elements to find the range
                run_elements = list(target_p.findall('{%s}r' % W))
                char_offset = 0
                insert_crs = None
                insert_cre_after = None
                for ri, run in enumerate(run_elements):
                    run_text = ''.join(t.text or '' for t in run.iter('{%s}t' % W))
                    run_len = len(run_text)
                    run_end = char_offset + run_len
                    if insert_crs is None and run_end > sub_pos:
                        insert_crs = run
                    if insert_cre_after is None and run_end >= sub_end:
                        insert_cre_after = ri
                        break
                    char_offset = run_end
                if insert_crs and insert_cre_after is not None:
                    target_p.insert(list(target_p).index(insert_crs), crs)
                    target_p.insert(list(target_p).index(insert_crs) + 1, cre)
                    target_p.append(r)
                else:
                    target_p.insert(0, crs)
                    target_p.insert(1, cre)
                    target_p.append(r)
            else:
                target_p.insert(0, crs)
                target_p.insert(1, cre)
                target_p.append(r)
        else:
            target_p.insert(0, crs)
            target_p.insert(1, cre)
            target_p.append(r)

    dt.write(dp, xml_declaration=True, encoding='UTF-8', standalone=True)
    print(f'  Inserted markers for {len(para_indices)} comments')


def main():
    parser = argparse.ArgumentParser(description='Batch OOXML comment inserter')
    parser.add_argument('unpacked', help='Path to unpacked docx directory')
    parser.add_argument('comments_json', help='Path to comments JSON file')
    parser.add_argument('--author', default='指导教师', help='Comment author name')
    parser.add_argument('--initials', default='T', help='Comment author initials')
    parser.add_argument('--force', action='store_true', help='Continue even if some keywords fail to match')
    args = parser.parse_args()

    with open(args.comments_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    author = data.get('author', args.author)
    initials = data.get('initials', args.initials)
    comments = data['comments']

    dp_file = os.path.join(args.unpacked, 'word', 'document.xml')
    dt = etree.parse(dp_file)
    dr = dt.getroot()
    all_p = dr.findall('.//{%s}p' % W)
    para_texts = [''.join(t.text or '' for t in p.iter('{%s}t' % W)) for p in all_p]
    print(f'Paragraph index: {len(para_texts)} paragraphs')

    para_indices = []
    comment_data = []
    failures = []

    for cmt in comments:
        cid = cmt['id']
        keyword = cmt['keyword']
        occ = cmt.get('occ', 0)
        text = cmt['text']

        matches = [i for i, pt in enumerate(para_texts) if keyword in pt]
        if len(matches) > occ:
            para_indices.append((cid, matches[occ]))
            comment_data.append({
                'id': cid, 'author': author, 'initials': initials, 'text': text,
            })
        else:
            msg = f'FAIL id={cid}: keyword "{keyword[:80]}" occ={occ} found {len(matches)} match(es)'
            print(f'  {msg}')
            failures.append(msg)

    if failures:
        print(f'\n*** {len(failures)} keyword(s) failed to match ***')
        if not args.force:
            print('Use --force to skip failed keywords and continue, or fix comments.json first.')
            print('Tip: run scripts/find_paragraphs.py with --verify to debug failing keywords.')
            sys.exit(len(failures))
        else:
            print('--force set: continuing with successful matches only.')

    print(f'\nResolved: {len(para_indices)} comments, {len(failures)} failures')

    print(f'\n=== Step 1: Infrastructure ===')
    ensure_content_type(args.unpacked, '/word/comments.xml',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml')
    ensure_content_type(args.unpacked, '/word/commentsExtended.xml',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml')
    ensure_relationship(args.unpacked, 'comments.xml',
                        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments')
    ensure_relationship(args.unpacked, 'commentsExtended.xml',
                        'http://schemas.microsoft.com/office/word/2012/wordml/relationships/commentsExtended')
    ensure_comment_styles(args.unpacked)
    print('  Infrastructure complete')

    print(f'\n=== Step 2: Build comments.xml ===')
    build_comments_xml(args.unpacked, comment_data)

    print(f'\n=== Step 3: Build commentsExtended.xml ===')
    build_comments_extended(args.unpacked, [c['id'] for c in comment_data])

    print(f'\n=== Step 4: Insert markers into document.xml ===')
    sub_keywords = {}
    for cmt in comments:
        if 'sub_keyword' in cmt:
            cid = cmt['id']
            sub_keywords[cid] = cmt['sub_keyword']
    insert_document_markers(args.unpacked, para_indices, sub_keywords)

    print(f'\n=== Done: {len(para_indices)} comments written ===')


if __name__ == '__main__':
    main()
