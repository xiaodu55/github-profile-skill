#!/usr/bin/env python3
"""build_intake.py 的聚焦回归测试（全部离线）。"""

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "build_intake.py"
SPEC = importlib.util.spec_from_file_location("build_intake", SCRIPT_PATH)
build_intake = importlib.util.module_from_spec(SPEC)
sys.modules["build_intake"] = build_intake
assert SPEC.loader is not None
SPEC.loader.exec_module(build_intake)


FACTS = {
    "user": {"login": "ada", "name": "Ada Lovelace", "bio": "Building agents"},
    "repos": [
        {"name": "CoreCoder", "stargazers_count": 1885, "description": "engine"},
        {"name": "SmallTool", "stargazers_count": 12, "description": None},
    ],
    "languages": {"Python": 3, "TypeScript": 1},
    "merged_prs": {
        "total": 45,
        "by_repo": [{"repo": "deer-flow", "count": 29, "samples": [{"title": "fix sandbox"}]}],
    },
}


class QuestionnaireTests(unittest.TestCase):
    def setUp(self):
        self.text = build_intake.build_questionnaire("ada", FACTS)

    def test_covers_all_intake_sections(self):
        for heading in (
            "身份与首屏",
            "当前状态",
            "代表项目",
            "上游贡献",
            "专注方向",
            "技术栈",
            "联系方式",
            "版式与视觉",
            "个人网站",
        ):
            self.assertIn(heading, self.text)

    def test_asks_user_to_choose_site_style(self):
        self.assertIn("spec：`theme.preset`", self.text)
        self.assertIn("hybrid", self.text)
        self.assertIn("runoob-classic", self.text)

    def test_prefills_public_facts(self):
        self.assertIn("Building agents", self.text)
        self.assertIn("CoreCoder", self.text)
        self.assertIn("1885", self.text)
        self.assertIn("deer-flow", self_text := self.text)
        self.assertIn("45", self_text)

    def test_marks_fields_that_need_the_user(self):
        self.assertIn("需你补充", self.text)

    def test_maps_questions_to_spec_paths(self):
        self.assertIn("spec：`profile.title`", self.text)
        self.assertIn("spec：`projects[].notes`", self.text)
        self.assertIn("spec：`upstream[].what`", self.text)
        self.assertIn("spec：`social.email`", self.text)
        self.assertIn("spec：`profile.focus_en`", self.text)

    def test_states_that_generation_must_not_skip_intake(self):
        self.assertIn("不要跳过这一步", self.text)

    def test_handles_empty_facts(self):
        text = build_intake.build_questionnaire("newbie", {})
        self.assertIn("公开仓库列表为空", text)
        self.assertIn("公开数据里没有已合并 PR", text)


if __name__ == "__main__":
    unittest.main()
