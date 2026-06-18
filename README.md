# dxp-skills

自用技能（Skills）仓库，涵盖论文审核、代码开发、教学研究等场景。支持通过 **CC Switch** 一键切换 API Provider，使用 **DeepSeek V4** 模型驱动。

## 目录

- [技能列表](#技能列表)
- [环境安装](#环境安装)
  - [前置要求](#前置要求)
  - [Step 1: 安装 Node.js 与 npm](#step-1-安装-nodejs-与-npm)
  - [Step 2: 安装 Claude Code](#step-2-安装-claude-code)
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

更多技能正在开发中。分类目录：

- `coding/` — 编码相关技能
- `researching/` — 研究相关技能
- `teaching/` — 教学相关技能

## 环境安装

> 🚀 本指南面向 Windows 11 环境，通过 **CC Switch** 工具实现一键切换 API Provider 为 **DeepSeek V4**，无需手动修改环境变量或配置文件。

### 前置要求

| 项目 | 要求 | 备注 |
|------|------|------|
| 操作系统 | Windows 11 (22H2+) | 推荐开启 WSL2（可选） |
| Node.js | ≥ 18.0.0 | LTS 版本推荐 |
| Git | ≥ 2.40 | Claude Code 依赖 Git |
| DeepSeek 账号 | 已实名认证 | 需有可用额度 |

> ⚠️ **注意**: Claude Code 原生为 CLI 工具，在 Windows 上建议以 **管理员身份** 运行 PowerShell 或 CMD 进行安装和首次配置。

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

### Step 2: 安装 Claude Code

在 **管理员权限** 的终端中执行：

```bash
npm install -g @anthropic-ai/claude-code
```

验证安装：

```bash
claude --version
```

> 💡 **提示**: 此时不要直接运行 `claude` 登录官方账号。我们将通过 CC Switch 绕过官方认证，直接使用 DeepSeek API。

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

1. 打开终端（普通权限即可），输入：

```cmd
claude
```

2. 进入交互界面后，输入 `/model` 命令，确认当前模型已切换为 `deepseek-v4-pro` 或你配置的模型名
3. 发送一条测试指令，例如：

```
> Hi。
```

如果正常返回代码且无报错，说明配置成功！🎉

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

### Skills 管理（CC Switch 进阶）

CC Switch 还支持统一管理 Claude Code 的 Skills：

- 在 CC Switch 的 **「Skills」** 标签页中，可从 GitHub 仓库一键安装社区 Skills（如 baoyu-skills）
- 也支持从本地 ZIP 文件导入自定义 Skill
- 安装后在 Claude Code 中即可自动生效，无需额外配置

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

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `claude` 命令未找到 | npm 全局路径未加入 PATH | 重启终端；或重新安装 Node.js 并勾选 "Add to PATH" |
| 连接超时 / 401 | API Key 错误或网络问题 | 检查 Key 是否正确；确认 Base URL 无多余 `/v1` 后缀 |
| 切换模型后报错 | 旧会话缓存了旧模型名 | 在 Claude Code 中输入 `/model` 重新选择；或退出重进 |
| CC Switch 启用无效 | 未以正确权限写入配置 | 尝试以管理员身份运行 CC Switch |
| 中文乱码 | Windows 终端编码问题 | 执行 `chcp 65001` 切换 UTF-8 编码 |

## 贡献指南

1. Fork 本仓库
2. 新建 `feat/xxx` 分支
3. 提交代码
4. 发起 Pull Request

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [CC Switch GitHub](https://github.com/farion1231/cc-switch)
- [DeepSeek 开放平台](https://platform.deepseek.com/)
- [DeepSeek V4 技术报告](https://arxiv.org/abs/2512.14175)

## 许可证

[MIT License](LICENSE)
