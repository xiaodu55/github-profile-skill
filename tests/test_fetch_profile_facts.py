#!/usr/bin/env python3
"""fetch_profile_facts.py 的聚焦回归测试（全部离线，接口调用均被替换）。"""

import importlib.util
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "fetch_profile_facts.py"
SPEC = importlib.util.spec_from_file_location("fetch_profile_facts", SCRIPT_PATH)
fetch_profile_facts = importlib.util.module_from_spec(SPEC)
sys.modules["fetch_profile_facts"] = fetch_profile_facts
assert SPEC.loader is not None
SPEC.loader.exec_module(fetch_profile_facts)


def search_page(items, total):
    return {"total_count": total, "items": items}


def pr_item(repo, number, title):
    return {
        "repository_url": f"https://api.github.com/repos/owner/{repo}",
        "title": title,
        "html_url": f"https://github.com/owner/{repo}/pull/{number}",
        "number": number,
        "created_at": "2026-01-01T00:00:00Z",
    }


class MergedPullRequestTests(unittest.TestCase):
    def test_groups_prs_by_repository_and_keeps_total(self):
        pages = [
            search_page(
                [
                    pr_item("alpha", 1, "first"),
                    pr_item("beta", 2, "second"),
                    pr_item("alpha", 3, "third"),
                ],
                total=42,
            ),
            search_page([], total=42),
        ]

        with patch.object(fetch_profile_facts, "api_get", side_effect=[(page, {}) for page in pages]):
            result = fetch_profile_facts.fetch_merged_prs("ada", "")

        self.assertEqual(result["total"], 42)
        self.assertEqual(result["sampled"], 3)
        self.assertEqual(result["by_repo"][0], {"repo": "alpha", "count": 2, "samples": result["by_repo"][0]["samples"]})
        self.assertEqual(result["by_repo"][0]["repo"], "alpha")
        self.assertEqual(result["by_repo"][1]["repo"], "beta")

    def test_keeps_at_most_sample_per_repo(self):
        items = [pr_item("alpha", index, f"pr {index}") for index in range(5)]
        pages = [search_page(items, total=5)]

        with patch.object(fetch_profile_facts, "api_get", side_effect=[(page, {}) for page in pages]):
            result = fetch_profile_facts.fetch_merged_prs("ada", "", sample_per_repo=2)

        self.assertEqual(len(result["by_repo"][0]["samples"]), 2)
        self.assertEqual(result["by_repo"][0]["count"], 5)


class FactsAssemblyTests(unittest.TestCase):
    def test_builds_facts_from_api_responses(self):
        user_payload = {"login": "ada", "name": "Ada Lovelace", "followers": 643}
        repos_payload = [
            {
                "name": "CoreCoder",
                "full_name": "ada/CoreCoder",
                "html_url": "https://github.com/ada/CoreCoder",
                "description": "engine",
                "language": "Python",
                "stargazers_count": 1885,
                "forks_count": 20,
                "topics": ["agent"],
                "updated_at": "2026-10-01T00:00:00Z",
                "fork": False,
            },
            {
                "name": "forked",
                "full_name": "ada/forked",
                "html_url": "https://github.com/ada/forked",
                "description": None,
                "language": "Go",
                "stargazers_count": 1,
                "forks_count": 0,
                "topics": [],
                "updated_at": "2026-09-01T00:00:00Z",
                "fork": True,
            },
        ]
        responses = [
            (user_payload, {}),
            (repos_payload, {}),
            (search_page([], total=0), {}),
        ]

        with patch.object(fetch_profile_facts, "api_get", side_effect=responses):
            facts = fetch_profile_facts.build_facts("ada", "", top=5, deep_languages=False, max_pr_pages=1)

        self.assertEqual(facts["user"]["name"], "Ada Lovelace")
        self.assertEqual([repo["name"] for repo in facts["repos"]], ["CoreCoder"])
        self.assertEqual(facts["languages"], {"Python": 1})
        self.assertEqual(facts["top_repos"][0]["stargazers_count"], 1885)
        self.assertEqual(facts["meta"]["repo_count"], 1)
        self.assertFalse(facts["meta"]["authenticated"])


class RateLimitTests(unittest.TestCase):
    def test_reports_rate_limit_with_token_hint(self):
        error = urllib.error.HTTPError(
            url="https://api.github.com/users/ada",
            code=403,
            msg="rate limited",
            hdrs=None,
            fp=io.BytesIO(b'{"message": "API rate limit exceeded"}'),
        )

        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(fetch_profile_facts.GitHubError) as raised:
                fetch_profile_facts.api_get("/users/ada", "")

        message = str(raised.exception)
        self.assertIn("403", message)
        self.assertIn("GITHUB_TOKEN", message)


if __name__ == "__main__":
    unittest.main()
