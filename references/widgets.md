# 组件目录

组件按**稳定性**分三级。默认只用 Tier A；Tier B 必须先向用户说明失效风险并给降级方案；Tier C 基本不用。

## Tier A：静态、长期可用（默认）

| 组件 | 用途 | URL 模板 | 备注 |
| --- | --- | --- | --- |
| shields.io 徽章 | 邮箱、语言、社交、赞助 | `https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>?style=flat-square&logo=<LOGO>&logoColor=white` | 文字含空格用 `_` 或 `%20`；统一 `flat-square` |
| skillicons.dev | 技术栈图标（首选） | `https://skillicons.dev/icons?i=<id>` | 自带深浅色适配；`python→py`、`typescript→ts`、`postgresql→postgres` 等别名见脚本 `SKILLICONS_IDS` |
| simple-icons | 社交与品牌图标 | `https://cdn.simpleicons.org/<slug>` | 社交图标统一走这里，不依赖任何第三方仓库的图片资源 |
| devicon | 技术栈图标兜底 | `https://cdn.jsdelivr.net/gh/devicons/devicon/icons/<slug>/<slug>-original.svg` | 用于 skillicons 没有的项（oracle、numpy、pandas、jupyter 等） |
| GitHub 头像 | Hero 区头像 | `https://github.com/<user>.png?size=200` | 也可直接用 `assets/` 下的本地图 |
| 自绘 SVG | Hero、分隔线、卡片 | 存 `assets/`，用 raw 链接引用 | 见 style-patterns.md 的 SVG 规格 |
| 表格 | 数据速览、贡献表、方向表 | 原生 Markdown | 移动端不横向溢出，列数 ≤ 4 |

### 图标解析顺序

`scripts/render_profile_readme.py` 统一处理，不手写图标 URL：

1. 技术栈图标 → skillicons.dev（命中别名表则先转 id）→ devicon 兜底表 → 名称直接当 skillicons 标识符；
2. 社交图标 → `cdn.simpleicons.org/<slug>`，图标尺寸 `height="30" width="30"`；
3. 社交链接 → 按平台查表拼 URL，未内置的平台退化为 `https://<platform>/<username>`。

这套三级回退的做法来自 `rahuldkjain/github-profile-readme-generator`：它用 skillicons.dev 为主源，对 skillicons 缺失的品牌再退到 simple-icons 或 devicon。本仓库把映射表收进了脚本，避免每次生成都要人肉查表。

Markdown 徽章写法：

```markdown
<a href="mailto:you@example.com"><img src="https://img.shields.io/badge/Email-you%40example.com-181717?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>
```

## Tier B：动态数据卡（可选，需确认）

这些卡片由第三方服务渲染，可能限流、超时或返回 502。**使用前必须同时准备降级方案**：把同一信息用表格或静态文本再写一遍，或把卡片自托管到自己的仓库。

| 组件 | 用途 | URL 模板 | 失效表现 | 降级方案 |
| --- | --- | --- | --- | --- |
| github-readme-stats | 提交/语言/星标统计 | `https://github-readme-stats.vercel.app/api?username=<user>&show_icons=true&theme=<theme>&hide_border=true` | 公共实例限流后 502 | 自建部署，或改用数据速览表 |
| github-readme-stats 部署 | 同上，稳定版 | `https://<your-deployment>.vercel.app/api?username=<user>` | 自己承担维护成本 | 定时脚本抓取后写入本地 SVG |
| github-readme-streak-stats | 连续贡献天数 | `https://streak-stats.demolab.com?user=<user>&theme=<theme>` | 统计延迟或服务下线 | 用贡献数表格代替 |
| github-profile-views-counter | 主页访问量 | `https://komarev.com/ghpvc/?username=<user>&label=Profile%20views&color=0e75b6&style=flat` | 服务不稳定、计数不准 | 直接删掉，不是有价值指标 |
| github-readme-activity-graph | 贡献热力图 | `https://github-readme-activity-graph.vercel.app/graph?username=<user>` | 依赖 GraphQL，匿名调用易失败 | 自建 Action 生成 SVG 存 `output/` |
| 自托管卡片 | 自己控制的统计卡 | GitHub Actions 生成 `output/*.svg`，README 用 raw 链接引用 | 需要维护 Action，但完全可控 | 无 |

自托管卡片的工作流（模板见 `templates/profile-stats-workflow.yml`）：

1. 仓库里放 `scripts/update_stats.py` 或直接调用公开 API 生成 SVG。
2. `.github/workflows/profile-stats.yml` 每天定时运行，把结果提交到 `output/`。
3. README 引用 `https://raw.githubusercontent.com/<user>/<user>/main/output/stats-light.svg` 与 `stats-dark.svg`，用 `<picture>` 双主题切换。

> 贡献图 / 提交数这类数据需要 GraphQL API 与 token；没有 token 时只使用 REST 能拿到的公开数据，并在 README 注明口径。

## Tier C：慎用或淘汰

| 组件 | 问题 |
| --- | --- |
| readme-typing-svg 打字机 | 廉价感强、占首屏、影响可读性与截图效果 |
| github-profile-trophy 奖杯墙 | 刷出来的奖杯与能力无关，容易误导 |
| Giphy / 随机图 API | 内容不可控、会失效、可能违规 |
| "Buy Me a Coffee" 按钮 | 没有真实使用就别放 |
| 大量 emoji 徽章墙 | 信息密度低，掩盖真实内容 |
| 长 GIF 背景 | 首屏加载慢，暗色模式下刺眼 |

## 组合建议

- 首屏：一个 hero（SVG 或头像 + 标题）+ 一句定位 + ≤4 个导航链接。
- 第一屏之后：一张数据速览表 或 两张并排动态卡（`width="49%"`）。
- 中段：成果表（纯 Markdown，不依赖任何服务）。
- 末段：联系方式徽章（≤3 个）。

动态卡与静态表格**不要表达同一件事**：数据卡负责"整体概览"，表格负责"具体做了什么"。
