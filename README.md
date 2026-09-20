# content-share-generator — 技术分享内容生成 skill

> 🔗 **https://github.com/DczAnt/content-share-generator**
>
> 给任意 AI skill 一键产出朋友圈图文、抖音口播脚本、技术长文（公众号/知乎/CSDN）成品。
> 内置事实底库 + 统一叙事公式 + 三平台模板 + 图卡 HTML→PNG 自动渲染，保证产出数字准确、仓库地址醒目、定位为技术分享。

[![Version](https://img.shields.io/badge/version-2.5.0-blue.svg)](#版本)
[![Skills](https://img.shields.io/badge/fact--bases-rk3xx%20%7C%20frontend--design-green.svg)](#已沉淀的事实底库)

---

## 快速开始（3 步）

```bash
# 1. 克隆到 AI 智能体的 skills 目录（以 CodeArts 为例）
git clone https://github.com/DczAnt/content-share-generator.git \
  ~/.codeartsdoer/skills/content-share-generator

# 2. 在任意会话里说一句话（提及"分享/文案/脚本"等触发词即激活）
#    例："给 rk3xx 做朋友圈分享，选题 NPU 双核踩坑"

# 3. AI 产出成品到指定位置，直接可发布
```

## 两种使用模式

### 模式 A：目标 skill 已有事实底库（最快）

直接说 skill 名 + 选题 + 平台：

```
你：给 rk3xx 做分享，选题 #2，平台 朋友圈
→ AI 加载 fact-bases/rk3xx.md → 套模板 → 产出成品
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

## 产出物（四类，位置约定）

| 类型 | 模板 | 成品形态 | 建议存放 |
|------|------|----------|----------|
| 朋友圈图文 | `templates/moments.md` | 正文文案 + 配图清单 + 发布技巧 | `<工作目录>/skill-share-content/` |
| 抖音口播脚本 | `templates/douyin-script.md` | 分镜表（时间/画面/口播/字幕）+ 发布配套 | 同上 |
| 技术长文 | `templates/tech-article.md` | Markdown 长文，可粘公众号/知乎/CSDN | 同上 |
| 朋友圈配图 | `templates/cards/` | HTML 图卡 → Edge 渲染 1080×1440 PNG | `.../images/` |

## 配图自动生成

### 朋友圈配图（3 套风格 × 3 张）

三套去 AI 风格（A GitHub Dark / B 暖色编辑 / C 白板手绘），每套 3 张（报错钩子卡 / 干货清单卡 / 仓库封面卡），换题只改 HTML 文字，跑一条 Edge 命令出 PNG：

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --hide-scrollbars `
  --screenshot="输出.png" --window-size=1080,1440 `
  "file:///.../templates/cards/card1-xxx.html"
```

### 公众号配图（5 套风格 × 4 张）

五套去 AI 风格（A 混合 / B 复古印刷 / C 极简水墨 / D 赛博暗夜 / E 杂志双色调），每套 4 张（封面 900×383 / 决策树 1080×720 / 数据表 1080×600 / 文末引导 1080×400），按选题调性选套系。

完整复用步骤见 [`templates/cards/README.md`](templates/cards/README.md)。

### 配图插入长文

技术长文里的 `📷` 标记是占位，用 `scripts/insert-image.py` 一键替换为 Markdown 图片语法：

```bash
# 自动模式：标记里已有路径，直接转换
python scripts/insert-image.py 长文.md --verify -o 长文-配图.md

# 套系模式：换配图套系（A/B/C/D/E）
python scripts/insert-image.py 长文.md --style-set D --verify -o 长文-D.md

# 公众号 HTML 宽度模式
python scripts/insert-image.py 长文.md --style-set D --width 100 -o 长文-html.md
```

### 公众号排版（Markdown → 富文本 HTML）

配图插入后，用 `scripts/md2wechat.py` 转为公众号编辑器可直接粘贴的富文本（CSS 全内联化 + 代码语法高亮）：

```bash
# 完整链路：长文 → 配图 → 公众号 HTML
python scripts/insert-image.py 长文.md --style-set D -o 长文-配图.md
python scripts/md2wechat.py 长文-配图.md -o 长文.html

# 浏览器打开 → 复制内容 → 粘贴公众号编辑器
start 长文.html
```

> 依赖：`pip install markdown premailer pygments`

## 目录结构

```
content-share-generator/
├── SKILL.md                      # AI 执行入口：工作流 + 路由 + 红线
├── assets/
│   ├── fact-bases/               # 各 skill 的事实底库（多实例）
│   │   ├── rk3xx.md              # rk3xx-chip-dev 已沉淀
│   │   └── frontend-design.md    # 现场提炼范例
│   ├── fact-base-template.md     # 新 skill 提炼模板（五节结构）
│   └── narrative.md              # 统一叙事公式 + 地址曝光规范
├── templates/
│   ├── moments.md                # 朋友圈模板
│   ├── douyin-script.md          # 抖音分镜模板
│   ├── tech-article.md           # 技术长文模板
│   └── cards/                    # 图卡 HTML 模板 + 渲染说明
├── scripts/
│   ├── insert-image.py           # 📷 标记 → Markdown 图片语法
│   └── md2wechat.py              # Markdown → 公众号富文本 HTML
└── examples/                     # 已验证成品范例（few-shot）
```

## 给我自己的 skill 做分享（完整流程）

1. **首次提炼**：说"给 `<我的skill路径>` 做分享" → AI 读 SKILL.md + references + 仓库 README，提炼 fact-base 存档
2. **核对**：检查 `fact-bases/<我的skill>.md` 的数字/陷阱是否准确，错的地方让 AI 改
3. **产出**：说"给 `<skill名>` 做分享，选题 X，平台 Y" → AI 产出文案/脚本/长文
4. **配图**：说"给这条出三张配图" → AI 改 cards 模板文字 + 渲染 PNG
5. **发布**：复制文案 + 选图 → 发圈/发抖音/发公众号
6. **沉淀**：效果好就把成品加到 `examples/`；发现新坑就更新 fact-base（版本号 +1）

## 已沉淀的事实底库

| fact-base | 来源 skill | 内容 |
|-----------|-----------|------|
| `rk3xx.md` | [rk3xx-chip-dev](https://github.com/DczAnt/rk3xx-chip-dev) | 56 陷阱 + 46 准则，84.27fps 实测背书，10 条选题 |
| `frontend-design.md` | 系统 frontend-design skill | 5 主题框架，3 审美陷阱，4 条选题 |

## 硬性红线（产出自动遵守）

- 数字只来自 fact-base，不编造不夸大
- 仓库地址按平台规范醒目出现（朋友圈单独成行加粗 / 抖音口播+字幕+置顶 / 长文双位置）
- 不出现真实 IP/密码/凭据；截图用公开仓内容
- 每条内容至少让读者带走一个可复现知识点

## 版本

- v2.5.0（2026-09-20）：新增 `scripts/md2wechat.py` Markdown 转公众号富文本（CSS 内联化 + Pygments 代码高亮 + tech 主题）
- v2.4.0（2026-09-20）：新增 `scripts/insert-image.py` 配图插入脚本（套系切换/自定义图片/HTML 宽度/文件校验）
- v2.3.0（2026-09-20）：公众号配图扩至 5 套风格（+C 极简水墨 / D 赔博暗夜 / E 杂志双色调）
- v2.2.0（2026-09-20）：朋友圈 3 套 + 公众号 2 套去 AI 风多风格配图模板
- v2.1.0（2026-09-20）：公众号长文自带 4 张配图 + tech-article.md 配图位置标注
- v2.0.0（2026-09-20）：多 skill 路由 + 模式 B 现场提炼 + 地址变量化
- v1.0.0：单 skill（rk3xx）+ 三平台模板 + 图卡自动渲染

## License

Apache 2.0