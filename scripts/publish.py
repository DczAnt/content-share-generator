#!/usr/bin/env python3
"""
publish.py — 公众号长文一键发布脚本

串联完整链路：长文.md → 自动选套系 → 插入配图 → 转公众号 HTML → 打开浏览器
产出的 HTML 可直接复制粘贴到公众号编辑器发布。

用法：
  python publish.py 长文.md                    # 全自动，输出 长文-公众号.html 并打开
  python publish.py 长文.md -o out.html        # 指定输出路径
  python publish.py 长文.md --style-set D      # 手动指定套系（覆盖自动选择）
  python publish.py 长文.md --no-open          # 不自动打开浏览器
  python publish.py 长文.md --keep-temp        # 保留中间文件（配图.md）

前置条件：
  - 长文.md 里有 📷 配图标记（由 tech-article.md 模板生成）
  - 对应套系的配图 PNG 已渲染到 images/gzh-X/ 目录
  - pip install markdown premailer pygments
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
INSERT_IMAGE = SCRIPTS_DIR / "insert-image.py"
MD2WECHAT = SCRIPTS_DIR / "md2wechat.py"


def run(cmd: list[str], desc: str) -> int:
    """运行子命令，实时透传输出"""
    print(f"\n▶ {desc}", file=sys.stderr)
    print(f"  {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.stderr:
        for line in result.stderr.strip().splitlines():
            print(f"  {line}", file=sys.stderr)
    if result.returncode != 0:
        print(f"  ✗ 失败（退出码 {result.returncode}）", file=sys.stderr)
        if result.stdout:
            print(result.stdout[:500], file=sys.stderr)
    return result.returncode


def open_file(path: Path) -> None:
    """跨平台打开文件"""
    import platform
    system = platform.system()
    if system == "Windows":
        subprocess.run(["start", "", str(path)], shell=True)
    elif system == "Darwin":
        subprocess.run(["open", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="公众号长文一键发布（自动选套系 → 插图 → 转HTML → 开浏览器）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("article", type=Path, help="输入 Markdown 长文")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="输出 HTML 路径（默认 <文章名>-公众号.html）")
    ap.add_argument("--style-set", choices=["A", "B", "C", "D", "E"],
                    help="手动指定套系（覆盖自动选择）")
    ap.add_argument("--no-open", action="store_true",
                    help="不自动打开浏览器")
    ap.add_argument("--keep-temp", action="store_true",
                    help="保留中间文件（配图 .md）")
    ap.add_argument("--width", type=str, default=None,
                    help="图片 HTML 宽度百分比（传给 insert-image.py）")
    args = ap.parse_args(argv)

    if not args.article.exists():
        print(f"错误：输入文件不存在：{args.article}", file=sys.stderr)
        return 1

    if not INSERT_IMAGE.exists() or not MD2WECHAT.exists():
        print(f"错误：找不到 insert-image.py 或 md2wechat.py", file=sys.stderr)
        print(f"  期望位置：{SCRIPTS_DIR}", file=sys.stderr)
        return 1

    stem = args.article.stem
    base_dir = args.article.parent

    temp_md = base_dir / f"{stem}-配图.md"
    output_html = args.output or base_dir / f"{stem}-公众号.html"

    print(f"╔══ 公众号一键发布 ══╗", file=sys.stderr)
    print(f"║ 输入：{args.article}", file=sys.stderr)
    print(f"║ 输出：{output_html}", file=sys.stderr)
    print(f"╚════════════════════╝", file=sys.stderr)

    # Step 1: 插入配图
    cmd1 = ["python", str(INSERT_IMAGE), str(args.article), "-o", str(temp_md)]
    if args.style_set:
        cmd1 += ["--style-set", args.style_set]
    else:
        cmd1 += ["--auto-style"]
    if args.width:
        cmd1 += ["--width", args.width]

    rc = run(cmd1, "Step 1/2: 插入配图（自动选套系）")
    if rc != 0:
        return rc

    # Step 2: 转公众号 HTML
    cmd2 = ["python", str(MD2WECHAT), str(temp_md), "-o", str(output_html)]
    rc = run(cmd2, "Step 2/2: 转公众号富文本 HTML")
    if rc != 0:
        return rc

    # 清理临时文件
    if not args.keep_temp and temp_md.exists():
        temp_md.unlink()
        print(f"\n✓ 已清理临时文件：{temp_md}", file=sys.stderr)

    print(f"\n✅ 完成！输出：{output_html}", file=sys.stderr)
    print(f"   打开浏览器 → Ctrl+A 全选 → 复制 → 粘贴公众号编辑器", file=sys.stderr)

    # 打开浏览器
    if not args.no_open:
        print(f"\n▶ 打开浏览器预览...", file=sys.stderr)
        open_file(output_html)

    return 0


if __name__ == "__main__":
    sys.exit(main())