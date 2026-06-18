#!/usr/bin/env python3
"""将解包后的目录重新打包为 .docx 文件。"""
import zipfile, os, sys

def pack_docx(unpacked_dir, output_file, original=None):
    if os.path.exists(output_file):
        os.remove(output_file)

    existing = set()
    for root, dirs, files in os.walk(unpacked_dir):
        for fname in files:
            existing.add(os.path.relpath(os.path.join(root, fname), unpacked_dir).replace('\\', '/'))

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(unpacked_dir):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, unpacked_dir).replace('\\', '/')
                zout.write(full, arc)

        if original and os.path.exists(original):
            with zipfile.ZipFile(original, 'r') as oz:
                for name in oz.namelist():
                    if name not in existing:
                        zout.writestr(name, oz.read(name))

    size = os.path.getsize(output_file)
    print(f"Packed: {output_file} ({size:,} bytes)")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python pack_docx.py <unpacked_dir/> <output.docx> [--original <input.docx>]")
        sys.exit(1)
    original = None
    if '--original' in sys.argv:
        idx = sys.argv.index('--original')
        original = sys.argv[idx + 1]
    pack_docx(sys.argv[1], sys.argv[2], original)
