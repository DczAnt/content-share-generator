#!/usr/bin/env python3
"""
md2wechat.py — Markdown 转公众号富文本 HTML

把技术长文 Markdown 一键转为公众号编辑器可直接粘贴的富文本 HTML。
所有 CSS 内联化（公众号不支持 class/外部样式表），代码块带语法高亮。

用法：
  python md2wechat.py 长文.md -o 长文.html
  python md2wechat.py 长文.md --theme tech --title "自定义标题" -o 长文.html
  python md2wechat.py 长文.md --fragment -o 片段.html
  python md2wechat.py 长文.md --in-place  # 输出 长文.html

链路：
  insert-image.py 产出配图长文.md → md2wechat.py → 长文.html → 粘贴公众号编辑器
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown
import premailer

THEME_TECH = """
article {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: #333333;
  max-width: 100%;
  margin: 0 auto;
  padding: 20px;
}
article h1 {
  font-size: 22px;
  font-weight: bold;
  color: #1a1a1a;
  border-bottom: 2px solid #1a1a1a;
  padding-bottom: 10px;
  margin: 25px 0 20px 0;
}
article h2 {
  font-size: 18px;
  font-weight: bold;
  color: #1a1a1a;
  border-left: 4px solid #2c7be5;
  padding-left: 10px;
  margin: 30px 0 15px 0;
}
article h3 {
  font-size: 16px;
  font-weight: bold;
  color: #1a1a1a;
  margin: 20px 0 10px 0;
}
article p {
  margin: 15px 0;
  word-wrap: break-word;
}
article a {
  color: #2c7be5;
  text-decoration: none;
  border-bottom: 1px solid #2c7be5;
}
article strong {
  font-weight: bold;
  color: #1a1a1a;
}
article em {
  font-style: italic;
}
article blockquote {
  border-left: 4px solid #2c7be5;
  background-color: #f8f9fa;
  padding: 10px 15px;
  margin: 15px 0;
  color: #555555;
}
article blockquote p {
  margin: 5px 0;
}
article ul, article ol {
  padding-left: 25px;
  margin: 15px 0;
}
article li {
  margin: 8px 0;
}
article code {
  font-family: "Cascadia Code", Consolas, "Courier New", monospace;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 14px;
  color: #c7254e;
}
article pre {
  background-color: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 15px 0;
}
article pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  color: #e0e0e0;
  font-size: 14px;
}
article table {
  border-collapse: collapse;
  width: 100%;
  margin: 15px 0;
  font-size: 15px;
}
article th {
  border: 1px solid #dddddd;
  background-color: #f5f5f5;
  font-weight: bold;
  padding: 8px 12px;
  text-align: left;
}
article td {
  border: 1px solid #dddddd;
  padding: 8px 12px;
}
article tr:nth-child(even) td {
  background-color: #fafafa;
}
article img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 15px auto;
}
article hr {
  border: none;
  border-top: 1px solid #dddddd;
  margin: 25px 0;
}
"""

PYGMENTS_MONOKAI_CSS = """
.codehilite .c { color: #75715e; }
.codehilite .k { color: #f92672; }
.codehilite .o { color: #f92672; }
.codehilite .n { color: #f8f8f2; }
.codehilite .p { color: #f8f8f2; }
.codehilite .s { color: #e6db74; }
.codehilite .s1 { color: #e6db74; }
.codehilite .s2 { color: #e6db74; }
.codehilite .mi { color: #ae81ff; }
.codehilite .mf { color: #ae81ff; }
.codehilite .mh { color: #ae81ff; }
.codehilite .mo { color: #ae81ff; }
.codehilite .nb { color: #f8f8f2; }
.codehilite .nf { color: #a6e22e; }
.codehilite .nc { color: #a6e22e; }
.codehilite .nn { color: #a6e22e; }
.codehilite .nt { color: #f92672; }
.codehilite .nv { color: #f8f8f2; }
.codehilite .vc { color: #f8f8f2; }
.codehilite .vg { color: #f8f8f2; }
.codehilite .vi { color: #f8f8f2; }
.codehilite .kd { color: #f92672; }
.codehilite .kn { color: #f92672; }
.codehilite .kp { color: #f92672; }
.codehilite .kr { color: #f92672; }
.codehilite .kt { color: #f92672; }
.codehilite .m { color: #ae81ff; }
.codehilite .l { color: #ae81ff; }
.codehilite .ge { font-style: italic; }
.codehilite .gs { font-weight: bold; }
.codehilite .ld { color: #e6db74; }
.codehilite .se { color: #ae81ff; }
.codehilite .sb { color: #e6db74; }
.codehilite .sh { color: #e6db74; }
.codehilite .sx { color: #e6db74; }
.codehilite .sr { color: #e6db74; }
.codehilite .sd { color: #e6db74; }
.codehilite .si { color: #e6db74; }
.codehilite .sc { color: #e6db74; }
.codehilite .sa { color: #e6db74; }
.codehilite .ow { color: #f92672; }
.codehilite .bp { color: #f8f8f2; }
.codehilite .fm { color: #a6e22e; }
.codehilite .dl { color: #e6db74; }
.codehilite .il { color: #ae81ff; }
.codehilite .na { color: #a6e22e; }
.codehilite .no { color: #66d9ef; }
.codehilite .nd { color: #a6e22e; }
.codehilite .ne { color: #a6e22e; }
.codehilite .nl { color: #f8f8f2; }
.codehilite .py { color: #f8f8f2; }
.codehilite .cp { color: #75715e; }
.codehilite .c1 { color: #75715e; }
.codehilite .cm { color: #75715e; }
.codehilite .cs { color: #75715e; }
.codehilite .ch { color: #75715e; }
.codehilite .cpf { color: #75715e; }
.codehilite .gu { color: #75715e; font-weight: bold; }
.codehilite .gd { color: #f92672; }
.codehilite .gi { color: #a6e22e; }
.codehilite .gr { color: #f92672; }
.codehilite .gh { color: #f8f8f2; font-weight: bold; }
.codehilite .gp { color: #f92672; }
.codehilite .go { color: #f8f8f2; }
.codehilite .gt { color: #f92672; }
.codehilite .err { color: #960050; background-color: #1e0010; }
"""

CLASS_CLEAN_RE = re.compile(r'\s*class="[^"]*"')
ID_CLEAN_RE = re.compile(r'\s*id="[^"]*"')


def extract_title(md_text: str) -> str | None:
    """从 Markdown 首行 # 提取标题"""
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def clean_attrs(html: str) -> str:
    """清理残留 class/id 属性（公众号不需要）"""
    html = CLASS_CLEAN_RE.sub("", html)
    html = ID_CLEAN_RE.sub("", html)
    return html


def convert(
    md_text: str,
    theme: str = "tech",
    title: str | None = None,
    no_highlight: bool = False,
    fragment: bool = False,
) -> str:
    """Markdown → 公众号兼容 HTML"""

    extensions = ["fenced_code", "tables", "nl2br"]
    extension_configs = {}

    if not no_highlight:
        extensions.append("codehilite")
        extension_configs["codehilite"] = {
            "guess_lang": True,
            "css_class": "codehilite",
            "noclasses": False,
        }

    html_body = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs=extension_configs,
    )

    if title is None:
        title = extract_title(md_text) or "技术文章"

    css = THEME_TECH
    if not no_highlight:
        css += PYGMENTS_MONOKAI_CSS

    if fragment:
        full_html = f'<style>{css}</style>\n<article>\n{html_body}\n</article>'
    else:
        full_html = (
            f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
            f'<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{title}</title>\n<style>{css}</style>\n</head>\n<body>\n'
            f'<article>\n{html_body}\n</article>\n</body>\n</html>'
        )

    result = premailer.transform(
        full_html,
        remove_classes=True,
        strip_important=True,
        keep_style_tags=False,
        base_url=None,
    )

    if fragment:
        article_match = re.search(r"<article>(.*?)</article>", result, re.DOTALL)
        if article_match:
            result = article_match.group(1).strip()

    result = clean_attrs(result)

    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Markdown 转公众号富文本 HTML（CSS 内联化）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("input", type=Path, help="输入 Markdown 文件")
    ap.add_argument("-o", "--output", type=Path, help="输出 HTML 文件（默认 stdout）")
    ap.add_argument("--theme", default="tech", choices=["tech"],
                    help="主题名（目前仅 tech）")
    ap.add_argument("--title", type=str, default=None,
                    help="文章标题（默认从 md 首行 # 提取）")
    ap.add_argument("--no-highlight", action="store_true",
                    help="禁用代码语法高亮")
    ap.add_argument("--fragment", action="store_true",
                    help="只输出 HTML 片段（不包 <html><body>）")
    ap.add_argument("--in-place", action="store_true",
                    help="原地输出同名 .html 文件")
    args = ap.parse_args(argv)

    if args.in_place and args.output:
        ap.error("--in-place 和 --output 互斥")

    if not args.input.exists():
        print(f"错误：输入文件不存在：{args.input}", file=sys.stderr)
        return 1

    md_text = args.input.read_text(encoding="utf-8")
    result = convert(
        md_text,
        theme=args.theme,
        title=args.title,
        no_highlight=args.no_highlight,
        fragment=args.fragment,
    )

    if args.in_place:
        out_path = args.input.with_suffix(".html")
        out_path.write_text(result, encoding="utf-8")
        print(f"已输出：{out_path}", file=sys.stderr)
    elif args.output:
        args.output.write_text(result, encoding="utf-8")
        print(f"已输出：{args.output}", file=sys.stderr)
    else:
        sys.stdout.write(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())