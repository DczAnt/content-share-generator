# 事实底库：frontend-design skill

> v1.0.0（2026-09-20，由 content-share-generator 模式 B 现场提炼）
> 源：系统内置 frontend-design skill 的 SKILL.md

## 一、产品事实

| 项 | 事实 |
|----|------|
| 仓库 | 系统内置 skill（无独立 GitHub 仓库，通过 CodeArts skill 系统加载） |
| 定位 | 创建独特、生产级前端界面，避免"AI 生成"的通用审美 |
| 支持范围 | 5 种设计主题 + 设计思考框架（Purpose/Tone/Constraints/Differentiation） |
| 知识规模 | 5 主题参考文档（Linear Aesthetic / Minimalist Modern / Apple Minimalist / Cyberpunk / Skeuomorphism） |
| 架构特点 | 主题与场景映射表；强调"选择清晰概念方向并精确执行" |
| 核心理念 | **intentionality 而非 intensity level**——bold maximalism 和 refined minimalism 都能成功，关键是意图明确 |

## 二、实测性能数字

暂无实践项目背书，纯方法论分享。

## 三、陷阱库（从设计原则反推"AI 写前端的坑"）

### T1 "AI 味"太重

- **现象**：AI 产出的前端界面千篇一律——渐变卡片、模糊光晕、通用 hero，无记忆点。
- **根因**：未先选清晰概念方向（Tone），直接堆"好看"的效果。
- **解法**：编码前先走 Design Thinking 四问——Purpose（解决什么问题）/ Tone（5 主题选 1 极端风格）/ Constraints（技术约束）/ Differentiation（让人记住的独特点）。先定方向再写代码。

### T2 主题与场景错配

- **现象**：用 Cyberpunk 做高端消费品牌官网，用 Skeuomorphism 做 SaaS 仪表盘——违和。
- **根因**：凭个人喜好选主题，未对照"Best for"映射。
- **解法**：按主题场景映射选——Linear Aesthetic→开发者工具/AI 平台；Minimalist Modern→企业官网/文档；Apple Minimalist→高端消费/效率工具；Cyberpunk→游戏/加密货币营销；Skeuomorphism→智能控制/音频编辑器。

### T3 强度≠设计感

- **现象**：堆砌特效（glitch/霓虹/视差）当"设计感"，结果花哨但不好用。
- **根因**：把 bold 等同于好。
- **解法**：intentionality 而非 intensity level——每个视觉决策服务于功能与记忆点，不是效果叠加。

## 四、实践项目工程亮点

无独立实践项目。可结合用户工程 `frontend-design-lab`（Ant Design Vue 三层约束体系验证工程）作为佐证，但该工程为私有仓，引用时注明。

## 五、选题池

| # | 选题 | 平台 | 核心知识点 | 素材 |
|---|------|------|-----------|------|
| 1 | 给 AI 写前端总是"AI 味"太重？五主题框架一招破 | 公众号/知乎 | T1 + 五主题框架 | §一 + T1 |
| 2 | Cyberpunk 还是 Apple Minimalist？前端设计主题选型指南 | CSDN/知乎 | T2 主题场景映射表 | T2 |
| 3 | AI 生成界面的三个审美陷阱 | 朋友圈 | T1/T2/T3 浓缩 | §三 |
| 4 | 怎么让 AI 写出有"设计感"的前端：intentionality 而非 intensity | 公众号 | T3 + 设计思考四问 | T3 |