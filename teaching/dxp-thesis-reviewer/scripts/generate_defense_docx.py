#!/usr/bin/env python3
"""
生成答辩问题及参考答案的独立 docx 文件。

用法:
    python scripts/generate_defense_docx.py <defense_qa.json> <output.docx>

defense_qa.json 格式:
{
  "student_info": {
    "student_id": "学号",
    "student_name": "姓名",
    "thesis_title": "论文题目"
  },
  "questions": [
    {
      "category": "基础知识",
      "question": "...",
      "reference_answer": "参考答案或解答思路..."
    }
  ]
}
"""

import json, sys, os, uuid
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
W15 = 'http://schemas.microsoft.com/office/word/2012/wordml'

NS_ATTRS = {
    '{%s}Ignorable' % 'http://schemas.openxmlformats.org/markup-compatibility/2006': 'w14 w15 w16se w16cid w16 w16cex wp14',
}


def qn(tag):
    ns, local = tag.split(':')
    return '{%s}%s' % ({'w': W, 'r': R}[ns], local)


def make_paragraph(text, font_size='24', bold=False, color=None, alignment='left'):
    """Create a styled w:p element."""
    p = etree.Element(qn('w:p'))
    pPr = etree.SubElement(p, qn('w:pPr'))

    # Alignment
    if alignment != 'left':
        jc = etree.SubElement(pPr, qn('w:jc'))
        jc.set(qn('w:val'), alignment)

    # Spacing
    spacing = etree.SubElement(pPr, qn('w:spacing'))
    spacing.set(qn('w:after'), '120')
    spacing.set(qn('w:line'), '360')
    spacing.set(qn('w:lineRule'), 'auto')

    r = etree.SubElement(p, qn('w:r'))
    rPr = etree.SubElement(r, qn('w:rPr'))

    if color:
        color_el = etree.SubElement(rPr, qn('w:color'))
        color_el.set(qn('w:val'), color)

    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), font_size)
    szCs = etree.SubElement(rPr, qn('w:szCs'))
    szCs.set(qn('w:val'), font_size)

    if bold:
        etree.SubElement(rPr, qn('w:b'))
        etree.SubElement(rPr, qn('w:bCs'))

    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), 'Microsoft YaHei')
    rFonts.set(qn('w:hAnsi'), 'Microsoft YaHei')
    rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    t = etree.SubElement(r, qn('w:t'))
    t.text = text
    t.set('{%s}space' % XML_NS, 'preserve')

    return p


def build_docx(questions_data, output_path):
    """Build a minimal standalone .docx file."""
    student = questions_data.get('student_info', {})
    questions = questions_data.get('questions', [])

    sid = student.get('student_id', '')
    sname = student.get('student_name', '')
    title = student.get('thesis_title', '')

    # Build document.xml
    doc = etree.Element(qn('w:document'), nsmap={'w': W, 'r': R, 'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'})
    doc.attrib.update(NS_ATTRS)
    body = etree.SubElement(doc, qn('w:body'))

    # Title
    body.append(make_paragraph('答辩问题及参考答案', font_size='32', bold=True, alignment='center'))
    body.append(make_paragraph(''))

    # Student info section
    info_lines = [
        f'学号：{sid}',
        f'姓名：{sname}',
        f'论文题目：{title}',
    ]
    body.append(make_paragraph('基本信息', font_size='24', bold=True))
    for line in info_lines:
        body.append(make_paragraph(line, font_size='22'))

    body.append(make_paragraph(''))
    body.append(make_paragraph('━' * 40, font_size='20'))
    body.append(make_paragraph(''))

    # Questions and answers
    body.append(make_paragraph('答辩问题', font_size='28', bold=True, color='0070C0'))
    body.append(make_paragraph('—以下问题由指导教师根据论文具体弱点拟定—', font_size='20', color='0070C0'))
    body.append(make_paragraph(''))

    for i, q in enumerate(questions, 1):
        cat = q.get('category', '')
        question = q.get('question', '')
        answer = q.get('reference_answer', '')

        # Question in blue
        q_text = f'{i}. '
        if cat:
            q_text += f'[{cat}] '
        q_text += question
        body.append(make_paragraph(q_text, font_size='22', bold=True, color='0070C0'))

        # Answer in black
        if answer:
            body.append(make_paragraph(f'  参考解答/思路：{answer}', font_size='21'))
        else:
            body.append(make_paragraph(f'  （参考答案待补充）', font_size='21', color='888888'))

        body.append(make_paragraph(''))

    # Footer note
    body.append(make_paragraph('━' * 40, font_size='20'))
    body.append(make_paragraph('注意：本文件仅供指导教师答辩前参考，不应向学生公开。', font_size='18', color='888888'))

    # Section properties (required for page size)
    sectPr = etree.SubElement(body, qn('w:sectPr'))
    pgSz = etree.SubElement(sectPr, qn('w:pgSz'))
    pgSz.set(qn('w:w'), '11906')   # A4 width
    pgSz.set(qn('w:h'), '16838')   # A4 height
    pgMar = etree.SubElement(sectPr, qn('w:pgMar'))
    pgMar.set(qn('w:top'), '1440')
    pgMar.set(qn('w:right'), '1440')
    pgMar.set(qn('w:bottom'), '1440')
    pgMar.set(qn('w:left'), '1440')
    pgMar.set(qn('w:header'), '720')
    pgMar.set(qn('w:footer'), '720')

    # Build relations
    rels = etree.Element('Relationships', xmlns=R)
    rels.set('{%s}space' % XML_NS, 'preserve')
    rel = etree.SubElement(rels, 'Relationship')
    rel.set('Id', 'rId1')
    rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles')
    rel.set('Target', 'styles.xml')

    rel2 = etree.SubElement(rels, 'Relationship')
    rel2.set('Id', 'rId2')
    rel2.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme')
    rel2.set('Target', 'theme/theme1.xml')

    # Build content types
    ct = etree.Element('Types', xmlns='http://schemas.openxmlformats.org/package/2006/content-types')
    etree.SubElement(ct, 'Default', Extension='rels', ContentType='application/vnd.openxmlformats-package.relationships+xml')
    etree.SubElement(ct, 'Default', Extension='xml', ContentType='application/xml')
    etree.SubElement(ct, 'Override', PartName='/word/document.xml', ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml')
    etree.SubElement(ct, 'Override', PartName='/word/styles.xml', ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml')
    etree.SubElement(ct, 'Override', PartName='/word/theme/theme1.xml', ContentType='application/vnd.openxmlformats-officedocument.theme+xml')

    # Minimal styles.xml
    styles = etree.Element(qn('w:styles'), nsmap={'w': W, 'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'})
    docDefaults = etree.SubElement(styles, qn('w:docDefaults'))
    rPrDefault = etree.SubElement(docDefaults, qn('w:rPrDefault'))
    rPr = etree.SubElement(rPrDefault, qn('w:rPr'))
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), 'Microsoft YaHei')
    rFonts.set(qn('w:hAnsi'), 'Microsoft YaHei')
    rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), '22')
    lang = etree.SubElement(rPr, qn('w:lang'))
    lang.set(qn('w:val'), 'zh-CN')
    lang.set(qn('w:eastAsia'), 'zh-CN')

    pPrDefault = etree.SubElement(docDefaults, qn('w:pPrDefault'))
    pPr = etree.SubElement(pPrDefault, qn('w:pPr'))

    # Minimal theme
    theme = etree.Element('{%s}theme' % 'http://schemas.openxmlformats.org/drawingml/2006/main', nsmap={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'})
    theme.set('name', 'Office Theme')
    themeElements = etree.SubElement(theme, '{%s}themeElements' % 'http://schemas.openxmlformats.org/drawingml/2006/main')
    clrScheme = etree.SubElement(themeElements, '{%s}clrScheme' % 'http://schemas.openxmlformats.org/drawingml/2006/main')
    clrScheme.set('name', 'Office')
    etree.SubElement(clrScheme, '{%s}dk1' % 'http://schemas.openxmlformats.org/drawingml/2006/main').append(etree.Element('{%s}sysClr' % 'http://schemas.openxmlformats.org/drawingml/2006/main', val='windowText', lastClr='000000'))
    etree.SubElement(clrScheme, '{%s}lt1' % 'http://schemas.openxmlformats.org/drawingml/2006/main').append(etree.Element('{%s}sysClr' % 'http://schemas.openxmlformats.org/drawingml/2006/main', val='window', lastClr='FFFFFF'))
    fontScheme = etree.SubElement(themeElements, '{%s}fontScheme' % 'http://schemas.openxmlformats.org/drawingml/2006/main')
    fontScheme.set('name', 'Office')
    majorFont = etree.SubElement(fontScheme, '{%s}majorFont' % 'http://schemas.openxmlformats.org/drawingml/2006/main')
    etree.SubElement(majorFont, '{%s}ea' % 'http://schemas.openxmlformats.org/drawingml/2006/main').text = 'Microsoft YaHei'
    minorFont = etree.SubElement(fontScheme, '{%s}minorFont' % 'http://schemas.openxmlformats.org/drawingml/2006/main')
    etree.SubElement(minorFont, '{%s}ea' % 'http://schemas.openxmlformats.org/drawingml/2006/main').text = 'Microsoft YaHei'
    fmtScheme = etree.SubElement(themeElements, '{%s}fmtScheme' % 'http://schemas.openxmlformats.org/drawingml/2006/main')
    fmtScheme.set('name', 'Office')

    # Build the zip
    import zipfile
    from io import BytesIO

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',
                   etree.tostring(ct, xml_declaration=True, encoding='UTF-8', standalone=True))
        z.writestr('_rels/.rels',
                   '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
        z.writestr('word/document.xml',
                   etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True))
        z.writestr('word/_rels/document.xml.rels',
                   etree.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True))
        z.writestr('word/styles.xml',
                   etree.tostring(styles, xml_declaration=True, encoding='UTF-8', standalone=True))
        z.writestr('word/theme/theme1.xml',
                   etree.tostring(theme, xml_declaration=True, encoding='UTF-8', standalone=True))

    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_defense_docx.py <defense_qa.json> <output.docx>")
        sys.exit(1)

    qa_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(qa_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    path = build_docx(data, output_path)
    file_size = os.path.getsize(path)
    print(f'  Generated: {path} ({file_size:,} bytes)')


if __name__ == '__main__':
    main()
