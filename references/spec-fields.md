# spec 字段说明

`scripts/render_profile_readme.py` 读一份 JSON spec，输出确定性的 README。同样的 spec 永远渲染出同样的结果，因此结果可复现、可评审、可回归。

字段模型参考了 `rahuldkjain/github-profile-readme-generator` 的表单契约（profile / links / social / support / skills / widgets）与 `maurodesouza/profile-readme-generator` 的区块模型（每种区块一个渲染器，按数组顺序拼装）。

示例见 [`assets/profile.example.json`](../assets/profile.example.json)。

## 顶层字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `username` | string | GitHub 用户名，决定默认链接与仓库地址；facts 里能取到时会自动补 |
| `layout` | string | `data-narrative`（默认）/ `classic-form` / `minimal` |
| `sections` | string[] | 可选，显式指定区块顺序，覆盖 layout 的默认顺序 |
| `note` | string | 可选，渲染成 README 最上方的 HTML 注释（写清"示例数据"或数据来源） |
| `stats` | [label, value][] | 可选，覆盖数据速览表；不填则从 facts 自动生成 |
| `stats_scope` | string | 数据口径说明，写在速览表下方 |
| `data_date` | string | 数据截止日期，拼在口径后面 |
| `upstream_extra` | string | 代表贡献表下方的一句补充（例如"另有 5 个 PR…"） |
| `closing` | string | 结尾一句话 |

区块名（`sections` 可选值）：`hero`、`about`、`stats`、`upstream`、`focus`、`projects`、`techs`、`socials`、`community`、`contact`、`widgets`。

## profile

| 字段 | 说明 |
| --- | --- |
| `title` | 首屏标题，例如 `Hi, I'm xiaodu55 👋`；不填则用用户名生成 |
| `subtitle` | 副标题，一行定位 |
| `focus_zh` | 中文定位句，渲染成斜体说明 |
| `focus_en` | 英文定位句（需要双语时填），紧跟中文定位句渲染 |
| `currentWork` | 当前在做（配 💼） |
| `currentLearn` | 在学什么（配 🌱） |
| `collaborateOn` | 希望一起做什么（配 🤝） |
| `helpWith` | 可以帮什么（配 💬） |
| `ama` | 可以问我什么（配 💭） |
| `funFact` | 趣事（配 ⚡） |
| `portfolio` / `blog` / `resume` | 站点 / 博客 / 简历（配 🌐 / 📝 / 📄） |
| `contact` | 联系方式（配 📫） |

`classic-form` / `minimal` 布局会按 `currentWork → currentLearn → collaborateOn → helpWith → ama → funFact → portfolio → blog → resume → contact` 的固定顺序渲染，空字段自动跳过。

## links

`currentWork`、`collaborateOn`、`helpWith`、`portfolio`、`blog`、`resume`：填了就把对应的 profile 文本变成超链接。`portfolio` / `blog` / `resume` 同时会在首屏导航行出现。

## social

社交平台 → 用户名。内置平台与链接规则：

| 键 | 链接 | 图标 |
| --- | --- | --- |
| `github` | `https://github.com/{u}` | simple-icons |
| `linkedin` | `https://www.linkedin.com/in/{u}` | simple-icons |
| `twitter` / `x` | `https://twitter.com/{u}` / `https://x.com/{u}` | simple-icons |
| `dev` | `https://dev.to/{u}` | simple-icons |
| `stackoverflow` | `https://stackoverflow.com/users/{u}` | simple-icons |
| `youtube` | `https://www.youtube.com/@{u}` | simple-icons |
| `leetcode` / `codepen` / `codesandbox` / `kaggle` / `discord` / `medium` | 见脚本 `SOCIAL_URLS` | simple-icons |
| `zhihu` / `bilibili` / `wechat` / `telegram` | 见脚本 `SOCIAL_URLS` | simple-icons |
| `email` | `mailto:{u}` | 不出图标，只进首屏与联系方式 |

未内置的平台按 `https://{platform}/{username}` 兜底；图标走 `https://cdn.simpleicons.org/{platform}`。

## skills

技术栈名称数组，渲染成一行图标。图标解析顺序：

1. `skillicons.dev/icons?i=<id>`——主路径，自带深浅色适配；
2. devicon CDN——`skillicons.dev` 没有的（如 oracle、numpy、pandas、jupyter 等）；
3. 名称直接当 `skillicons.dev` 标识符（未知项一般也能命中）。

常见别名已内置映射：`python→py`、`typescript→ts`、`javascript→js`、`cplusplus→cpp`、`csharp→cs`、`vuejs→vue`、`postgresql→postgres`、`kubernetes→kubernetes` 等。

## upstream

上游贡献数组，每项：

| 字段 | 说明 |
| --- | --- |
| `repo` | `owner/repo`；不填 `merged` 时按仓库名从 facts 里取合并数 |
| `url` | 可选，不填则用 `https://github.com/{repo}` |
| `merged` | 已合并 PR 数；facts 里没有就写用户提供的数 |
| `what` | 做了什么（一行，动词开头） |

## focus / projects / community

| 字段 | 结构 |
| --- | --- |
| `focus` | `[{direction, detail}]`，渲染成两列表格 |
| `projects` | `[{area, name, url, stars, notes}]`；`stars` 不填时按仓库名从 facts 取，`notes` 不填时取仓库描述；stars ≥ 1000 自动写成 `1.9k` |
| `community` | 字符串数组，渲染成项目符号列表 |

## widgets

动态卡片开关，默认全关（Tier B 组件有失效风险）：

| 字段 | 组件 |
| --- | --- |
| `github_stats` | github-readme-stats 统计卡 |
| `top_languages` | github-readme-stats 语言卡 |
| `streak` | streak-stats 连续贡献卡 |

打开任何一项都要同时准备降级方案：同一信息用表格再写一遍，或自托管成 SVG 存进仓库。

## 与 facts 的合并规则

渲染时传入 `--facts`（`fetch_profile_facts.py` 的产物）后：

- `stats` 未显式给出 → 用 facts 里的已合并 PR 总数、有合并记录的上游仓库数、非 fork 仓库数、关注者数；
- `projects[].stars` 为空 → 按仓库名取 star 数；`notes` 为空 → 取仓库描述；
- `upstream[].merged` 为空 → 按仓库名取合并数。

**用户显式写的数字永远优先**，facts 只补空缺。
