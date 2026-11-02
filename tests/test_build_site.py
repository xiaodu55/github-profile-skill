#!/usr/bin/env python3
"""build_site.py 的聚焦回归测试（全部离线）。"""

import importlib.util
import sys
import unittest
import unittest.mock
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "build_site.py"
SPEC = importlib.util.spec_from_file_location("build_site", SCRIPT_PATH)
build_site = importlib.util.module_from_spec(SPEC)
sys.modules["build_site"] = build_site
assert SPEC.loader is not None
SPEC.loader.exec_module(build_site)


SPEC_DATA = {
    "site": {"title": "Ada | Runtime", "brand": "Ada", "author": "Ada", "description": "个人站点"},
    "theme": {"preset": "hybrid"},
    "home": {
        "title": "你好，我是 Ada。",
        "paragraphs": ["在做 Agent 运行时。"],
        "stats": [["Merged PRs", 59]],
        "contact": [{"label": "Email", "value": "ada@example.org", "copy": True}],
    },
    "open_source": {
        "entries": [
            {
                "repo": "acme/runtime",
                "role": "贡献者",
                "summary": "修并发",
                "prs": [{"number": 7, "title": "fix", "url": "https://example.org/7"}],
                "all_link": "https://example.org/all",
            }
        ],
        "repo_index": [{"repo": "acme/runtime", "url": "https://example.org/idx"}],
    },
    "projects": {"items": [{"name": "CoreCoder", "url": "https://example.org/cc", "tags": ["Python"]}]},
    "learning": {"items": [{"title": "笔记一", "date": "2026-10"}]},
    "footer": {"text": "© 2026"},
}


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.files = build_site.build_site(SPEC_DATA)

    def test_generates_expected_pages(self):
        for name in ("index.html", "open-source.html", "projects.html", "learning.html", "404.html"):
            self.assertIn(name, self.files)
        self.assertIn("assets/site.css", self.files)
        self.assertIn("assets/site.js", self.files)

    def test_nav_lists_pages_in_order(self):
        html = self.files["index.html"]
        self.assertLess(html.index("open-source.html"), html.index("projects.html"))
        self.assertIn('aria-current="page"', html)

    def test_page_has_breadcrumb_and_title(self):
        html = self.files["open-source.html"]
        self.assertIn('class="breadcrumb"', html)
        self.assertIn("<title>开源贡献 |", html)

    def test_open_source_entry_shows_index_role_and_prs(self):
        html = self.files["open-source.html"]
        self.assertIn("01", html)
        self.assertIn("贡献者", html)
        self.assertIn("#7 fix ↗", html)
        self.assertIn("全部记录 ↗", html)

    def test_contact_copy_button_carries_value(self):
        html = self.files["index.html"]
        self.assertIn('data-copy="ada@example.org"', html)

    def test_escapes_html_in_user_content(self):
        data = dict(SPEC_DATA)
        data["home"] = {**SPEC_DATA["home"], "title": "<script>alert(1)</script>"}
        files = build_site.build_site(data)
        self.assertNotIn("<script>alert(1)</script>", files["index.html"])
        self.assertIn("&lt;script&gt;", files["index.html"])


class ThemeTests(unittest.TestCase):
    def test_css_uses_shadcn_semantic_tokens(self):
        css = build_site.build_site(SPEC_DATA)["assets/site.css"]
        for token in ("--background", "--foreground", "--card", "--primary", "--muted", "--accent", "--border", "--ring", "--radius"):
            self.assertIn(token, css)

    def test_css_has_dark_mode_override(self):
        css = build_site.build_site(SPEC_DATA)["assets/site.css"]
        self.assertIn(".dark {", css)

    def test_theme_preset_changes_link_color(self):
        neutral = build_site.build_site({**SPEC_DATA, "theme": {"preset": "shadcn-neutral"}})["assets/site.css"]
        runoob = build_site.build_site({**SPEC_DATA, "theme": {"preset": "runoob-classic"}})["assets/site.css"]
        self.assertNotEqual(neutral, runoob)
        self.assertIn("#2f69d4", runoob)

    def test_body_carries_preset_class(self):
        for preset in ("hybrid", "shadcn-neutral", "runoob-classic"):
            files = build_site.build_site({**SPEC_DATA, "theme": {"preset": preset}})
            self.assertIn(f'class="preset-{preset}"', files["index.html"])

    def test_presets_differ_visually(self):
        css = build_site.build_site(SPEC_DATA)["assets/site.css"]
        for preset in ("shadcn-neutral", "runoob-classic"):
            self.assertIn(f"body.preset-{preset}", css)

    def test_css_has_no_unreplaced_placeholders(self):
        css = build_site.build_site(SPEC_DATA)["assets/site.css"]
        self.assertNotIn("@PRIMARY@", css)
        self.assertNotIn("@LINK@", css)
        self.assertNotIn("@RADIUS@", css)

    def test_unknown_preset_is_rejected_by_cli(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            spec_path = Path(temp_dir) / "site.json"
            spec_path.write_text(json.dumps({**SPEC_DATA, "theme": {"preset": "nope"}}), encoding="utf-8")
            code = build_site.main(["--spec", str(spec_path), "--out", str(Path(temp_dir) / "out")])
        self.assertEqual(code, 2)

    def test_missing_spec_file_returns_error_code(self):
        self.assertEqual(build_site.main(["--spec", "definitely-missing.json", "--out", "out"]), 2)


RSS_XML = """<?xml version="1.0"?>
<rss version="2.0"><channel><title>Blog</title>
<item><title>第一篇：Agent 运行时边界</title><link>https://example.org/p1</link><pubDate>Mon, 05 Oct 2026 10:00:00 +0800</pubDate></item>
<item><title>第二篇：Windows 上的并发陷阱</title><link>https://example.org/p2</link><pubDate>Sun, 04 Oct 2026 10:00:00 +0800</pubDate></item>
</channel></rss>"""


class RssTests(unittest.TestCase):
    def test_parses_items_from_rss(self):
        posts = build_site.parse_rss(RSS_XML)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]["title"], "第一篇：Agent 运行时边界")
        self.assertEqual(posts[0]["url"], "https://example.org/p1")

    def test_returns_empty_on_broken_xml(self):
        self.assertEqual(build_site.parse_rss("not xml"), [])

    def test_learning_page_renders_blog_card(self):
        data = {**SPEC_DATA, "learning": {"blog": {"title": "我的博客", "url": "https://example.org/blog"}}}
        html = build_site.build_site(data, fetch_posts=False)["learning.html"]
        self.assertIn("我的博客", html)
        self.assertIn("打开博客 ↗", html)

    def test_rss_posts_are_listed_on_learning_page(self):
        data = {**SPEC_DATA, "learning": {"blog": {"title": "博客", "url": "https://example.org/blog", "rss": "https://example.org/rss.xml"}}}
        with unittest.mock.patch.object(build_site, "fetch_rss", return_value=build_site.parse_rss(RSS_XML)):
            html = build_site.build_site(data)["learning.html"]
        self.assertIn("第一篇：Agent 运行时边界", html)
        self.assertIn("https://example.org/p1", html)

    def test_nojekyll_is_emitted(self):
        self.assertIn(".nojekyll", build_site.build_site(SPEC_DATA))


class HybridPresetTests(unittest.TestCase):
    def test_hybrid_keeps_runoob_links_and_shadcn_radius(self):
        css = build_site.build_site({**SPEC_DATA, "theme": {"preset": "hybrid"}})["assets/site.css"]
        self.assertIn("body.preset-hybrid", css)
        self.assertIn("text-underline-offset", css)
        self.assertIn("--radius: 0.5rem", css)


NEON_SPEC = {
    **SPEC_DATA,
    "site": {"title": "Ada | Runtime", "brand": "Ada", "initials": "AD", "handle": "@ada"},
    "theme": {"preset": "neon-bento"},
    "home": {
        "hero": {"tagline": "Ready to ship", "title": "消灭静默", "highlight": "失败。", "bio": "你好"},
        "meta": {"name": "Ada", "handle": "@ada", "chips": ["🎓 学生"]},
        "focus": {"title": "⚡ 方向", "text": "让链条不假死、零静默抛错", "highlight": "零静默抛错", "pills": ["Agent"]},
        "highlights": {"title": "🏆 数据", "items": [{"icon": "⭐", "title": "45 PR", "desc": "上游"}]},
        "contact": {"title": "随时碰个头！", "text": "戳我", "items": [{"icon": "💬", "label": "微信", "value": "123", "copy": True}]},
    },
}


class NeonBentoTests(unittest.TestCase):
    def setUp(self):
        self.files = build_site.build_site(NEON_SPEC)

    def test_builds_bento_pages(self):
        for name in ("index.html", "open-source.html", "projects.html", "learning.html"):
            self.assertIn(name, self.files)

    def test_home_uses_bento_grid(self):
        html = self.files["index.html"]
        self.assertIn('class="bento-grid"', html)
        self.assertIn("card card-hero", html)
        self.assertIn("card card-meta", html)
        self.assertIn("card card-focus", html)
        self.assertIn("card card-highlights", html)
        self.assertIn("card card-contact", html)

    def test_css_matches_reference_design_tokens(self):
        css = self.files["assets/site.css"]
        for token in ("--bg: #0b0f17", "--accent-neon: #00f2fe", "--accent-lime: #a3e635", "--radius: 20px"):
            self.assertIn(token, css)
        self.assertIn("backdrop-filter: blur(12px)", css)
        self.assertIn("grid-template-columns: repeat(12, 1fr)", css)

    def test_contact_items_render_text_and_copy(self):
        html = self.files["index.html"]
        self.assertIn("💬 微信 123", html)
        self.assertIn('data-copy-value="123"', html)

    def test_js_has_toast_copy(self):
        js = self.files["assets/site.js"]
        self.assertIn("copyText", js)
        self.assertIn("toast", js)

    def test_inner_page_contact_button_points_home(self):
        self.assertIn('href="index.html#contact"', self.files["projects.html"])


class EditableContentTests(unittest.TestCase):
    def setUp(self):
        self.files = build_site.build_site(NEON_SPEC)

    def test_content_js_is_emitted_with_editable_data(self):
        content = self.files["assets/content.js"]
        self.assertIn("window.SITE_CONTENT", content)
        self.assertIn("home", content)
        self.assertIn("open_source", content)
        self.assertIn("projects", content)
        self.assertIn("learning", content)

    def test_pages_load_content_js_before_site_js(self):
        html = self.files["index.html"]
        self.assertLess(html.index("assets/content.js"), html.index("assets/site.js"))

    def test_editable_nodes_carry_data_bind(self):
        html = self.files["index.html"]
        for path in ("home.hero.title", "home.hero.bio", "home.meta.name", "home.focus.title", "home.contact.title"):
            self.assertIn(f'data-bind="{path}"', html)

    def test_lists_carry_data_list(self):
        html = self.files["index.html"]
        for path in ("home.hero.actions", "home.meta.chips", "home.focus.pills", "home.contact.items"):
            self.assertIn(f'data-list="{path}"', html)
        self.assertIn('data-list="open_source.entries"', self.files["open-source.html"])
        self.assertIn('data-list="projects.items"', self.files["projects.html"])
        self.assertIn('data-list="learning.items"', self.files["learning.html"])

    def test_runtime_js_renders_lists_and_binds(self):
        js = self.files["assets/site.js"]
        self.assertIn("SITE_CONTENT", js)
        self.assertIn("data-bind", js)
        self.assertIn("data-list", js)
        self.assertIn("open_source.entries", js)


class StructureBalanceTests(unittest.TestCase):
    """回归：包裹层必须闭合，否则 Bento 网格会塌成一列。"""

    def _main_of(self, html: str) -> str:
        return html.split('<main class="bento-grid">', 1)[1].split("</main>", 1)[0]

    def test_generated_pages_have_balanced_divs(self):
        files = build_site.build_site(NEON_SPEC)
        for name in ("index.html", "open-source.html", "projects.html", "learning.html"):
            main = self._main_of(files[name])
            self.assertEqual(
                main.count("<div"),
                main.count("</div>"),
                f"{name} 的 div 标签不配对",
            )

    def test_learning_page_has_single_list_wrapper(self):
        html = build_site.build_site(NEON_SPEC)["learning.html"]
        self.assertEqual(html.count('data-list="learning.items"'), 1)
        self.assertNotIn('data-list="projects.items"', html)

    def test_projects_page_has_single_list_wrapper(self):
        html = build_site.build_site(NEON_SPEC)["projects.html"]
        self.assertEqual(html.count('data-list="projects.items"'), 1)
        self.assertNotIn('data-list="learning.items"', html)

    def test_blog_page_is_named_personal_blog(self):
        files = build_site.build_site(NEON_SPEC)
        self.assertIn("个人博客", files["learning.html"])
        self.assertIn("个人博客", files["index.html"])


class LiveDataTests(unittest.TestCase):
    def test_live_row_is_rendered_with_data_live_markers(self):
        spec = {
            **NEON_SPEC,
            "home": {
                **NEON_SPEC["home"],
                "live": [{"key": "mergedPRs", "label": "个已合并上游 PR", "value": "45"}],
            },
        }
        html = build_site.build_site(spec)["index.html"]
        self.assertIn('data-live="mergedPRs"', html)
        self.assertIn("个已合并上游 PR", html)

    def test_content_js_carries_github_username(self):
        content = build_site.build_site({**NEON_SPEC, "username": "ada"})["assets/content.js"]
        self.assertIn('"github"', content)
        self.assertIn('"username": "ada"', content)

    def test_runtime_js_queries_github_api(self):
        js = build_site.build_site(NEON_SPEC)["assets/site.js"]
        self.assertIn("api.github.com", js)
        self.assertIn("is:pr author:", js)
        self.assertIn("data-live", js)

    def test_copy_button_uses_data_attributes_not_inline_js(self):
        html = build_site.build_site(NEON_SPEC)["index.html"]
        self.assertIn("data-copy-value=", html)
        self.assertNotIn("onclick=", html)


class StackMatrixTests(unittest.TestCase):
    def test_stack_groups_render_on_projects_page(self):
        spec = {
            **NEON_SPEC,
            "projects": {
                **NEON_SPEC["projects"],
                "stack": {"title": "技术栈矩阵", "groups": [{"label": "AGENT", "items": ["LangGraph"]}]},
            },
        }
        html = build_site.build_site(spec)["projects.html"]
        self.assertIn('data-list="projects.stack.groups"', html)
        self.assertIn("技术栈矩阵", html)


HUD_SPEC = {
    "username": "ada",
    "theme": {"preset": "hud"},
    "site": {
        "title": "Ada | Agent Ops",
        "brand": "杜凯峰",
        "brand_tag": "AGENT OPS",
        "status": "OPEN TO WORK",
        "tz": "UTC+8",
        "stats": [["MERGED PRs", "45"]],
        "contact": [{"label": "Email", "text": "ada@example.org", "value": "ada@example.org"}],
    },
    "home": {
        "hero": {"tagline": "AGENT ENGINEER", "title": "用确定性工程", "highlight": "驯化不确定性。", "bio": "bio"},
        "live": [{"key": "mergedPRs", "label": "个已合并上游 PR", "value": "45"}],
        "highlights": {"title": "数据", "items": [{"icon": "⭐", "title": "45 PR", "desc": "上游"}]},
    },
    "projects": {
        "items": [{"name": "CoreCoder", "code": "TS", "summary": "s", "metrics": ["4013 TESTS"], "tags": ["t"]}],
        "stack": {"groups": [{"label": "AGENT", "items": ["LangGraph"]}]},
        "chrono": [{"period": "2026.09–", "title": "deer-flow", "detail": "45 PR"}],
    },
    "learning": {"items": [{"title": "文章", "url": "https://example.org/p", "date": "2026-11"}]},
    "terminal": {"lines": [{"text": "> whoami", "tone": "ok"}]},
}


class HudPresetTests(unittest.TestCase):
    def setUp(self):
        self.files = build_site.build_site(HUD_SPEC)

    def test_generates_five_sections_plus_assets(self):
        for name in ("index.html", "missions.html", "arsenal.html", "blog.html", "terminal.html"):
            self.assertIn(name, self.files)
        self.assertIn("assets/site.css", self.files)
        self.assertIn("assets/content.js", self.files)

    def test_uses_reference_design_tokens(self):
        css = self.files["assets/site.css"]
        for token in ("--bg-void: #05070a", "--accent-cyan: #00f0ff", "--accent-red: #ff2a4a", "--cut-sm:", "--font-mono:"):
            self.assertIn(token, css)

    def test_layout_has_hud_bar_sidebar_and_viewport(self):
        html = self.files["index.html"]
        self.assertIn('class="hud"', html)
        self.assertIn('class="sidebar"', html)
        self.assertIn('class="viewport"', html)
        self.assertIn("scanlines", html)

    def test_sidebar_nav_is_numbered(self):
        html = self.files["index.html"]
        for idx in ("01", "02", "03", "04", "05"):
            self.assertIn(f'class="nav-idx">{idx}<', html)

    def test_live_metrics_are_marked(self):
        html = self.files["index.html"]
        self.assertIn('data-live="mergedPRs"', html)

    def test_sections_render_content(self):
        self.assertIn("CoreCoder", self.files["missions.html"])
        self.assertIn("LangGraph", self.files["arsenal.html"])
        self.assertIn("deer-flow", self.files["arsenal.html"])
        self.assertIn("文章", self.files["blog.html"])
        self.assertIn("whoami", self.files["terminal.html"])

    def test_terminal_lines_carry_tone(self):
        self.assertIn('class="ok"', self.files["terminal.html"])


class ScriptTests(unittest.TestCase):
    def test_js_handles_theme_toggle_and_copy(self):
        js = build_site.build_site(SPEC_DATA)["assets/site.js"]
        self.assertIn("data-theme-toggle", js)
        self.assertIn("data-copy", js)
        self.assertIn("prefers-color-scheme: dark", js)


if __name__ == "__main__":
    unittest.main()
