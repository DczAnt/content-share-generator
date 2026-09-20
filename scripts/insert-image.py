#!/usr/bin/env python3
"""
insert-image.py — 公众号长文配图插入脚本

把技术长文里的 📷 配图标记替换为 Markdown 图片语法，产出可直接粘贴公众号的成品。

标记格式（由 tech-article.md 模板生成）：
    > 📷 **封面图**：`images/gzh/wx-cover.png`（900×383，公众号首图）

替换后：
    ![封面图](images/gzh/wx-cover.png)

三种用法：
  1. 自动模式：标记里已有路径，直接转换
       python insert-image.py article.md -o out.md
  2. 套系模式：换公众号配图套系（A/B/C/D/E），自动把 gzh/ → gzh-X/
       python insert-image.py article.md --style-set D -o out.md
  3. 自定义模式：显式给图片路径，按标记出现顺序映射
       python insert-image.py article.md --images a.png b.png c.png d.png -o out.md

可选：
  --auto-style 根据文章标题/内容关键词自动选择套系（D硬核/E数据/C方法论/B深度/A通用）
  --verify     检查图片文件是否存在，缺失则警告
  --in-place   原地改写输入文件
  --width N    给图片加 HTML 宽度属性（公众号排版用），如 --width 100 表示 width="100%"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER_RE = re.compile(
    r"^>\s*📷\s*\*\*(?P<label>[^*]+)\*\*\s*[：:]\s*"
    r"`(?P<path>[^`]+)`"
    r"(?:\s*[（(](?P<desc>[^）)]+)[）)])?\s*$"
)

STYLE_SET_DIR = {
    "A": "gzh",
    "B": "gzh-B",
    "C": "gzh-C",
    "D": "gzh-D",
    "E": "gzh-E",
}

WX_FILE_NAMES = [
    "wx-cover.png",
    "wx-decision-tree.png",
    "wx-data-table.png",
    "wx-cta.png",
]

AUTO_STYLE_KEYWORDS: dict[str, list[str]] = {
    "D": ["硬核", "终端", "底层", "内核", "驱动", "编译", "交叉编译", "glibc", "abi",
          "npu", "gpu", "drm", "egl", "内存", "链接", "固件", "嵌入式", "工具链",
          "sysroot", "二进制", "elf", "汇编", "寄存器", "中断", "调度"],
    "E": ["数据", "报告", "优化", "性能", "基准", "fps", "延迟", "吞吐", "对比",
          "实测", "量化", "benchmark", "压测", "监控", "指标", "提升", "倍速"],
    "C": ["方法论", "设计模式", "架构", "原则", "最佳实践", "如何", "为什么",
          "思考", "简洁", "哲学", "范式", "心智模型", "认知"],
    "B": ["怀旧", "历史", "演进", "踩坑实录", "排查实录", "复盘", "踩坑",
          "填坑", "血泪", "教训", "走过的"],
}


def auto_style_set(text: str) -> str:
    """根据文章标题+前几段内容关键词自动选择配图套系，返回 A/B/C/D/E"""
    lines = text.splitlines()
    title = ""
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            title = line[2:]
            break

    sample = title + " " + " ".join(
        line.strip() for line in lines[:30] if line.strip() and not line.startswith(">")
    )
    sample_lower = sample.lower()

    scores: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for style, keywords in AUTO_STYLE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in sample_lower:
                scores[style] += 1

    best = max(scores, key=lambda s: scores[s])
    if scores[best] == 0:
        return "A"
    return best


def parse_markers(lines: list[str]) -> list[tuple[int, str, str, str | None]]:
    """返回 [(line_idx, label, path, desc), ...]"""
    results = []
    for i, line in enumerate(lines):
        m = MARKER_RE.match(line)
        if m:
            results.append((i, m["label"], m["path"], m["desc"]))
    return results


def apply_style_set(path: str, style_set: str) -> str:
    """把路径里的 gzh/ 或 gzh-X/ 替换为目标套系目录"""
    target = STYLE_SET_DIR.get(style_set.upper())
    if not target:
        return path
    for d in STYLE_SET_DIR.values():
        if f"/{d}/" in path or f"\\{d}\\" in path:
            return path.replace(f"/{d}/", f"/{target}/").replace(f"\\{d}\\", f"\\{target}\\")
    return path


def build_image_line(label: str, path: str, desc: str | None, width: str | None) -> str:
    """构造 Markdown 图片行"""
    alt = label
    if width:
        return f'<img src="{path}" alt="{alt}" width="{width}%" />'
    md = f"![{alt}]({path})"
    if desc:
        md += f"\n\n*{desc}*"
    return md


def verify_image(path: str, base: Path) -> bool:
    """检查图片文件是否存在（相对路径基于 base 解析）"""
    p = Path(path)
    if not p.is_absolute():
        p = base / p
    return p.exists()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="把长文里的 📷 标记替换为 Markdown 图片语法",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("article", type=Path, help="输入 Markdown 文件")
    ap.add_argument("--style-set", choices=["A", "B", "C", "D", "E", "a", "b", "c", "d", "e"],
                    help="公众号配图套系，自动把路径里的 gzh/ → gzh-X/")
    ap.add_argument("--auto-style", action="store_true",
                    help="根据文章标题/内容关键词自动选择套系（D硬核/E数据/C方法论/B深度/A通用）")
    ap.add_argument("--images", nargs="+", metavar="PATH",
                    help="自定义图片路径，按标记出现顺序映射")
    ap.add_argument("--output", "-o", type=Path, help="输出文件（默认 stdout）")
    ap.add_argument("--in-place", action="store_true", help="原地改写输入文件")
    ap.add_argument("--verify", action="store_true", help="检查图片文件是否存在")
    ap.add_argument("--width", type=str, default=None,
                    help='HTML 宽度属性百分比，如 100 表示 width="100%%"')
    args = ap.parse_args(argv)

    if args.in_place and args.output:
        ap.error("--in-place 和 --output 互斥")

    if args.auto_style and args.style_set:
        ap.error("--auto-style 和 --style-set 互斥")

    if not args.article.exists():
        print(f"错误：输入文件不存在：{args.article}", file=sys.stderr)
        return 1

    article_text = args.article.read_text(encoding="utf-8")
    lines = article_text.splitlines(keepends=False)
    markers = parse_markers(lines)

    if not markers:
        print("警告：未找到任何 📷 配图标记", file=sys.stderr)

    if args.images and len(args.images) < len(markers):
        print(f"警告：给了 {len(args.images)} 张图，但文中有 {len(markers)} 个标记，"
              f"不足的保留原标记", file=sys.stderr)

    style_set = args.style_set
    if args.auto_style:
        style_set = auto_style_set(article_text)
        print(f"自动选择套系：{style_set}", file=sys.stderr)

    base_dir = args.article.parent
    width = args.width

    for idx, (line_i, label, path, desc) in enumerate(markers):
        new_path = path

        if args.images and idx < len(args.images):
            new_path = args.images[idx]
        elif style_set:
            new_path = apply_style_set(path, style_set)

        if args.verify:
            if verify_image(new_path, base_dir):
                print(f"  ✓ {label}: {new_path}", file=sys.stderr)
            else:
                print(f"  ✗ {label}: {new_path} （文件不存在）", file=sys.stderr)

        lines[line_i] = build_image_line(label, new_path, desc, width)

    result = "\n".join(lines) + "\n"

    if args.in_place:
        args.article.write_text(result, encoding="utf-8")
        print(f"已原地改写：{args.article}（替换 {len(markers)} 个标记）", file=sys.stderr)
    elif args.output:
        args.output.write_text(result, encoding="utf-8")
        print(f"已输出：{args.output}（替换 {len(markers)} 个标记）", file=sys.stderr)
    else:
        sys.stdout.write(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())