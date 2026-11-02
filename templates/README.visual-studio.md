<!--
  使用前删除本注释块（自检会把注释里的说明文字判为占位残留）。
  范式 B · 视觉设计型
  用法：
  1. 把 {{占位符}} 替换为真实内容；
  2. 在仓库 assets/ 下放 hero-light.svg / hero-dark.svg / divider-light.svg / divider-dark.svg；
  3. data-narrative 表里的统计卡可换成自托管 SVG（output/stats-*.svg）；
  4. 运行 python3 scripts/check_profile_readme.py README.md --username <你的用户名>
-->

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img src="assets/hero-light.svg" alt="{{HERO_ALT}}" width="100%">
</picture>

</div>

### ✎ about

- 💼 {{CURRENT_ROLE}}
- 🎓 {{STUDY_OR_TEAM}}
- 🔭 {{CURRENT_FOCUS}}
- 📫 [{{EMAIL}}](mailto:{{EMAIL}})

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/divider-light.svg">
  <img src="assets/divider-light.svg" alt="" width="100%">
</picture>

### ▧ stats <sub>数据速览</sub>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="output/stats-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="output/stats-light.svg">
  <img src="output/stats-light.svg" alt="{{STATS_ALT}}" width="49%">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="output/collaboration-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="output/collaboration-light.svg">
  <img src="output/collaboration-light.svg" alt="{{COLLAB_ALT}}" width="49%">
</picture>

</div>

### ▧ open-source <sub>开源贡献</sub>

| Project | Merged / landed | What it covers |
| :--- | :---: | :--- |
| [{{OWNER}}/{{REPO}}]({{REPO_URL}}) | **{{MERGED_COUNT}}** | {{COVERAGE}} |

**Selected merged PRs**

- **{{REPO}}** — [{{PR_TITLE}} #{{PR_NUMBER}}]({{PR_URL}})

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/footer-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/footer-light.svg">
  <img src="assets/footer-light.svg" alt="{{FOOTER_ALT}}" width="100%">
</picture>

<p align="right"><sub>{{CREDITS}}</sub></p>
