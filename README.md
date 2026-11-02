# github-profile-skill

中文 GitHub 个人主页美化技能包：先抓取真实公开数据，**再向本人采集个人信息**，然后按三套成型的版式范式生成 `<username>/<username>` 仓库的 README。

和"填表式 README 生成器"（填表 → 导出 Markdown）的区别是 **先取数、先问人、再渲染、最后自检**：

- **数据真实**：star、仓库、语言、已合并 PR 全部来自公开接口或用户口述，取不到就删掉那一行，不编造。
- **生成前必问本人**：定位句、"做了什么"、专注方向、联系方式这些公开接口拿不到，`build_intake.py` 生成一份问卷交给用户确认，不替用户编。
- **确定性输出**：写一份 spec（JSON），`render_profile_readme.py` 渲染出 README——同样的 spec 永远渲染出同样的结果，可复现、可评审、可回归。
- **结构清楚**：从三套范式里选（数据叙事型 / 视觉设计型 / 极简工程型），章节顺序固定，不自由发挥。
- **视觉克制**：动态卡不超过 2 处、徽章一行不超过 6 个、并排卡片宽度统一 49%、深浅主题必须成对提供。
- **交付前自检**：静态脚本逐条检查占位符残留、缺 `alt`、`<picture>` 缺主题、表格列数、链接协议、自指仓库 owner。

## 目录

```text
github-profile-skill/
├── SKILL.md                             # 技能主体：六步流程 + 硬规则
├── agents/openai.yaml                   # OpenAI 宿主元数据
├── references/
│   ├── spec-fields.md                   # spec 字段契约、layout、区块、图标解析、facts 合并
│   ├── style-patterns.md                # 三套范式骨架、视觉硬约束、文案公式、反面清单
│   ├── site-style.md                    # 站点页面结构、设计令牌、排版基线、风格预设、部署
│   ├── widgets.md                       # 组件目录（Tier A/B/C）与降级方案
│   └── intake.md                        # 信息清单、取证方法、降级策略、交付前确认项
├── assets/
│   ├── profile.example.json             # 可直接改写的 README spec 示例
│   └── site.example.json                # 可直接改写的站点 spec 示例
├── templates/
│   ├── README.data-narrative.md         # 范式 A：数据叙事型
│   ├── README.visual-studio.md          # 范式 B：视觉设计型
│   ├── README.minimal-engineering.md    # 范式 C：极简工程型
│   └── profile-stats-workflow.yml       # 自托管统计卡的 GitHub Actions
├── scripts/
│   ├── fetch_profile_facts.py           # 采集公开事实（纯标准库，无第三方依赖）
│   ├── build_intake.py                  # 生成"生成前必问"的信息采集问卷
│   ├── render_profile_readme.py         # 按 spec 渲染 README（确定性输出）
│   ├── build_site.py                    # 按站点 spec 生成静态个人网站
│   ├── neon_style.py                    # 霓虹 Bento 版式（暗底玻璃拟态 + Bento 网格）
│   └── check_profile_readme.py          # README 静态自检
├── examples/
│   └── README.data-narrative.example.md # 填好的样例（虚构数据），可直接看成品
└── tests/                               # 82 条离线单元测试
```

## 安装

把整个目录放进宿主的 skills 目录：

| 宿主 | 目标路径 |
| --- | --- |
| Claude Code | `~/.claude/skills/github-profile/` |
| Codex | `~/.codex/skills/github-profile/` |
| OpenCode | `~/.config/opencode/skills/github-profile/` |
| DeepSeek Harness | `~/.dsh/skills/github-profile/` |

```bash
git clone https://github.com/<owner>/github-profile-skill.git
cp -r github-profile-skill ~/.claude/skills/github-profile
```

装完重新加载技能列表，用 `/github-profile` 或"美化我的 GitHub 个人主页"触发。

## 用法

```text
/github-profile
我的 GitHub 用户名是 xxx，正在做 Agent 运行时方向，想让主页看起来专业一点。
请先抓我的公开数据，再选一套版式生成 README，并告诉我还需要我自己做哪些事。
```

技能的执行顺序：

1. **取证**：`scripts/fetch_profile_facts.py` 抓账号信息、仓库、语言、已合并 PR；
2. **采集个人信息（必问）**：`scripts/build_intake.py` 生成问卷——公开数据能确认的预填让用户确认，定位句/"做了什么"/专注方向/联系方式等必须用户给，一次问全；
3. **选型**：按范式选骨架，按可靠性选组件（Tier A 静态优先，Tier B 动态必须配降级方案）；
4. **渲染**：把问卷答案写进 spec JSON → `scripts/render_profile_readme.py` 出初稿 → 人工润色；
5. **个人网站**（用户要才有）：`scripts/build_site.py` 生成静态站点；**风格预设由用户选**，上线前用浏览器逐页检查；站点额外产出 `assets/content.js`，用户以后只改这一个文件就能更新内容，不必重新生成；
6. **自检**：`scripts/check_profile_readme.py` 零错误才交付；
7. **交付**：给出 README、"需要你自己做的事"清单、数据口径说明。

### 手动使用脚本

```bash
# 抓取公开事实（JSON 打到标准输出）
python3 scripts/fetch_profile_facts.py --user <github-handle>

# 生成采集问卷（交给用户填）
python3 scripts/build_intake.py --user <github-handle> --facts facts.json

# 按 spec 渲染 README
python3 scripts/render_profile_readme.py --spec assets/profile.example.json --facts facts.json --out README.md

# 生成静态个人网站（RSS 不抓取时加 --no-rss）
python3 scripts/build_site.py --spec assets/site.example.json --out site/

# 自检生成的 README
python3 scripts/check_profile_readme.py README.md --username <github-handle>
```

未认证时 GitHub 公共接口限流为 60 次/小时（core）与 10 次/分钟（search）；需要贡献图等 GraphQL 数据时设置 `GITHUB_TOKEN`（令牌只进请求头，不写进 README 或仓库）。

## 三套范式

| 范式 | 适合谁 | 骨架 | 样例 |
| --- | --- | --- | --- |
| A 数据叙事型 | 有量化成果的工程师、开源贡献者 | 定位 → 数据速览 → 代表贡献表 → 方向表 → 项目表 → 社区 → 联系 | `examples/README.data-narrative.example.md` |
| B 视觉设计型 | 有插画素材、愿意维护 SVG | Hero SVG → about → 分隔线 → 自绘卡片 → 精选 PR → 结尾 | `templates/README.visual-studio.md` |
| C 极简工程型 | 学生、后端工程师、简历导向 | about → 技术栈 → 精选项目 → 联系方式 | `templates/README.minimal-engineering.md` |

组件清单（shields 徽章、simple-icons、devicon、readme-stats、streak、访客计数……）按可靠性分三级，见 [`references/widgets.md`](references/widgets.md)。

## 验证

```bash
python3 -m unittest discover -s tests -t . -v
```

82 条用例全部通过（自检脚本 19 条、取数脚本 4 条、渲染器 15 条、问卷 8 条、站点 36 条），全部离线运行；CI 在 Ubuntu 与 Windows 上各跑一遍，并额外校验样例 README 仍然零错误。

## 参考来源

生成器的两块内核来自开源项目，本仓库独立实现并做了收敛：

- [`rahuldkjain/github-profile-readme-generator`](https://github.com/rahuldkjain/github-profile-readme-generator)：表单模型（profile / links / social / skills / widgets）与固定拼装顺序；技术栈图标以 skillicons.dev 为主源、simple-icons 与 devicon 两级回退的做法。
- [`maurodesouza/profile-readme-generator`](https://github.com/maurodesouza/profile-readme-generator)：区块模型——每种区块一个渲染器，按数组顺序拼装，可产出额外的仓库文件（如 GitHub Actions）。
- [`abhisheknaiidu/awesome-github-profile-readme`](https://github.com/abhisheknaiidu/awesome-github-profile-readme)：主页风格分类与可用工具清单，用于确定组件分级与取舍。

与它们的差异：本仓库不提供网页表单，改为 spec（JSON）+ 命令行渲染器 + 静态自检，数据全部来自公开接口或用户口述，并强制"取不到就删那一行"的降级纪律。

## 设计约束

- 不编造 star、PR 数、贡献数、任职经历、获奖；取不到就删掉那一行或整节。
- 动态卡不超过 2 处，徽章一行不超过 6 个，并排图片宽度统一 `49%`。
- 每张表写清数据口径与统计日期；每个"做了什么"用动词开头并给出结果。
- 不使用打字机 SVG、奖杯墙、随机图这类廉价或易失效组件。
- 交付前自检零错误。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。改动后必须跑通 `python3 -m unittest discover -s tests -t . -v`，提交信息遵循 Conventional Commits。

## 许可

[MIT](LICENSE)
