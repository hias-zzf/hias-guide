#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert experience-post PDFs (and docx) into Markdown.

Usage:
    python convert_experiences.py [input_dir] [output_dir]

Defaults:
    input_dir  = D:\\codex program\\pdf
    output_dir = D:\\codex program\\hias\\上岸经验分享
"""

import os
import re
import sys
from pathlib import Path

import pdfplumber
import pymupdf
import numpy as np
from docx import Document
from rapidocr_onnxruntime import RapidOCR


DEFAULT_INPUT = Path(r"D:\codex program\pdf")
DEFAULT_OUTPUT = Path(r"D:\codex program\hias\上岸经验分享")

_HEADING_WORDS = (
    "背景",
    "个人",
    "情况",
    "备考",
    "择校",
    "复试",
    "写在前面",
    "前言",
    "结语",
    "碎碎念",
    "建议",
    "资料",
    "时间",
    "经验",
    "其他",
    "心态",
    "焦虑",
    "圣杭高",
    "英语",
    "政治",
    "数学",
    "408",
    "考研",
)


def is_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) > 26:
        return False
    if re.fullmatch(r"\d{1,4}", line):
        return False
    if len(line) > 8 and re.search(r"[，。；、！？]", line):
        return False
    if re.match(r"^\d+\s+\S", line):
        return True
    if line.endswith(("：", ":")):
        return True
    if re.search(r"[：:]\s*\S", line):
        return False
    if line.endswith(("。", "！", "？", "，", ",", ";", "；")):
        return False
    return any(line.startswith(word) for word in _HEADING_WORDS)


def clean_line(line: str) -> str:
    line = re.sub(r"\(cid:\d+\)", "", line)
    line = re.sub(r"(?<=[\u4e00-\u9fff])’(?=\s*[\u4e00-\u9fff\d])", "，", line)
    line = re.sub(r"(?<=[\u4e00-\u9fff\s])A(?=[\u4e00-\u9fff\s。]|$)", "？", line)
    line = re.sub(r"(?<=[\u4e00-\u9fff\d])J(?=[\u4e00-\u9fff])", "、", line)
    line = re.sub(r"(?<=[\u4e00-\u9fff\d])P(?=[\u4e00-\u9fff\s､…｡]|$)", "，", line)
    line = line.replace("¥", "。")
    return line.strip()


def pdf_text_to_markdown(pages: list[str]) -> str:
    md: list[str] = []
    for page_text in pages:
        for raw in page_text.splitlines():
            line = clean_line(raw)
            if not line:
                continue
            if re.fullmatch(r"\d{1,4}", line):
                continue
            if is_heading(line):
                md.append("\n## " + line + "\n")
            elif line.startswith(("•", "▪", "- ")):
                md.append("- " + line.lstrip("•▪- ").strip())
            else:
                md.append(line)
    return "\n".join(md).strip() + "\n"


def ocr_pdf_to_markdown(path: Path, engine: RapidOCR, dpi: int = 150) -> str:
    doc = pymupdf.open(path)
    md: list[str] = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if img.shape[2] == 4:
            img = img[:, :, :3]
        result, _ = engine(img)
        if not result:
            continue
        boxes = []
        for box, text, _score in result:
            ys = [point[1] for point in box]
            xs = [point[0] for point in box]
            boxes.append((min(ys), min(xs), str(text)))
        boxes.sort(key=lambda item: (item[0], item[1]))
        for _y, _x, text in boxes:
            line = clean_line(text)
            if not line:
                continue
            if is_heading(line):
                md.append("\n## " + line + "\n")
            elif line.startswith(("•", "▪", "- ")):
                md.append("- " + line.lstrip("•▪- ").strip())
            else:
                md.append(line)
    doc.close()
    return "\n".join(md).strip() + "\n"


def docx_to_markdown(path: Path) -> str:
    doc = Document(path)
    md: list[str] = []
    for para in doc.paragraphs:
        text = clean_line(para.text)
        if not text:
            continue
        style = (para.style.name or "").lower()
        if "heading" in style:
            md.append("\n## " + text + "\n")
        else:
            md.append(text)
    return "\n".join(md).strip() + "\n"


def convert_all(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(input_dir.iterdir())
    ocr_engine = None
    for file in files:
        if file.suffix.lower() not in {".pdf", ".docx"}:
            continue
        target = output_dir / (file.stem + ".md")
        print(f"转换: {file.name}")
        if file.suffix.lower() == ".docx":
            content = docx_to_markdown(file)
        else:
            with pdfplumber.open(file) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            total_chars = sum(len(page.strip()) for page in pages)
            if total_chars > 300:
                content = pdf_text_to_markdown(pages)
            else:
                if ocr_engine is None:
                    print("扫描版 PDF 使用 OCR 识别...")
                    ocr_engine = RapidOCR()
                content = ocr_pdf_to_markdown(file, ocr_engine)
        target.write_text(content, encoding="utf-8")
        print(f"  完成 -> {target.name} ({len(content)} 字符)")


if __name__ == "__main__":
    input_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    convert_all(input_dir, output_dir)
