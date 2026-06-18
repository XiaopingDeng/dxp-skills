#!/usr/bin/env python3
"""验证 .docx 文件中批注嵌入是否正确。用于 Stage 2 打包后的质量检查。"""
import zipfile, sys, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W15 = 'http://schemas.microsoft.com/office/word/2012/wordml'
W16CID = 'http://schemas.microsoft.com/office/word/2016/wordml/cid'

def verify(docx_path):
    results = []
    with zipfile.ZipFile(docx_path, 'r') as z:
        names = z.namelist()

        # 1. comments.xml
        if 'word/comments.xml' not in names:
            results.append(('FAIL', 'word/comments.xml missing'))
        else:
            with z.open('word/comments.xml') as f:
                ct = etree.parse(f)
                cmts = ct.findall('.//{%s}comment' % W)
                cmt_count = len(cmts)
                durable_ok = sum(1 for c in cmts if c.get('{%s}durableId' % W16CID))
                results.append(('OK' if cmt_count > 0 else 'FAIL',
                                f'comments.xml: {cmt_count} comments (durableId: {durable_ok}/{cmt_count})'))

        # 2. commentsExtended.xml
        if 'word/commentsExtended.xml' not in names:
            results.append(('WARN', 'word/commentsExtended.xml missing'))
        else:
            with z.open('word/commentsExtended.xml') as f:
                ce = etree.parse(f)
                ce_count = len(ce.findall('.//{%s}commentEx' % W15))
                results.append(('OK' if ce_count > 0 else 'WARN',
                                f'commentsExtended.xml: {ce_count} entries'))

        # 3. document.xml markers
        with z.open('word/document.xml') as f:
            raw = f.read().decode('utf-8')
        crs = re.findall(r'<w:commentRangeStart w:id="(\d+)"', raw)
        cre = re.findall(r'<w:commentRangeEnd w:id="(\d+)"', raw)
        cref = re.findall(r'<w:commentReference w:id="(\d+)"', raw)
        crs_set = set(int(x) for x in crs)
        cre_set = set(int(x) for x in cre)
        cref_set = set(int(x) for x in cref)
        match_all = crs_set == cre_set == cref_set
        results.append(('OK' if match_all else 'FAIL',
                        f'Markers: CRS={len(crs)} CRE={len(cre)} CRef={len(cref)} ID_match={match_all}'))

        # 4. Marker placement: CRS inside w:p
        with z.open('word/document.xml') as f:
            dt = etree.parse(f)
            all_crs_el = dt.getroot().findall('.//{%s}commentRangeStart' % W)
            crs_in_p = sum(1 for c in all_crs_el if c.getparent().tag == '{%s}p' % W)
        results.append(('OK' if crs_in_p == len(all_crs_el) else 'FAIL',
                        f'CRS inside w:p: {crs_in_p}/{len(all_crs_el)}'))

        # 5. Styles
        with z.open('word/styles.xml') as f:
            st = etree.parse(f)
            styles_root = st.getroot()
            for sid in ['CommentText', 'CommentReference', 'CommentSubject', 'BalloonText']:
                found = any(s.get('{%s}styleId' % W) == sid for s in styles_root)
                results.append(('OK' if found else 'FAIL', f'Style {sid}: {"FOUND" if found else "MISSING"}'))

        # 6. Content Types & Relationships
        with z.open('[Content_Types].xml') as f:
            ct_raw = f.read().decode('utf-8')
        for kw in ['comments.xml', 'commentsExtended']:
            results.append(('OK' if kw in ct_raw else 'FAIL', f'[Content_Types].xml: {kw} {"FOUND" if kw in ct_raw else "MISSING"}'))

        with z.open('word/_rels/document.xml.rels') as f:
            rels_raw = f.read().decode('utf-8')
        for kw in ['comments.xml', 'commentsExtended']:
            results.append(('OK' if kw in rels_raw else 'FAIL', f'rels: {kw} {"FOUND" if kw in rels_raw else "MISSING"}'))

    # Print results
    fails = sum(1 for r in results if r[0] == 'FAIL')
    warns = sum(1 for r in results if r[0] == 'WARN')
    for status, msg in results:
        icon = 'PASS' if status == 'OK' else ('FAIL' if status == 'FAIL' else 'WARN')
        print(f'  [{icon}] {msg}')

    print()
    if fails == 0 and warns == 0:
        print('ALL CHECKS PASSED — comments should display correctly in Word.')
    elif fails > 0:
        print(f'{fails} FAILURES detected — comments may NOT display correctly in Word.')
        sys.exit(1)
    else:
        print(f'{warns} WARNINGS — comments should work but may have issues in older Word versions.')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python verify_comments.py <output.docx>")
        sys.exit(1)
    verify(sys.argv[1])
