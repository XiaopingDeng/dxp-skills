#!/usr/bin/env python3
"""
批量批注写入工具 —— 一步完成所有 OOXML 级批注基础设施构建和标记插入。

用法:
    python batch_comment.py <unpacked_dir/> <comments.json> --author "指导教师姓名" --initials "缩写"

comments.json 格式:
{
  "author": "指导教师：邓晓平",
  "initials": "DXP",
  "comments": [
    {"id": 0, "keyword": "需要批注的关键词", "occ": 0, "text": "[问题类型] 具体修改建议。"},
    ...
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
    """Add CommentText, CommentReference, CommentSubject, BalloonText to styles.xml."""
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
    """Build word/comments.xml with all comments and durableId."""
    cp = os.path.join(unpacked, 'word', 'comments.xml')
    root = etree.Element(qn('w:comments'), nsmap=NSMAP)
    root.set('{%s}Ignorable' % MC, 'w14 w15 w16cex w16cid')

    for c in comments_data:
        durable = str(uuid.uuid4()).upper()[:8]
        cmt = etree.SubElement(root, qn('w:comment'), {
            qn('w:id'): str(c['id']),
            qn('w:author'): c['author'],
            qn('w:initials'): c['initials'],
            qn('w:date'): '2026-06-12T00:00:00Z',
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
    """Build word/commentsExtended.xml with w15:commentEx entries."""
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


def insert_document_markers(unpacked, para_indices):
    """Remove old markers and insert correct ones INSIDE target paragraphs."""
    dp = os.path.join(unpacked, 'word', 'document.xml')
    dt = etree.parse(dp)
    dr = dt.getroot()
    all_p = dr.findall('.//{%s}p' % W)

    # Remove all existing markers
    for tag_name in ['commentRangeStart', 'commentRangeEnd', 'commentReference']:
        for el in list(dr.iter('{%s}%s' % (W, tag_name))):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
    print(f'  Cleared old markers from {len(all_p)} paragraphs')

    # Add w15:paraId to all paragraphs
    for p in all_p:
        if not p.get(qn('w15:paraId')):
            p.set(qn('w15:paraId'), str(uuid.uuid4()).upper()[:8])

    # Insert markers for each comment
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

        # Insert CRS + CRE at position 0 in the paragraph
        target_p.insert(0, crs)
        target_p.insert(1, cre)
        # Append commentReference run at the end of the paragraph
        target_p.append(r)

    dt.write(dp, xml_declaration=True, encoding='UTF-8', standalone=True)
    print(f'  Inserted markers for {len(para_indices)} comments')


def main():
    parser = argparse.ArgumentParser(description='Batch OOXML comment inserter')
    parser.add_argument('unpacked', help='Path to unpacked docx directory')
    parser.add_argument('comments_json', help='Path to comments JSON file')
    parser.add_argument('--author', default='指导教师', help='Comment author name')
    parser.add_argument('--initials', default='DS', help='Comment author initials')
    args = parser.parse_args()

    with open(args.comments_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    author = data.get('author', args.author)
    initials = data.get('initials', args.initials)
    comments = data['comments']

    # Build paragraph text index for keyword matching
    dp = os.path.join(args.unpacked, 'word', 'document.xml')
    dt = etree.parse(dp)
    dr = dt.getroot()
    all_p = dr.findall('.//{%s}p' % W)
    para_texts = [''.join(t.text or '' for t in p.iter('{%s}t' % W)) for p in all_p]
    print(f'Paragraph index: {len(para_texts)} paragraphs')

    # Resolve paragraph indices from keywords
    para_indices = []
    comment_data = []
    skipped = 0

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
            print(f'  SKIP [{cid}]: keyword "{keyword[:60]}" occ={occ} found {len(matches)} matches')
            skipped += 1

    print(f'\nResolved: {len(para_indices)} comments, {skipped} skipped')
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
    insert_document_markers(args.unpacked, para_indices)

    print(f'\n=== Done: {len(para_indices)} comments written ===')


if __name__ == '__main__':
    main()
