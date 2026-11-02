#!/usr/bin/env python3
"""自检个人主页 README：占位符残留、主题覆盖、表格结构、链接与组件配比。

用法:
    python3 check_profile_readme.py README.md
    python3 check_profile_readme.py README.md --username <github-handle> --strict

退出码:
    0  没有错误（可能有警告）
    1  存在错误
    2  文件不可读或参数错误

脚本只做静态检查，不访问网络。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER_PATTERNS = (
    (r"\{\{[^{}\n]+\}\}", "模板占位符未替换"),
    (r"<your[-_][A-Za-z0-9_-]*>", "占位链接未替换"),
    (r"\bYOUR_[A-Z_]+\b", "占位变量未替换"),
    (r"\bTODO\b", "残留 TODO"),
    (r"\bFIXME\b", "残留 FIXME"),
    (r"(?<![@\w.-])example\.com", "示例域名未替换"),
    (r"your[-_]username", "示例用户名未替换"),
    (r"你的用户名|请替换|待填写|待补充", "中文占位提示未替换"),
)

DYNAMIC_HOSTS = (
    "github-readme-stats",
    "streak-stats",
    "komarev.com/ghpvc",
    "github-profile-views-counter",
    "activity-graph",
    "github-readme-language-stats",
    "github-readme-recent-activity",
)

DEPRECATED_HOSTS = (
    "readme-typing-svg",
    "github-profile-trophy",
    "giphy.com",
)

IMAGE_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
WIDTH_RE = re.compile(r'width\s*=\s*["\']?(\d+)%', re.IGNORECASE)
PIXEL_WIDTH_RE = re.compile(r'width\s*=\s*["\'](\d+)["\']', re.IGNORECASE)
ALT_RE = re.compile(r'alt\s*=\s*["\']', re.IGNORECASE)
SRC_RE = re.compile(r'src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
PICTURE_RE = re.compile(r"<picture\b.*?</picture>", re.IGNORECASE | re.DOTALL)
SOURCE_RE = re.compile(r"<source\b[^>]*>", re.IGNORECASE)
MEDIA_RE = re.compile(r'media\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SHIELDS_RE = re.compile(r"https://img\.shields\.io/[^)\s\"']+", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
GITHUB_REPO_RE = re.compile(r"github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]*))/(?:([A-Za-z0-9_.-]+))")


class Issue:
    __slots__ = ("level", "line", "message")

    def __init__(self, level: str, line: int, message: str) -> None:
        self.level = level
        self.line = line
        self.message = message

    def __str__(self) -> str:
        return f"{self.level.upper():7} 行 {self.line:>4}: {self.message}"


def _is_fence_line(line: str) -> bool:
    return line.lstrip().startswith("```") or line.lstrip().startswith("~~~")


def _table_cell_count(line: str) -> int:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return len(stripped.split("|"))


def _is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells)


def check_placeholders(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if _is_fence_line(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for pattern, label in PLACEHOLDER_PATTERNS:
            match = re.search(pattern, line)
            if match:
                issues.append(Issue("error", number, f"{label}：{match.group(0)!r}"))
    return issues


def check_images(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    in_fence = False
    pixel_widths: dict[int, int] = {}
    percent_widths: dict[int, int] = {}
    for number, line in enumerate(lines, start=1):
        if _is_fence_line(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        tags = IMAGE_TAG_RE.findall(line)
        line_widths = [int(value) for value in WIDTH_RE.findall(line)]
        if len(line_widths) > 1 and len(set(line_widths)) > 1:
            issues.append(Issue("warn", number, f"同一行的图片宽度不一致：{line_widths}，并排卡片应统一宽度"))
        for tag in tags:
            if not ALT_RE.search(tag):
                issues.append(Issue("error", number, f"图片缺少 alt 属性：{tag[:80]}"))
            width = WIDTH_RE.search(tag)
            if width:
                percent_widths.setdefault(int(width.group(1)), number)
            pixel = PIXEL_WIDTH_RE.search(tag)
            if pixel:
                pixel_widths.setdefault(int(pixel.group(1)), number)
        if len(tags) > 12:
            issues.append(Issue("warn", number, f"单行 {len(tags)} 张图片，视觉密度过高（技术栈图标建议控制在 12 个以内）"))
        if len(SHIELDS_RE.findall(line)) > 6:
            issues.append(Issue("warn", number, "单行 shields 徽章超过 6 个，建议只保留联系方式类徽章"))
    if len(pixel_widths) > 1:
        issues.append(
            Issue("warn", min(pixel_widths.values()), f"图标尺寸不统一：{sorted(pixel_widths)}，同一组图标应使用同一尺寸")
        )
    if 49 in percent_widths and 50 in percent_widths:
        issues.append(
            Issue("warn", min(percent_widths[49], percent_widths[50]), "并排卡片同时出现 49% 与 50% 宽度，请统一")
        )
    unusual = sorted(value for value in percent_widths if value not in (100, 50, 49))
    if unusual:
        issues.append(
            Issue("warn", percent_widths[unusual[0]], f"百分比宽度 {unusual} 建议只用 100%（整宽）、50% 或 49%（并排）")
        )
    return issues


def check_pictures(text: str) -> list[Issue]:
    """检查跨行的 <picture> 块是否同时提供深色与浅色源。"""
    issues: list[Issue] = []
    for match in PICTURE_RE.finditer(text):
        block = match.group(0)
        number = text[: match.start()].count("\n") + 1
        medias = []
        for source in SOURCE_RE.findall(block):
            media = MEDIA_RE.search(source)
            medias.append(media.group(1).lower() if media else "")
        has_dark = any("dark" in media for media in medias)
        has_light = any("light" in media for media in medias)
        if not (has_dark and has_light):
            issues.append(
                Issue("error", number, "picture 缺少浅色/深色双主题源，GitHub 会按系统主题显示错误配色")
            )
        img = IMAGE_TAG_RE.findall(block)
        if img and not ALT_RE.search(img[0]):
            issues.append(Issue("error", number, "picture 内的兜底 img 缺少 alt 属性"))
    return issues


def check_tables(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if _is_fence_line(line):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence or not line.strip().startswith("|"):
            index += 1
            continue
        block_start = index
        block: list[tuple[int, str]] = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            block.append((index + 1, lines[index]))
            index += 1
        if len(block) < 2 or not _is_table_separator(block[1][1]):
            issues.append(Issue("error", block_start + 1, "表格缺少 `| --- |` 分隔行，GitHub 不会渲染成表格"))
            continue
        expected = _table_cell_count(block[0][1])
        if expected < 2:
            issues.append(Issue("error", block[0][0], "表格至少需要两列"))
        for line_number, row in block:
            actual = _table_cell_count(row)
            if actual != expected:
                issues.append(
                    Issue("error", line_number, f"表格列数不一致：表头 {expected} 列，本行 {actual} 列")
                )
    return issues


def check_links(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if _is_fence_line(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in MARKDOWN_LINK_RE.findall(line):
            if target.startswith("http://"):
                issues.append(Issue("warn", number, f"外链仍是 http://{target[len('http://'):][:60]}，建议改 https"))
        for tag in IMAGE_TAG_RE.findall(line):
            src = SRC_RE.search(tag)
            if src and src.group(1).startswith("http://"):
                issues.append(Issue("warn", number, "图片仍使用 http:// 源，GitHub 会阻断混合内容"))
    return issues


def check_components(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    dynamic = 0
    for number, line in enumerate(lines, start=1):
        lowered = line.lower()
        for host in DEPRECATED_HOSTS:
            if host in lowered:
                issues.append(Issue("warn", number, f"使用了廉价/易失效组件（{host}），建议替换为静态徽章或表格"))
        for host in DYNAMIC_HOSTS:
            if host in lowered:
                dynamic += 1
    if dynamic > 2:
        issues.append(Issue("warn", 0, f"共 {dynamic} 处动态数据卡，建议不超过 2 处，避免首屏变成图片墙"))
    return issues


def check_self_links(lines: list[str], username: str) -> list[Issue]:
    issues: list[Issue] = []
    target = username.lower()
    for number, line in enumerate(lines, start=1):
        for owner, repo in GITHUB_REPO_RE.findall(line):
            if repo and repo.lower() == target and owner.lower() != target:
                issues.append(
                    Issue("error", number, f"自指仓库链接的 owner 是 {owner}，与用户名 {username} 不一致")
                )
    return issues


def check_readme_shape(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    body = [line for line in lines if line.strip()]
    if len(body) < 10:
        issues.append(Issue("warn", 0, "正文内容过少，主页信息量不足"))
    return issues


def analyze(text: str, username: str | None) -> list[Issue]:
    lines = text.splitlines()
    issues: list[Issue] = []
    issues += check_placeholders(lines)
    issues += check_images(lines)
    issues += check_pictures(text)
    issues += check_tables(lines)
    issues += check_links(lines)
    issues += check_components(lines)
    issues += check_readme_shape(lines)
    if username:
        issues += check_self_links(lines, username)
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查个人主页 README")
    parser.add_argument("readme", help="README 文件路径")
    parser.add_argument("--username", default=None, help="GitHub 用户名，用于校验自指仓库链接")
    parser.add_argument("--strict", action="store_true", help="把警告也视为失败")
    args = parser.parse_args(argv)

    path = Path(args.readme)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"无法读取 {path}：{exc}", file=sys.stderr)
        return 2

    issues = analyze(text, args.username)
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warn"]
    for issue in sorted(issues, key=lambda item: (item.level != "error", item.line)):
        print(issue)

    print(f"\n检查完成：{len(errors)} 个错误，{len(warnings)} 个警告。")
    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
