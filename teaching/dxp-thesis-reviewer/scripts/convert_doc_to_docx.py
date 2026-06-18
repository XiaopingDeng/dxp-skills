#!/usr/bin/env python3
"""
将 .doc（二进制 OLE2 格式）转换为 .docx（OOXML 格式）。

中文大学环境中，学生普遍使用 WPS Office 保存为 .doc 格式而非 .docx，
本脚本提供自动转换能力，是 Stage 0 的前置步骤。

用法:
    python convert_doc_to_docx.py <input.doc> [output.docx]

依赖: pywin32 + 本机安装的 Microsoft Word 或 WPS Office
"""

import os, sys


def convert_with_word(doc_path: str, docx_path: str) -> bool:
    """使用 Word COM 自动化转换 .doc → .docx"""
    try:
        import win32com.client
    except ImportError:
        print("ERROR: pywin32 not installed. Run: pip install pywin32")
        return False

    try:
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        doc = word.Documents.Open(doc_path)
        # 16 = wdFormatXMLDocument
        doc.SaveAs(docx_path, FileFormat=16)
        doc.Close()
        word.Quit()
        return True
    except Exception as e:
        print(f"ERROR: Word COM conversion failed: {e}")
        print("Make sure Microsoft Word is installed, or use --manual mode.")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_doc_to_docx.py <input.doc> [output.docx]")
        print("  [output.docx] defaults to <input>.docx")
        sys.exit(1)

    doc_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(doc_path):
        print(f"ERROR: Input file not found: {doc_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        docx_path = os.path.abspath(sys.argv[2])
    else:
        docx_path = doc_path.replace('.doc', '.docx')
        if docx_path == doc_path:
            docx_path = doc_path + '.docx'

    print(f"Converting: {doc_path}")
    print(f"       ->: {docx_path}")

    ext = os.path.splitext(doc_path)[1].lower()
    if ext == '.docx':
        import shutil
        shutil.copy2(doc_path, docx_path)
        print("Already .docx — copied as-is.")
        return

    if ext != '.doc':
        print(f"WARNING: Unrecognized extension '{ext}', attempting conversion anyway...")

    ok = convert_with_word(doc_path, docx_path)
    if ok:
        size_kb = os.path.getsize(docx_path) / 1024
        print(f"SUCCESS: {size_kb:.1f} KB")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
