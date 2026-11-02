# 个人网站：内容结构与视觉规范

主页 README 是"仓库页"，个人网站是"作品与履历的展开"。两者内容同源，但结构与视觉不同：README 用表格讲成果，网站用分节讲过程。

## 一、页面结构（参照 JasonBuildAI 个人站点）

| 页面 | 文件 | 内容 |
| --- | --- | --- |
| 首页 | `index.html` | 自述段落（身份、城市、学校、专注方向）→ 经历段落 → 数据速览 → 最近在做 → 联系方式（带复制按钮） |
| 开源贡献 | `open-source.html` | 说明段 → **主要贡献**（编号条目：仓库名 + 角色标签 + 工作概述 + 代表 PR 列表 + "全部记录"入口）→ **参与过的仓库**（列表，每项链到该仓库的已合并 PR 搜索）→ **数据说明**（核对自 GitHub、更新时间、未合并不计入） |
| 项目 | `projects.html` | 说明段 → 项目条目（名称 + 标签 + 概述 + 要点） |
| 个人博客 | `learning.html` | 说明段 → 博客卡片（掘金 / RSS）→ 文章条目（标题 + 日期 + 标签 + 摘要） |

要点：

- 每个仓库条目要有**角色标签**（组织成员 / 活跃贡献者 / 核心贡献者），让人一眼知道你在那里的分量。
- 代表 PR 列表最多 3 条，每条写 `#编号 标题 ↗`，"全部记录"链接到该仓库的 PR 搜索页。
- 末尾必须有"数据说明"，写清数据核对来源与截止日期——这是可信度的来源。
- 联系方式支持一键复制（邮箱、微信等），国内用户习惯用 QQ 邮箱，海外用 Gmail，可以两个都给。

## 二、设计令牌（参照 shadcn/ui）

用语义化 CSS 变量，深浅两套共用同一组 token，深色模式在 `.dark` 下覆盖同名变量：

| 令牌 | 作用 |
| --- | --- |
| `--background` / `--foreground` | 页面底色与正文色 |
| `--card` / `--card-foreground` | 卡片面与其上的文字 |
| `--popover` / `--popover-foreground` | 浮层 |
| `--primary` / `--primary-foreground` | 主色（按钮、强调面）与其上文字 |
| `--secondary` / `--secondary-foreground` | 次级填充面 |
| `--muted` / `--muted-foreground` | 弱化面与辅助文字（说明、注释、页脚） |
| `--accent` / `--accent-foreground` | 悬停与选中态 |
| `--destructive` | 危险操作与错误 |
| `--border` / `--input` / `--ring` | 描边、输入框边框、焦点环 |
| `--radius` + 派生尺度 | `--radius-sm` = 0.6×、`--radius-md` = 0.8×、`--radius-lg` = 1×、`--radius-xl` = 1.4×、`--radius-2xl` = 1.8× |

底色用 `oklch()` 表达（shadcn 的中性底色就是 `oklch(0.145 0 0)` 一类的无彩度值），改一个 token 就能整站换肤。

## 三、排版规则（参照菜鸟教程的长文可读性）

- 正文 16px，行高 1.75；内容列宽 `76ch`，页面容器 `1080px`——中文长文在 70ch 左右最舒服。
- 链接用蓝色（`#2f69d4`），悬停变深并加下划线；正文链接不靠颜色深浅区分层级。
- 标题层级清晰：`h1` 页面标题 → `h2` 分节（带一条下边框）→ `h3` 条目标题。
- 代码块：等宽字体、浅灰底、1px 边框、圆角、行高 1.6，横向可滚动。
- 表格：通栏、边框清晰、表头居中。
- 不用花哨动画、不用视差滚动、不用弹窗——内容优先。
- 站点顶栏固定、当前页高亮、二级页面带面包屑。

## 四、四种风格预设

**风格必须问用户选**，不要替用户决定。

| 预设 | 可见差异 | 适合 |
| --- | --- | --- |
| `hud` | **战术终端 HUD**：底色 `#05070a`、切角面板（clip-path）、钛灰描边 + 霓虹青/红/金三色点缀、等宽字体做数据与标签、顶部 HUD 条（状态灯 + 实时数据 + 时钟）、左侧编号导航栏（01 概览 / 02 项目 / 03 武器库 / 04 个人博客 / 05 终端）+ 状态与联系方式 | 想要强终端感、工程感、编号分区的作品集 |
| --- | --- | --- |
| `neon-bento` | **暗底霓虹 Bento**：底色 `#0b0f17` + 双径向光晕、玻璃拟态卡片（半透明 + 1px 描边 + 20px 圆角 + 背景模糊）、霓虹青 `#00f2fe` 强调、胶囊顶栏、12 栏 Bento 网格（Hero 8 栏 + 头像卡 4 栏 + 方向卡 7 栏 + 数据卡 5 栏 + 联系卡 12 栏）、渐变标题、状态呼吸灯、复制后弹 Toast | 想要强烈个人标识、视觉冲击力强 |
| `hybrid`（默认推荐） | **两者混合**：shadcn 的令牌体系与 0.5rem 卡片圆角 + 轻投影，配 runoob 的蓝色链接（带下划线与偏移）、`01/02` 序号、`h2` 分隔线 | 大多数人：干净、现代、信息密度适中 |
| `shadcn-neutral` | 全中性无彩度、链接黑色带下划线、卡片圆角 0.75rem 并带极轻投影、`h2` 无分隔线、当前导航项反白（主色底） | 喜欢极简克制的技术风 |
| `runoob-classic` | 15px 字号、顶栏不吸顶、卡片直角、条目无序号、`h1` 下有分隔线、链接全部带下划线、标签方角 | 偏教程/文档气质、信息量大 |

`hybrid` / `shadcn-neutral` / `runoob-classic` 共用同一套"文档式"页面结构，只改 CSS 变量与 `<body class="preset-xxx">` 下的排版差异；`neon-bento` 换的是**页面结构本身**（Bento 网格卡片），实现放在 `scripts/neon_style.py`。

### HUD 版式的 spec 字段

| 字段 | 作用 |
| --- | --- |
| `site.brand` / `brand_tag` / `brand_sub` | 侧栏品牌区（名字 / 标签 / 副信息） |
| `site.hud_status` / `tz` / `status` | 顶栏状态（ONLINE）、时区、侧栏底部状态（如 OPEN TO WORK） |
| `site.stats[]` | 侧栏统计行（`[标签, 值]`） |
| `site.contact[]` | 侧栏联系方式（有 `href` 是链接，否则可复制） |
| `home.hero.paragraphs[]` | 概览正文（多段） |
| `home.live[]` | 概览指标条 + 顶栏实时数据（同一个 key 两处都显示） |
| `home.operator{}` | 首屏的操作者档案行（`OPERATOR` / `ROLE` / `BASE` / `STATUS` 等键值对） |
| `home.signals[]` | 雷达卡下方的信号行（`key` + `text`） |
| `home.milestones[]` | 近期里程碑（`when` / `what` / `why`） |
| `projects.items[].code` / `.metrics[]` | 项目卡的编号标签与指标胶囊 |
| `projects.stack.groups[]` | 武器库技术栈表（分组 → 条目） |
| `projects.chrono[]` | 经历线（`period` / `title` / `detail`） |
| `learning.items[]` | 个人博客条目（标题 / 链接 / 日期 / 标签 / 摘要 / `views` 阅读量） |
| `learning.stats[]` | 博客页顶部统计（`[标签, 值]`） |
| `learning.platforms` | 平台说明句 |
| `learning.cta` | 订阅面板（`text` / `url`） |
| `terminal.lines[]` | 终端面板输出（`text` / `tone`：ok / warn / err） |
| `terminal.commands{}` | 终端可输入的命令 → 回复文本（键名即命令，如 `help` / `whoami` / `status`） |
| `boot_lines[]` | 启动序列逐行文案（可用 `<b>` 强调） |
| `i18n.zh` / `i18n.en` | 双语词典，键是 `data-bind` 路径（如 `home.hero.title`、`nav.overview.label`） |

HUD 版式带的交互：**启动序列**（按 `boot_lines` 逐行打印 + 进度条，完成后淡出移除）——**进站播一次、站内切页不重播**：`sessionStorage` 里记 `hud_booted` 与时间戳，30 分钟内再进站也不再播（站内切页当然不播）；想再看一次，点侧栏品牌名会带 `#reboot` 强制重播；同时 `<head>` 里有一段同步脚本直接给 `<html>` 加 `no-boot` 类，切页不会闪黑屏、**神经网络背景 canvas**（粒子连线）、**雷达扫描 canvas**（带方位角读数）、**双语切换**（顶栏 `ZH / EN` 按钮，按 `i18n` 词典替换 `data-bind` 文本）、**可输入终端**（回车执行 `terminal.commands`，`clear` 清屏）、**音频引擎**（WebAudio 合成的低频环境垫 + 悬停/点击短音，顶栏 `🔊 ON/OFF` 可关；浏览器自动播放策略要求首次交互后才真正出声，切页点击会先响一声再跳转）。

### 霓虹 Bento 的 spec 字段

除了通用字段，霓虹版多用这几组：

| 字段 | 作用 |
| --- | --- |
| `site.initials` | 头像圆环里的缩写（如 `XD`） |
| `site.handle` | 头像卡下方的 `@账号` |
| `site.logo_href` | 顶栏 Logo 链到的地址 |
| `home.hero.tagline` / `title` / `highlight` | 首屏小标签、标题、渐变高亮片段 |
| `home.hero.actions[]` | 首屏按钮（`primary` 为白底主按钮） |
| `home.meta.chips[]` | 头像卡下的小标签 |
| `home.focus.pills[]` | 方向卡的 `# 标签` 药丸 |
| `home.highlights.items[]` | 数据卡的图标 + 标题 + 说明 |
| `home.contact.items[]` | 联系卡条目（`icon` / `label` / `value` / `href` / `copy`） |

## 五、动态数据

站点有两种"动态"：

1. **实时（浏览器端）**：`home.live[]` 里声明的指标，页面打开时直接向 GitHub 公开接口取值并替换：

   ```json
   "live": [
     { "key": "mergedPRs", "label": "个已合并上游 PR", "value": "45" },
     { "key": "repoCount", "label": "个公开仓库", "value": "27" },
     { "key": "totalStars", "label": "总 Star", "value": "1" },
     { "key": "followers", "label": "关注者", "value": "10" }
   ]
   ```

   可用 key：`mergedPRs`（已合并 PR 总数）、`repoCount`（公开仓库数，含 fork）、`totalStars`（所有仓库 star 之和）、`topRepoStars`（最高 star）、`followers`、`publicRepos`、`publicGists`。`value` 是兜底值（接口失败时显示），会被实时值覆盖。

   注意口径：`repoCount` 取自 `users/{u}/repos`，**包含 fork**；"自建非 fork 仓库"要用构建时抓的事实，静态写在文案里。

2. **定时（构建时）**：`templates/site-refresh-workflow.yml` 是 GitHub Actions 模板，放进站点仓库后每天抓一次 GitHub 公开数据、重新渲染并提交，站点内容自动保鲜。

博客文章（掘金等）**抓不到就手填**：这些平台普遍有反爬，普通 HTTP 请求只会拿到空壳，需要真实浏览器或 RSS；把文章写进 `content.js` 的 `learning.items` 即可。

## 六、自己编辑站点内容（不重新生成）

生成器会额外写一个 **`assets/content.js`**：

```js
// 站点内容文件：改这里就能改网站，不用重新生成。
window.SITE_CONTENT = {
  "home": { "hero": { "title": "...", "bio": "..." }, ... },
  "open_source": { "entries": [...] },
  "projects": { "items": [...] },
  "learning": { "items": [...] }
};
```

页面里每个可编辑节点都带 `data-bind="路径"` 或 `data-list="路径"`，`site.js` 载入 `content.js` 后按路径覆盖：

- **改文案**：改 `content.js` 里对应的字符串，保存、刷新页面即可；
- **改列表**：改 `content.js` 里的数组（开源贡献条目、项目、学习笔记），页面会整体重建；
- **不动代码**：需要新样式时才重新跑生成器；日常只改 `content.js`。

这样分工清晰：**生成器负责结构与视觉，`content.js` 负责内容**。没有 JS 时页面仍然显示生成时烘焙好的内容（不依赖 JS 也能看）。

## 六、个人博客页放博客内容

博客页不写正文，只做**索引**：顶部一张博客卡片（标题 + 链接 + 简介），下面列出已发布文章。

文章列表优先从掘金等平台的公开页面抓取（用浏览器渲染，普通 HTTP 请求会拿到反爬空壳）；抓不到再由用户手填。

- `learning.blog.url`：博客地址
- `learning.blog.rss`：RSS 地址；填了就会在生成时抓取最近若干篇的标题、链接与日期，列在页面上
- `learning.blog.limit`：最多列几篇（默认 8）
- `learning.items[]`：手写条目（不接 RSS 时的补充）

抓取失败不阻断生成——博客暂时取不到就只保留卡片。命令行加 `--no-rss` 可以完全跳过抓取（离线或 CI 里用）。

## 八、要不要问用户的站点问题

在采集问卷里新增"个人网站"一组：

- 要不要做个人网站？（不要就跳过整个站点分支）
- 要哪几页？（首页 / 开源贡献 / 项目 / 学习笔记）
- 风格预设选哪个？（给出三个预设的直观描述与链接）
- 主色与圆角要不要改？（默认蓝色 + 0.5rem）
- 联系方式要不要一键复制？
- 部署到哪？（`<user>.github.io` 独立仓库 / 主页仓库的 `docs/` 目录）

## 九、部署

两种常见方式，都不需要构建工具：

1. **独立仓库 `<user>.github.io`**：新建仓库（名字必须正好是 `<用户名>.github.io`），把生成目录里的文件放仓库根，Settings → Pages → Source 选 `main` 分支、根目录。生成器已经会写好 `.nojekyll`，避免 Pages 走 Jekyll 解析。
2. **主页仓库的 `docs/`**：把生成目录放进 `<user>/<user>` 仓库的 `docs/`，Pages 的 Source 选 `main` 分支、`/docs`。

两种方式下站内链接都是相对路径（`open-source.html`），无需改。

独立仓库的完整步骤：

```bash
cd site
git init -b main
git add .
git commit -m "docs: 更新个人站点"
gh repo create xiaodu55.github.io --public --source=. --remote=origin --push
# 然后到仓库 Settings → Pages → Build and deployment → Source 选 Deploy from a branch
# 分支 main，目录 / (root)，保存后等一两分钟
```

## 十、注意事项

- 站点是静态 HTML + 一份 CSS + 一份 JS，零依赖、零构建，10 年后照样能打开。
- 所有数字与 PR 记录必须来自 GitHub 公开数据或用户口述，末尾写明数据来源与截止日期。
- 不要在站点里放私钥、内部路径、未公开的雇主信息。
- **实习期间参与的雇主项目默认不上公开站点与主页**，除非用户明确确认可以公开——雇主内部平台的细节可能涉及保密要求。只保留自己独立设计与开发的项目；用户要求删除时，连项目卡片、标签与经历行一起删干净，不要只改措辞。
