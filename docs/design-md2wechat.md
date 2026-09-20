# 方案 C：Markdown 转公众号富文本工具 — 设计文档

> 日期：2026-09-20
> 状态：设计完成，待实现
> 依赖：Python 3.8+，`markdown` + `premailer` + `pygments`

## 一、目标

把 `insert-image.py` 产出的配图长文（Markdown）一键转为**公众号编辑器可直接粘贴的富文本 HTML**，完成"长文 → 配图 → 排版 → 发布"链路最后一步。

```
tech-article.md 模板 → 产出长文.md → insert-image.py → 长文-配图.md → md2wechat.py → 长文.html → 粘贴公众号编辑器
```

## 二、公众号编辑器技术约束

| 约束 | 说明 | 应对 |
|------|------|------|
| **只支持内联样式** | 不支持 class、外部 CSS、`<style>` 标签 | 用 `premailer` 把 CSS 转为 `style="..."` 内联 |
| **不支持 `<script>`** | JS 会被过滤 | 纯 HTML 输出，无 JS |
| **图片须公众号图床** | 外链图片可能不显示 | 保留 `<img src="路径">`，发布时手动上传替换（公众号编辑器支持批量上传） |
| **代码块样式有限** | 不支持语法高亮插件 | 用 Pygments 生成内联高亮 HTML |
| **表格须内联样式** | 默认表格无边框 | CSS 内联 `border` + `padding` |
| **不支持 mermaid/ASCII** | 流程图不渲染 | tech-article.md 模板已用 ASCII/代码块，转 HTML 后保持 `<pre>` |

## 三、技术方案

**自建 Python 脚本**，不依赖 Node.js/npm（用户环境 Python 优先，skill 自包含）。

### 3.1 依赖

```
markdown >= 3.5        # Markdown → HTML
premailer >= 3.10      # CSS → 内联样式
pygments >= 2.15       # 代码语法高亮
```

### 3.2 处理流水线

```
输入.md
  ↓ markdown.markdown(extensions=[fenced_code, codehilite, tables, toc])
HTML 片段（带 class）
  ↓ Pygments 语法高亮（codehilite 扩展自动处理）
高亮 HTML（<span class="k">...</span>）
  ↓ 注入主题 CSS + 包裹 <article>
带 <style> 的完整 HTML
  ↓ premailer.transform()（CSS → 内联 style）
公众号兼容 HTML（全内联样式）
  ↓ 清理残留 class/id（公众号不需要）
最终 HTML → 输出
```

### 3.3 主题设计

内置 1 个技术文章主题（可扩展）：

**主题 `tech`（技术文章）**：
- 正文：16px、行高 1.8、颜色 #333、字体系统默认
- 标题 H1：22px 加粗 #1a1a1a、底部边框
- 标题 H2：18px 加粗 #1a1a1a、左侧色条
- 代码块：深色背景 #1e1e1e、14px 等宽字体、圆角、Pygments monokai 高亮
- 行内代码：浅灰背景 #f5f5f5、等宽字体
- 表格：全边框、表头加粗浅灰底
- 引用块：左侧色条 + 浅灰底
- 图片：居中、最大宽度 100%
- 殖落间距：15px

### 3.4 CLI 设计

```bash
python scripts/md2wechat.py <input.md> [options]

选项：
  -o, --output FILE      输出 HTML 文件（默认 stdout）
  --theme NAME           主题名（目前仅 tech，默认 tech）
  --title TEXT           文章标题（注入 <h1>，默认从 md 首行 # 提取）
  --no-highlight         禁用代码语法高亮（纯黑白代码块）
  --fragment             只输出 HTML 片段（不包 <html><body>），用于嵌入
  --in-place             原地改写（.md → .html 同名）
```

### 3.5 使用示例

```bash
# 完整链路：长文 → 配图插入 → 公众号 HTML
python scripts/insert-image.py 长文.md --style-set D -o 长文-配图.md
python scripts/md2wechat.py 长文-配图.md -o 长文.html

# 打开 HTML 复制内容，粘贴到公众号编辑器
start 长文.html
```

## 四、不做的事（明确边界）

1. **不做图片自动上传**：公众号图床须手动上传（编辑器支持批量拖拽），脚本只保留 `<img src>` 路径
2. **不做公众号 API 调用**：那是方案 A 的范畴，须认证服务号
3. **不做浏览器自动化**：那是方案 B 的范畴
4. **不做多主题**：先做好 1 个技术文章主题，后续按需扩展

## 五、验收标准

1. 08-公众号长文-GLIBC决策树.md 转出的 HTML 粘贴到公众号编辑器后：
   - [ ] 标题/正文/代码块/表格/引用块样式正确
   - [ ] 代码块语法高亮可见
   - [ ] 图片占位正确（发布时手动上传）
   - [ ] 无 class/外部 CSS 残带
2. HTML 文件可浏览器直接打开预览
3. 脚本无外部网络依赖（纯本地转换）