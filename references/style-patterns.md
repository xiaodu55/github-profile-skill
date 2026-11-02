# 版面范式与视觉规范

个人主页的高级感来自**结构清晰 + 数据可信 + 视觉克制**，不是来自徽章数量。先定范式，再填内容。

## 一、范式选择

| 范式 | 适合谁 | 骨架 | 关键组件 | 参考主页 |
| --- | --- | --- | --- | --- |
| A 数据叙事型 | 有可展示成果的工程师、开源贡献者、研究者 | 定位 → 数据速览 → 代表贡献表 → 方向表 → 项目表 → 社区 → 联系 | Markdown 表格、少量动态卡 | he-yufeng、JasonBuildAI |
| B 视觉设计型 | 有插画/品牌素材、想留个人印记的人 | Hero SVG → about → 分隔线 → 自绘卡片 → 精选 PR → 结尾 | 自绘 SVG、`<picture>` 双主题、自托管卡片 | Theater-ahyeon |
| C 极简工程型 | 学生、后端工程师、简历导向、不想维护动态卡 | 标题 → about → 技术栈 → 精选项目 → 联系方式 | devicon、shields 徽章 | 多数成熟后端 profile |

选择规则：

- 有 3 个以上可量化的成果（star、合并 PR、发布、用户数）→ 选 A。
- 有可用插画或明确视觉风格，且愿意维护 SVG → 选 B。
- 只想 30 分钟搞定、且以简历投递为目标 → 选 C。
- 不确定就选 A：数据叙事型最不容易过时，也不依赖任何第三方服务。

## 二、通用七段骨架

任何范式都按这七段组织，顺序不要随意调整：

1. **定位句**：第一屏唯一要传达的信息。
2. **导航行**：个人网站 / 邮箱 / 社交，最多 4 个入口。
3. **数据速览**：最多 4 个数字，必须标注口径与统计日期。
4. **成果叙事**：代表贡献表或精选项目（核心段，占篇幅一半以上）。
5. **方向与能力**：2-4 个专注方向，每个方向一句话说清"做什么"。
6. **社区与日常**：2-4 条非技术信息，让主页有"人味"。
7. **联系方式**：一行收尾，不重复前面的链接。

## 三、范式 A：数据叙事型

```markdown
<div align="center">

# Hi, I'm {{NAME}} 👋

**{{ROLE}}** · {{ONE_LINE_FOCUS}}

<p><i>{{ONE_LINE_FOCUS_ZH}}</i></p>

</div>

---

## 📊 By the Numbers <sub>数据速览</sub>

| Contributions | Commits | PRs merged | Issues |
| :---: | :---: | :---: | :---: |
| **{{N1}}** | **{{N2}}** | **{{N3}}** | **{{N4}}** |

<i>统计口径：{{SCOPE}} · 截至 {{DATE}}</i>

## 🚀 Selected Contributions <sub>代表贡献</sub>

| Project | ⭐ | What I did |
| :--- | :---: | :--- |
| [{{OWNER}}/{{REPO}}]({{REPO_URL}}) | {{STARS}} | {{动词 + 对象 + 手段 + 结果}} |

## 🔭 What I Focus On <sub>专注方向</sub>

| Direction | What I work on |
| :--- | :--- |
| {{方向一}} | {{做什么}} |
```

每节的写法要求：

- **数据速览**：数字必须来自可复算的来源（GitHub 公开接口、贡献图），并写明"近 12 个月 / 含私密贡献"这类口径与截止日期。没有口径的数字等于噪声，宁可不写这一节。
- **代表贡献表**：项目名超链接到仓库，⭐ 列写真实 star（用 `1.8k+` 这类简写），第三列必须是**做了什么**而不是"是什么"。动词开头。
- **专注方向表**：2-4 行，每行写"在做什么"，不写技能名词堆砌。
- **项目清单**：可折叠或放在末位，列 Area / Project / Stars / Notes，Notes 写规模或影响。
- **社区与日常**：写出组织成员、正在学的东西、代码之外的事。

## 四、范式 B：视觉设计型

```markdown
<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img src="assets/hero-light.svg" alt="{{ALT_TEXT}}" width="100%">
</picture>

</div>

### ✎ about

- 💼 {{一句当前状态}}
- 🎓 {{一句学校/学习状态}}
- 📫 [{{EMAIL}}](mailto:{{EMAIL}})

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img src="assets/divider-light.svg" alt="" width="100%">
</picture>
```

规则：

- Hero 与分隔线用**自绘 SVG**，存在自己仓库的 `assets/` 下，通过 `raw.githubusercontent.com/<user>/<user>/main/assets/...` 引用，避免相对路径在 GitHub 之外的渲染环境丢失。
- `<picture>` 里必须同时给 dark 与 light 两个 `<source>`，`<img>` 兜底指向浅色版，且写 `alt`。
- 数据卡片可以自绘，也可以由 GitHub Actions 生成 SVG 存进 `output/`，README 用 raw 链接引用（参考 Theater-ahyeon 的 `output/stats-*.svg`）。
- 精选 PR 列表最多 5 条，写清"仓库 — 标题 #编号"。
- 结尾注明素材来源与版权（AI 生成图要标注）。

### 自绘 SVG 规格

| 项 | 规格 |
| --- | --- |
| Hero 高度 | 180-260px，内容四周留白 ≥ 40px |
| 标题字号 | ≥ 28px；正文 ≥ 16px（GitHub 会缩放显示） |
| 文字 | 长句不要写进 SVG，交给 HTML 文本；SVG 只做图形与短标签 |
| 深浅两版 | 结构一致，只换背景色与主色；主色不超过 2 个 |
| 格式 | 纯 SVG，不嵌位图；导出后控制在 200KB 内 |
| 命名 | `hero-light.svg` / `hero-dark.svg` / `divider-light.svg` / `divider-dark.svg` |

## 五、范式 C：极简工程型

```markdown
<div align="center">

# {{NAME}}

{{ROLE}} · {{FOCUS}}

</div>

## About

{{两行自我介绍：现在在做什么 + 擅长什么}}

## Tech Stack

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40" alt="Python">
<!-- 每个图标一行，width/height 统一 40 -->

## Selected Projects

### [{{PROJECT}}]({{URL}})
- {{做了什么}}
- {{做了什么}}
- {{结果}}

## Contact

<a href="mailto:{{EMAIL}}"><img src="https://img.shields.io/badge/Email-{{EMAIL}}-181717?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>
```

规则：技术栈图标一行不超过 12 个；联系方式只保留 2-3 个徽章；不放动态卡。

## 六、视觉规范（硬约束）

- 并排卡片统一 `width="49%"`，不要 50% / 49% 混用。
- 所有图片都要有 `alt`；装饰性图片写 `alt=""` 并只出现在 `<picture>` 内。
- 徽章统一 `style=flat-square`，一行不超过 6 个。
- 表格列数必须一致，分隔行写 `| :--- | :---: |`。
- 字体层级：`h1` 标题 → 粗体定位句 → `<sub>` 中文小标 → `<i>` 补充说明。中文小标统一跟在英文标题后面。
- 全页主色不超过 2 个，其余用中性灰。
- 章节之间用 `---` 或 SVG 分隔线，不要连续堆三个以上装饰元素。
- 动态卡片最多 2 处，且放在数据速览或成果段附近，不要堆在首屏。

## 七、文案公式

- **定位句**：`我是[角色]，专注[领域]，[一个硬指标]。[一个背书]`
  - 例：`AI Agent Runtime Engineer · 让 Agent 跑得起、跑得稳、跑得安全 · 560+ 上游 PR 合并`
  - 反例：`热爱技术的开发者 ⭐ 喜欢开源 ✨`
- **项目一句话**：`[动词] + [对象] + [技术手段] + [结果]`
  - 例：`把 512K 行 Claude Code 蒸馏成 1,309 行可运行引擎，8 篇架构拆解`
  - 反例：`一个很酷的 AI 项目`
- **方向标题**：名词化短语（`Agent Runtime & Reliability`），不要动宾结构（`我在研究 Agent`）。

## 八、双语写法

- 中文正文在前，英文用 `<i>` 紧跟，或用 `<sub>` 小标区分；不要整段复制两遍。
- 项目表格里用 `<br>` 换行写双语，不要拆成两列。
- 只保留一种语言的读者也能读完：任何一条关键信息都不能只存在于另一种语言里。

## 九、反面清单

明确不做的事：

- 不编造 star、PR 数、贡献数、任职经历、获奖信息；数据取不到就删掉那一行。
- 不用 typing SVG 打字机、奖杯墙、随机风景图、动图表情包——廉价且会失效。
- 不做徽章墙：一屏内徽章不超过 6 个，且每个徽章都要有信息量。
- 不把关键信息放进 `<details>` 折叠，招聘方和爬虫都看不到。
- 不用外部随机图片 API（内容会变、不可控、可能违规）。
- 不放不使用的赞助按钮、不用的社交账号。
- 不写"TODO/待补充"进最终稿。

## 十、主页之外的延伸

- 主页里的"代表贡献表"是简历 bullet 的原料：同一句话在简历里要更短、更前置动作。
- 想让主页数字持续增长：去修一个真实 issue，比在主页上加工具更有效。
- 主页上写的技术点可能被追问：写之前先确认自己能讲清实现与取舍。
- 简历文件本身与主页分开维护：主页可公开细节，简历只留与岗位相关的部分。
