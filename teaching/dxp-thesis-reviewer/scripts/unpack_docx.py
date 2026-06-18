#!/usr/bin/env python3
"""解包 .docx 文件到指定目录。"""
import zipfile, os, sys, shutil

def unpack_docx(docx_path, output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    with zipfile.ZipFile(docx_path, 'r') as z:
        z.extractall(output_dir)
    file_count = sum(1 for _ in os.walk(output_dir) for __ in _[2])
    print(f"Unpacked {file_count} files to: {output_dir}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python unpack_docx.py <input.docx> <output_dir/>")
        sys.exit(1)
    unpack_docx(sys.argv[1], sys.argv[2])
