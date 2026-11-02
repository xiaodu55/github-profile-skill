#!/usr/bin/env python3
"""按 site spec 生成静态个人网站（GitHub Pages 可直接用）。

用法:
    python3 build_site.py --spec assets/site.example.json --out site/

产出:
    site/index.html            首页
    site/open-source.html      开源贡献
    site/projects.html         项目
    site/learning.html         学习笔记
    site/assets/site.css       设计令牌与排版
    site/assets/site.js        主题切换、复制按钮、导航高亮
    site/404.html              兜底页

内容结构参照 JasonBuildAI 个人站点的组织方式（首页自述 + 联系方式、
开源贡献按"主要贡献 / 参与过的仓库 / 数据说明"分层、代表 PR 列表与
"全部记录"入口）；视觉参照 shadcn/ui 的语义化设计令牌与暗色模式，
排版参照菜鸟教程的中文长文可读性（宽内容列、清晰层级、蓝色链接、
带边框的代码块与表格）。具体规则见 references/site-style.md。
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# 主题预设
# --------------------------------------------------------------------------- #

THEMES = {
    # shadcn/ui 中性底色：主色近黑，链接随正文色
    "shadcn-neutral": {
        "label": "shadcn 中性",
        "primary": "oklch(0.205 0 0)",
        "primary_foreground": "oklch(0.985 0 0)",
        "link": "oklch(0.205 0 0)",
        "link_hover": "oklch(0.42 0 0)",
        "radius": "0.5rem",
        "table_style": "plain",
    },
    # 菜鸟教程经典：白底蓝链、紧凑导航
    "runoob-classic": {
        "label": "菜鸟教程经典",
        "primary": "oklch(0.55 0.16 255)",
        "primary_foreground": "oklch(0.985 0 0)",
        "link": "#2f69d4",
        "link_hover": "#1d4ea8",
        "radius": "0.25rem",
        "table_style": "bordered",
    },
    # 默认混合：shadcn 令牌体系 + runoob 的长文可读性
    "hybrid": {
        "label": "混合（推荐）",
        "primary": "oklch(0.55 0.16 255)",
        "primary_foreground": "oklch(0.985 0 0)",
        "link": "#2f69d4",
        "link_hover": "#1d4ea8",
        "radius": "0.5rem",
        "table_style": "bordered",
    },
}

CSS_TEMPLATE = """/* 由 build_site.py 生成，勿手改；改设计令牌请改 site spec 的 theme 段。 */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: @PRIMARY@;
  --primary-foreground: @PRIMARY_FOREGROUND@;
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --link: @LINK@;
  --link-hover: @LINK_HOVER@;
  --radius: @RADIUS@;
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
  --radius-2xl: calc(var(--radius) * 1.8);
  --content-width: 76ch;
  --page-width: 1080px;
  --font-sans: "Inter", "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.92 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 12%);
  --input: oklch(1 0 0 / 16%);
  --ring: oklch(0.556 0 0);
  --link: #7aa5f0;
  --link-hover: #a8c4f7;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--background);
  color: var(--foreground);
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
}

.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
  z-index: 20;
  padding: 0.5rem 0.75rem;
  background: var(--primary);
  color: var(--primary-foreground);
  border-radius: var(--radius-sm);
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: color-mix(in oklch, var(--background) 88%, transparent);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}
.site-header__inner {
  max-width: var(--page-width);
  margin: 0 auto;
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.site-brand {
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--foreground);
  text-decoration: none;
}
.site-nav {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  margin-left: auto;
}
.site-nav a {
  color: var(--muted-foreground);
  text-decoration: none;
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
}
.site-nav a:hover {
  background: var(--accent);
  color: var(--accent-foreground);
}
.site-nav a[aria-current="page"] {
  color: var(--foreground);
  background: var(--secondary);
}
.theme-toggle {
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--foreground);
  border-radius: var(--radius-sm);
  padding: 0.35rem 0.6rem;
  cursor: pointer;
  font-size: 0.9rem;
}
.theme-toggle:hover {
  background: var(--accent);
}

main {
  max-width: var(--page-width);
  margin: 0 auto;
  padding: 2.5rem 1.25rem 4rem;
}
.prose {
  max-width: var(--content-width);
}
.prose h1 {
  font-size: 2rem;
  line-height: 1.3;
  letter-spacing: -0.02em;
  margin: 0 0 1rem;
}
.prose h2 {
  font-size: 1.35rem;
  margin: 2.5rem 0 0.75rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}
.prose h3 {
  font-size: 1.1rem;
  margin: 1.75rem 0 0.5rem;
}
.prose p { margin: 0.85rem 0; }
.prose a { color: var(--link); text-decoration: none; }
.prose a:hover { color: var(--link-hover); text-decoration: underline; }
.prose strong { font-weight: 650; }
.prose code {
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--muted);
  padding: 0.15em 0.4em;
  border-radius: var(--radius-sm);
}
.prose pre {
  background: var(--muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem;
  overflow-x: auto;
  line-height: 1.6;
}
.prose pre code { background: none; padding: 0; }
.prose blockquote {
  margin: 1.25rem 0;
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--border);
  background: var(--muted);
  border-radius: var(--radius-sm);
  color: var(--muted-foreground);
}
.prose ul { padding-left: 1.25rem; }
.prose li { margin: 0.3rem 0; }

.breadcrumb {
  font-size: 0.875rem;
  color: var(--muted-foreground);
  margin-bottom: 1.25rem;
}
.breadcrumb a { color: var(--muted-foreground); }

.lede {
  font-size: 1.05rem;
  color: var(--muted-foreground);
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin: 1.5rem 0 0;
  padding: 0;
  list-style: none;
}
.stats li {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.85rem 1rem;
  background: var(--card);
}
.stats b { display: block; font-size: 1.5rem; letter-spacing: -0.02em; }
.stats span { color: var(--muted-foreground); font-size: 0.875rem; }

.entries { display: grid; gap: 1.5rem; }
.entry {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.35rem;
  background: var(--card);
}
.entry__index {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--muted-foreground);
}
.entry__title {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin: 0.35rem 0 0.5rem;
}
.entry__title h3 { margin: 0; font-size: 1.15rem; }
.tag {
  font-size: 0.78rem;
  color: var(--secondary-foreground);
  background: var(--secondary);
  border-radius: 999px;
  padding: 0.1rem 0.55rem;
}
.entry__label {
  font-size: 0.85rem;
  color: var(--muted-foreground);
  margin: 0.9rem 0 0.35rem;
}
.entry ul { margin: 0.2rem 0 0; padding-left: 1.2rem; }
.entry__all {
  display: inline-block;
  margin-top: 0.9rem;
  font-size: 0.92rem;
}

.list-plain { list-style: none; padding: 0; }
.list-plain li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
}
.list-plain li:last-child { border-bottom: none; }

.contact-list { list-style: none; padding: 0; }
.contact-list li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  padding: 0.45rem 0;
}
.copy-btn {
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted-foreground);
  border-radius: var(--radius-sm);
  padding: 0.1rem 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
}
.copy-btn:hover { background: var(--accent); color: var(--accent-foreground); }

.note {
  margin-top: 2.5rem;
  font-size: 0.875rem;
  color: var(--muted-foreground);
}

.pager {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  font-size: 0.95rem;
}
.pager a { color: var(--link); text-decoration: none; }

.site-footer {
  border-top: 1px solid var(--border);
  color: var(--muted-foreground);
  font-size: 0.9rem;
}
.site-footer__inner {
  max-width: var(--page-width);
  margin: 0 auto;
  padding: 1.5rem 1.25rem 2.5rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: space-between;
}

/* ---- 风格预设差异：让三种风格真的看起来不同 ---- */
body.preset-hybrid { line-height: 1.72; }
body.preset-hybrid .prose a { text-decoration: underline; text-underline-offset: 3px; text-decoration-color: color-mix(in oklch, var(--link) 45%, transparent); }
body.preset-hybrid .entry { box-shadow: 0 1px 2px rgb(0 0 0 / 4%); }
body.preset-hybrid .stats li { box-shadow: 0 1px 2px rgb(0 0 0 / 4%); }

body.preset-shadcn-neutral { --radius: 0.75rem; }
body.preset-shadcn-neutral .entry,
body.preset-shadcn-neutral .stats li { box-shadow: 0 1px 2px rgb(0 0 0 / 5%); }
body.preset-shadcn-neutral .prose h2 { border-bottom: none; padding-bottom: 0; }
body.preset-shadcn-neutral .prose a { text-decoration: underline; text-underline-offset: 3px; }
body.preset-shadcn-neutral .stats li { background: color-mix(in oklch, var(--card) 82%, var(--muted)); }
body.preset-shadcn-neutral .site-nav a[aria-current="page"] { background: var(--primary); color: var(--primary-foreground); }

body.preset-runoob-classic { font-size: 15px; line-height: 1.7; }
body.preset-runoob-classic .site-header { position: static; backdrop-filter: none; }
body.preset-runoob-classic .prose h1 { font-size: 1.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
body.preset-runoob-classic .prose h2 { font-size: 1.15rem; }
body.preset-runoob-classic .entry,
body.preset-runoob-classic .stats li { border-radius: 0; }
body.preset-runoob-classic .prose a { text-decoration: underline; }
body.preset-runoob-classic .entry__index { display: none; }
body.preset-runoob-classic .tag { border-radius: 0; }

@media (max-width: 640px) {
  .site-nav { margin-left: 0; width: 100%; }
  .prose h1 { font-size: 1.6rem; }
}
"""

JS_SOURCE = """// 由 build_site.py 生成
(function () {
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem('theme'); } catch (e) { stored = null; }
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (stored === 'dark' || (!stored && prefersDark)) root.classList.add('dark');

  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var dark = root.classList.toggle('dark');
      try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) { /* ignore */ }
      toggle.textContent = dark ? '☀ 浅色' : '☾ 深色';
    });
    toggle.textContent = root.classList.contains('dark') ? '☀ 浅色' : '☾ 深色';
  }

  document.querySelectorAll('[data-copy]').forEach(function (button) {
    button.addEventListener('click', function () {
      var value = button.getAttribute('data-copy');
      var done = function () {
        var old = button.textContent;
        button.textContent = '已复制';
        setTimeout(function () { button.textContent = old; }, 1500);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(done, function () {});
      }
    });
  });
})();
"""


def esc(text: object) -> str:
    return html.escape(str(text if text is not None else ""), quote=True)


def render_css(theme: dict) -> str:
    replacements = {
        "@PRIMARY@": theme["primary"],
        "@PRIMARY_FOREGROUND@": theme["primary_foreground"],
        "@LINK@": theme["link"],
        "@LINK_HOVER@": theme["link_hover"],
        "@RADIUS@": theme["radius"],
    }
    css = CSS_TEMPLATE
    for token, value in replacements.items():
        css = css.replace(token, value)
    return css



def parse_rss(xml_text: str, limit: int = 8) -> list[dict]:
    """从 RSS/Atom 文本里取最近若干条（标题、链接、日期）。"""
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    def _text(node, names):
        for name in names:
            found = node.find(name)
            if found is not None and (found.text or "").strip():
                return found.text.strip()
        return ""

    def _link(node):
        link = node.find("link")
        if link is not None:
            if (link.text or "").strip():
                return link.text.strip()
            href = link.get("href")
            if href:
                return href.strip()
        guid = node.find("guid")
        if guid is not None and (guid.text or "").strip().startswith("http"):
            return guid.text.strip()
        return ""

    entries = []
    for node in list(root.iter("item")) + list(root.iter("{http://www.w3.org/2005/Atom}entry")):
        title = _text(node, ["title", "{http://www.w3.org/2005/Atom}title"])
        url = _link(node)
        if not title or not url:
            continue
        date = _text(node, ["pubDate", "updated", "{http://www.w3.org/2005/Atom}updated", "{http://purl.org/dc/elements/1.1/}date"])
        entries.append({"title": title, "url": url, "date": date})
        if len(entries) >= limit:
            break
    return entries


def fetch_rss(url: str, limit: int = 8) -> list[dict]:
    """抓取 RSS 源；失败返回空列表，不影响站点生成。"""
    if not url:
        return []
    import urllib.request

    request = urllib.request.Request(url, headers={"User-Agent": "github-profile-skill"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return parse_rss(response.read().decode("utf-8", "replace"), limit)
    except Exception:
        return []

def _nav_html(nav: list[dict], current: str) -> str:
    items = []
    for entry in nav:
        active = ' aria-current="page"' if entry.get("href") == current else ""
        items.append(f'<a href="{esc(entry.get("href"))}"{active}>{esc(entry.get("label"))}</a>')
    return "\n        ".join(items)


def _shell(
    *,
    page: str,
    title: str,
    description: str,
    nav: list[dict],
    body: str,
    footer: str,
    base: str,
    body_class: str = "",
    breadcrumb: list[tuple[str, str]] | None = None,
    pager: list[tuple[str, str]] | None = None,
) -> str:
    crumbs = ""
    if breadcrumb:
        parts = []
        for index, (label, href) in enumerate(breadcrumb):
            if href:
                parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
            else:
                parts.append(f"<span>{esc(label)}</span>")
            if index < len(breadcrumb) - 1:
                parts.append('<span class="sep">/</span>')
        crumbs = f'<nav class="breadcrumb">{" ".join(parts)}</nav>'

    pager_html = ""
    if pager:
        left = f'<a href="{esc(pager[0][1])}">← {esc(pager[0][0])}</a>' if len(pager) > 0 else ""
        right = f'<a href="{esc(pager[1][1])}">{esc(pager[1][0])} →</a>' if len(pager) > 1 else ""
        pager_html = f'<nav class="pager">{left}{right}</nav>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="{esc(base.get("author", ""))}">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="assets/site.css">
</head>
<body class="{body_class}">
<a class="skip-link" href="#main">跳到主要内容</a>
<header class="site-header">
  <div class="site-header__inner">
    <a class="site-brand" href="index.html">{esc(base.get("brand", ""))}</a>
    <nav class="site-nav" aria-label="主导航">
        {_nav_html(nav, page)}
    </nav>
    <button class="theme-toggle" type="button" data-theme-toggle aria-label="切换深浅主题">☾ 深色</button>
  </div>
</header>
<main id="main">
{crumbs}
{body}
{pager_html}
</main>
<footer class="site-footer">
  <div class="site-footer__inner">
    <span>{esc(footer.get("text", ""))}</span>
    <span>{esc(footer.get("meta", ""))}</span>
  </div>
</footer>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


def render_home(spec: dict, nav: list[dict]) -> str:
    site = spec.get("site", {})
    home = spec.get("home", {})
    parts = ['<div class="prose">']
    parts.append(f"<h1>{esc(home.get('title') or site.get('title', ''))}</h1>")
    if home.get("lede"):
        parts.append(f'<p class="lede">{esc(home["lede"])}</p>')
    for paragraph in home.get("paragraphs", []) or []:
        parts.append(f"<p>{esc(paragraph)}</p>")
    if home.get("focus"):
        parts.append(f"<h2>{esc(home.get('focus_title', '专注方向'))}</h2>")
        parts.append(f"<p>{esc(home['focus'])}</p>")
    if home.get("stats"):
        items = "".join(
            f"<li><b>{esc(value)}</b><span>{esc(label)}</span></li>" for label, value in home["stats"]
        )
        parts.append(f'<ul class="stats">{items}</ul>')
    if home.get("recent"):
        parts.append(f"<h2>{esc(home.get('recent_title', '最近在做'))}</h2>")
        parts.append(f"<p>{esc(home['recent'])}</p>")
    if home.get("contact"):
        parts.append(f"<h2>{esc(home.get('contact_title', '联系方式'))}</h2>")
        if home.get("contact_intro"):
            parts.append(f"<p>{esc(home['contact_intro'])}</p>")
        rows = []
        for item in home["contact"]:
            value = item.get("value", "")
            href = item.get("href", "")
            copy = f'<button class="copy-btn" type="button" data-copy="{esc(value)}">复制</button>' if item.get("copy") else ""
            link = f'<a href="{esc(href)}">{esc(value)}</a>' if href else esc(value)
            rows.append(f"<li><span>{esc(item.get('label', ''))}</span>{link}{copy}</li>")
        parts.append(f'<ul class="contact-list">{"".join(rows)}</ul>')
    if home.get("note"):
        parts.append(f'<p class="note">{esc(home["note"])}</p>')
    parts.append("</div>")
    return "\n".join(parts)


def render_open_source(spec: dict, nav: list[dict]) -> str:
    section = spec.get("open_source", {})
    parts = ['<div class="prose">']
    parts.append(f"<h1>{esc(section.get('title', '开源贡献'))}</h1>")
    if section.get("lede"):
        parts.append(f'<p class="lede">{esc(section["lede"])}</p>')
    for paragraph in section.get("paragraphs", []) or []:
        parts.append(f"<p>{esc(paragraph)}</p>")

    entries = section.get("entries", []) or []
    if entries:
        parts.append(f"<h2>{esc(section.get('entries_title', '主要贡献'))}</h2>")
        parts.append('<div class="entries">')
        for index, entry in enumerate(entries, start=1):
            repo = entry.get("repo", "")
            url = entry.get("url") or f"https://github.com/{repo}"
            parts.append('<article class="entry">')
            parts.append(f'<div class="entry__index">{index:02d}</div>')
            title = f'<h3><a href="{esc(url)}">{esc(repo)}</a></h3>'
            if entry.get("role"):
                title += f'<span class="tag">{esc(entry["role"])}</span>'
            parts.append(f'<div class="entry__title">{title}</div>')
            if entry.get("summary"):
                parts.append(f"<p>{esc(entry['summary'])}</p>")
            prs = entry.get("prs", []) or []
            if prs:
                parts.append('<div class="entry__label">代表 PR</div>')
                items = "".join(
                    f'<li><a href="{esc(pr.get("url", ""))}">#{esc(pr.get("number", ""))} {esc(pr.get("title", ""))} ↗</a></li>'
                    for pr in prs
                )
                parts.append(f"<ul>{items}</ul>")
            if entry.get("all_link"):
                parts.append(f'<a class="entry__all" href="{esc(entry["all_link"])}">全部记录 ↗</a>')
            parts.append("</article>")
        parts.append("</div>")

    index_rows = section.get("repo_index", []) or []
    if index_rows:
        parts.append(f"<h2>{esc(section.get('index_title', '参与过的仓库'))}</h2>")
        if section.get("index_intro"):
            parts.append(f"<p>{esc(section['index_intro'])}</p>")
        items = "".join(
            f'<li><a href="{esc(row.get("url", ""))}">{esc(row.get("repo", ""))} ↗</a></li>'
            for row in index_rows
        )
        parts.append(f'<ul class="list-plain">{items}</ul>')
    if section.get("data_note"):
        parts.append(f'<p class="note">{esc(section["data_note"])}</p>')
    parts.append("</div>")
    return "\n".join(parts)


def render_projects(spec: dict, nav: list[dict]) -> str:
    section = spec.get("projects", {})
    parts = ['<div class="prose">']
    parts.append(f"<h1>{esc(section.get('title', '项目'))}</h1>")
    if section.get("lede"):
        parts.append(f'<p class="lede">{esc(section["lede"])}</p>')
    items = section.get("items", []) or []
    if items:
        parts.append('<div class="entries">')
        for index, item in enumerate(items, start=1):
            parts.append('<article class="entry">')
            parts.append(f'<div class="entry__index">{index:02d}</div>')
            url = item.get("url", "")
            title = f'<h3><a href="{esc(url)}">{esc(item.get("name", ""))}</a></h3>' if url else f'<h3>{esc(item.get("name", ""))}</h3>'
            tags = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in item.get("tags", []) or [])
            parts.append(f'<div class="entry__title">{title}{tags}</div>')
            if item.get("summary"):
                parts.append(f"<p>{esc(item['summary'])}</p>")
            for point in item.get("points", []) or []:
                parts.append(f"<p>· {esc(point)}</p>")
            parts.append("</article>")
        parts.append("</div>")
    if section.get("note"):
        parts.append(f'<p class="note">{esc(section["note"])}</p>')
    parts.append("</div>")
    return "\n".join(parts)


def render_learning(spec: dict, nav: list[dict]) -> str:
    section = spec.get("learning", {})
    parts = ['<div class="prose">']
    parts.append(f"<h1>{esc(section.get('title', '学习笔记'))}</h1>")
    if section.get("lede"):
        parts.append(f'<p class="lede">{esc(section["lede"])}</p>')
    blog = section.get("blog") or {}
    if blog.get("title") or blog.get("url"):
        parts.append('<div class="entries">')
        parts.append('<article class="entry">')
        parts.append('<div class="entry__title">')
        title = esc(blog.get("title") or "博客")
        if blog.get("url"):
            title = f'<a href="{esc(blog["url"])}">{title}</a>'
        parts.append(f"<h3>{title}</h3>")
        if blog.get("rss"):
            parts.append(f'<span class="tag">RSS</span>')
        parts.append("</div>")
        if blog.get("summary"):
            parts.append(f"<p>{esc(blog['summary'])}</p>")
        if blog.get("url"):
            parts.append(f'<a class="entry__all" href="{esc(blog["url"])}">打开博客 ↗</a>')
        parts.append("</article>")
        parts.append("</div>")
    items = section.get("items", []) or []
    if items:
        parts.append('<div class="entries">')
        for index, item in enumerate(items, start=1):
            parts.append('<article class="entry">')
            parts.append(f'<div class="entry__index">{index:02d}</div>')
            url = item.get("url", "")
            title = f'<h3><a href="{esc(url)}">{esc(item.get("title", ""))}</a></h3>' if url else f'<h3>{esc(item.get("title", ""))}</h3>'
            tags = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in item.get("tags", []) or [])
            parts.append(f'<div class="entry__title">{title}{tags}</div>')
            if item.get("date"):
                parts.append(f'<div class="entry__label">{esc(item["date"])}</div>')
            if item.get("summary"):
                parts.append(f"<p>{esc(item['summary'])}</p>")
            parts.append("</article>")
        parts.append("</div>")
    if section.get("note"):
        parts.append(f'<p class="note">{esc(section["note"])}</p>')
    parts.append("</div>")
    return "\n".join(parts)


PAGES = [
    {"key": "open_source", "file": "open-source.html", "title": "开源贡献", "render": render_open_source},
    {"key": "projects", "file": "projects.html", "title": "项目", "render": render_projects},
    {"key": "learning", "file": "learning.html", "title": "学习笔记", "render": render_learning},
]


def build_nav(spec: dict) -> list[dict]:
    explicit = spec.get("nav")
    if explicit:
        return [{"label": item.get("label", ""), "href": item.get("href", "")} for item in explicit]
    nav = [{"label": "首页", "href": "index.html"}]
    for page in PAGES:
        if spec.get(page["key"]):
            nav.append({"label": page["title"], "href": page["file"]})
    return nav


def build_site(spec: dict, fetch_posts: bool = True) -> dict[str, str]:
    """生成站点文件。fetch_posts=True 时会按 learning.blog.rss 拉取最新文章。"""
    site = spec.get("site", {})
    base = {
        "title": site.get("title", ""),
        "brand": site.get("brand", site.get("title", "")),
        "author": site.get("author", ""),
        "description": site.get("description", ""),
    }
    nav = build_nav(spec)
    learning = spec.get("learning") or {}
    blog = learning.get("blog") or {}
    if fetch_posts and blog.get("rss"):
        posts = fetch_rss(blog["rss"], limit=blog.get("limit", 8))
        if posts:
            learning = dict(learning)
            learning["items"] = [
                {"title": post["title"], "url": post["url"], "date": post.get("date", ""), "tags": ["博客"]}
                for post in posts
            ] + list(learning.get("items", []) or [])
            spec = {**spec, "learning": learning}
    preset = spec.get("theme", {}).get("preset", "hybrid")
    body_class = f"preset-{preset}"
    theme = dict(THEMES[spec.get("theme", {}).get("preset", "hybrid")])
    theme.update({key: value for key, value in spec.get("theme", {}).items() if key in theme})
    footer = spec.get("footer", {})

    files: dict[str, str] = {}
    files["index.html"] = _shell(
        page="index.html",
        title=base["title"],
        description=base["description"],
        nav=nav,
        body=render_home(spec, nav),
        footer=footer,
        base=base,
        body_class=body_class,
    )

    for page in PAGES:
        section = spec.get(page["key"])
        if not section:
            continue
        files[page["file"]] = _shell(
            page=page["file"],
            title=f"{page['title']} | {base['title']}",
            description=section.get("description", base["description"]),
            nav=nav,
            body=page["render"](spec, nav),
            footer=footer,
            base=base,
            body_class=body_class,
            breadcrumb=[("首页", "index.html"), (page["title"], None)],
        )

    files["assets/site.css"] = render_css(theme)
    files[".nojekyll"] = ""
    files["assets/site.js"] = JS_SOURCE
    files["404.html"] = _shell(
        page="404.html",
        title=f"页面不存在 | {base['title']}",
        description=base["description"],
        nav=nav,
        body='<div class="prose"><h1>404</h1><p>这个页面不存在。<a href="index.html">回到首页</a></p></div>',
        footer=footer,
        base=base,
        body_class=body_class,
    )
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成静态个人网站")
    parser.add_argument("--spec", required=True, help="site spec JSON 路径")
    parser.add_argument("--out", required=True, help="输出目录")
    parser.add_argument("--no-rss", action="store_true", help="不抓取 learning.blog.rss 的最新文章")
    args = parser.parse_args(argv)

    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"无法读取 spec：{exc}", file=sys.stderr)
        return 2
    if not isinstance(spec, dict):
        print("spec 必须是 JSON 对象", file=sys.stderr)
        return 2

    preset = spec.get("theme", {}).get("preset", "hybrid")
    if preset not in THEMES:
        print(f"未知主题预设：{preset}，可选 {', '.join(THEMES)}", file=sys.stderr)
        return 2

    files = build_site(spec, fetch_posts=not args.no_rss)
    out = Path(args.out)
    for name, content in files.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    print(f"已生成 {len(files)} 个文件到 {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
