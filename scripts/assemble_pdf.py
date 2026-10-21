#!/usr/bin/env python3
"""Assemble verified handwriting page images into an A4/Letter PDF.

Requires Pillow, reportlab and pypdf. Explicit image paths retain their order;
each quoted glob is expanded in natural filename order. Repeated --append-pdf
arguments add existing PDFs after the handwritten pages.
"""

import argparse
import glob
import json
import os
import re
import sys
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def natural_key(path):
    return tuple(int(x) if x.isdigit() else x.casefold()
                 for x in re.split(r'(\d+)', str(path)))


def image_paths(patterns):
    result = []
    for token in patterns:
        if glob.has_magic(token):
            matches = sorted(glob.glob(token), key=natural_key)
            if not matches:
                raise ValueError(f'No images match: {token}')
            result.extend(Path(p).expanduser().resolve() for p in matches)
        else:
            result.append(Path(token).expanduser().resolve())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--images', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--append-pdf', action='append', default=[])
    parser.add_argument('--page-size', choices=['A4', 'Letter'], default='A4')
    parser.add_argument('--title', default='Handwritten assignment')
    parser.add_argument('--author', default='')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    try:
        paths = image_paths(args.images)
        destination = Path(args.output).expanduser().resolve()
        appendices = [Path(p).expanduser().resolve() for p in args.append_pdf]
        if destination.exists() and not args.overwrite:
            raise ValueError(f'Output exists; choose a new filename: {destination}')
        if destination in paths or destination in appendices:
            raise ValueError('Output must be different from every input file.')
        dimensions = []
        for path in paths:
            if not path.is_file():
                raise ValueError(f'Image not found: {path}')
            with Image.open(path) as img:
                dimensions.append(img.size)
        appendix_readers = [PdfReader(str(path)) for path in appendices]
        appendix_pages = sum(len(reader.pages) for reader in appendix_readers)

        buffer = BytesIO()
        page_size = A4 if args.page_size == 'A4' else LETTER
        width, height = page_size
        document = canvas.Canvas(buffer, pagesize=page_size, pageCompression=1)
        document.setTitle(args.title)
        document.setAuthor(args.author)
        document.setCreator('Codex / my-handwriting / image_gen')
        for path, (iw, ih) in zip(paths, dimensions):
            scale = min(width / iw, height / ih)
            dw, dh = iw * scale, ih * scale
            document.setFillColorRGB(1, 1, 1)
            document.rect(0, 0, width, height, stroke=0, fill=1)
            document.drawImage(ImageReader(str(path)), (width - dw) / 2,
                               (height - dh) / 2, dw, dh, mask='auto')
            document.showPage()
        document.save()
        buffer.seek(0)
        writer = PdfWriter()
        writer.append(PdfReader(buffer))
        for reader in appendix_readers:
            writer.append(reader)
        writer.add_metadata({'/Title': args.title, '/Author': args.author,
                             '/Creator': 'Codex / my-handwriting / image_gen'})

        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                    prefix=f'.{destination.stem}-', suffix='.pdf',
                    dir=destination.parent, delete=False) as output:
                temporary = Path(output.name)
                writer.write(output)
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            writer.close()
        print(json.dumps({'path': str(destination), 'handwritten_pages': len(paths),
                          'appendix_pages': appendix_pages,
                          'total_pages': len(paths) + appendix_pages},
                         ensure_ascii=False))
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
