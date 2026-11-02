#!/usr/bin/env python3
"""按 spec 渲染 GitHub 个人主页 README（确定性输出，可复现）。

用法:
    python3 render_profile_readme.py --spec assets/profile.example.json \
        --facts facts.json --out README.md

设计来源（移植自两个开源生成器的内核，思路借鉴但实现独立）:
    - rahuldkjain/github-profile-readme-generator：表单模型 + 固定拼装顺序，
      社交图标统一走 simple-icons，技术栈图标走 skillicons.dev 并带
      simple-icons / devicon 两级回退。
    - maurodesouza/profile-readme-generator：区块模型（每种区块一个渲染器，
      按数组顺序拼装），并允许区块附带额外产物（这里对应 GitHub Actions）。

spec 字段见 references/spec-fields.md；示例见 assets/profile.example.json。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# 技术栈图标：skillicons.dev 优先，simple-icons / devicon 兜底
# --------------------------------------------------------------------------- #

SKILLICONS_IDS = {
    "python": "py",
    "javascript": "js",
    "typescript": "ts",
    "cplusplus": "cpp",
    "csharp": "cs",
    "golang": "go",
    "go": "go",
    "vuejs": "vue",
    "vue": "vue",
    "tailwind": "tailwind",
    "postgresql": "postgres",
    "mongodb": "mongodb",
    "redis": "redis",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "nodejs": "nodejs",
    "react": "react",
    "nextjs": "nextjs",
    "nuxtjs": "nuxtjs",
    "svelte": "svelte",
    "angularjs": "angular",
    "spring": "spring",
    "nestjs": "nestjs",
    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",
    "express": "express",
    "graphql": "graphql",
    "bash": "bash",
    "linux": "linux",
    "git": "git",
    "aws": "aws",
    "azure": "azure",
    "gcp": "gcp",
    "html5": "html",
    "css3": "css",
    "sass": "sass",
    "webpack": "webpack",
    "vite": "vite",
    "pytest": "pytest",
    "jest": "jest",
    "cypress": "cypress",
    "playwright": "playwright",
    "mysql": "mysql",
    "sqlite": "sqlite",
    "elasticsearch": "elasticsearch",
    "kafka": "kafka",
    "rabbitmq": "rabbitmq",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "numpy": "numpy",
    "pandas": "pandas",
    "jupyter": "jupyter",
    "llamaindex": "llamaindex",
    "langchain": "langchain",
    "huggingface": "huggingface",
    "ollama": "ollama",
    "gradio": "gradio",
    "figma": "figma",
    "unity": "unity",
    "electron": "electron",
    "linuxserver": "linux",
}

# devicon 兜底：skillicons.dev 没有的图标
DEVICON_PATHS = {
    "oracle": "oracle/oracle-original",
    "mssql": "microsoftsqlserver/microsoftsqlserver-plain",
    "mariadb": "mysql/mysql-original-wordmark",
    "erlang": "erlang/erlang-original",
    "materialize": "materialui/materialui-original",
    "openresty": "nginx/nginx-original",
    "hadoop": "hadoop/hadoop-original",
    "keras": "keras/keras-original",
    "numpy": "numpy/numpy-original",
    "pandas": "pandas/pandas-original",
    "matplotlib": "matplotlib/matplotlib-original",
    "jupyter": "jupyter/jupyter-original-wordmark",
    "vuepress": "vuejs/vuejs-original",
    "jekyll": "jekyll/jekyll-original",
    "quasar": "quasar/quasar-plain",
    "mocha": "mocha/mocha-plain",
    "jasmine": "jasmine/jasmine-original",
    "sketch": "sketch/sketch-original",
    "hugo": "hugo/hugo-original",
    "ipython": "jupyter/jupyter-original",
}

SOCIAL_SLUGS = {
    "github": "github",
    "linkedin": "linkedin",
    "twitter": "twitter",
    "x": "x",
    "dev": "devto",
    "stackoverflow": "stackoverflow",
    "kaggle": "kaggle",
    "youtube": "youtube",
    "codepen": "codepen",
    "codesandbox": "codesandbox",
    "leetcode": "leetcode",
    "discord": "discord",
    "medium": "medium",
    "instagram": "instagram",
    "facebook": "facebook",
    "dribbble": "dribbble",
    "behance": "behance",
    "telegram": "telegram",
    "wechat": "wechat",
    "zhihu": "zhihu",
    "bilibili": "bilibili",
}

SOCIAL_URLS = {
    "github": "https://github.com/{u}",
    "linkedin": "https://www.linkedin.com/in/{u}",
    "twitter": "https://twitter.com/{u}",
    "x": "https://x.com/{u}",
    "dev": "https://dev.to/{u}",
    "stackoverflow": "https://stackoverflow.com/users/{u}",
    "kaggle": "https://kaggle.com/{u}",
    "youtube": "https://www.youtube.com/@{u}",
    "codepen": "https://codepen.io/{u}",
    "codesandbox": "https://codesandbox.io/u/{u}",
    "leetcode": "https://leetcode.com/{u}",
    "discord": "https://discord.gg/{u}",
    "medium": "https://medium.com/@{u}",
    "instagram": "https://instagram.com/{u}",
    "facebook": "https://facebook.com/{u}",
    "dribbble": "https://dribbble.com/{u}",
    "behance": "https://behance.net/{u}",
    "telegram": "https://t.me/{u}",
    "zhihu": "https://www.zhihu.com/people/{u}",
    "bilibili": "https://space.bilibili.com/{u}",
}

PLATFORM_LABELS = {
    "github": "GitHub",
    "linkedin": "LinkedIn",
    "twitter": "Twitter",
    "x": "X",
    "dev": "DEV",
    "stackoverflow": "Stack Overflow",
    "youtube": "YouTube",
    "codepen": "CodePen",
    "codesandbox": "CodeSandbox",
    "leetcode": "LeetCode",
    "discord": "Discord",
    "medium": "Medium",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "dribbble": "Dribbble",
    "behance": "Behance",
    "telegram": "Telegram",
    "wechat": "WeChat",
    "zhihu": "Zhihu",
    "bilibili": "Bilibili",
    "kaggle": "Kaggle",
    "email": "Email",
}


def platform_label(platform: str) -> str:
    return PLATFORM_LABELS.get(platform, platform.capitalize())


ABOUT_ICONS = {
    "currentWork": "💼",
    "currentLearn": "🌱",
    "collaborateOn": "🤝",
    "helpWith": "💬",
    "ama": "💭",
    "funFact": "⚡",
    "contact": "📫",
    "portfolio": "🌐",
    "blog": "📝",
    "resume": "📄",
}

ABOUT_ORDER = (
    "currentWork",
    "currentLearn",
    "collaborateOn",
    "helpWith",
    "ama",
    "funFact",
    "portfolio",
    "blog",
    "resume",
    "contact",
)


SKILL_LABELS = {
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "cplusplus": "C++",
    "csharp": "C#",
    "go": "Go",
    "golang": "Go",
    "nodejs": "Node.js",
    "vuejs": "Vue",
    "vue": "Vue",
    "nextjs": "Next.js",
    "nuxtjs": "Nuxt.js",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "kubernetes": "Kubernetes",
    "html5": "HTML",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring",
    "nestjs": "NestJS",
    "graphql": "GraphQL",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "langchain": "LangChain",
    "huggingface": "Hugging Face",
    "llamaindex": "LlamaIndex",
    "dotnet": ".NET",
    "bash": "Bash",
    "git": "Git",
}


def skill_label(skill: str) -> str:
    key = skill.strip()
    if key in SKILL_LABELS:
        return SKILL_LABELS[key]
    return key.replace("_", " ").replace("-", " ").title()


def skill_icon_url(skill: str) -> str:
    """技术栈图标：skillicons.dev → devicon → simple-icons。"""
    key = skill.strip()
    lowered = key.lower()
    if lowered in DEVICON_PATHS:
        return f"https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{DEVICON_PATHS[lowered]}.svg"
    identifier = SKILLICONS_IDS.get(lowered, lowered)
    return f"https://skillicons.dev/icons?i={identifier}"


def social_icon_url(platform: str) -> str:
    slug = SOCIAL_SLUGS.get(platform, platform)
    return f"https://cdn.simpleicons.org/{slug}"


def social_link(platform: str, username: str) -> str:
    template = SOCIAL_URLS.get(platform)
    if template:
        return template.format(u=username)
    if platform in ("portfolio", "blog", "resume", "website", "email"):
        return username
    return f"https://{platform}/{username}"


# --------------------------------------------------------------------------- #
# 事实合并
# --------------------------------------------------------------------------- #


def load_facts(path: str | None) -> dict:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def facts_index(facts: dict) -> dict:
    """把 facts 压成渲染器好查的索引。"""
    stars: dict[str, int] = {}
    descriptions: dict[str, str] = {}
    for repo in facts.get("repos", []) or []:
        name = (repo.get("name") or "").lower()
        if not name:
            continue
        stars[name] = repo.get("stargazers_count", 0)
        descriptions[name] = repo.get("description") or ""
    upstream: dict[str, dict] = {}
    merged = facts.get("merged_prs", {}) or {}
    for entry in merged.get("by_repo", []) or []:
        repo = (entry.get("repo") or "").lower()
        if repo:
            upstream[repo] = entry
    user = facts.get("user", {}) or {}
    return {
        "stars": stars,
        "descriptions": descriptions,
        "upstream": upstream,
        "upstream_total": merged.get("total", 0),
        "upstream_projects": len(upstream),
        "own_repos": len(facts.get("repos", []) or []),
        "followers": user.get("followers", 0),
        "languages": facts.get("languages", {}) or {},
        "user": user,
    }


def merge_spec(spec: dict, facts: dict) -> dict:
    """用 facts 补齐 spec 里没写的数字，不覆盖用户已填的内容。"""
    index = facts_index(facts)
    merged = dict(spec)
    merged["username"] = spec.get("username") or index["user"].get("login") or ""

    projects = []
    for project in spec.get("projects", []) or []:
        item = dict(project)
        key = (item.get("name") or "").lower()
        if item.get("stars") is None:
            item["stars"] = index["stars"].get(key, 0)
        if not item.get("notes") and not item.get("what"):
            item["notes"] = index["descriptions"].get(key, "")
        projects.append(item)
    merged["projects"] = projects

    upstream = []
    for entry in spec.get("upstream", []) or []:
        item = dict(entry)
        key = (item.get("repo") or "").split("/")[-1].lower()
        if item.get("merged") is None:
            item["merged"] = index["upstream"].get(key, {}).get("count", 0)
        upstream.append(item)
    merged["upstream"] = upstream

    merged["_index"] = index
    return merged


# --------------------------------------------------------------------------- #
# 区块渲染器（每种一个函数，顺序由 layout 决定）
# --------------------------------------------------------------------------- #


def render_hero(spec: dict) -> list[str]:
    profile = spec.get("profile", {}) or {}
    username = spec.get("username", "")
    title = profile.get("title") or f"Hi, I'm {username} 👋"
    lines = ["<div align=\"center\">", "", f"# {title}", ""]
    if profile.get("subtitle"):
        lines.append(f"**{profile['subtitle']}**")
        lines.append("")
    if profile.get("focus_zh"):
        lines.append(f"<p><i>{profile['focus_zh']}</i></p>")
        lines.append("")
    socials = spec.get("social", {}) or {}
    links = spec.get("links", {}) or {}
    nav = []
    if links.get("portfolio"):
        nav.append(f'<a href="{links["portfolio"]}">Site</a>')
    if links.get("blog"):
        nav.append(f'<a href="{links["blog"]}">Blog</a>')
    if links.get("resume"):
        nav.append(f'<a href="{links["resume"]}">Resume</a>')
    for platform in ("github", "email"):
        value = socials.get(platform)
        if value:
            nav.append(f'<a href="{social_link(platform, value)}">{platform_label(platform)}</a>')
    if nav:
        lines.append("<p>")
        lines.append("  " + " · ".join(nav))
        lines.append("</p>")
        lines.append("")
    lines.append("</div>")
    lines.append("")
    return lines


def render_about(spec: dict) -> list[str]:
    profile = spec.get("profile", {}) or {}
    links = spec.get("links", {}) or {}
    items = []
    for key in ABOUT_ORDER:
        value = profile.get(key)
        if not value:
            continue
        icon = ABOUT_ICONS.get(key, "•")
        link = links.get(key) or (profile.get(f"{key}_link") if key in ("portfolio", "blog", "resume") else None)
        text = f"**[{value}]({link})**" if link else f"**{value}**"
        items.append(f"- {icon} {text}")
    if not items:
        return []
    return ["### ✎ about", ""] + items + [""]


def render_stats(spec: dict) -> list[str]:
    index = spec.get("_index", {})
    rows = spec.get("stats")
    if rows is None:
        rows = [
            ("Merged PRs", index.get("upstream_total", 0)),
            ("Upstream projects", index.get("upstream_projects", 0)),
            ("Own repos", index.get("own_repos", 0)),
            ("Followers", index.get("followers", 0)),
        ]
    if not rows:
        return []
    header = " | ".join(str(label) for label, _ in rows)
    divider = " | ".join(":---:" for _ in rows)
    values = " | ".join(f"**{value}**" for _, value in rows)
    lines = [
        "## 📊 By the Numbers <sub>数据速览</sub>",
        "",
        f"| {header} |",
        f"| {divider} |",
        f"| {values} |",
        "",
    ]
    scope = spec.get("stats_scope") or (
        "统计口径：GitHub 公开接口抓取，作者维度已合并 PR 总数 / 有合并记录的上游仓库数 / "
        "非 fork 公开仓库数 / 关注者数"
    )
    date = spec.get("data_date")
    lines.append(f"<i>{scope}{' · 截至 ' + date if date else ''}</i>")
    lines.append("")
    return lines


def render_upstream(spec: dict) -> list[str]:
    entries = spec.get("upstream", []) or []
    if not entries:
        return []
    lines = [
        "## 🚀 Selected Contributions <sub>代表贡献</sub>",
        "",
        "| Upstream project | PRs merged | What I did |",
        "| :--- | :---: | :--- |",
    ]
    for entry in entries:
        repo = entry.get("repo", "")
        url = entry.get("url") or f"https://github.com/{repo}"
        lines.append(f"| [{repo}]({url}) | **{entry.get('merged', 0)}** | {entry.get('what', '')} |")
    lines.append("")
    extra = spec.get("upstream_extra")
    if extra:
        lines.append(f"> {extra}")
        lines.append("")
    return lines


def render_focus(spec: dict) -> list[str]:
    rows = spec.get("focus", []) or []
    if not rows:
        return []
    lines = [
        "## 🔭 What I Focus On <sub>专注方向</sub>",
        "",
        "| Direction | What I work on |",
        "| :--- | :--- |",
    ]
    for row in rows:
        lines.append(f"| {row.get('direction', '')} | {row.get('detail', '')} |")
    lines.append("")
    return lines


def render_projects(spec: dict) -> list[str]:
    rows = spec.get("projects", []) or []
    if not rows:
        return []
    lines = [
        "## 🧰 Projects <sub>项目清单</sub>",
        "",
        "| Area | Project | Stars | Notes |",
        "| :--- | :--- | :---: | :--- |",
    ]
    for row in rows:
        name = row.get("name", "")
        url = row.get("url") or f"https://github.com/{spec.get('username', '')}/{name}"
        stars = row.get("stars", 0)
        stars_text = f"{stars / 1000:.1f}k".replace(".0k", "k") if stars >= 1000 else str(stars)
        notes = row.get("notes") or row.get("what") or ""
        lines.append(f"| {row.get('area', '')} | [{name}]({url}) | {stars_text} | {notes} |")
    lines.append("")
    return lines


def render_techs(spec: dict) -> list[str]:
    skills = spec.get("skills", []) or []
    if not skills:
        return []
    icons = []
    for skill in skills:
        label = skill_label(skill)
        icons.append(f'<img src="{skill_icon_url(skill)}" alt="{label}" width="40" height="40">')
    return [
        "## 🛠️ Tech Stack <sub>技术栈</sub>",
        "",
        " ".join(icons),
        "",
    ]


def render_socials(spec: dict) -> list[str]:
    social = spec.get("social", {}) or {}
    entries = []
    for platform, value in social.items():
        if not value or platform in ("email",) or not isinstance(value, str):
            continue
        entries.append(
            f'<a href="{social_link(platform, value)}" target="_blank">'
            f'<img src="{social_icon_url(platform)}" alt="{platform_label(platform)}" height="30" width="30">'
            "</a>"
        )
    if not entries:
        return []
    return ["<h3 align=\"left\">Connect with me:</h3>", "", "<p>", "  ".join(entries), "</p>", ""]


def render_community(spec: dict) -> list[str]:
    rows = spec.get("community", []) or []
    if not rows:
        return []
    return ["## 🤝 Community & More <sub>社区与日常</sub>", ""] + [f"- {row}" for row in rows] + [""]


def render_contact(spec: dict) -> list[str]:
    social = spec.get("social", {}) or {}
    username = spec.get("username", "")
    items = []
    if social.get("github"):
        items.append(f'<a href="https://github.com/{social["github"]}"><strong>GitHub</strong></a>')
    if social.get("email"):
        items.append(f'<a href="mailto:{social["email"]}"><strong>Email</strong></a>')
    if social.get("linkedin"):
        items.append(f'<a href="{social_link("linkedin", social["linkedin"])}"><strong>LinkedIn</strong></a>')
    if not items:
        items.append(f'<a href="https://github.com/{username}"><strong>GitHub</strong></a>')
    lines = [
        "## 📫 Get in Touch <sub>联系我</sub>",
        "",
        "<p align=\"center\">",
        "  " + " · ".join(items),
        "</p>",
        "",
    ]
    if spec.get("closing"):
        lines.append(f'<p align="center"><i>{spec["closing"]}</i></p>')
        lines.append("")
    return lines


def render_widgets(spec: dict) -> list[str]:
    """动态卡片（Tier B）：只在显式开启时输出。"""
    widgets = spec.get("widgets", {}) or {}
    username = spec.get("username", "")
    lines = []
    if widgets.get("github_stats"):
        lines += [
            '<p align="center">',
            f'<img src="https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&hide_border=true" alt="GitHub stats" width="49%">',
            "</p>",
            "",
        ]
    if widgets.get("top_languages"):
        lines += [
            '<p align="center">',
            f'<img src="https://github-readme-stats.vercel.app/api/top-langs?username={username}&layout=compact&hide_border=true" alt="Top languages" width="49%">',
            "</p>",
            "",
        ]
    if widgets.get("streak"):
        lines += [
            '<p align="center">',
            f'<img src="https://streak-stats.demolab.com?user={username}&hide_border=true" alt="Contribution streak" width="49%">',
            "</p>",
            "",
        ]
    return lines


SECTION_RENDERERS = {
    "hero": render_hero,
    "about": render_about,
    "stats": render_stats,
    "upstream": render_upstream,
    "focus": render_focus,
    "projects": render_projects,
    "techs": render_techs,
    "socials": render_socials,
    "community": render_community,
    "contact": render_contact,
    "widgets": render_widgets,
}

LAYOUTS = {
    "data-narrative": ("hero", "stats", "upstream", "focus", "projects", "community", "contact"),
    "classic-form": ("hero", "about", "socials", "techs", "widgets"),
    "minimal": ("hero", "about", "techs", "projects", "contact"),
}


def render(spec: dict, facts: dict | None = None) -> str:
    merged = merge_spec(spec, facts or {})
    layout = merged.get("layout", "data-narrative")
    if layout not in LAYOUTS:
        raise ValueError(f"未知 layout：{layout}，可选 {', '.join(LAYOUTS)}")
    order = merged.get("sections") or LAYOUTS[layout]
    lines: list[str] = []
    if merged.get("note"):
        lines.append(f"<!-- {merged['note']} -->")
        lines.append("")
    for name in order:
        renderer = SECTION_RENDERERS.get(name)
        if renderer is None:
            raise ValueError(f"未知区块：{name}，可选 {', '.join(SECTION_RENDERERS)}")
        lines += renderer(merged)
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按 spec 渲染个人主页 README")
    parser.add_argument("--spec", required=True, help="spec JSON 路径")
    parser.add_argument("--facts", default=None, help="fetch_profile_facts.py 产出的 JSON 路径")
    parser.add_argument("--out", default="-", help="输出路径，- 表示标准输出")
    args = parser.parse_args(argv)

    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"无法读取 spec：{exc}", file=sys.stderr)
        return 2
    if not isinstance(spec, dict):
        print("spec 必须是 JSON 对象", file=sys.stderr)
        return 2

    try:
        facts = load_facts(args.facts)
        output = render(spec, facts)
    except ValueError as exc:
        print(f"渲染失败：{exc}", file=sys.stderr)
        return 2

    if args.out == "-":
        print(output, end="")
    else:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"已写入 {args.out}（{len(output.splitlines())} 行）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
