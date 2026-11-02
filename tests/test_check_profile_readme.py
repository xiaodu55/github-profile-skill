#!/usr/bin/env python3
"""check_profile_readme.py 的聚焦回归测试。"""

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "check_profile_readme.py"
SPEC = importlib.util.spec_from_file_location("check_profile_readme", SCRIPT_PATH)
check_profile_readme = importlib.util.module_from_spec(SPEC)
sys.modules["check_profile_readme"] = check_profile_readme
assert SPEC.loader is not None
SPEC.loader.exec_module(check_profile_readme)


GOOD_README = """<div align="center">

# Hi, I'm Ada Lovelace 👋

**Engineer** · Building reliable agents

</div>

| Repos | PRs merged |
| :---: | :---: |
| **12** | **34** |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img src="assets/hero-light.svg" alt="Hero" width="100%">
</picture>
"""


def errors_of(text: str, username: str | None = None) -> list[str]:
    return [issue.message for issue in check_profile_readme.analyze(text, username) if issue.level == "error"]


def warnings_of(text: str, username: str | None = None) -> list[str]:
    return [issue.message for issue in check_profile_readme.analyze(text, username) if issue.level == "warn"]


class PlaceholderTests(unittest.TestCase):
    def test_reports_template_placeholder(self):
        self.assertTrue(any("占位符" in message for message in errors_of("# {{NAME}}\n\n正文\n")))

    def test_reports_example_domain_and_todo(self):
        messages = errors_of("# A\n\nsee example.com\n\nTODO: write\n")
        self.assertTrue(any("示例域名" in message for message in messages))
        self.assertTrue(any("TODO" in message for message in messages))

    def test_ignores_content_inside_code_fence(self):
        text = "# A\n\n```bash\npython3 tool.py --name {{VALUE}}\n```\n"
        self.assertEqual(errors_of(text), [])

    def test_ignores_example_domain_inside_email_address(self):
        text = "# A\n\nEmail: [me@example.com](mailto:me@example.com)\n"
        self.assertEqual(errors_of(text), [])

    def test_still_reports_example_domain_in_link(self):
        text = "# A\n\n[site](https://example.com/page)\n"
        self.assertTrue(any("示例域名" in message for message in errors_of(text)))


class ImageTests(unittest.TestCase):
    def test_requires_alt_attribute(self):
        messages = errors_of('# A\n\n<img src="https://img.shields.io/badge/x-y-blue">\n')
        self.assertTrue(any("alt" in message for message in messages))

    def test_accepts_empty_alt_for_decorative_image(self):
        text = '# A\n\n<img src="assets/divider-light.svg" alt="" width="100%">\n'
        self.assertEqual(errors_of(text), [])

    def test_warns_on_mixed_side_by_side_widths(self):
        text = (
            "# A\n\n"
            '<img src="https://img.shields.io/a" alt="a" width="49%">\n'
            '<img src="https://img.shields.io/b" alt="b" width="50%">\n'
        )
        self.assertTrue(any("49% 与 50%" in message for message in warnings_of(text)))

    def test_warns_on_mixed_icon_sizes(self):
        text = (
            "# A\n\n"
            '<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="40" height="40">\n'
            '<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg" alt="Go" width="32" height="32">\n'
        )
        self.assertTrue(any("图标尺寸不统一" in message for message in warnings_of(text)))


class PictureTests(unittest.TestCase):
    def test_requires_both_themes_across_lines(self):
        text = (
            "# A\n\n<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="a.svg">\n'
            '  <img src="a.svg" alt="a" width="100%">\n'
            "</picture>\n"
        )
        self.assertTrue(any("双主题" in message for message in errors_of(text)))

    def test_accepts_complete_picture_block(self):
        self.assertEqual(errors_of(GOOD_README), [])


class TableTests(unittest.TestCase):
    def test_reports_column_mismatch(self):
        text = "# A\n\n| A | B |\n| :--- | :--- |\n| only one |\n"
        self.assertTrue(any("列数不一致" in message for message in errors_of(text)))

    def test_reports_missing_separator_row(self):
        text = "# A\n\n| A | B |\n| 1 | 2 |\n"
        self.assertTrue(any("分隔行" in message for message in errors_of(text)))


class LinkTests(unittest.TestCase):
    def test_warns_on_plain_http_link(self):
        text = "# A\n\n[site](http://example.org/page)\n"
        self.assertTrue(any("http://" in message for message in warnings_of(text)))

    def test_reports_self_repo_owner_mismatch(self):
        text = "# A\n\n[me](https://github.com/someone-else/ada)\n"
        messages = errors_of(text, "ada")
        self.assertTrue(any("owner" in message for message in messages))

    def test_accepts_matching_self_repo_owner(self):
        text = "# A\n\n[me](https://github.com/ada/ada)\n"
        self.assertEqual(errors_of(text, "ada"), [])


class ComponentTests(unittest.TestCase):
    def test_warns_on_typing_svg(self):
        text = '# A\n\n<img src="https://readme-typing-svg.demolab.com?text=hi" alt="t">\n'
        self.assertTrue(any("readme-typing-svg" in message for message in warnings_of(text)))

    def test_warns_when_too_many_dynamic_cards(self):
        lines = [
            f'<img src="https://github-readme-stats.vercel.app/api?username=ada&n={index}" alt="stats">'
            for index in range(3)
        ]
        text = "# A\n\n" + "\n".join(lines) + "\n"
        self.assertTrue(any("动态数据卡" in message for message in warnings_of(text)))


class GoodReadmeTests(unittest.TestCase):
    def test_clean_readme_has_no_issues(self):
        issues = check_profile_readme.analyze(GOOD_README, "ada")
        self.assertEqual([issue.message for issue in issues], [])


if __name__ == "__main__":
    unittest.main()
