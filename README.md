# github-profile-skill

中文 GitHub 个人主页美化技能包：先抓取真实公开数据，再按三套成型的版式范式生成 `<username>/<username>` 仓库的 README。

和"填表式 README 生成器"（填表 → 导出 Markdown）的区别是 **先取数、再排版、最后自检**：

- **数据真实**：star、仓库、语言、已合并 PR 全部来自公开接口或用户口述，取不到就删掉那一行，不编造。
- **结构清楚**：从三套范式里选（数据叙事型 / 视觉设计型 / 极简工程型），章节顺序固定，不自由发挥。
- **视觉克制**：动态卡不超过 2 处、徽章一行不超过 6 个、并排卡片宽度统一 49%、深浅主题必须成对提供。
- **交付前自检**：静态脚本逐条检查占位符残留、缺 `alt`、`<picture>` 缺主题、表格列数、链接协议、自指仓库 owner。

## 目录

```text
github-profile-skill/
├── SKILL.md                             # 技能主体：六步流程 + 硬规则
├── agents/openai.yaml                   # OpenAI 宿主元数据
├── references/
│   ├── style-patterns.md                # 三套范式骨架、视觉硬约束、文案公式、反面清单
│   ├── widgets.md                       # 组件目录（Tier A/B/C）与降级方案
│   └── intake.md                        # 信息清单、取证方法、降级策略、交付前确认项
├── templates/
│   ├── README.data-narrative.md         # 范式 A：数据叙事型
│   ├── README.visual-studio.md          # 范式 B：视觉设计型
│   ├── README.minimal-engineering.md    # 范例 C：极简工程型
│   └── profile-stats-workflow.yml       # 自托管统计卡的 GitHub Actions
├── scripts/
│   ├── fetch_profile_facts.py           # 采集公开事实（纯标准库，无第三方依赖）
│   └── check_profile_readme.py          # README 静态自检
├── examples/
│   └── README.data-narrative.example.md # 填好的样例（虚构数据），可直接看成品
└── tests/                               # 23 条离线单元测试
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
2. **补问**：只问脚本拿不到的部分（每个项目"做了什么"、上游贡献亮点、定位句、社交入口、是否双语、是否启用动态卡），一次问全；
3. **选型**：按范式选骨架，按可靠性选组件（Tier A 静态优先，Tier B 动态必须配降级方案）；
4. **组装**：填模板、删占位、删多余段落；
5. **自检**：`scripts/check_profile_readme.py` 零错误才交付；
6. **交付**：给出 README、"需要你自己做的事"清单、数据口径说明。

### 手动使用脚本

```bash
# 抓取公开事实（JSON 打到标准输出）
python3 scripts/fetch_profile_facts.py --user <github-handle>

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

23 条用例全部通过（自检脚本 19 条、取数脚本 4 条），全部离线运行；CI 在 Ubuntu 与 Windows 上各跑一遍，并额外校验样例 README 仍然零错误。

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
