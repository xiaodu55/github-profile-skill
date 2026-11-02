---
name: github-profile
description: 中文 GitHub 个人主页美化技能：先抓取真实公开数据，再按数据叙事型、视觉设计型或极简工程型三种范式生成 <username>/<username> 个人主页 README，含成果表格、动态数据卡、深浅双主题与自绘 SVG 规范；用户输入 /github-profile 或要求美化 GitHub profile、profile README、个人主页时使用。
license: MIT
---

# /github-profile：美化 GitHub 个人主页

把"我想让主页好看"变成一份**数据真实、结构清楚、能长期维护**的个人主页 README。所有数字来自公开接口或用户陈述，不编造；所有版面从三套范式里选，不自由发挥。

## 适用与不适用

- 适用：制作或重构 `<username>/<username>` 仓库的 README；统一主页视觉；把主页数据喂给简历。
- 不适用：批量生成虚假主页、刷 star/关注、给别人的账号代写经历。

## 工作流程

### 1. 取证（先取数）

确认 GitHub 用户名后采集公开事实：

```bash
python3 scripts/fetch_profile_facts.py --user <github-handle>
```

结果默认以 JSON 打印到标准输出；需要落盘时追加 `--out <输出文件路径>`。

脚本输出账号信息、仓库清单（star / 语言 / 描述）、语言分布、已合并 PR 总数与按仓库分组。详细字段与限流处理见 `references/intake.md`。

### 2. 采集个人信息（必问，不可跳过）

**生成之前必须先问本人。** 主页里最容易编、也最影响可信度的是定位句、"做了什么"、专注方向、联系方式——这些公开接口拿不到，只能问。

先生成一份问卷（公开数据能确认的已预填，让用户确认或改写）：

```bash
python3 scripts/build_intake.py --user <github-handle> --facts <facts.json>
```

把问卷交给用户，**一次问全**，逐条等答案；用户没回的问题标"待补充"，不要替他编。问题覆盖十组：身份与首屏、当前状态、代表项目、上游贡献、专注方向、技术栈、社区与日常、联系方式、版式与视觉、数据口径。每条都标了对应的 spec 字段路径，答完直接映射进 spec，不用二次转述。

问卷里的预填值来自公开接口（仓库、star、已合并 PR 数、仓库描述、关注者），**只作参考，用户确认后才算数**。

### 3. 选范式

三选一：数据叙事型（有量化成果）、视觉设计型（有插画素材、愿意维护 SVG）、极简工程型（简历导向、不用动态卡）。判据、章节顺序与每节写法见 `references/style-patterns.md`。

渲染层面对应三个 layout：`data-narrative`（默认）、`classic-form`（表单式直出，about + 社交 + 技术栈 + 动态卡）、`minimal`。

### 4. 选组件

默认只用 Tier A 静态组件（shields 徽章、simple-icons、skillicons、devicon、自绘 SVG、Markdown 表格）。Tier B 动态卡（readme-stats、streak、views counter、活动图）要先向用户说明失效风险，并同时准备表格或自托管 SVG 作为降级方案。Tier C（打字机、奖杯墙、随机图）不使用。组件清单见 `references/widgets.md`。

### 5. 写 spec 并渲染

**优先用渲染器出初稿**，而不是手写 Markdown：同样的 spec 永远渲染出同样的结果，可复现、可评审。

1. 复制 `assets/profile.example.json` 改成用户的 spec，字段含义见 `references/spec-fields.md`；
2. 渲染：

```bash
python3 scripts/render_profile_readme.py --spec <spec.json> --facts <facts.json> --out README.md
```

3. 渲染后**人工润色**：每个"做了什么"换成用户口述的真实内容，删掉没用的区块。

只有需要视觉设计型（自绘 SVG、深浅双主题 hero）时才改用 `templates/` 里的手写骨架：把 `{{占位符}}` 全部替换为真实内容，**删除模板顶部的说明注释块**，再删除所有未使用的段落——不留空章节，不留"待补充"。

模板：

- `templates/README.data-narrative.md`：数据叙事型（成果表 + 方向表 + 项目表）。
- `templates/README.visual-studio.md`：视觉设计型（自绘 SVG hero + 双主题 + 自托管卡片位）。
- `templates/README.minimal-engineering.md`：极简工程型（about + 技术栈 + 精选项目）。
- `templates/profile-stats-workflow.yml`：自托管统计卡的 GitHub Actions。

### 6. 个人网站（用户要才有）

README 之外，很多人的主页会再挂一个个人站点（像 `jasonbuildai.github.io` 那样），把履历与过程展开。**风格必须让用户选**，不要替他决定。

1. 问卷里问清：要不要站点、要哪几页、风格预设、主色与圆角、联系方式要不要复制按钮、部署到独立仓库还是主页仓库的 `docs/`；
2. 复制 `assets/site.example.json` 改成站点 spec，字段含义见 `references/site-style.md`；
3. 生成：

```bash
python3 scripts/build_site.py --spec <site.json> --out <输出目录>
```

产出首页、开源贡献、项目、学习笔记四个页面（缺哪段就不生成哪页），外加 `assets/site.css`、`assets/site.js` 和 `404.html`。零依赖、零构建，直接丢进 GitHub Pages 就能上线。

4. **上线前必须用浏览器看过**：本地起一个静态服务，逐页截图检查浅色/深色两种模式，确认导航高亮、面包屑、复制按钮、长表格不溢出。

站点内容结构与视觉规则（分节方式、设计令牌、排版基线、三种风格预设、部署方式）见 `references/site-style.md`。

### 7. 自检

```bash
python3 scripts/check_profile_readme.py README.md --username <github-handle>
```

脚本检查占位符残留、缺 `alt` 的图片、`<picture>` 缺少深浅双主题、表格列数不一致、`http://` 外链、自指仓库 owner 不一致、动态卡过多。**必须零错误**才能交付；有警告时先判断是否需要修，再向用户说明。

### 8. 交付

给出：

1. 完整 `README.md` 内容或文件绝对路径。
2. 一份"需要你自己做的事"清单：建 `<user>/<user>` 仓库、推送 README、启用 Actions、配 token、配置 Pages。
3. 数据口径说明：哪些数字来自接口、统计到哪天、哪些是用户口述。

## 硬规则

- **生成前必须先问本人个人信息**：定位句、"做了什么"、专注方向、联系方式这些只能问，不能推断；没答的标"待补充"，不替他编。
- **网站风格必须由用户选**：不替用户决定视觉预设、主色与圆角。
- 不编造 star、PR 数、贡献数、任职经历、获奖；取不到就删掉那一行或整节。
- 动态卡不超过 2 处，徽章一行不超过 6 个，并排图片宽度统一 `49%`。
- 每张表写清数据口径与日期；每个"做了什么"用动词开头并给出结果。
- 不把关键信息放进 `<details>` 折叠。
- 交付前自检零错误；自检不通过不出最终稿；站点上线前必须浏览器逐页看过。

## 资源

- `references/spec-fields.md`：spec 字段契约、layout、区块、图标解析与 facts 合并规则。
- `references/style-patterns.md`：三种范式的骨架、视觉硬约束、文案公式、双语写法、反面清单。
- `references/site-style.md`：个人网站的页面结构、设计令牌、排版基线、三种风格预设与部署方式。
- `references/widgets.md`：组件目录与可靠性分级、降级方案、自托管卡片工作流。
- `references/intake.md`：必填信息、公开接口取证方法、只能口述的部分、降级策略、交付前确认项。
- `assets/profile.example.json`：可直接改写的 README spec 示例。
- `assets/site.example.json`：可直接改写的站点 spec 示例。
- `templates/`：三套 README 骨架与 GitHub Actions 模板。
- `scripts/fetch_profile_facts.py`：采集公开事实，输出 JSON。
- `scripts/build_intake.py`：生成"生成前必问"的信息采集问卷（公开数据预填 + 需用户补充项）。
- `scripts/render_profile_readme.py`：按 spec 渲染 README（确定性输出）。
- `scripts/build_site.py`：按站点 spec 生成静态个人网站。
- `scripts/check_profile_readme.py`：README 静态自检。

## 衔接

主页里的代表贡献表可以直接当作简历 bullet 的原料；想继续攒上游贡献，先去修一个真实 issue；主页上写的技术点可能会被面试官追问，先自己讲一遍。

如果环境里同时装了 ASu-skills，可以用 `/great-resume` 把成果表展开成简历要点、用 `/contributor` 找下一个可合并的 PR、用 `/interview` 对主页上的技术点做掌握度检查、用 `/make-resume` 生成简历文件。
