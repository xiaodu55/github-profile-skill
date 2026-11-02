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

只有脚本拿不到的才问用户，且一次问全：每个项目"做了什么"、上游贡献亮点、定位句、社交入口、是否中英双语、是否启用动态卡。缺数据的处理方式见 `references/intake.md` 的降级策略表。

### 2. 选范式

三选一：数据叙事型（有量化成果）、视觉设计型（有插画素材、愿意维护 SVG）、极简工程型（简历导向、不用动态卡）。判据、章节顺序与每节写法见 `references/style-patterns.md`。

### 3. 选组件

默认只用 Tier A 静态组件（shields 徽章、simple-icons、devicon、自绘 SVG、Markdown 表格）。Tier B 动态卡（readme-stats、streak、views counter、活动图）要先向用户说明失效风险，并同时准备表格或自托管 SVG 作为降级方案。Tier C（打字机、奖杯墙、随机图）不使用。组件清单见 `references/widgets.md`。

### 4. 组装

从 `templates/` 复制对应范式的骨架到 `<user>/<user>/README.md`，把 `{{占位符}}` 全部替换为真实内容，**删除模板顶部的说明注释块**，再删除所有未使用的段落——不留空章节，不留"待补充"。

模板：

- `templates/README.data-narrative.md`：数据叙事型（成果表 + 方向表 + 项目表）。
- `templates/README.visual-studio.md`：视觉设计型（自绘 SVG hero + 双主题 + 自托管卡片位）。
- `templates/README.minimal-engineering.md`：极简工程型（about + 技术栈 + 精选项目）。
- `templates/profile-stats-workflow.yml`：自托管统计卡的 GitHub Actions。

### 5. 自检

```bash
python3 scripts/check_profile_readme.py README.md --username <github-handle>
```

脚本检查占位符残留、缺 `alt` 的图片、`<picture>` 缺少深浅双主题、表格列数不一致、`http://` 外链、自指仓库 owner 不一致、动态卡过多。**必须零错误**才能交付；有警告时先判断是否需要修，再向用户说明。

### 6. 交付

给出：

1. 完整 `README.md` 内容或文件绝对路径。
2. 一份"需要你自己做的事"清单：建 `<user>/<user>` 仓库、推送 README、启用 Actions、配 token、配置 Pages。
3. 数据口径说明：哪些数字来自接口、统计到哪天、哪些是用户口述。

## 硬规则

- 不编造 star、PR 数、贡献数、任职经历、获奖；取不到就删掉那一行或整节。
- 动态卡不超过 2 处，徽章一行不超过 6 个，并排图片宽度统一 `49%`。
- 每张表写清数据口径与日期；每个"做了什么"用动词开头并给出结果。
- 不把关键信息放进 `<details>` 折叠。
- 交付前自检零错误；自检不通过不出最终稿。

## 资源

- `references/style-patterns.md`：三种范式的骨架、视觉硬约束、文案公式、双语写法、反面清单。
- `references/widgets.md`：组件目录与可靠性分级、降级方案、自托管卡片工作流。
- `references/intake.md`：必填信息、公开接口取证方法、只能口述的部分、降级策略、交付前确认项。
- `templates/`：三套 README 骨架与 GitHub Actions 模板。
- `scripts/fetch_profile_facts.py`：采集公开事实，输出 JSON。
- `scripts/check_profile_readme.py`：README 静态自检。

## 衔接

主页里的代表贡献表可以直接当作简历 bullet 的原料；想继续攒上游贡献，先去修一个真实 issue；主页上写的技术点可能会被面试官追问，先自己讲一遍。

如果环境里同时装了 ASu-skills，可以用 `/great-resume` 把成果表展开成简历要点、用 `/contributor` 找下一个可合并的 PR、用 `/interview` 对主页上的技术点做掌握度检查、用 `/make-resume` 生成简历文件。
