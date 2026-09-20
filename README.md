# content-share-generator — 技术分享内容生成 skill

> 🔗 **https://github.com/DczAnt/content-share-generator**

> 给任意 AI skill 一键产出朋友圈图文、抖音口播脚本、技术长文（公众号/知乎/CSDN）成品。
> 内置事实底库 + 统一叙事公式 + 三平台模板 + 图卡 HTML→PNG 自动渲染 + **一键发布到公众号**，
> 保证产出数字准确、仓库地址醒目、定位为技术分享。

[![Version](https://img.shields.io/badge/version-2.6.0-blue.svg)](#版本)
[![Skills](https://img.shields.io/badge/fact--bases-rk3xx%20%7C%20frontend--design-green.svg)](#已沉淀的事实底库)

---

## 目录

- [一、最简用法（一条命令发布）](#一最简用法一条命令发布)
- [二、完整链路图](#二完整链路图)
- [三、在 AI 会话里使用](#三在-ai-会话里使用)
- [四、三个脚本速查](#四三个脚本速查)
- [五、配图系统](#五配图系统)
- [六、给新 skill 做分享](#六给新-skill-做分享)
- [七、安装与依赖](#七安装与依赖)
- [八、目录结构](#八目录结构)
- [九、硬性红线](#九硬性红线)
- [十、版本历史](#十版本历史)

---

## 一、最简用法（一条命令发布）

```bash
# 公众号长文 → 自动选配图套系 → 插图 → 转公众号 HTML → 开浏览器
python scripts/publish.py 长文.md
```

浏览器打开 → `Ctrl+A` 全选 → 复制 → 粘贴公众号编辑器 → 发布。

**就这样。** 从 Markdown 长文到可发布的公众号 HTML，一条命令。

---

## 二、完整链路图

```
                    AI 会话
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     朋友圈文案    抖音脚本     公众号长文.md
     (moments.md) (douyin.md)  (tech-article.md)
          │            │            │
          ▼            ▼            ▼
     朋友圈配图    抖音配图     渲染配图 PNG
     (3套×3张)    (可选)      (5套×4张,Edge截图)
          │                        │
          │                        ▼
          │              insert-image.py --auto-style
          │              (自动选套系→插图标记替换)
          │                        │
          │                        ▼
          │              md2wechat.py
          │              (Markdown→公众号富文本HTML)
          │                        │
          │                        ▼
          │              publish.py (一键串联)
          │                        │
          ▼                        ▼
     发朋友圈                   开浏览器
     (文案+配图)               →复制→粘贴公众号→发布
```

---

## 三、在 AI 会话里使用

### 触发词

说以下任意一句即激活 skill：

```
写分享内容 / 出一条分享 / 朋友圈文案CSDN博客 / 自媒体内容 / 给XX做分享
```

### 模式 A：目标 skill 已有事实底库（最快）

直接说 skill 名 + 选题 + 平台：

```
你：给 rk3xx 做分享，选题 GLIBC 兼容，平台 公众号
→ AI 加载 fact-bases/rk3xx.md → 套模板 → 产出长文.md（含 📷 配图标记）
→ 渲染配图 PNG → publish.py 一键转公众号 HTML
```

### 模式 B：给新 skill 做分享（首次，现场提炼）

给 skill 路径，AI 读源码提炼事实底库并存档复用：

```
你：给 C:\...\skills\frontend-design 做分享，选题"AI 味太重"，平台 朋友圈
→ AI 读 frontend-design 的 SKILL.md/references
→ 按 fact-base-template 提炼五节结构（产品事实/数字/陷阱库/选题池）
→ 存到 fact-bases/frontend-design.md（下次直接走模式 A）
→ 套模板产出成品
```

### 产出物（四类）

| 类型 | 模板 | 成品形态 | 建议存放 |
|------|------|----------|----------|
| 朋友圈图文 | `templates/moments.md` | 正文文案 + 配图清单 + 发布技巧 | `<工作目录>/skill-share-content/` |
| 抖音口播脚本 | `templates/douyin-script.md` | 分镜表（时间/画面/口播/字幕） | 同上 |
| 技术长文 | `templates/tech-article.md` | Markdown 长文 + 4 张配图标记 | 同上 |
| 公众号 HTML | `publish.py` 产出 | 可直接粘贴公众号的富文本 HTML | 同上 |

---

## 四、三个脚本速查

### `publish.py` — 一键发布（推荐）

```bash
python scripts/publish.py 长文.md                          # 全自动：选套系→插图→转HTML→开浏览器
python scripts/publish.py 长文.md --style-set E            # 手动指定套系
python scripts/publish.py 长文.md --no-open                # 不开浏览器
python scripts/publish.py 长文.md -o out.html              # 指定输出路径
python scripts/publish.py 长文.md --keep-temp              # 保留中间 .md 文件
```

### `insert-image.py` — 配图插入

```bash
python scripts/insert-image.py 长文.md --auto-style -o out.md    # 自动选套系（关键词匹配）
python scripts/insert-image.py 长文.md --style-set D -o out.md   # 手动指定套系 D
python scripts/insert-image.py 长文.md --images a.png b.png c.png d.png -o out.md  # 自定义图片
python scripts/insert-image.py 长文.md --verify -o out.md        # 校验图片文件存在
python scripts/insert-image.py 长文.md --width 100 -o out.md     # HTML <img> 宽度属性
python scripts/insert-image.py 长文.md --in-place                # 原地改写
```

**`--auto-style` 关键词匹配规则：**

| 套系 | 关键词 | 适用选题 |
|------|--------|----------|
| **D** 赝博暗夜 | 硬核/终端/编译/底层/内核/驱动/GLIBC/NPU/DRM/嵌入式 | 硬核技术 |
| **E** 杂志双色调 | 数据/报告/优化/性能/FPS/延迟/对比/实测/基准 | 数据/正式报告 |
| **C** 极简水墨 | 方法论/设计模式/架构/原则/最佳实践/如何/为什么 | 简洁/方法论 |
| **B** 复古印刷 | 怀旧/历史/演进/踩坑实录/排查/复盘/教训 | 深度技术/踩坑 |
| **A** 混合 | （默认 fallback） | 通用 |

### `md2wechat.py` — Markdown 转公众号 HTML

```bash
python scripts/md2wechat.py 长文.md -o out.html             # 基本转换
python scripts/md2wechat.py 长文.md --title "自定义标题" -o out.html  # 指定标题
python scripts/md2wechat.py 长文.md --no-highlight -o out.html       # 关代码高亮
python scripts/md2wechat.py 长文.md --fragment -o 片段.html          # 只输出片段
python scripts/md2wechat.py 长文.md --in-place                      # 输出同名 .html
```

> 内置 `tech` 主题：深色代码块 + Pygments monokai 高亮 + 左色条标题 + 全边框表格 + 内联样式（公众号不支持 class）。

---

## 五、配图系统

### 朋友圈配图（3 套风格 × 3 张）

| 套系 | 风格 | 模板 |
|------|------|------|
| **A** | GitHub Dark 技术风 | `card1-glibc-error.html` / `card2-glibc-decision-tree.html` / `card3-repo-cover.html` |
| **B** | 暖色编辑风 | 同名 + `-B` 后缀 |
| **C** | 白板手绘风 | 同名 + `-C` 后缀 |

每套 3 张：报错钩子卡 / 干货清单卡 / 仓库封面卡，1080×1440 竖版。

### 公众号配图（5 套风格 × 4 张）

| 套系 | 风格 | 适用选题 | 模板 |
|------|------|----------|------|
| **A** | 混合 4 风格 | 通用 | `wx-cover.html` 等 |
| **B** | 复古印刷风 | 怀旧/深度技术 | `wx-cover-B.html` 等 |
| **C** | 极简水墨风 | 简洁/方法论 | `wx-cover-C.html` 等 |
| **D** | 赝博暗夜风 | 硬核/终端向 | `wx-cover-D.html` 等 |
| **E** | 杂志双色调风 | 数据/正式报告 | `wx-cover-E.html` 等 |

每套 4 张：封面 900×383 / 决策树 1080×720 / 数据表 1080×600 / 文末引导 1080×400。

### 渲染配图 PNG

```powershell
# 公众号 D 套系 4 张（PowerShell）
$EDGE = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$CARDS = "C:\Users\dongz\.codeartsdoer\skills\content-share-generator\templates\cards"
$OUT   = "E:\AIcomm\skill-share-content\images\gzh-D"

& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-cover.png"         --window-size=900,383  "file:///$CARDS/wx-cover-D.html"
& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-decision-tree.png" --window-size=1080,720 "file:///$CARDS/wx-decision-tree-D.html"
& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-data-table.png"    --window-size=1080,600 "file:///$CARDS/wx-data-table-D.html"
& $EDGE --headless=new --disable-gpu --hide-scrollbars --screenshot="$OUT\wx-cta.png"           --window-size=1080,400 "file:///$CARDS/wx-cta-D.html"
```

> 完整复用步骤（换题改文字）见 [`templates/cards/README.md`](templates/cards/README.md)。

### 去AI风设计

每套风格在配色/字体/版式/装饰四维度完全独立，加 SVG 噪点/便签微旋转/不对称圆角/混排字体，避免平台标记为 AI 产出。

---

## 六、给新 skill 做分享

```
1. 首次提炼：说"给 <我的skill路径> 做分享"
   → AI 读 SKILL.md + references + 仓库 README，提炼 fact-base 存档

2. 核对：检查 fact-bases/<我的skill>.md 的数字/陷阱是否准确

3. 产出：说"给 <skill名> 做分享，选题 X，平台 Y"
   → AI 产出文案/脚本/长文

4. 配图：渲染配图 PNG（改 cards 模板文字 + Edge 截图）

5. 发布：
   - 朋友圈/抖音：复制文案 + 选图 → 发
   - 公众号：python scripts/publish.py 长文.md → 复制粘贴公众号编辑器

6. 沉淀：效果好把成品加到 examples/；发现新坑更新 fact-base（版本号 +1）
```

---

## 七、安装与依赖

```bash
# 克隆到 AI 智能体的 skills 目录（以 CodeArts 为例）
git clone https://github.com/DczAnt/content-share-generator.git \
  ~/.codeartsdoer/skills/content-share-generator

# 安装 Python 依赖（md2wechat.py / publish.py 用）
pip install markdown premailer pygments

# insert-image.py 无外部依赖（纯标准库）
```

---

## 八、目录结构

```
content-share-generator/
├── SKILL.md                      # AI 执行入口：工作流 + 路由 + 红线
├── README.md                     # 本文件：面向人的使用说明
├── assets/
│   ├── fact-bases/               # 各 skill 的事实底库（多实例）
│   │   ├── rk3xx.md              # rk3xx-chip-dev 已沉淀
│   │   └── <其他skill>.md        # 现场提炼后存档复用
│   ├── fact-base-template.md     # 新 skill 提炼模板（五节结构）
│   └── narrative.md              # 统一叙事公式 + 地址曝光规范
├── templates/
│   ├── moments.md                # 朋友圈模板
│   ├── douyin-script.md          # 抖音分镜模板
│   ├── tech-article.md           # 技术长文模板（含 📷 配图标记）
│   └── cards/                    # 图卡 HTML 模板 + 渲染说明
│       ├── README.md             # 模板复用步骤 + 渲染命令
│       ├── card1-glibc-error*.html    # 朋友圈 3 套 × 3 张
│       ├── card2-glibc-decision-tree*.html
│       ├── card3-repo-cover*.html
│       ├── wx-cover*.html        # 公众号 5 套 × 4 张
│       ├── wx-decision-tree*.html
│       ├── wx-data-table*.html
│       └── wx-cta*.html
├── scripts/
│   ├── insert-image.py           # 📷 标记 → Markdown 图片（--auto-style 自动选套系）
│   ├── md2wechat.py              # Markdown → 公众号富文本 HTML（CSS 内联 + 代码高亮）
│   └── publish.py                # 一键发布：选套系 → 插图 → 转HTML → 开浏览器
├── docs/
│   └── design-md2wechat.md       # md2wechat.py 设计文档
└── examples/                     # 已验证成品范例（few-shot）
```

---

## 九、硬性红线

产出自动遵守以下规则（AI 会自检）：

1. **数字准确**：性能数据、陷阱现象只来自 fact-base，不编造不夸大
2. **仓库地址醒目**：按平台规范出现（朋友圈单独成行加粗 / 抖音口播+字幕+置顶 / 长文双位置）
3. **脱敏**：不出现真实 IP/密码/凭据；截图用公开仓内容
4. **技术分享定位**：每条内容至少让读者带走一个可复现知识点
5. **事实核对声明**：成品末尾附"事实核对：与 fact-bases/<skill>.md 一致"

---

## 已沉淀的事实底库

| fact-base | 来源 skill | 内容 |
|-----------|-----------|------|
| `rk3xx.md` | [rk3xx-chip-dev](https://github.com/DczAnt/rk3xx-chip-dev) | 56 陷阱 + 46 准则，84.27fps 实测背书，10 条选题 |
| `frontend-design.md` | 系统 frontend-design skill | 5 主题框架，3 审美陷阱，4 条选题 |

---

## 十、版本历史

| 版本 | 日期 | 内容 |
|------|------|------|
| v2.6.0 | 2026-09-20 | `publish.py` 一键发布 + `--auto-style` 自动选套系 |
| v2.5.0 | 2026-09-20 | `md2wechat.py` Markdown 转公众号富文本（CSS 内联 + Pygments 高亮） |
| v2.4.0 | 2026-09-20 | `insert-image.py` 配图插入（套系切换/自定义/HTML 宽度/校验） |
| v2.3.0 | 2026-09-20 | 公众号配图 5 套风格（+C 水墨 / D 暗夜 / E 双色调） |
| v2.2.0 | 2026-09-20 | 朋友圈 3 套 + 公众号 2 套去 AI 风多风格配图 |
| v2.1.0 | 2026-09-20 | 公众号长文自带 4 张配图 + 配图位置标注 |
| v2.0.0 | 2026-09-20 | 多 skill 路由 + 模式 B 现场提炼 + 地址变量化 |
| v1.0.0 | — | 单 skill（rk3xx）+ 三平台模板 + 图卡自动渲染 |

---

## License

Apache 2.0
