# dxp-skills

自用 [Claude Code](https://claude.com/claude-code) 技能（Skills）仓库，涵盖论文审核、代码开发、教学研究等场景。

## 目录

- [技能列表](#技能列表)
- [环境安装](#环境安装)
  - [安装 Claude Code CLI](#安装-claude-code-cli)
  - [安装与切换 Node.js 版本](#安装与切换-nodejs-版本)
- [技能使用](#技能使用)
- [仓库结构](#仓库结构)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 技能列表

| 技能名称 | 分类 | 说明 |
|----------|------|------|
| **dxp-thesis-reviewer** | `teaching/` | 本科毕业论文审核与批注：自动体检报告 + OOXML 批注写入，支持 .doc/.docx |

更多技能正在开发中。分类目录：

- `coding/` — 编码相关技能
- `researching/` — 研究相关技能
- `teaching/` — 教学相关技能

## 环境安装

### 安装 Claude Code CLI

**方式一：npm 全局安装（推荐）**

```bash
npm install -g @anthropic-ai/claude-code
```

**方式二：直接运行（无需安装）**

```bash
npx @anthropic-ai/claude-code
```

**首次启动与认证：**

```bash
claude
```

首次运行会引导你完成 Anthropic 账号登录或 API Key 配置。也可通过以下命令手动登录：

```bash
claude login
```

**更新 Claude Code：**

```bash
npm update -g @anthropic-ai/claude-code
```

### 安装与切换 Node.js 版本

Claude Code 依赖 Node.js 18+。推荐使用版本管理器管理 Node.js。

**方式一：nvm（Node Version Manager）— 推荐**

Windows（nvm-windows）:

```powershell
# 下载安装 nvm-windows: https://github.com/coreybutler/nvm-windows/releases
# 安装后：
nvm install 20        # 安装 Node.js 20 LTS
nvm use 20            # 切换到 Node.js 20
nvm list              # 查看已安装版本
```

macOS / Linux:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# 重启终端后：
nvm install --lts     # 安装 LTS 版本
nvm use --lts         # 使用 LTS 版本
nvm alias default lts/* # 设为默认
```

**方式二：fnm（快速 Node 管理器）**

```bash
# macOS / Linux
curl -fsSL https://fnm.vercel.app/install | bash

# Windows (PowerShell)
winget install Schniz.fnm

# 安装并使用 Node
fnm install 20
fnm use 20
fnm default 20
```

**方式三：直接安装 Node.js**

从 [nodejs.org](https://nodejs.org/) 下载 LTS 版本安装。

**验证安装：**

```bash
node --version    # 应 >= v18.0.0
npm --version
```

## 技能使用

### 注册技能

将此仓库克隆到本地后，在仓库根目录执行：

```bash
# 注册所有技能
npx skills add .

# 或注册单个技能
npx skills add ./teaching/dxp-thesis-reviewer
```

### 查看已注册技能

```bash
npx skills list
```

### 触发技能

在 Claude Code 交互界面中，通过 `/skill-name` 或者自然语言描述即可触发技能。例如：

```bash
# 斜杠命令方式
/dxp-thesis-reviewer

# 自然语言方式
评审 my_thesis.docx
审核这篇论文
```

### 移除技能

```bash
npx skills remove dxp-thesis-reviewer
```

## 仓库结构

```
dxp-skills/
├── coding/                          # 编码相关技能
├── researching/                     # 研究相关技能
├── teaching/                        # 教学相关技能
│   └── dxp-thesis-reviewer/         # 本科毕业论文审核与批注
│       ├── SKILL.md                 # 技能定义文件
│       └── scripts/                 # 配套脚本
│           ├── append_summary.py    # 追加红色总结
│           ├── batch_comment.py     # 批量写入批注
│           ├── convert_doc_to_docx.py # .doc → .docx 转换
│           ├── extract_structure.py # 提取文档结构
│           ├── extract_styles.py    # 提取文档样式
│           ├── pack_docx.py         # 重新打包 .docx
│           ├── unpack_docx.py       # 解包 .docx
│           ├── validate_keywords.py # 预验证关键词
│           └── verify_comments.py   # 验证批注完整性
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## 贡献指南

1. Fork 本仓库
2. 新建 `feat/xxx` 分支
3. 提交代码
4. 发起 Pull Request

## 许可证

[MIT License](LICENSE)
