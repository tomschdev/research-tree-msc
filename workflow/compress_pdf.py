#!/usr/bin/env python3
"""Shrink scanned PDFs (e.g. handwritten notes) before they enter git.

Rewrites each PDF in place with ghostscript, downsampling images. A file is only
replaced when the result is smaller, so re-running is harmless.

Usage (from the repo root):
  python3 workflow/compress_pdf.py <file.pdf> [...]              # /ebook (~150 dpi)
  python3 workflow/compress_pdf.py --quality printer <file.pdf>  # ~300 dpi, for faint pencil
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

QUALITIES = ("screen", "ebook", "printer", "prepress")


def compress(src, quality):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / src.name
        subprocess.run(
            ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=pdfwrite",
             f"-dPDFSETTINGS=/{quality}", f"-sOutputFile={out}", str(src)],
            check=True,
        )
        before, after = src.stat().st_size, out.stat().st_size
        if after >= before:
            print(f"{src}: kept ({before / 1e6:.1f} MB; compressed was not smaller)")
            return
        shutil.move(out, src)
        print(f"{src}: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdfs", nargs="+", type=Path)
    ap.add_argument("--quality", choices=QUALITIES, default="ebook")
    args = ap.parse_args()
    if not shutil.which("gs"):
        sys.exit("ghostscript not found: brew install ghostscript")
    for pdf in args.pdfs:
        if pdf.suffix.lower() != ".pdf" or not pdf.is_file():
            sys.exit(f"not a PDF file: {pdf}")
        compress(pdf, args.quality)


if __name__ == "__main__":
    main()
