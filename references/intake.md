# 信息采集与取证

原则：**先取数，再排版**。所有数字先来自公开接口或用户陈述，排版只是最后一步。

## 一、必填信息

**生成之前必须先问本人**（问卷由 `scripts/build_intake.py` 生成，公开数据能确认的已预填）。下表是问卷覆盖的必填内容：

| 信息 | 说明 | 缺失时的处理 |
| --- | --- | --- |
| GitHub 用户名 | 决定仓库名 `<user>/<user>` 与所有链接 | 必须先确认，不能猜 |
| 一句定位 | 角色 + 领域 + 硬指标 | 必须问用户；不能用"热爱技术的开发者"这类空话 |
| 代表项目 3-5 个 | 名称 + 一句话 + 是否公开 | 少于 3 个就改成"精选项目"单条叙述 |
| 社交/联系入口 | 邮箱、博客、LinkedIn、Twitter/X | 只保留用户实际在用的 |
| 语言风格 | 单语或中英双语 | 默认跟随用户提问语言 |

问卷脚本的用法：

```bash
python3 scripts/build_intake.py --user <github-handle> --facts <facts.json>
```

输出按十组组织（身份与首屏、当前状态、代表项目、上游贡献、专注方向、技术栈、社区与日常、联系方式、版式与视觉、数据口径），每条标出对应的 spec 字段路径，并区分「预填（需确认）」与「需你补充」。把问卷交给用户，一次问全；未回答的项标"待补充"，不替他编。

## 二、可选信息

- 专注方向（2-4 条）。
- 上游贡献：仓库名、合并 PR 数、亮点 PR 链接。
- 个人网站与其它站点。
- 正在做的事（近期关注点）。
- 视觉素材：头像、插画、品牌色、喜欢的风格。
- 是否启用动态数据卡（Tier B）。
- GitHub token（仅用于 GraphQL 贡献图等需要认证的接口）。

## 三、自动取证：公开接口

用 `scripts/fetch_profile_facts.py` 采集账号公开信息：

```bash
python3 scripts/fetch_profile_facts.py --user <github-handle> --out facts.json
```

能拿到的字段：

| 字段 | 来源 | 用途 |
| --- | --- | --- |
| `user.bio` / `user.company` / `user.location` / `user.blog` | `/users/{user}` | 定位句素材 |
| `repos[]`（名称、star、语言、描述、topics） | `/users/{user}/repos` | 项目表、技术栈 |
| `top_repos[]` | 同上按 star 排序 | 代表项目 |
| `languages` | 按仓库主语言聚合 | 技术栈图标选择 |
| `merged_prs.total` 与 `by_repo` | `/search/issues?q=is:pr+author:<user>+is:merged` | 上游贡献统计 |

注意事项：

- 未认证时 core 接口 60 次/小时、search 接口 10 次/分钟；脚本在限流时明确报错并提示设置 `GITHUB_TOKEN`。
- `merged_prs.total` 是接口给出的总数，`by_repo` 的分组只统计本次抓到的样本页，README 里要写清"抽样/总计"口径。
- `/users/{user}/languages` 对未认证请求返回 404，语言分布用仓库主语言字段或 `--deep-languages` 逐仓库统计。

需要 token 才能拿到的数据（贡献图、完整提交统计、PR 评审记录）：

```bash
export GITHUB_TOKEN=<token>
python3 scripts/fetch_profile_facts.py --user <github-handle> --out facts.json
```

token 只用于请求头，不要写进 README、仓库或日志。

## 四、只能由用户提供的部分

脚本拿不到、需要用户口述：

- 每个项目的**具体贡献**：做了什么、面向谁、结果如何（star 数可自动取，"做了什么"不可）。
- 上游贡献的亮点（脚本只给标题与链接，不替你判断价值）。
- 定位句与硬指标（简历/主页里"最想被记住的一句话"）。
- 私有仓库贡献数（用户自行提供，需说明口径）。
- 视觉素材与配色偏好。

追问方式：一次问全，用编号列表让用户逐条回；不要挤牙膏式追问。

## 五、降级策略

| 缺什么 | 怎么降级 |
| --- | --- |
| 没有代表项目 | 用"研究/在做的东西"段落替代项目表 |
| 没有上游贡献 | 整段删除贡献表，不要放占位表格 |
| 没有 star 颇高的仓库 | 不写 ⭐ 列，改成"项目 / 简介 / 角色"三列 |
| 不愿用动态卡 | 全静态：数据速览表 + 项目表 + shields 徽章 |
| 没有插画素材 | 范式 A 或 C，不要用占位图 |
| 数据接口限流 | 等额度恢复或配置 token；不要用估算数字顶替 |

## 六、交付前确认项

- 仓库名与用户名一致（`<user>/<user>`）。
- 所有链接指向真实存在的页面。
- 每个数字都有口径与日期。
- 自检脚本零错误（`python3 scripts/check_profile_readme.py README.md --username <user>`）。
- 需要用户自己做的动作单独列出：建仓、开启 Actions、设置 token、配置 Pages。
