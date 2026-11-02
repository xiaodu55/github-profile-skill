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


class ScriptTests(unittest.TestCase):
    def test_js_handles_theme_toggle_and_copy(self):
        js = build_site.build_site(SPEC_DATA)["assets/site.js"]
        self.assertIn("data-theme-toggle", js)
        self.assertIn("data-copy", js)
        self.assertIn("prefers-color-scheme: dark", js)


if __name__ == "__main__":
    unittest.main()
