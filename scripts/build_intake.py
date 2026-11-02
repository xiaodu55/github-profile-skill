#!/usr/bin/env python3
"""生成"生成前必问"的信息采集问卷（Markdown）。

用法:
    python3 build_intake.py --user <github-handle> --facts facts.json --out intake.md

设计意图:
    个人主页里最容易被编造、也最影响可信度的部分，是"定位句""做了什么"
    "专注方向""联系方式"——这些公开接口拿不到，只能问本人。所以生成流程
    必须先走这一步：把能从公开数据确认的内容预填好让用户确认，把拿不到的
    明确标成待补充，问完再进渲染。

输出是一份 Markdown 问卷，每个问题都标注它对应的 spec 字段路径，
用户答完即可直接映射进 spec，不会二次转述丢失信息。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_profile_readme as renderer  # noqa: E402


def _bullet(field: str, question: str, prefilled: str | None = None) -> str:
    if prefilled:
        return f"- **{question}**（spec：`{field}`）\n  - 预填：`{prefilled}`\n  - 需要你确认或改写"
    return f"- **{question}**（spec：`{field}`）\n  - 需你补充（公开数据里没有）"


def build_questionnaire(username: str, facts: dict) -> str:
    index = renderer.facts_index(facts)
    user = index.get("user", {}) or {}
    lines: list[str] = []

    lines.append(f"# 信息采集 · {username}")
    lines.append("")
    lines.append(
        "生成个人主页 README 前必须先问本人。下面每条都标了对应的 spec 字段："
        "带「预填」的是公开数据里能确认的，确认或改写即可；标「需你补充」的必须你给。"
        "**不要跳过这一步直接生成**——定位句与「做了什么」编不出来，只能问。"
    )
    lines.append("")

    # 1 身份与首屏
    name = user.get("name") or ""
    lines.append("## 1. 身份与首屏")
    lines.append("")
    lines.append(_bullet("profile.title", f"主页第一行怎么称呼你？（例如 `Hi, I'm {username} 👋`）", f"Hi, I'm {username} 👋"))
    lines.append(
        _bullet(
            "profile.subtitle",
            "一句话身份（角色 + 方向）是什么？",
            user.get("bio") or None,
        )
    )
    lines.append(_bullet("profile.focus_zh", "中文定位句想强调什么？"))
    lines.append(_bullet("profile.focus_en", "要不要配一句英文定位？（要双语就填，只要中文就留空）"))
    lines.append("")

    # 2 当前状态
    lines.append("## 2. 当前状态")
    lines.append("")
    for field, question in (
        ("profile.currentWork", "现在在做什么？（在职 / 实习 / 求职 / 学校）"),
        ("profile.currentLearn", "最近在学或研究什么？"),
        ("profile.collaborateOn", "希望有人一起做什么？"),
        ("profile.helpWith", "能帮别人做什么？"),
        ("profile.ama", "可以问我什么？"),
        ("profile.funFact", "有什么趣事或反差？"),
    ):
        lines.append(_bullet(field, question))
    lines.append("")

    # 3 代表项目
    lines.append("## 3. 代表项目（2-5 个）")
    lines.append("")
    repos = sorted(facts.get("repos", []) or [], key=lambda repo: repo.get("stargazers_count", 0), reverse=True)
    if repos:
        lines.append("公开仓库里 star 最高的几个（star 数已预填，「做了什么」需要你写）：")
        lines.append("")
        for repo in repos[:5]:
            name = repo.get("name", "")
            stars = repo.get("stargazers_count", 0)
            desc = repo.get("description") or ""
            lines.append(f"- `{name}` — star `{stars}`，描述：{desc or '（无描述）'}")
            lines.append(f"  - 问：你在 `{name}` 里具体做了什么？（动词开头，一行，spec：`projects[].notes`）")
        lines.append("")
    else:
        lines.append("- 公开仓库列表为空，请直接列出你的代表项目（spec：`projects[]`）")
        lines.append("")
    lines.append(_bullet("projects[].area", "这些项目属于什么方向？（如 Agent 平台 / 工具 / 文档）"))
    lines.append("")

    # 4 上游贡献
    lines.append("## 4. 上游贡献")
    lines.append("")
    merged = facts.get("merged_prs", {}) or {}
    by_repo = merged.get("by_repo", []) or []
    if by_repo:
        lines.append(f"已合并 PR 共 `{merged.get('total', 0)}` 个，分布在 `{len(by_repo)}` 个上游仓库：")
        lines.append("")
        for entry in by_repo[:6]:
            samples = entry.get("samples", []) or []
            titles = "；".join((sample.get("title") or "") for sample in samples[:2])
            lines.append(f"- `{entry.get('repo')}` — `{entry.get('count')}` 个：{titles}")
            lines.append(f"  - 问：这批 PR 归成一句话怎么讲？（spec：`upstream[].what`）")
        lines.append("")
    else:
        lines.append("- 公开数据里没有已合并 PR，跳过本节")
        lines.append("")
    lines.append(_bullet("upstream_extra", "剩下的 PR 要不要合并成一句话？"))
    lines.append("")

    # 5 专注方向
    lines.append("## 5. 专注方向（2-4 条）")
    lines.append("")
    lines.append(_bullet("focus[].direction", "方向标题用名词短语（如 Agent Runtime & Reliability）"))
    lines.append(_bullet("focus[].detail", "每个方向具体在做什么？"))
    lines.append("")

    # 6 技术栈
    lines.append("## 6. 技术栈")
    lines.append("")
    languages = index.get("languages", {}) or {}
    if languages:
        preview = "、".join(f"{name}({count})" for name, count in list(languages.items())[:8])
        lines.append(f"从仓库主语言统计到的分布：{preview}")
        lines.append("")
    lines.append(_bullet("skills[]", "你真正写得多的技术是什么？（可多选，会渲染成图标行）"))
    lines.append("")

    # 7 社区与日常
    lines.append("## 7. 社区与日常")
    lines.append("")
    lines.append(_bullet("community[]", "代码之外：组织成员、最近在折腾什么、业余爱好"))
    lines.append("")

    # 8 联系方式
    lines.append("## 8. 联系方式")
    lines.append("")
    lines.append(_bullet("social.email", "邮箱（可留空）"))
    lines.append(_bullet("social.linkedin", "LinkedIn 或其它社交账号（可留空）"))
    lines.append(_bullet("links.portfolio", "个人网站 / 作品集（可留空）"))
    lines.append(_bullet("links.blog", "博客（可留空）"))
    lines.append(_bullet("links.resume", "简历文件链接（可留空）"))
    lines.append("")

    # 9 版式与视觉
    lines.append("## 9. 版式与视觉")
    lines.append("")
    lines.append(
        _bullet(
            "layout",
            "想要哪种版式？`data-narrative`（成果表叙事）/ `classic-form`（表单式直出）/ `minimal`（极简）",
            "data-narrative",
        )
    )
    lines.append(_bullet("sections[]", "要调整区块顺序或增删区块吗？（如加 techs）"))
    lines.append(_bullet("widgets.*", "要不要动态数据卡（readme-stats / streak）？默认关闭"))
    lines.append("")

    # 10 数据口径
    lines.append("## 10. 数据口径")
    lines.append("")
    lines.append(_bullet("stats_scope", "速览表的数字口径怎么写？"))
    lines.append(_bullet("data_date", "数据截止到哪天？"))
    lines.append(
        _bullet(
            "stats[]",
            "速览表想放哪几个指标？（默认：已合并 PR / 上游项目数 / 自建仓库数 / 关注者）",
        )
    )
    lines.append("")

    # 11 个人网站
    lines.append("## 11. 个人网站（可选，但风格要你定）")
    lines.append("")
    lines.append(_bullet("site", "要不要再做一个个人网站？（很多主页会挂一个站点展开履历）"))
    lines.append(_bullet("nav[]", "站点要哪几页？（首页 / 开源贡献 / 项目 / 学习笔记）"))
    lines.append(
        _bullet(
            "theme.preset",
            "风格预设选哪个？`hybrid`（干净现代，默认）/ `shadcn-neutral`（全中性极简）/ `runoob-classic`（蓝链经典文档风）",
            "hybrid",
        )
    )
    lines.append(_bullet("theme.primary", "主色要改吗？（默认蓝；可给一个 hex）"))
    lines.append(_bullet("theme.radius", "圆角要改吗？（默认 0.5rem）"))
    lines.append(_bullet("home.contact[].copy", "联系方式要不要一键复制按钮？"))
    lines.append(_bullet("deploy", "部署到哪？`<用户名>.github.io` 独立仓库，还是主页仓库的 `docs/` 目录？"))
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("回答完以上问题后，我会把答案写进 spec 并渲染，再跑自检。")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成生成前必问的信息采集问卷")
    parser.add_argument("--user", required=True, help="GitHub 用户名")
    parser.add_argument("--facts", default=None, help="fetch_profile_facts.py 产出的 JSON 路径")
    parser.add_argument("--out", default="-", help="输出路径，- 表示标准输出")
    args = parser.parse_args(argv)

    facts: dict = {}
    if args.facts:
        try:
            facts = json.loads(Path(args.facts).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"无法读取 facts：{exc}", file=sys.stderr)
            return 2

    questionnaire = build_questionnaire(args.user, facts)
    if args.out == "-":
        print(questionnaire, end="")
    else:
        Path(args.out).write_text(questionnaire, encoding="utf-8")
        print(f"已写入 {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
