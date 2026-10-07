#!/usr/bin/env python3
"""Extract a PDF paper into a page-marked text dump, for reading notes.

Usage:
    python extract_pdf.py <paper.pdf> [<out.txt>]

Default output: <paper 所在目录>/<paper 主文件名>.extracted.txt

Design notes (all verified on this box, 2026-10-07):
  * PyMuPDF (fitz) is the primary engine -- it keeps the spaces between words.
    markitdown and pdfplumber are pdfminer-based and silently glue words together
    on PDFs whose fonts lack space glyphs ("Providedproperattribution..."), which
    makes every quoted sentence unusable.
  * Every page gets a `===== PAGE n =====` marker so notes can anchor to a page.
  * Section numbers often sit on their own line above the title (the layout has
    two text blocks); that is normal, do not "fix" it.
  * If the dump looks empty or space-stripped, the script says so on stdout.
"""

import re
import sys
from pathlib import Path

PAGE_MARK = "\n\n===== PAGE {} =====\n"


def _reconfigure_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def extract_with_fitz(pdf):
    import fitz  # PyMuPDF

    doc = fitz.open(str(pdf))
    if doc.needs_pass:
        raise RuntimeError("PDF 已加密，需要密码才能抽文本")
    return [page.get_text("text") for page in doc]


def extract_with_pypdf(pdf):
    import pypdf

    reader = pypdf.PdfReader(str(pdf))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise RuntimeError("PDF 已加密，需要密码才能抽文本")
    return [(page.extract_text() or "") for page in reader.pages]


def extract(pdf):
    for name, fn in (("fitz", extract_with_fitz), ("pypdf", extract_with_pypdf)):
        try:
            pages = fn(pdf)
        except ImportError:
            continue
        except RuntimeError:
            raise
        except Exception as exc:  # engine-specific failure -> try the next one
            print(f"[warn] {name} 抽取失败：{exc}", file=sys.stderr)
            continue
        if pages:
            return name, pages
    raise SystemExit(
        "没有可用的 PDF 抽取引擎。这个脚本要跑在装了 PyMuPDF 或 pypdf 的解释器上；\n"
        "本机托管解释器只有 openpyxl，请改用 D:\\dev\\Python\\Python312\\python.exe。"
    )


def health_report(pages):
    """Return (warnings, stats) for the extracted pages."""
    text = "\n".join(pages)
    chars = len(text)
    per_page = chars / max(len(pages), 1)
    warnings = []

    if per_page < 200:
        warnings.append(
            f"每页平均只有 {per_page:.0f} 个字符 —— 疑似扫描件 / 图片型 PDF（没有文本层）。"
            "走 OCR（pdf / pdfkit-py 技能），或向用户索取带文本层的版本；不要靠猜补内容。"
        )

    # Space-stripping detector: pdfminer-style engines glue words into long runs.
    tokens = [t for t in re.split(r"\s+", text) if re.fullmatch(r"[A-Za-z]{25,}", t)]
    all_tokens = [t for t in re.split(r"\s+", text) if t]
    ratio = len(tokens) / max(len(all_tokens), 1)
    if ratio > 0.01:
        warnings.append(
            f"{ratio:.1%} 的词是 25 个字母以上的连写串 —— 空格丢失（pdfminer 系抽取器的典型症状）。"
            "换 PyMuPDF 重抽；引用的句子在这种 dump 里不可信。"
        )

    caps = re.findall(r"^(?:Figure|Table)\s+\d+", text, re.M)
    return warnings, {
        "pages": len(pages),
        "chars": chars,
        "per_page": per_page,
        "captions": len(caps),
    }


def main(argv):
    _reconfigure_stdout()
    if len(argv) < 2:
        raise SystemExit(__doc__)
    pdf = Path(argv[1]).expanduser().resolve()
    if not pdf.is_file():
        raise SystemExit(f"找不到文件：{pdf}")
    out = Path(argv[2]).expanduser().resolve() if len(argv) > 2 \
        else pdf.with_suffix(".extracted.txt")

    engine, pages = extract(pdf)
    body = "".join(PAGE_MARK.format(i + 1) + p for i, p in enumerate(pages))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")

    warnings, stats = health_report(pages)
    print(f"engine   : {engine}")
    print(f"pages    : {stats['pages']}")
    print(f"chars    : {stats['chars']}  ({stats['per_page']:.0f}/page)")
    print(f"captions : {stats['captions']} 个 Figure/Table 编号")
    print(f"dump     : {out}")
    if warnings:
        print("\n[!] 需要处理：")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("health   : OK")


if __name__ == "__main__":
    main(sys.argv)
