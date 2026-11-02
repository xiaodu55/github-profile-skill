<!--
  使用前删除本注释块（自检会把注释里的说明文字判为占位残留）。
  范式 A · 数据叙事型
  用法：把所有 {{占位符}} 替换为真实内容，删除用不到的整段，再运行
  python3 scripts/check_profile_readme.py README.md --username <你的用户名>
-->

<div align="center">

# Hi, I'm {{NAME}} 👋

**{{ROLE}}** · {{ONE_LINE_FOCUS_EN}}

<p><i>{{ONE_LINE_FOCUS_ZH}}</i></p>

<p>
  <a href="{{WEBSITE_URL}}">{{WEBSITE_LABEL}}</a> ·
  <a href="mailto:{{EMAIL}}">Email</a> ·
  <a href="https://github.com/{{USERNAME}}">GitHub</a>
</p>

</div>

---

## 📊 By the Numbers <sub>数据速览</sub>

| Contributions | Commits | PRs merged | Issues |
| :---: | :---: | :---: | :---: |
| **{{CONTRIBUTIONS}}** | **{{COMMITS}}** | **{{PRS_MERGED}}** | **{{ISSUES}}** |

<i>统计口径：{{SCOPE}} · 截至 {{DATA_DATE}}</i>

## 🚀 Selected Contributions <sub>代表贡献</sub>

| Project | ⭐ | What I did |
| :--- | :---: | :--- |
| [{{OWNER}}/{{REPO}}]({{REPO_URL}}) | {{STARS}} | {{WHAT_I_DID}} |

> 更多仓库与项目说明见下方清单。

## 🔭 What I Focus On <sub>专注方向</sub>

| Direction | What I work on |
| :--- | :--- |
| {{DIRECTION_1}} | {{DIRECTION_1_DETAIL}} |
| {{DIRECTION_2}} | {{DIRECTION_2_DETAIL}} |

## 🧰 Projects <sub>项目清单</sub>

| Area | Project | Stars | Notes |
| :--- | :--- | :---: | :--- |
| {{AREA}} | [{{REPO2}}]({{REPO2_URL}}) | {{STARS2}} | {{NOTES2}} |

## 🤝 Community & More <sub>社区与日常</sub>

- {{COMMUNITY_1}}
- {{COMMUNITY_2}}
- {{HOBBY}}

## 📫 Get in Touch <sub>联系我</sub>

<p align="center">
  <a href="mailto:{{EMAIL}}"><strong>Email</strong></a> ·
  <a href="https://github.com/{{USERNAME}}"><strong>GitHub</strong></a> ·
  <a href="{{LINKEDIN_URL}}"><strong>LinkedIn</strong></a>
</p>

<p align="center"><i>{{CLOSING_LINE}}</i></p>
