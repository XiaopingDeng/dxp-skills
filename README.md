# dxp-skills

自用技能（Skills）仓库，涵盖论文审核、代码开发、教学研究等场景。推荐使用 **Opencode**（生态开放，原生 Windows 支持）驱动；模型优先级：**DeepSeek-V4-Flash**（主力，内置免费、开箱即用）→ **DeepSeek-V4-Pro**（专家模式）→ **GLM-5.2**（长上下文备选）。

## 目录

- [技能列表](#技能列表)
- [环境安装](#环境安装)
   - [前置要求](#前置要求)
   - [Step 1: 安装 Node.js 与 npm](#step-1-安装-nodejs-与-npm)
   - [安装 Python 环境（技能脚本依赖）](#安装-python-环境技能脚本依赖)
   - [Step 2: 安装 Opencode](#step-2-安装-opencode)
   - [Step 3: 配置模型](#step-3-配置模型)
   - [Step 4: 安装与注册技能](#step-4-安装与注册技能)
- [使用技能](#使用技能)
   - [dxp-thesis-reviewer 使用方法](#dxp-thesis-reviewer-使用方法)
   - [dxp-syllabus-creator 使用方法](#dxp-syllabus-creator-使用方法)
   - [dxp-paper-reviewer 使用方法](#dxp-paper-reviewer-使用方法)
   - [resume-doc-to-personal-homepage 使用方法](#resume-doc-to-personal-homepage-使用方法)
   - [个性化定制](#个性化定制)
   - [Skills 管理与移除](#skills-管理与移除)
- [仓库结构](#仓库结构)
- [常见问题排查](#常见问题排查)
- [贡献指南](#贡献指南)
- [相关资源](#相关资源)
- [许可证](#许可证)

## 技能列表

| 技能名称 | 分类 | 说明 |
|----------|------|------|
| **dxp-thesis-reviewer** | `teaching/` | 本科毕业论文审核与批注(v2.1)：自动体检 + 三档批注密度 + AI幻觉术语检测 + OOXML 批注写入 + 答辩问题及参考答案独立文档生成，支持 .doc/.docx |
| **dxp-syllabus-creator** | `teaching/` | 高校课程教学大纲智能编制（配套 2026 版培养方案）：理论课/课程设计/实习实训/毕业论文（设计）四类模板自动识别；理论课使用含完整评分标准表的示例大纲作模板、替换内容生成 docx 并配套生成课程简介，其余三类按对应模板填充，输出格式合规的 .docx |
| **dxp-paper-reviewer** | `researching/` | 投稿论文体检（v1.0）：四本账系统性对账（承诺 vs 交付 / 数字 / 量纲 / 符号）+ 五维排查（归因 / 复现 / 基线 / 呈现），输出按严重度分级的编号问题清单（P0 硬伤 / P1·P2 软伤），每条附可执行改法；支持导出 Word（审稿人 / 导师两种口吻），输入 .pdf/.docx |
| **resume-doc-to-personal-homepage** | `researching/` | 简历文档（.doc/.docx/.wps）→ 可部署的 GitHub Pages 个人主页：自包含静态站点（index.html + styles.css + images/ + files/cv.pdf），可选中英文一键切换，逐宽度数值化验证无横向溢出，默认隐私处理（手机号 / 群照不发布） |

更多技能正在开发中。分类目录：

- `coding/` — 编码相关技能
- `researching/` — 研究相关技能
- `teaching/` — 教学相关技能

## 环境安装

> 🚀 本指南面向 Windows 11 环境。推荐使用 **Opencode**（生态开放，原生 Windows 支持）驱动；模型优先级：**DeepSeek-V4-Flash**（主力，内置免费）→ **DeepSeek-V4-Pro** → **GLM-5.2**。详见 Step 3。

### 前置要求

| 项目 | 要求 | 备注 |
|------|------|------|
| 操作系统 | Windows 11 (22H2+) | 推荐开启 WSL2（可选） |
| Node.js | ≥ 18.0.0 | LTS 版本推荐 |
| Python | ≥ 3.10 | 技能脚本运行环境 |
| Git | ≥ 2.40 | 可选 |
| 模型 API Key | DeepSeek-V4-Flash（主力）内置免费；DeepSeek-V4-Pro / GLM-5.2 需对应 Key | 见 Step 3；Opencode 自带免费模型无需 Key |

### Step 1: 安装 Node.js 与 npm

1. 访问 [Node.js 官网](https://nodejs.org/) 下载 LTS 版本 (`.msi`)
2. 双击安装，勾选 **"Automatically install the necessary tools"**（自动安装构建工具）
3. 打开终端验证：

```bash
node -v    # 应输出 v18.x.x 或更高
npm -v     # 应输出 9.x.x 或更高
```

**（国内用户推荐）设置 npm 淘宝镜像加速：**

```bash
npm config set registry https://registry.npmmirror.com
```

### 安装 Python 环境（技能脚本依赖）

> ⚠️ **重要**：多数技能的配套脚本需要 Python 运行环境（`dxp-thesis-reviewer` 与 `dxp-syllabus-creator` 的核心脚本、`dxp-paper-reviewer` 的全文提取、`resume-doc-to-personal-homepage` 的文件与图像处理），安装 Python 后才能正常执行。

1. 访问 [Python 官网](https://www.python.org/downloads/) 下载 3.10+ 版本 (`.exe`)
2. 双击安装，**务必勾选** `Add python.exe to PATH`（将 Python 加入系统路径）
3. 打开终端验证：

```bash
python --version   # 应输出 Python 3.10.x 或更高
pip --version      # 应输出 pip 版本号
```

4. 安装脚本所需的 Python 依赖包：

```bash
pip install python-docx pywin32 pymupdf pillow
```

| 依赖包 | 用途 | 关联技能 |
|--------|------|----------|
| `python-docx` | 生成/操作 .docx 文件 | dxp-thesis-reviewer, dxp-syllabus-creator, dxp-paper-reviewer |
| `pywin32` | .doc → .docx 格式转换（Word COM 自动化） | dxp-thesis-reviewer |
| `pymupdf` (fitz) | PDF 全文文本提取 | dxp-paper-reviewer |
| `pillow` | 图像处理（简历照片裁切/缩放、渲染截图扫描） | resume-doc-to-personal-homepage |

> 💡 **Node 依赖**：`dxp-paper-reviewer` 导出 Word 问题清单需要 node 的 `docx` 包：`npm i -g docx`（脚本兼容全局 node_modules；若 `require("docx")` 失败，设置 `NODE_PATH`，见排查表）。

> 💡 **提示**：如果 `pip` 命令提示未找到，请确认 Step 1 安装 Python 时已勾选 "Add python.exe to PATH"。也可重新运行安装程序并选择 "Modify" 追加该选项。

### Step 2: 安装 Opencode

[Opencode](https://opencode.ai) 是一个开源、免费的 AI 编码助手 CLI，优势显著：

- ✅ **完全免费**：自带限量免费模型（无需 API Key 即可使用）；也支持接入 GLM-5.2、DeepSeek、GPT、Gemini 等 75+ 模型提供商
- ✅ **生态开放**：支持自定义 Skills、Agents、MCP Server，社区活跃（160K+ GitHub Stars）
- ✅ **原生 Windows 支持**：可通过 npm/scoop/chocolatey 安装，无需管理员权限
- ✅ **Skills 兼容**：本仓库所有技能均可直接在 Opencode 中使用

安装方式（任选其一）：

**方式一：npm 全局安装（推荐）**
```bash
npm install -g opencode-ai
```

**方式二：Windows 包管理器**
```bash
# Scoop
scoop install opencode

# Chocolatey
choco install opencode
```

**方式三：一键脚本（需 WSL）**
```bash
curl -fsSL https://opencode.ai/install | bash
```

**方式四：GitHub Releases**
前往 [Opencode Releases](https://github.com/anomalyco/opencode/releases) 下载对应平台的预构建二进制文件，解压后加入 PATH。

验证安装：
```bash
opencode --version
```

> 💡 **零成本上手**：安装后直接运行 `opencode` 即可使用自带限量免费模型（含主力模型 `deepseek-v4-flash`），无需任何 API Key！如需更强模型，按 Step 3 接入 `deepseek-v4-pro` 或 `glm-5.2`。

### Step 3: 配置模型

本仓库推荐模型优先级（从高到低）：

| 优先级 | 模型 | 说明 | 获取方式 |
|:---:|:---|:---|:---|
| 1 | `deepseek-v4-flash` | **主力**，快速模式、中文友好，开箱即用 | Opencode 内置免费模型，无需 Key；亦可按 [DeepSeek 开放平台](https://platform.deepseek.com/) 接入自有 Key |
| 2 | `deepseek-v4-pro` | 次选，1.6T 专家模式，深度推理更强 | [DeepSeek 开放平台](https://platform.deepseek.com/) 获取 API Key |
| 3 | `glm-5.2` | 备选，长上下文、中文友好 | 参见 [GLM API 文档](https://open.bigmodel.cn/dev/api)，在 Opencode 中以 OpenAI 兼容供应商接入 |

> 💡 **接入方式**：在 Opencode 中通过 `/model` 选择已配置的模型。主力 `deepseek-v4-flash` 为 Opencode 内置免费模型，无需 API Key；各模型的 Base URL / API Key 等参数以对应官方 API 文档为准（DeepSeek 见其开放平台，GLM-5.2 见上表链接）。

### Step 4: 安装与注册技能

将此仓库克隆到本地后，在仓库根目录执行注册：

```bash
# 注册所有技能
npx skills add .

# 或注册单个技能
npx skills add ./teaching/dxp-thesis-reviewer
npx skills add ./teaching/dxp-syllabus-creator
npx skills add ./researching/dxp-paper-reviewer
npx skills add ./researching/resume-doc-to-personal-homepage
```

查看已注册技能：

```bash
npx skills list
```

> 💡 注册完成后，即可在 Opencode 交互界面中通过 `/skill-name`（TAB 补全）或自然语言描述触发技能。具体使用见下节。

## 使用技能

在 Opencode 交互界面中，先输入 `/model` 选择模型（推荐主力 `deepseek-v4-flash`，`deepseek-v4-pro` / `glm-5.2` 亦可），再通过 `/skill-name` 或自然语言触发对应技能。各技能的使用方法分别说明如下。

### dxp-thesis-reviewer 使用方法

本科毕业论文审核与批注，最终生成加入了批注的评审版本 Word 文件。

1. **新建一个文件夹作为工作目录**，将待审阅论文（支持 .doc/.docx 格式，不支持 pdf）放入该文件夹下
2. 在该文件夹下打开终端：文件资源管理器中点击顶部地址栏，输入 `cmd` 回车，运行：

```cmd
opencode
```

3. 进入交互界面后，输入 `/model` 选择模型（推荐 `deepseek-v4-flash`）
4. 触发技能（斜杠命令 + TAB 补全，或自然语言描述）：

```bash
/dxp-thesis-reviewer 评审该文件夹下的论文xxxx.docx
```

5. 过程中需要多次授权，最终会在该工作目录下生成加入了批注的评审版本 Word 文件

### dxp-syllabus-creator 使用方法

高校课程教学大纲智能编制，自动识别课程性质、匹配四类模板，生成 Markdown + .docx 大纲（理论课额外生成课程简介）。

1. **新建一个文件夹作为工作目录**
2. ⚠️ **运行技能之前**，将**包含工程认证支撑关系的培养方案**（`.docx`）放入该工作目录下（技能会扫描工作目录解析培养方案，提取课程元数据与毕业要求指标点支撑关系）
3. 在该文件夹下打开终端：文件资源管理器中点击顶部地址栏，输入 `cmd` 回车，运行：

```cmd
opencode
```

4. 进入交互界面后，输入 `/model` 选择模型（推荐 `deepseek-v4-flash`）
5. 触发技能（斜杠命令 + TAB 补全，或自然语言描述）：

```bash
/dxp-syllabus-creator 专业: 机械工程，课程: 机械原理，按该文件夹下的培养方案.docx编写教学大纲
```

6. 技能会先确认教材、考核比重等，再生成大纲；过程中需要多次授权，最终在该工作目录下输出格式合规的 .docx 大纲

> 💡 培养方案中应包含工程认证毕业要求指标点与课程的支撑关系矩阵；若另有独立的工程认证矩阵 xlsx，可一并放入工作目录，技能会优先从中提取细分指标点。

### dxp-paper-reviewer 使用方法

投稿论文体检：对一篇待投稿论文做系统性对账与排查（承诺 vs 交付 / 数字与量纲 / 符号四本账 + 归因 / 复现 / 基线 / 呈现五维排查），输出按严重度分级的编号问题清单（P0 硬伤 / P1·P2 软伤），每条附可执行改法。

1. **新建一个文件夹作为工作目录**，将待投稿论文（支持 .pdf / .docx）放入该文件夹下
2. 在该文件夹下打开终端：文件资源管理器中点击顶部地址栏，输入 `cmd` 回车，运行：

```cmd
opencode
```

3. 进入交互界面后，输入 `/model` 选择模型（推荐 `deepseek-v4-flash`）
4. 触发技能（斜杠命令 + TAB 补全，或自然语言描述）：

```bash
/dxp-paper-reviewer 审阅该文件夹下的 article.pdf
```

5. 默认走"完整体检"，输出分级问题清单；需要文档版时要求导出 Word（审稿人 / 导师两种口吻）：

```bash
/dxp-paper-reviewer 审阅 article.pdf，导出审稿人口吻的 Word 问题清单
```

> 💡 支持**单维问诊**：如"只查统计有没有问题""重点查基线公平性"，技能会直接跳到对应维度。导出 Word 需要 `npm i -g docx`（见"安装 Python 环境"一节的 Node 依赖说明）。

### resume-doc-to-personal-homepage 使用方法

把简历文档转换为可部署的 GitHub Pages 个人主页（自包含静态站点：index.html + styles.css + images/ + files/cv.pdf，可选中英文一键切换）。

1. **新建一个文件夹作为工作目录**，放入简历文档（支持 .doc / .docx / .wps；暂无简历时可用技能自带的 `resume-template.docx` 模板填写）
2. 在该文件夹下打开终端：文件资源管理器中点击顶部地址栏，输入 `cmd` 回车，运行：

```cmd
opencode
```

3. 进入交互界面后，输入 `/model` 选择模型（推荐 `deepseek-v4-flash`），再触发技能（斜杠命令 + TAB 补全，或自然语言描述）：

```bash
/resume-doc-to-personal-homepage 把这份简历.docx 转成我的个人主页并部署到 GitHub Pages
```

4. 如有参考主页可一并提供 URL（技能只复刻其布局系统，不复刻内容）；需要中英文切换时一并说明
5. 技能在本地构建并逐宽度验证（无横向溢出）后，交付 `homepage/` 目录 + 部署说明（`<用户名>.github.io` 或项目仓库 + Settings → Pages）；默认省略手机号、群照等隐私内容，需发布时按提示取消注释

> 💡 技能读取简历依赖本机 Office / 文档读取工具链（lark-cli 的 doc 工具），首次运行请按提示完成授权；渲染验证需要本机 Chrome。

### 个性化定制

可基于评审 / 编制过程与需求，采用 `/skill-creator`（该 Skill 可从 GitHub 仓库一键安装）进行个性化定制迭代，例如：

```bash
# 斜杠命令方式 TAB选择
/skill-creator 基于本次评审过程，对dxp-thesis-reviewer进行完善，支持xxxx，增加xxxx检查...
```

### Skills 管理与移除

Opencode 原生支持 Skills 管理：

- 在 Opencode 交互界面中，输入 `/skill` 即可浏览和安装社区 Skills
- 或使用命令行：`npx skills add .` 注册本地技能
- 已注册的技能即可通过 `/skill-name` 直接触发

移除技能：

```bash
npx skills remove dxp-thesis-reviewer
npx skills remove dxp-syllabus-creator
npx skills remove dxp-paper-reviewer
npx skills remove resume-doc-to-personal-homepage
```

## 仓库结构

```
dxp-skills/
├── .gitee/                          # Gitee 平台模板
│   ├── ISSUE_TEMPLATE.zh-CN.md
│   └── PULL_REQUEST_TEMPLATE.zh-CN.md
├── teaching/                        # 教学相关技能
│   ├── dxp-thesis-reviewer/         # 本科毕业论文审核与批注
│   │   ├── SKILL.md                 # 技能定义文件
│   │   └── scripts/                 # 配套脚本
│   │       ├── analyze_thesis.py    # 论文综合分析
│   │       ├── append_summary.py    # 追加红色总结
│   │       ├── batch_comment.py     # 批量写入批注
│   │       ├── convert_doc_to_docx.py # .doc → .docx 转换
│   │       ├── extract_structure.py # 提取文档结构
│   │       ├── extract_styles.py    # 提取文档样式
│   │       ├── find_paragraphs.py   # 查找特定段落
│   │       ├── generate_defense_docx.py # ⭐ 生成答辩问题及参考答案独立文档 (v2.1)
│   │       ├── pack_docx.py         # 重新打包 .docx
│   │       ├── unpack_docx.py       # 解包 .docx
│   │       ├── validate_keywords.py # 预验证关键词
│   │       └── verify_comments.py   # 验证批注完整性
│   └── dxp-syllabus-creator/        # 高校课程大纲智能编制（2026版培养方案）
│       ├── SKILL.md                 # 技能定义文件
│       ├── scripts/
│       │   └── generate_syllabus_docx.py # docx 生成器（含工具函数）
│       ├── references/
│       │   ├── 培养方案解析指南.md   # 培养方案解析指引
│       │   └── docx_generation_guide.md # docx 生成详细规则
│       ├── 示例：机械原理 课程教学大纲.docx # 理论课首选模板（含完整评分标准表）
│       ├── 1. 理论课程教学大纲的格式.docx  # 理论课备选模板（简版）
│       ├── 2. 课程设计教学大纲的格式.docx  # 课程设计模板
│       ├── 3. 实习教学大纲的格式.docx      # 实习实训模板
│       ├── 4. 毕业论文（设计）教学大纲的格式.docx # 毕设模板
│       ├── 附件2：课程简介模板.doc   # 课程简介结构参考
│       ├── 附件4：实验项目汇总表.xlsx # 实验项目汇总表参考
│       └── eval_set.json            # 评测数据集
├── researching/                     # 研究相关技能
│   ├── dxp-paper-reviewer/          # 投稿论文体检
│   │   ├── SKILL.md                 # 技能定义文件
│   │   ├── scripts/
│   │   │   ├── extract_manuscript.py # PDF/DOCX 全文提取（含元数据）
│   │   │   └── build_review_docx.js  # 问题清单 JSON → Word 导出
│   │   ├── references/
│   │   │   └── docx-export.md        # Word 导出规则（审稿人/导师两套口吻）
│   │   └── assets/
│   │       └── example_review.json   # 问题清单样例
│   └── resume-doc-to-personal-homepage/ # 简历 → GitHub Pages 个人主页
│       ├── SKILL.md                 # 技能定义文件
│       ├── references/
│       │   ├── reading-the-doc.md   # 读取简历文档（扩展名路由/握手/轮询）
│       │   ├── building-the-site.md # 构建站点（设计令牌/图廊组件）
│       │   ├── verifying-render.md  # 渲染验证（数值化溢出探针/长截图）
│       │   ├── shipping-pages.md    # GitHub Pages 部署（HTTPS + PAT 配方）
│       │   ├── bilingual.md         # 中英文切换实现
│       │   └── windows-gotchas.md   # Windows 环境坑位速查表
│       └── assets/
│           └── resume-template.docx # 简历模板（无简历时填写用）
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `python` / `pip` 命令未找到 | Python 未安装或未加入 PATH | 重新安装 Python 并勾选 "Add python.exe to PATH"；或手动将 Python 目录添加到系统环境变量 |
| `opencode` 命令未找到 | npm 全局路径未加入 PATH | 重启终端；或重新安装 Node.js 并勾选 "Add to PATH" |
| 运行脚本报 `ModuleNotFoundError` | 缺少 Python 依赖包 | 执行 `pip install python-docx pywin32` |
| 连接超时 / 401 | API Key 错误或网络问题 | 检查 Key 是否正确；确认 Base URL 无多余 `/v1` 后缀 |
| GLM-5.2 调用报错（模型不存在 / 404） | 模型名或供应商配置错误 | 确认模型名填 `glm-5.2`；按 [GLM API 文档](https://open.bigmodel.cn/dev/api) 核对 Base URL 与鉴权方式 |
| 切换模型后报错 | 旧会话缓存了旧模型名 | 在 Opencode 中输入 `/model` 重新选择；或退出重进 |
| 中文乱码 | Windows 终端编码问题 | 执行 `chcp 65001` 切换 UTF-8 编码 |
| Opencode 无法连接免费模型 | 网络环境限制 | 确保终端可访问外网；或配置代理 `set HTTPS_PROXY=http://127.0.0.1:7890` |
| dxp-syllabus-creator 找不到培养方案 | 工作目录下无培养方案 .docx | 运行技能前将含工程认证支撑关系的培养方案放入工作目录 |
| dxp-thesis-reviewer 不识别论文 | 论文为 pdf 或未放入工作目录 | 仅支持 .doc/.docx；将论文放入工作目录后再运行 |
| dxp-paper-reviewer 导出 Word 报 `Cannot find module 'docx'` | node 的 docx 包未安装或未解析到 | 执行 `npm i -g docx`；仍失败则设 `$env:NODE_PATH="$(npm root -g)"` 再运行 |
| dxp-paper-reviewer PDF 提取报 `ModuleNotFoundError` | 缺少 PDF 解析库 | 执行 `pip install pymupdf`（或 pdfplumber / pypdf） |
| resume-doc-to-personal-homepage 读取 .wps/.dot 报 `Unknown sheet tool` | 扩展名被误路由到表格工具 | 复制一份副本并另存为 .doc 再读取（勿改动原文件） |

## 贡献指南

1. Fork 本仓库
2. 新建 `feat/xxx` 分支
3. 提交代码
4. 发起 Pull Request

## 相关资源

- [Opencode 官方网站](https://opencode.ai) — 开源 AI 编码助手，内置免费模型
- [Opencode GitHub](https://github.com/anomalyco/opencode) — 160K+ Stars，社区活跃
- [DeepSeek 开放平台](https://platform.deepseek.com/) — 主力模型 deepseek-v4-flash 及专家模式 deepseek-v4-pro 接入平台
- [GLM API 文档](https://open.bigmodel.cn/dev/api) — 备选模型 GLM-5.2 接入说明

## 许可证

[MIT License](LICENSE)
