# 朋友圈图卡模板（HTML → PNG 自动渲染）

三张一组的朋友圈配图模板（1080×1440 竖版，GitHub Dark 技术风）：

| 模板 | 用途 | 对应内容位 |
|------|------|-----------|
| `card1-*-error.html` | 报错冲击卡（钩子） | 终端窗口命令/报错文字、大标题、副题 |
| `card2-*-tree.html` | 决策树/清单卡（干货收藏点） | 问题句、2-3 个分支的条件与解法 |
| `card3-repo-cover.html` | 仓库封面卡（转化） | 三个 stat 数字、副题、底部地址 |

## 复用步骤（换题出图三分钟）

1. **复制模板**改后缀命名，如 `card1-npu-error.html`；
2. **改文字**：只改 HTML 中中文文案与代码行，配色/布局不动；
3. **渲染 PNG**（Edge 无头截图，一条命令）：

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --hide-scrollbars `
  --screenshot="E:\AIcomm\skill-share-content\images\图1-xxx.png" `
  --window-size=1080,1440 `
  "file:///C:/Users/dongz/.codeartsdoer/skills/content-share-generator/templates/cards/card1-xxx.html"
```

4. **自检**：图片中文字无溢出、地址完整即可发布（可让 AI 会话用图片分析做视觉 QA）。

## 设计规范（改版式时遵守）

- 配色锁定 GitHub Dark：底 `#0d1117`、卡 `#161b22`、边 `#30363d`、文字 `#e6edf3`/`#7d8590`、绿 `#3fb950`、蓝 `#1f6feb`、红 `#f85149`
- 等宽字体用于代码/地址/数字（Cascadia Code/Consolas），中文用微软雅黑
- 三张一组保持统一页脚：仓库地址（左）+ 序号（右）
## 换 skill 时的改动清单

给其他 skill 做配图时，三张模板复用，只改内容不改版式：

1. **图1 报错卡**：换终端命令与报错文字为目标 skill 的代表性错误；改大标题与副题
2. **图2 决策树/清单卡**：换问题句与分支条件/解法为目标 skill 的核心决策或清单
3. **图3 仓库封面卡**：换 `rk3xx-chip-dev` 为目标 skill 仓库名；换三个 stat 数字（来自该 skill fact-base §一/§二）；换副题
4. **页脚地址**：三张图的 `.repo` 文字统一换成目标 skill 的 GitHub 地址
5. **渲染命令不变**：只改 HTML 文字，Edge 截图命令照跑

> 命名约定：`card1-<skill>-<topic>.html`，如 `card1-frontend-design-theme.html`。
---

## 公众号配图模板（HTML → PNG 自动渲染）

四张一组的公众号长文配图模板（GitHub Dark 技术风，尺寸适配公众号/知乎正文）：

| 模板 | 尺寸 | 用途 | 对应文章位置 |
|------|------|------|------------|
| `wx-cover.html` | 900×383 | 封面/首图（2.35:1 横版） | 文章顶部，公众号封面或知乎头图 |
| `wx-decision-tree.html` | 1080×720 | 决策树可视化 | "排查过程"末尾或"根因"开头 |
| `wx-data-table.html` | 1080×600 | 数据对比表可视化 | "验证"节末尾 |
| `wx-cta.html` | 1080×400 | 文末引导（仓库地址+二维码） | 文章置底 |

### 渲染命令（4 张一组）

```powershell
$EDGE = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$CARDS = "C:\Users\dongz\.codeartsdoer\skills\content-share-generator\templates\cards"
$OUT   = "E:\AIcomm\skill-share-content\images\gzh"

& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-cover.png"         --window-size=900,383  "file:///$CARDS/wx-cover.html"
& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-decision-tree.png" --window-size=1080,720 "file:///$CARDS/wx-decision-tree.html"
& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-data-table.png"    --window-size=1080,600 "file:///$CARDS/wx-data-table.html"
& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-cta.png"           --window-size=1080,400 "file:///$CARDS/wx-cta.html"
```

### 复用步骤（换题出图五分钟）

1. **复制 4 个模板**，按选题改后缀命名，如 `wx-cover-npu.html`；
2. **改文字**：只改 HTML 中中文文案、代码行、表格数字、stat 数字，配色/布局不动；
3. **渲染 PNG**：上面的命令改文件名照跑；
4. **自检**：图片中文字无溢出、GitHub 地址完整、二维码区域清晰即可发布。

### 换 skill 时的改动清单（公众号配图）

1. **封面 `wx-cover`**：换标题/副题/终端命令/3 个 stat 数字（来自 fact-base §一/§二）；换右上角芯片标识
2. **决策树 `wx-decision-tree`**：换问题句、左右分支条件与解法命令
3. **数据表 `wx-data-table`**：换表头指标名、修坑前后数值、提升列；换底部数据来源注释
4. **文末引导 `wx-cta`**：换标题/副题/仓库地址；二维码占位可保留（发布时贴真实码）
5. **页脚地址**：4 张图的 `.repo` 文字统一换成目标 skill 的 GitHub 地址

> 命名约定：`wx-<role>-<skill>-<topic>.html`，如 `wx-cover-frontend-design.html`。

### 设计规范（与朋友圈图卡一致）

- 配色锁定 GitHub Dark：底 `#0d1117`、卡 `#161b22`、边 `#30363d`、文字 `#e6edf3`/`#7d8590`、绿 `#3fb950`、蓝 `#1f6feb`、红 `#f85149`
- 等宽字体用于代码/地址/数字（Cascadia Code/Consolas），中文用微软雅黑
- 4 张一组保持统一页脚：仓库地址（左）+ 序号（右）
- 封面横版 900×383 适配公众号 2.35:1 首图比例；其余 1080 宽适配公众号正文满宽