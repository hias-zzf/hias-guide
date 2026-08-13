#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate 26 wlgd AI review charts and refresh the review page."""

from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "物理与光电工程学院" / "复试准备" / "26年复试录取情况.md"
IMG_DIR = ROOT / "overrides" / "assets" / "images"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


# (政治, 英语二, 数学二, 408, 初试总分, 复试成绩, 总成绩)，仅保留拟录取考生
D02 = [
    (58, 76, 142, 111, 387, 77.64, 77.52),
    (61, 73, 137, 110, 381, 74.36, 75.28),
    (56, 79, 136, 99, 370, 79.52, 76.76),
    (62, 67, 141, 99, 369, 93.8, 83.8),
    (57, 78, 124, 106, 365, 89.08, 81.04),
    (63, 80, 117, 102, 362, 88.1, 80.25),
    (55, 70, 134, 98, 357, 75.4, 73.4),
    (59, 75, 117, 105, 356, 79.58, 75.39),
    (56, 69, 118, 105, 348, 74.08, 71.84),
    (62, 77, 117, 91, 347, 75.74, 72.57),
    (55, 72, 122, 90, 339, 82.62, 75.21),
    (54, 70, 129, 83, 336, 74.38, 70.79),
    (48, 70, 112, 106, 336, 78.82, 73.01),
    (57, 81, 111, 84, 333, 90.72, 78.66),
    (55, 55, 113, 106, 329, 78.78, 72.29),
]

D03 = [
    (61, 79, 138, 115, 393, 81.12, 79.86),
    (59, 66, 149, 118, 392, 82.46, 80.43),
    (64, 83, 130, 106, 383, 78.52, 77.56),
    (60, 85, 131, 107, 383, 91.48, 84.04),
    (57, 78, 140, 103, 378, 84.7, 80.15),
    (56, 84, 135, 98, 373, 76.58, 75.59),
    (56, 85, 134, 98, 373, 71.74, 73.17),
    (52, 73, 133, 106, 364, 85.54, 79.17),
    (58, 74, 128, 103, 363, 89.04, 80.82),
    (58, 70, 130, 100, 358, 74.94, 73.27),
    (62, 73, 115, 106, 356, 79.54, 75.37),
    (69, 72, 101, 108, 350, 77.6, 73.8),
    (58, 67, 115, 110, 350, 79.26, 74.63),
    (64, 86, 108, 91, 349, 82.3, 76.05),
    (53, 69, 118, 108, 348, 79.76, 74.68),
    (52, 67, 129, 97, 345, 86.38, 77.69),
    (52, 73, 124, 91, 340, 86.4, 77.2),
    (55, 63, 130, 84, 332, 87.6, 77),
]

# 全部一志愿复试考生初试成绩
D02_ALL_INITIAL = [
    (58, 76, 142, 111),
    (61, 73, 137, 110),
    (56, 79, 136, 99),
    (62, 67, 141, 99),
    (57, 78, 124, 106),
    (63, 80, 117, 102),
    (55, 70, 134, 98),
    (59, 75, 117, 105),
    (54, 78, 130, 90),
    (56, 69, 118, 105),
    (62, 77, 117, 91),
    (55, 72, 122, 90),
    (54, 70, 129, 83),
    (48, 70, 112, 106),
    (57, 81, 111, 84),
    (55, 55, 113, 106),
    (56, 69, 120, 82),
    (50, 75, 96, 95),
]

D03_ALL_INITIAL = [
    (61, 79, 138, 115),
    (59, 66, 149, 118),
    (64, 83, 130, 106),
    (60, 85, 131, 107),
    (57, 78, 140, 103),
    (56, 84, 135, 98),
    (56, 85, 134, 98),
    (57, 83, 129, 103),
    (53, 80, 128, 110),
    (52, 73, 133, 106),
    (58, 74, 128, 103),
    (58, 70, 130, 100),
    (62, 73, 115, 106),
    (69, 72, 101, 108),
    (58, 67, 115, 110),
    (64, 86, 108, 91),
    (66, 78, 105, 99),
    (53, 69, 118, 108),
    (49, 70, 133, 95),
    (52, 67, 129, 97),
    (45, 69, 127, 104),
    (55, 66, 125, 99),
    (55, 77, 115, 96),
    (52, 73, 124, 91),
    (55, 63, 130, 84),
    (55, 83, 88, 105),
]


def save_curve(rows: list[tuple], filename: str, title: str) -> None:
    xs = list(range(1, len(rows) + 1))
    totals = [row[4] for row in rows]
    finals = [row[6] for row in rows]

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


def save_admission_compare() -> None:
    labels = ["02 小卫星联培", "03 智能光电"]
    review_nums = [18, 26]
    admit_nums = [15, 18]
    ratios = [round(r / a, 2) for r, a in zip(review_nums, admit_nums)]

    fig, ax1 = plt.subplots(figsize=(8, 4.6))
    x = range(len(labels))
    width = 0.35
    ax1.bar([i - width / 2 for i in x], review_nums, width, label="复试人数", color="#0f766e")
    ax1.bar([i + width / 2 for i in x], admit_nums, width, label="拟录取", color="#5eead4")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("人数")
    ax1.set_ylim(0, 30)
    ax1.set_title("02 与 03 复试 / 拟录取人数对比")
    ax1.legend(loc="upper left")

    for i, value in enumerate(review_nums):
        ax1.text(i - width / 2, value + 0.4, str(value), ha="center")
    for i, value in enumerate(admit_nums):
        ax1.text(i + width / 2, value + 0.4, str(value), ha="center")

    ax2 = ax1.twinx()
    ax2.plot(list(x), ratios, marker="o", linewidth=2, color="#d97706", label="复录比")
    ax2.set_ylabel("复录比", color="#d97706")
    ax2.tick_params(axis="y", labelcolor="#d97706")
    ax2.set_ylim(0, 2)
    for i, value in enumerate(ratios):
        ax2.text(i, value + 0.06, f"{value:.2f}", color="#d97706", ha="center")

    lines = ax1.get_lines() + ax2.get_lines()
    labels2 = [line.get_label() for line in lines]
    ax1.legend(lines, labels2, loc="upper right")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "wlgd-review-admission.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_avg_compare() -> None:
    labels = ["政治", "英语二", "数学二", "408"]
    d02_means = [round(mean(row[i] for row in D02), 2) for i in range(4)]
    d03_means = [round(mean(row[i] for row in D03), 2) for i in range(4)]
    d02_total = round(mean(row[4] for row in D02), 2)
    d03_total = round(mean(row[4] for row in D03), 2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    x = range(len(labels))
    width = 0.35
    ax1.bar([i - width / 2 for i in x], d02_means, width, label="02", color="#0f766e")
    ax1.bar([i + width / 2 for i in x], d03_means, width, label="03", color="#d97706")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("平均分")
    ax1.set_title("02 与 03 四科均分对比")
    ax1.legend()

    ax2.bar(["02", "03"], [d02_total, d03_total], color=["#0f766e", "#d97706"], width=0.45)
    ax2.set_ylabel("初试总分均分")
    ax2.set_title("02 与 03 初试总分均分")
    for idx, value in enumerate([d02_total, d03_total]):
        ax2.text(idx, value + 1, str(value), ha="center", fontsize=10)

    fig.tight_layout()
    fig.savefig(IMG_DIR / "wlgd-review-avg-compare.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fmt_mean(values: list[float]) -> str:
    return " · ".join(f"{v:.2f}" for v in values)


def render_stats(rows: list[tuple], all_initial: list[tuple], num: str, name: str) -> str:
    initial_all = [sum(row) for row in all_initial]
    initial_admitted = [row[4] for row in rows]
    retest = [row[5] for row in rows]
    final = [row[6] for row in rows]
    all_subjects = [mean(row[i] for row in all_initial) for i in range(4)]
    admitted_subjects = [mean(row[i] for row in rows) for i in range(4)]
    ratio = round(len(all_initial) / len(rows), 2)

    lines = [
        f"## （{num}）{name}复试统计",
        "",
        f"- 复试人数：{len(all_initial)}",
        f"- 拟录取：{len(rows)}",
        f"- 复录比：{ratio:.2f}",
        f"- 初试均分：{fmt_mean(all_subjects + [mean(initial_all)])}",
        f"- 录取均分：{fmt_mean(admitted_subjects + [mean(initial_admitted)])}",
        f"- 复试均分：{mean(retest):.2f}",
        f"- 总成绩均分：{mean(final):.2f}",
        "",
        "| 阶段 | 政治 | 英语二 | 数学二 | 408 | 总分 |",
        "| --- | --- | --- | --- | --- | --- |",
        f"| 初试均分（全部复试） | {' | '.join(f'{v:.2f}' for v in all_subjects)} | {mean(initial_all):.2f} |",
        f"| 录取均分（拟录取） | {' | '.join(f'{v:.2f}' for v in admitted_subjects)} | {mean(initial_admitted):.2f} |",
        "",
    ]
    return "\n".join(lines)


def render_rows(rows: list[tuple]) -> str:
    lines = [
        "| 政治 | 英语二 | 数学二 | 408 | 总分 | 复试成绩 | 总成绩 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    save_curve(D02, "wlgd-review-02-curve.png", "02 方向拟录取考生初试总分与总成绩曲线")
    save_curve(D03, "wlgd-review-03-curve.png", "03 方向拟录取考生初试总分与总成绩曲线")
    save_admission_compare()
    save_avg_compare()

    content = "\n".join(
        [
            "# 26 年复试录取情况",
            "",
            "> 数据依据《2026 年国科大杭高院物光学院人工智能（02/03 方向）专业型硕士考生拟录取名单（一志愿）》整理，仅保留拟录取考生，以官方公示为准。",
            "",
            "## 数据分析",
            "",
            "![02 与 03 复试/拟录取人数对比](../../assets/images/wlgd-review-admission.png)",
            "",
            "![02 成绩曲线](../../assets/images/wlgd-review-02-curve.png)",
            "",
            "![03 成绩曲线](../../assets/images/wlgd-review-03-curve.png)",
            "",
            "![02 与 03 均分对比](../../assets/images/wlgd-review-avg-compare.png)",
            "",
            render_stats(D02, D02_ALL_INITIAL, "02", "小卫星联培方向"),
            "## （02）拟录取名单",
            "",
            render_rows(D02),
            "",
            render_stats(D03, D03_ALL_INITIAL, "03", "智能光电方向"),
            "## （03）拟录取名单",
            "",
            render_rows(D03),
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content, encoding="utf-8")
    print(
        f"已生成 {OUT.name}：02 方向拟录取 {len(D02)} 人，03 方向拟录取 {len(D03)} 人，图表已输出。"
    )


if __name__ == "__main__":
    main()
