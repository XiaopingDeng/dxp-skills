# dxp-skills

自用技能（Skills）仓库，涵盖论文审核、代码开发、教学研究等场景。推荐使用 **Opencode**（免费模型可用，生态开放）驱动；也支持通过 **CC Switch** 一键切换 API Provider，使用 **DeepSeek V4** 模型。

## 目录

- [技能列表](#技能列表)
- [环境安装](#环境安装)
   - [前置要求](#前置要求)
   - [Step 1: 安装 Node.js 与 npm](#step-1-安装-nodejs-与-npm)
   - [Step 2: 安装 AI 工具（推荐 Opencode，可选 Claude Code）](#step-2-安装-ai-工具推荐-opencode可选-claude-code)
  - [Step 3: 获取 DeepSeek API Key](#step-3-获取-deepseek-api-key)
  - [Step 4: 安装并配置 CC Switch](#step-4-安装并配置-cc-switch)
  - [Step 5: 验证与使用](#step-5-验证与使用)
- [技能使用](#技能使用)
- [仓库结构](#仓库结构)
- [常见问题排查](#常见问题排查)
- [贡献指南](#贡献指南)
- [相关资源](#相关资源)
- [许可证](#许可证)

## 技能列表

| 技能名称 | 分类 | 说明 |
|----------|------|------|
| **dxp-thesis-reviewer** | `teaching/` | 本科毕业论文审核与批注：自动体检报告 + OOXML 批注写入，支持 .doc/.docx |
| **dxp-syllabus-creator** | `teaching/` | 高校课程教学大纲智能编制：理论课/课程设计/实习实训/毕设四类模板，支持导出格式合规的 .docx |

更多技能正在开发中。分类目录：

- `coding/` — 编码相关技能
- `researching/` — 研究相关技能
- `teaching/` — 教学相关技能

## 环境安装

> 🚀 本指南面向 Windows 11 环境。**推荐使用 Opencode**（内置免费模型，开箱即用）；也可通过 **CC Switch** 工具实现一键切换 API Provider 为 **DeepSeek V4**，配合 Claude Code 使用。

### 前置要求

| 项目 | 要求 | 备注 |
|------|------|------|
| 操作系统 | Windows 11 (22H2+) | 推荐开启 WSL2（可选） |
| Node.js | ≥ 18.0.0 | LTS 版本推荐 |
| Git | ≥ 2.40 | Claude Code 强制依赖；Opencode 可选 |
| DeepSeek 账号 | 已实名认证 | 如需使用 DeepSeek 模型则需余额 |

> ⚠️ **注意**: Claude Code 原生为 CLI 工具，在 Windows 上建议以 **管理员身份** 运行 PowerShell 或 CMD 进行安装和首次配置。Opencode 无此限制。

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

### Step 2: 安装 AI 工具（推荐 Opencode，可选 Claude Code）

#### 推荐：Opencode 🏆

[Opencode](https://opencode.ai) 是一个开源、免费的 AI 编码助手 CLI，优势显著：

- ✅ **完全免费**：自带免费模型（无需 API Key 即可使用）；也支持接入 DeepSeek、Claude、GPT、Gemini 等 75+ 模型提供商
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

> 💡 **零成本上手**：安装后直接运行 `opencode` 即可使用内置免费模型，无需任何 API Key！

#### 可选：Claude Code

如果希望使用 Claude Code 官方版本（需 Anthropic 账号付费订阅）：

在 **管理员权限** 的终端中执行：

```bash
npm install -g @anthropic-ai/claude-code
```

验证安装：

```bash
claude --version
```

> 💡 **提示**: 如果选择 Claude Code，此时不要直接运行 `claude` 登录官方账号。可通过 CC Switch 绕过官方认证，直接使用 DeepSeek API（见 Step 4）。

### Step 3: 获取 DeepSeek API Key

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/) 并登录
2. 进入 **「API Keys」** 页面 → 点击 **「创建新 Key」**
3. 复制生成的 Key（格式如 `sk-xxxxxxxx`），妥善保存
4. 确认账户余额充足（DeepSeek V4 定价极低：输入 ¥1/百万Tokens，输出 ¥3/百万Tokens）

**DeepSeek V4 模型参数参考：**

| 参数 | 值 | 说明 |
|------|------|------|
| Base URL | `https://api.deepseek.com` | 官方直连地址 |
| 专家模式 | `deepseek-v4-pro` | 1.6T |
| 快速模式 | `deepseek-v4-flash` | 284B |
| Context Window | 1M Tokens | 超长上下文支持 |

### Step 4: 安装并配置 CC Switch

#### 4.1 下载安装

- GitHub 仓库: [https://github.com/farion1231/cc-switch](https://github.com/farion1231/cc-switch)
- Releases 下载: [https://github.com/farion1231/cc-switch/releases](https://github.com/farion1231/cc-switch/releases)

Windows 用户选择 `.msi` 安装包（推荐，支持自动更新），双击按向导默认安装即可。

#### 4.2 添加 DeepSeek Provider

1. 启动 CC Switch，进入 **「Claude Code」** 标签页
2. 点击右上方 **「Add Provider」**（添加供应商）
3. 在预设列表中选择 **「DeepSeek」**（或手动填写以下信息）：

| 字段 | 填写内容 |
|------|----------|
|供应商名称 | `DeepSeek`（自定义名称） |
|官网链接 | `https://platform.deepseek.com` |
| API Key | 粘贴 Step 3 获取的 Key，以sk-开头 |
| Base URL | `https://api.deepseek.com/anthropic` |
| API 格式 | `Anthropic Messages (原生)` |
| Model (Sonnet) | `deepseek-v4-flash` | 勾选支持1M
| Model (Opus) | `deepseek-v4-pro`| 勾选支持1M
| Model (Fable) | `deepseek-v4-pro`| 勾选支持1M
| Model (Haiku) | `deepseek-v4-flash`|
| 默认兜底模型 | `deepseek-v4-flash`|

4. 点击 **「Test Connection」** 测试连通性，显示绿色 ✅ 即表示成功
5. 点击 **「Save」** 保存配置

#### 4.3 启用 Provider

在 Provider 列表中，找到刚创建的 `DeepSeek`，点击右侧的 **「启用」(Enable)** 按钮。CC Switch 会自动将配置写入 Claude Code 的本地配置文件。

### Step 5: 验证与使用

根据你选择的 AI 工具，按对应方式启动：

#### 方式 A：Opencode（推荐，免配置）

1. 新建一个文件夹，将待审阅论文（支持 doc/docx 格式，不支持 pdf）放入该文件夹下
2. 在文件资源管理器中，点击顶部的地址栏，输入 `cmd` 回车打开终端，输入：

```cmd
opencode
```

3. 进入交互界面后，直接发送一条测试指令即可（内置免费模型开箱即用）：

```
> Hi
```

如果正常返回且无报错，说明配置成功！🎉

#### 方式 B：Claude Code（需通过 CC Switch 配置 DeepSeek）

1. 新建一个文件夹，将待审阅论文放入该文件夹下
2. 在文件资源管理器中，点击顶部的地址栏，输入 `cmd` 回车打开终端，输入：

```cmd
claude
```

3. 进入交互界面后，输入 `/model` 确认模型已切换为 `deepseek-v4-pro`
4. 发送一条测试指令验证：

```
> Hi
```

## 技能使用

### 注册技能

将此仓库克隆到本地后，在仓库根目录执行：

```bash
# 注册所有技能
npx skills add .

# 或注册单个技能
npx skills add ./teaching/dxp-thesis-reviewer
npx skills add ./teaching/dxp-syllabus-creator
```

### 查看已注册技能

```bash
npx skills list
```

### 触发技能

在 Opencode（或 Claude Code）交互界面中，通过 `/skill-name` 或者自然语言描述即可触发技能。例如：

```bash
# 斜杠命令方式 TAB选择
/dxp-thesis-reviewer 评审该文件夹下的论文xxxx.docx
```
过程中需要多次授权，最终会在本地目录下生成加入了批注的评审版本word文件

大纲编制也同理：

```bash
# 按培养方案生成某课程的教学大纲
/dxp-syllabus-creator 专业: 机械工程，课程: 机械原理，按该文件夹下的培养方案.docx编写教学大纲
```

可以基于评审过程和需求采用 `/skill-creator`（该 Skill 可从 GitHub 仓库一键安装）进行个性化定制迭代，例如:
```bash
# 斜杠命令方式 TAB选择
/skill-creator 基于本次评审过程，对dxp-thesis-reviewer进行完善，支持xxxx，增加xxxx检查...
```

### Skills 管理

**Opencode 方式：**
Opencode 原生支持 Skills 管理：

- 在 Opencode 交互界面中，输入 `/skill` 即可浏览和安装社区 Skills
- 或使用命令行：`npx skills add .` 注册本地技能
- 已注册的技能即可通过 `/skill-name` 直接触发

**CC Switch 方式（仅 Claude Code）：**
CC Switch 还支持统一管理 Skills：

- 在 CC Switch 的 **「Skills」** 标签页中，可从 GitHub 仓库一键安装社区 Skills（如 `/skill-creator`）
- 也支持从本地 ZIP 文件导入自定义 Skill
- 安装后在 Claude Code 中即可自动生效，无需额外配置
- 也可将技能文件夹放到 Claude Code 的 Skill 目录下（通常位于 `C:\Users\admin\.claude\skills`）

### 移除技能

```bash
npx skills remove dxp-thesis-reviewer
npx skills remove dxp-syllabus-creator
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
│   │       ├── pack_docx.py         # 重新打包 .docx
│   │       ├── unpack_docx.py       # 解包 .docx
│   │       ├── validate_keywords.py # 预验证关键词
│   │       └── verify_comments.py   # 验证批注完整性
│   └── dxp-syllabus-creator/        # 高校课程教学大纲智能编制
│       ├── SKILL.md                 # 技能定义文件
│       ├── dxp-syllabus-creator.skill # 技能包文件
│       ├── scripts/
│       │   └── generate_syllabus_docx.py # 生成合规 .docx 大纲
│       ├── references/
│       │   └── 培养方案指导.md       # 培养方案编制参考资料
│       ├── 1. 理论课程教学大纲的格式.docx  # 理论课模板
│       ├── 2. 课程设计教学大纲的格式.docx  # 课程设计模板
│       ├── 3. 实习教学大纲的格式.docx      # 实习实训模板
│       ├── 5. 毕业论文（设计）教学大纲的格式.docx # 毕设模板
│       └── eval_set.json            # 评测数据集
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `opencode` / `claude` 命令未找到 | npm 全局路径未加入 PATH | 重启终端；或重新安装 Node.js 并勾选 "Add to PATH" |
| 连接超时 / 401 | API Key 错误或网络问题 | 检查 Key 是否正确；确认 Base URL 无多余 `/v1` 后缀 |
| 切换模型后报错 | 旧会话缓存了旧模型名 | 在 Opencode/Claude Code 中输入 `/model` 重新选择；或退出重进 |
| CC Switch 启用无效 | 未以正确权限写入配置 | 尝试以管理员身份运行 CC Switch |
| 中文乱码 | Windows 终端编码问题 | 执行 `chcp 65001` 切换 UTF-8 编码 |
| Opencode 无法连接免费模型 | 网络环境限制 | 确保终端可访问外网；或配置代理 `set HTTPS_PROXY=http://127.0.0.1:7890` |

## 贡献指南

1. Fork 本仓库
2. 新建 `feat/xxx` 分支
3. 提交代码
4. 发起 Pull Request

## 相关资源

- [Opencode 官方网站](https://opencode.ai) — 开源 AI 编码助手，内置免费模型
- [Opencode GitHub](https://github.com/anomalyco/opencode) — 160K+ Stars，社区活跃
- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [CC Switch GitHub](https://github.com/farion1231/cc-switch)
- [DeepSeek 开放平台](https://platform.deepseek.com/)
- [DeepSeek V4 技术报告](https://arxiv.org/abs/2512.14175)

## 许可证

[MIT License](LICENSE)
