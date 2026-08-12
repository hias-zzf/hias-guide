#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Export 26 AI/CS review statistics into Markdown plus score-curve charts."""

from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pdfplumber


ROOT = Path(__file__).resolve().parent
SRC = Path(r"D:\codex program\pdf\复试生源统计")
OUT = ROOT / "智能学院" / "复试准备" / "26年复试录取情况.md"
IMG_DIR = ROOT / "overrides" / "assets" / "images"

AI_FILE = "HIAS_26_AI复试统计.pdf"
CS_FILE = "HIAS_26_CS复试统计.pdf"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def clean(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    return "" if value in {"\\", "-"} else value


def load_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                for row in table:
                    if not row:
                        continue
                    if row[0] and str(row[0]).strip() == "姓名":
                        continue
                    rows.append([clean(cell) for cell in row])
    return rows


def load_stats(path: Path) -> dict[str, list[str]]:
    stats: dict[str, list[str]] = {}
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").splitlines():
                line = line.strip()
                for key in ("初试均分", "复试均分", "录取均分", "复录比"):
                    if line.startswith(key):
                        stats[key] = [part for part in line.split() if part != key]
    return stats


def admitted_rows(rows: list[list[str]]) -> list[list[str]]:
    return [row for row in rows if row[-1] == "拟录取"]


def render_rows(rows: list[list[str]]) -> str:
    lines = [
        "| 政治 | 英语二 | 数学二 | 408 | 总分 | 复试成绩 | 总成绩 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        cells = [cell or "\\" for cell in row[1:8]]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_stats(stats: dict[str, list[str]], label: str) -> str:
    lines = [f"- {label}：{stats[label][-1]}"]
    if "初试均分" in stats:
        lines.append("- 初试均分：" + " · ".join(stats["初试均分"]))
    for key in ("复试均分", "录取均分"):
        if key in stats:
            lines.append(f"- {key}：" + " · ".join(stats[key]))
    return "\n".join(lines)


def save_curve(rows: list[list[str]], filename: str, title: str) -> None:
    xs = list(range(1, len(rows) + 1))
    totals = [float(row[5]) for row in rows]
    finals = [float(row[7]) for row in rows]

    fig, ax1 = plt.subplots(figsize=(10, 4.6))
    ax1.plot(xs, totals, marker="o", linewidth=2, color="#0f766e", label="初试总分")
    ax1.set_xlabel("拟录取序号")
    ax1.set_ylabel("初试总分", color="#0f766e")
    ax1.tick_params(axis="y", labelcolor="#0f766e")
    ax1.set_ylim(min(totals) - 15, max(totals) + 15)

    ax2 = ax1.twinx()
    ax2.plot(xs, finals, marker="s", linewidth=2, color="#d97706", label="总成绩")
    ax2.set_ylabel("总成绩", color="#d97706")
    ax2.tick_params(axis="y", labelcolor="#d97706")
    ax2.set_ylim(min(finals) - 5, max(finals) + 5)

    ax1.set_title(title)
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="lower right")
    fig.tight_layout()
    fig.savefig(IMG_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_avg_compare(ai_rows: list[list[str]], cs_rows: list[list[str]]) -> None:
    labels = ["政治", "英语二", "数学二", "408"]
    ai_means = [round(mean(float(row[i + 1]) for row in ai_rows), 2) for i in range(4)]
    cs_means = [round(mean(float(row[i + 1]) for row in cs_rows), 2) for i in range(4)]
    ai_total = round(mean(float(row[5]) for row in ai_rows), 2)
    cs_total = round(mean(float(row[5]) for row in cs_rows), 2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    x = range(len(labels))
    width = 0.35
    ax1.bar([i - width / 2 for i in x], ai_means, width, label="AI", color="#0f766e")
    ax1.bar([i + width / 2 for i in x], cs_means, width, label="CS", color="#d97706")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("平均分")
    ax1.set_title("AI 与 CS 四科均分对比")
    ax1.legend()

    ax2.bar(["AI", "CS"], [ai_total, cs_total], color=["#0f766e", "#d97706"], width=0.45)
    ax2.set_ylabel("初试总分均分")
    ax2.set_title("AI 与 CS 初试总分均分")
    for idx, value in enumerate([ai_total, cs_total]):
        ax2.text(idx, value + 1, str(value), ha="center", fontsize=10)

    fig.tight_layout()
    fig.savefig(IMG_DIR / "review-avg-compare.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    all_ai = load_rows(SRC / AI_FILE)
    all_cs = load_rows(SRC / CS_FILE)
    ai_rows = admitted_rows(all_ai)
    cs_rows = admitted_rows(all_cs)
    ai_stats = load_stats(SRC / AI_FILE)
    cs_stats = load_stats(SRC / CS_FILE)

    save_curve(ai_rows, "review-ai-curve.png", "AI 拟录取考生初试总分与总成绩曲线")
    save_curve(cs_rows, "review-cs-curve.png", "CS 拟录取考生初试总分与总成绩曲线")
    save_avg_compare(ai_rows, cs_rows)

    content = "\n".join(
        [
            "# 26 年复试录取情况",
            "",
            "> 数据依据《HIAS_26_AI复试统计》《HIAS_26_CS复试统计》整理，仅保留拟录取考生，以官方公示为准。",
            "",
            "![复试生源统计](../../assets/images/review-source-2026.png)",
            "",
            "## 数据曲线",
            "",
            "![AI 成绩曲线](../../assets/images/review-ai-curve.png)",
            "",
            "![CS 成绩曲线](../../assets/images/review-cs-curve.png)",
            "",
            "![AI 与 CS 均分对比](../../assets/images/review-avg-compare.png)",
            "",
            "## AI 专业复试统计",
            "",
            f"- 复试人数：{len(all_ai)}",
            f"- 拟录取：{len(ai_rows)}",
            "",
            render_stats(ai_stats, "复录比"),
            "",
            "| 阶段 | 政治 | 英语二 | 数学二 | 408 | 总分 |",
            "| --- | --- | --- | --- | --- | --- |",
            f"| 初试均分 | {' | '.join(ai_stats.get('初试均分', ['-'] * 5))} |",
            f"| 复试均分 | {' | '.join(ai_stats.get('复试均分', ['-'] * 5))} |",
            "",
            "## AI 拟录取名单",
            "",
            render_rows(ai_rows),
            "",
            "## CS 专业复试统计",
            "",
            f"- 复试人数：{len(all_cs)}",
            f"- 拟录取：{len(cs_rows)}",
            "",
            render_stats(cs_stats, "复录比"),
            "",
            "| 阶段 | 政治 | 英语二 | 数学二 | 408 | 总分 |",
            "| --- | --- | --- | --- | --- | --- |",
            f"| 初试均分 | {' | '.join(cs_stats.get('初试均分', ['-'] * 5))} |",
            f"| 录取均分 | {' | '.join(cs_stats.get('录取均分', ['-'] * 5))} |",
            "",
            "## CS 拟录取名单",
            "",
            render_rows(cs_rows),
            "",
        ]
    )

    OUT.write_text(content, encoding="utf-8")
    print(
        f"已生成 {OUT.name}：AI 拟录取 {len(ai_rows)} 人，CS 拟录取 {len(cs_rows)} 人，图表已输出。"
    )


if __name__ == "__main__":
    main()
