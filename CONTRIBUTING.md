# 贡献指南

## 这个仓库是什么

一个独立的 Agent Skill：帮用户把自己的 GitHub 个人主页（`<username>/<username>` 仓库的 README）做得专业、可核验、能长期维护。

它和"填表式 README 生成器"的差别是**先取数、再排版、最后自检**：数据来自公开接口或用户陈述，版面从三套成型的范式里选，交付前跑一遍静态检查。

## 改动原则

- 一个 PR 只解决一件事，不要把新范式、新组件、新脚本混在一次提交里。
- 不要引入第三方依赖。两个脚本只用 Python 标准库，测试必须能离线跑。
- 新增组件时必须同时写清：用途、URL 模板、失效表现、降级方案。
- 新增自检规则时，先写一条会失败的用例，再改实现。
- 不要在示例、模板、测试里写真实用户的邮箱、token 或私密信息。

## 本地验证

```bash
python3 -m unittest discover -s tests -t . -v
```

只有全部用例通过才能提 PR。CI 会在 Ubuntu 和 Windows 上各跑一遍同样的命令。

改动 README 或模板后，额外确认自检脚本对样例仍然零错误：

```bash
python3 scripts/check_profile_readme.py examples/README.data-narrative.example.md --username ada
```

## 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.com/zh-hans/v1.0.0/)：

```text
<type>: <中文简短标题>
```

常用类型：`feat:` 新增能力；`fix:` 修复问题；`docs:` 文档；`test:` 测试；`chore:` 维护。

示例：

```text
feat: 组件目录新增自托管统计卡工作流
fix: 修复占位符检测把邮箱中的 example.com 误判为残留
```

## 报告问题

提 issue 时请写清：你的宿主（Claude Code / Codex / OpenCode / 其它）、触发方式、期望行为、实际行为，以及相关 README 片段。涉及动态卡片失效的，请附上访问时间和返回状态。
