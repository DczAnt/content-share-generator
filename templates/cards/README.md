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