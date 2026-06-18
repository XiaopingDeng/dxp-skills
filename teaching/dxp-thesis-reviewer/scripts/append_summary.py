#!/usr/bin/env python3
"""
在文档末尾追加红色字体的结构性问题总结段落。
用于表述不宜以批注形式呈现的整体性/全局性问题。

用法:
    python scripts/append_summary.py <unpacked_dir/> <summary_items.json>

summary_items.json 格式:
{
  "title": "论文整体结构与总体评价",
  "items": [
    "章节比例失衡：...",
    "缺少必要的...",
    ...
  ]
}
"""

import json, sys, os
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
XML_NS = 'http://www.w3.org/XML/1998/namespace'

def qn(tag):
    ns, local = tag.split(':')
    return '{%s}%s' % ({'w': W, 'r': R}[ns], local)

def make_red_paragraph(text, font_size='24', bold=False):
    """Create a w:p element with red font color."""
    p = etree.Element(qn('w:p'))

    # Add paragraph properties with red font in run properties
    pPr = etree.SubElement(p, qn('w:pPr'))

    # Create a run with red font
    r = etree.SubElement(p, qn('w:r'))
    rPr = etree.SubElement(r, qn('w:rPr'))

    # Set font color to red
    color = etree.SubElement(rPr, qn('w:color'))
    color.set(qn('w:val'), 'FF0000')

    # Set font size
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), font_size)
    szCs = etree.SubElement(rPr, qn('w:szCs'))
    szCs.set(qn('w:val'), font_size)

    # Bold if needed
    if bold:
        etree.SubElement(rPr, qn('w:b'))
        etree.SubElement(rPr, qn('w:bCs'))

    # Set font to Microsoft YaHei
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), 'Microsoft YaHei')
    rFonts.set(qn('w:hAnsi'), 'Microsoft YaHei')
    rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    # Add text
    t = etree.SubElement(r, qn('w:t'))
    t.text = text
    t.set('{%s}space' % XML_NS, 'preserve')

    return p


def make_red_separator():
    """Create a separator line between comments and summary."""
    p = etree.Element(qn('w:p'))
    pPr = etree.SubElement(p, qn('w:pPr'))

    # Add a paragraph with just a page break style separator effect
    r = etree.SubElement(p, qn('w:r'))
    rPr = etree.SubElement(r, qn('w:rPr'))
    color = etree.SubElement(rPr, qn('w:color'))
    color.set(qn('w:val'), 'FF0000')
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), '24')
    szCs = etree.SubElement(rPr, qn('w:szCs'))
    szCs.set(qn('w:val'), '24')
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
    rFonts.set(qn('w:ascii'), 'Microsoft YaHei')
    rFonts.set(qn('w:hAnsi'), 'Microsoft YaHei')
    rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    t = etree.SubElement(r, qn('w:t'))
    t.text = '══════════════════════════════════════'
    t.set('{%s}space' % XML_NS, 'preserve')

    return p


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/append_summary.py <unpacked_dir/> <summary_items.json>")
        sys.exit(1)

    unpacked = sys.argv[1]
    items_path = sys.argv[2]

    with open(items_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data.get('title', '论文整体结构与总体评价')
    items = data.get('items', [])

    if not items:
        print("  WARNING: No summary items provided, nothing to append.")
        return

    dp = os.path.join(unpacked, 'word', 'document.xml')
    dt = etree.parse(dp)
    dr = dt.getroot()
    body = dr.find('{%s}body' % W)

    # Append separator
    body.append(make_red_separator())

    # Append title
    body.append(make_red_paragraph(f'【{title}】', font_size='28', bold=True))

    # Append blank line
    body.append(make_red_paragraph(''))

    # Append each item
    for i, item in enumerate(items, 1):
        body.append(make_red_paragraph(f'{i}. {item}'))

    # Append blank line at end
    body.append(make_red_paragraph(''))

    dt.write(dp, xml_declaration=True, encoding='UTF-8', standalone=True)
    print(f'  Appended summary: {len(items)} items in red font')


if __name__ == '__main__':
    main()
