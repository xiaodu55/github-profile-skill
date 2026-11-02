#!/usr/bin/env python3
"""render_profile_readme.py 的聚焦回归测试（全部离线）。"""

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "render_profile_readme.py"
SPEC = importlib.util.spec_from_file_location("render_profile_readme", SCRIPT_PATH)
render_profile_readme = importlib.util.module_from_spec(SPEC)
sys.modules["render_profile_readme"] = render_profile_readme
assert SPEC.loader is not None
SPEC.loader.exec_module(render_profile_readme)


FACTS = {
    "user": {"login": "ada", "followers": 312},
    "repos": [
        {"name": "CoreCoder", "stargazers_count": 1885, "description": "engine"},
        {"name": "SmallTool", "stargazers_count": 12, "description": "tiny"},
    ],
    "languages": {"Python": 3},
    "merged_prs": {
        "total": 59,
        "by_repo": [{"repo": "deer-flow", "count": 29, "samples": []}],
    },
}


class IconTests(unittest.TestCase):
    def test_skillicons_id_for_known_language(self):
        self.assertEqual(
            render_profile_readme.skill_icon_url("python"),
            "https://skillicons.dev/icons?i=py",
        )

    def test_devicon_fallback_for_missing_skillicons(self):
        self.assertIn("devicons", render_profile_readme.skill_icon_url("oracle"))

    def test_skill_label_uses_proper_naming(self):
        self.assertEqual(render_profile_readme.skill_label("typescript"), "TypeScript")
        self.assertEqual(render_profile_readme.skill_label("golang"), "Go")
        self.assertEqual(render_profile_readme.skill_label("some_thing"), "Some Thing")

    def test_social_icon_uses_simple_icons(self):
        self.assertEqual(
            render_profile_readme.social_icon_url("linkedin"),
            "https://cdn.simpleicons.org/linkedin",
        )

    def test_social_link_uses_platform_template(self):
        self.assertEqual(
            render_profile_readme.social_link("github", "ada"),
            "https://github.com/ada",
        )

    def test_email_uses_mailto_scheme(self):
        self.assertEqual(
            render_profile_readme.social_link("email", "me@example.org"),
            "mailto:me@example.org",
        )

    def test_unknown_social_falls_back_to_path(self):
        self.assertEqual(render_profile_readme.social_link("example", "ada"), "https://example/ada")


class FactsMergeTests(unittest.TestCase):
    def test_fills_missing_star_counts_and_pr_counts(self):
        spec = {
            "username": "ada",
            "projects": [{"name": "CoreCoder"}],
            "upstream": [{"repo": "bytedance/deer-flow"}],
        }
        merged = render_profile_readme.merge_spec(spec, FACTS)

        self.assertEqual(merged["projects"][0]["stars"], 1885)
        self.assertEqual(merged["projects"][0]["notes"], "engine")
        self.assertEqual(merged["upstream"][0]["merged"], 29)

    def test_keeps_user_provided_numbers(self):
        spec = {
            "username": "ada",
            "projects": [{"name": "CoreCoder", "stars": 42, "notes": "手写"}],
            "upstream": [{"repo": "bytedance/deer-flow", "merged": 7}],
        }
        merged = render_profile_readme.merge_spec(spec, FACTS)

        self.assertEqual(merged["projects"][0]["stars"], 42)
        self.assertEqual(merged["projects"][0]["notes"], "手写")
        self.assertEqual(merged["upstream"][0]["merged"], 7)


class RenderTests(unittest.TestCase):
    def test_data_narrative_layout_contains_core_sections(self):
        spec = {
            "username": "ada",
            "layout": "data-narrative",
            "profile": {"title": "Hi, I'm ada", "subtitle": "Engineer"},
            "social": {"github": "ada"},
            "upstream": [{"repo": "bytedance/deer-flow", "merged": 29, "what": "修复"}],
            "focus": [{"direction": "Runtime", "detail": "调度"}],
            "projects": [{"area": "Agent", "name": "CoreCoder", "notes": "引擎"}],
        }
        output = render_profile_readme.render(spec, FACTS)

        self.assertIn("## 📊 By the Numbers", output)
        self.assertIn("| **59** | **1** | **2** | **312** |", output)
        self.assertIn("## 🚀 Selected Contributions", output)
        self.assertIn("## 🔭 What I Focus On", output)
        self.assertIn("## 🧰 Projects", output)
        self.assertIn("[bytedance/deer-flow](https://github.com/bytedance/deer-flow)", output)

    def test_classic_form_layout_uses_about_and_socials(self):
        spec = {
            "username": "ada",
            "layout": "classic-form",
            "profile": {"currentWork": "构建 Agent 平台", "currentLearn": "RAG"},
            "social": {"github": "ada", "linkedin": "ada"},
            "skills": ["python", "docker"],
        }
        output = render_profile_readme.render(spec, FACTS)

        self.assertIn("- 💼 **构建 Agent 平台**", output)
        self.assertIn("Connect with me", output)
        self.assertIn("https://cdn.simpleicons.org/linkedin", output)
        self.assertIn("https://skillicons.dev/icons?i=py", output)

    def test_widgets_are_opt_in(self):
        base = {"username": "ada", "layout": "classic-form"}
        without = render_profile_readme.render(base, FACTS)
        with_widgets = render_profile_readme.render(
            {**base, "widgets": {"github_stats": True}}, FACTS
        )

        self.assertNotIn("github-readme-stats", without)
        self.assertIn("github-readme-stats", with_widgets)

    def test_rejects_unknown_layout(self):
        with self.assertRaises(ValueError):
            render_profile_readme.render({"username": "ada", "layout": "nope"}, FACTS)

    def test_rejects_unknown_section(self):
        with self.assertRaises(ValueError):
            render_profile_readme.render(
                {"username": "ada", "sections": ["hero", "nope"]}, FACTS
            )

    def test_note_becomes_leading_comment(self):
        spec = {"username": "ada", "note": "虚构示例", "layout": "minimal"}
        output = render_profile_readme.render(spec, FACTS)
        self.assertTrue(output.startswith("<!-- 虚构示例 -->"))

    def test_output_has_no_triple_blank_lines(self):
        spec = {"username": "ada", "layout": "minimal", "profile": {"currentWork": "x"}}
        output = render_profile_readme.render(spec, FACTS)
        self.assertNotIn("\n\n\n", output)


if __name__ == "__main__":
    unittest.main()
