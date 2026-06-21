# dxp-skills

A personal Skills repository covering thesis review, code development, teaching, and research scenarios. **Opencode** (free models, open ecosystem) is recommended as the primary driver; also supports one-click API Provider switching via **CC Switch**.

## Table of Contents

- [Skills](#skills)
- [Environment Setup](#environment-setup)
   - [Prerequisites](#prerequisites)
   - [Step 1: Install Node.js & npm](#step-1-install-nodejs--npm)
   - [Install Python (Required by Skill Scripts)](#install-python-required-by-skill-scripts)
   - [Step 2: Install AI Tools (Recommended: Opencode, Optional: Claude Code)](#step-2-install-ai-tools-recommended-opencode-optional-claude-code)
  - [Step 3: Get DeepSeek API Key](#step-3-get-deepseek-api-key)
  - [Step 4: Install & Configure CC Switch](#step-4-install--configure-cc-switch)
  - [Step 5: Verify & Use](#step-5-verify--use)
- [Using Skills](#using-skills)
- [Repository Structure](#repository-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

## Skills

| Skill | Category | Description |
|-------|----------|-------------|
| **dxp-thesis-reviewer** | `teaching/` | Undergrad thesis review & annotation (v2.1): auto health-check + 3-level comment density + AI hallucination term detection + OOXML annotation + defense Q&A reference document generation, supports .doc/.docx |
| **dxp-syllabus-creator** | `teaching/` | University syllabus/course outline intelligent generator: 4 templates (theory/design/internship/thesis), exports compliant .docx |

More skills are in development. Categories:

- `coding/` — Code-related skills
- `researching/` — Research-related skills
- `teaching/` — Teaching-related skills

## Environment Setup

> 🚀 This guide is tailored for **Windows 11**. **Opencode** is recommended (free built-in models, ready to use out of the box); alternatively, use **CC Switch** to swap the API Provider to **DeepSeek V4** for Claude Code.

### Prerequisites

| Item | Requirement | Notes |
|------|-------------|-------|
| OS | Windows 11 (22H2+) | WSL2 recommended (optional) |
| Node.js | ≥ 18.0.0 | LTS version recommended |
| Python | ≥ 3.10 | Runtime for skill scripts |
| Git | ≥ 2.40 | Required by Claude Code; optional for Opencode |
| DeepSeek Account | Verified identity | Only needed if using DeepSeek models |

> ⚠️ **Note**: Claude Code requires **Administrator** privileges on Windows. Opencode has no such restriction.

### Step 1: Install Node.js & npm

1. Visit [nodejs.org](https://nodejs.org/) and download the LTS installer (`.msi`)
2. Run the installer, check **"Automatically install the necessary tools"**
3. Verify in terminal:

```bash
node -v    # Should output v18.x.x or higher
npm -v     # Should output 9.x.x or higher
```

**(Recommended for users in China) Use npm mirror:**

```bash
npm config set registry https://registry.npmmirror.com
```

### Install Python (Required by Skill Scripts)

> ⚠️ **Important**: The scripts bundled with `dxp-thesis-reviewer` and `dxp-syllabus-creator` require a Python runtime. Install Python before using these skills.

1. Visit [python.org](https://www.python.org/downloads/) and download Python 3.10+ (`.exe`)
2. Run the installer — **make sure to check** `Add python.exe to PATH`
3. Verify in terminal:

```bash
python --version   # Should output Python 3.10.x or higher
pip --version      # Should output a pip version number
```

4. Install required Python packages:

```bash
pip install python-docx pywin32
```

| Package | Purpose | Used By |
|---------|---------|---------|
| `python-docx` | Generate/manipulate .docx files | dxp-thesis-reviewer, dxp-syllabus-creator |
| `pywin32` | .doc → .docx conversion (Word COM automation) | dxp-thesis-reviewer |

> 💡 **Tip**: If `pip` is not recognized, verify that you checked "Add python.exe to PATH" during installation. You can re-run the installer and choose "Modify" to add it.

### Step 2: Install AI Tools (Recommended: Opencode, Optional: Claude Code)

#### Recommended: Opencode 🏆

[Opencode](https://opencode.ai) is an open-source, free AI coding assistant CLI with significant advantages:

- ✅ **Completely Free**: Built-in free models (no API Key needed); also supports 75+ providers including DeepSeek, Claude, GPT, Gemini
- ✅ **Open Ecosystem**: Supports custom Skills, Agents, MCP Servers; active community (160K+ GitHub Stars)
- ✅ **Native Windows Support**: Install via npm/scoop/chocolatey, no admin privileges required
- ✅ **Skills Compatible**: All skills in this repo work directly in Opencode

Choose any installation method:

**Method 1: npm global install (recommended)**
```bash
npm install -g opencode-ai
```

**Method 2: Windows package managers**
```bash
# Scoop
scoop install opencode

# Chocolatey
choco install opencode
```

**Method 3: One-liner script (requires WSL)**
```bash
curl -fsSL https://opencode.ai/install | bash
```

**Method 4: GitHub Releases**
Download the pre-built binary for your platform from [Opencode Releases](https://github.com/anomalyco/opencode/releases), extract it, and add it to your PATH.

Verify installation:
```bash
opencode --version
```

> 💡 **Zero-cost start**: Run `opencode` right after installation — the built-in free model works without any API Key!

#### Optional: Claude Code

If you prefer the official Claude Code (requires a paid Anthropic subscription):

Run in an **Administrator** terminal:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

> 💡 **Tip**: If you choose Claude Code, do NOT run `claude` to log into an official account yet. Use CC Switch to bypass official auth and connect directly to DeepSeek API (see Step 4).

### Step 3: Get DeepSeek API Key

1. Visit the [DeepSeek Platform](https://platform.deepseek.com/) and log in
2. Go to **"API Keys"** → click **"Create New Key"**
3. Copy the generated key (format: `sk-xxxxxxxx`) and store it safely
4. Ensure your account has sufficient credits (DeepSeek V4 pricing: ¥1/1M input tokens, ¥3/1M output tokens)

**DeepSeek V4 Model Reference:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Base URL | `https://api.deepseek.com` | Official endpoint |
| Expert Mode | `deepseek-v4-pro` | 1.6T |
| Fast Mode | `deepseek-v4-flash` | 284B |
| Context Window | 1M Tokens | Ultra-long context support |

### Step 4: Install & Configure CC Switch

#### 4.1 Download & Install

- GitHub Repo: [https://github.com/farion1231/cc-switch](https://github.com/farion1231/cc-switch)
- Releases: [https://github.com/farion1231/cc-switch/releases](https://github.com/farion1231/cc-switch/releases)

Windows users should pick the `.msi` installer (recommended, supports auto-update) and follow the setup wizard.

#### 4.2 Add DeepSeek Provider

1. Launch CC Switch, go to the **"Claude Code"** tab
2. Click **"Add Provider"** in the top-right corner
3. Select **"DeepSeek"** from the preset list (or fill in manually):

| Field | Value |
|-------|-------|
| Provider Name | `DeepSeek` (custom name) |
| Website | `https://platform.deepseek.com` |
| API Key | Paste the key from Step 3 (starts with `sk-`) |
| Base URL | `https://api.deepseek.com/anthropic` |
| API Format | `Anthropic Messages (native)` |
| Model (Sonnet) | `deepseek-v4-flash` | ✔ Support 1M |
| Model (Opus) | `deepseek-v4-pro` | ✔ Support 1M |
| Model (Fable) | `deepseek-v4-pro` | ✔ Support 1M |
| Model (Haiku) | `deepseek-v4-flash` | |
| Default Fallback Model | `deepseek-v4-flash` | |

4. Click **"Test Connection"** — a green ✅ indicates success
5. Click **"Save"** to store the configuration

#### 4.3 Enable Provider

Find `DeepSeek` in the Provider list and click the **"Enable"** button on the right. CC Switch will automatically write the configuration to Claude Code's local settings file.

### Step 5: Verify & Use

Depending on your chosen AI tool:

#### Option A: Opencode (recommended, zero config)

1. Create a new folder and place the thesis to be reviewed (supports .doc/.docx; PDF not supported) into it
2. In File Explorer, click the address bar, type `cmd` and press Enter, then:

```cmd
opencode
```

3. Inside the interactive interface, send a test prompt (free model works out of the box):

```
> Hi
```

If you get a response without errors, you're all set! 🎉

#### Option B: Claude Code (requires CC Switch + DeepSeek config)

1. Create a new folder and place the thesis into it
2. In File Explorer, click the address bar, type `cmd` and press Enter, then:

```cmd
claude
```

3. Run `/model` to confirm the model is set to `deepseek-v4-pro`
4. Send a test prompt:

```
> Hi
```

## Using Skills

### Register Skills

After cloning this repository, run from the repository root:

```bash
# Register all skills
npx skills add .

# Or register a single skill
npx skills add ./teaching/dxp-thesis-reviewer
npx skills add ./teaching/dxp-syllabus-creator
```

### List Registered Skills

```bash
npx skills list
```

### Trigger a Skill

In the Opencode (or Claude Code) interactive interface, trigger a skill via slash command (use `TAB` to autocomplete) or natural language:

```bash
# Slash command — TAB to select
/dxp-thesis-reviewer Review the thesis xxxx.docx in this folder
```

The process requires multiple authorizations along the way. When finished, a reviewed version of the Word document with comments embedded will be generated in the local directory.

For syllabus generation:

```bash
# Generate a course syllabus based on a training plan
/dxp-syllabus-creator Major: Mechanical Engineering, Course: Mechanical Principles, write the syllabus based on the training plan.docx in this folder
```

You can iterate on and customize `/dxp-thesis-reviewer` using `/skill-creator` (installable from GitHub community repos with one click). For example:

```bash
# Slash command — TAB to select
/skill-creator Based on this review session, improve dxp-thesis-reviewer to support xxxx, add xxxx checks...
```

### Skills Management

**Opencode mode:**
Opencode natively supports Skills management:

- Type `/skill` in the Opencode interface to browse and install community Skills
- Or use the CLI: `npx skills add .` to register local skills
- Registered skills are available via `/skill-name` immediately

**CC Switch mode (Claude Code only):**
CC Switch also provides unified Skills management:

- In the **"Skills"** tab of CC Switch, install community Skills (e.g., `/skill-creator`) from GitHub repos with one click
- Import custom Skills from local ZIP files
- Skills take effect in Claude Code immediately — no extra configuration needed
- You can also copy skill folders into Claude Code's skills directory (typically located at `C:\Users\admin\.claude\skills`)

### Remove a Skill

```bash
npx skills remove dxp-thesis-reviewer
npx skills remove dxp-syllabus-creator
```

## Repository Structure

```
dxp-skills/
├── .gitee/                          # Gitee platform templates
│   ├── ISSUE_TEMPLATE.zh-CN.md
│   └── PULL_REQUEST_TEMPLATE.zh-CN.md
├── teaching/                        # Teaching-related skills
│   ├── dxp-thesis-reviewer/         # Undergrad thesis review & annotation
│   │   ├── SKILL.md                 # Skill definition
│   │   └── scripts/                 # Supporting scripts
│   │       ├── analyze_thesis.py    # Comprehensive thesis analysis
│   │       ├── append_summary.py    # Append red summary
│   │       ├── batch_comment.py     # Batch comment injection
│   │       ├── convert_doc_to_docx.py # .doc → .docx conversion
│   │       ├── extract_structure.py # Extract document structure
│   │       ├── extract_styles.py    # Extract document styles
│   │       ├── find_paragraphs.py   # Find specific paragraphs
│   │       ├── generate_defense_docx.py # ⭐ Generate defense Q&A reference document (v2.1)
│   │       ├── pack_docx.py         # Re-pack .docx
│   │       ├── unpack_docx.py       # Unpack .docx
│   │       ├── validate_keywords.py # Pre-validate keywords
│   │       └── verify_comments.py   # Verify comment integrity
│   └── dxp-syllabus-creator/        # University syllabus generator
│       ├── SKILL.md                 # Skill definition
│       ├── dxp-syllabus-creator.skill # Skill package file
│       ├── scripts/
│       │   └── generate_syllabus_docx.py # Generate compliant .docx syllabus
│       ├── references/
│       │   └── 培养方案指导.md       # Training plan guidance reference
│       ├── 1. 理论课程教学大纲的格式.docx  # Theory course template
│       ├── 2. 课程设计教学大纲的格式.docx  # Course design template
│       ├── 3. 实习教学大纲的格式.docx      # Internship template
│       ├── 5. 毕业论文（设计）教学大纲的格式.docx # Thesis template
│       └── eval_set.json            # Evaluation dataset
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `python` / `pip` command not found | Python not installed or not in PATH | Reinstall Python with "Add python.exe to PATH" checked; or manually add Python directory to system environment variables |
| `opencode` / `claude` command not found | npm global path not in PATH | Restart terminal; or reinstall Node.js with "Add to PATH" checked |
| Scripts fail with `ModuleNotFoundError` | Missing Python dependencies | Run `pip install python-docx pywin32` |
| Connection timeout / 401 | Wrong API Key or network issue | Verify the key; ensure Base URL has no trailing `/v1` |
| Error after model switch | Old session cached the old model name | Run `/model` inside Opencode/Claude Code to reselect; or exit and restart |
| CC Switch enable not working | Insufficient permissions to write config | Try running CC Switch as Administrator |
| Chinese text garbled | Windows terminal encoding issue | Run `chcp 65001` to switch to UTF-8 encoding |
| Opencode can't connect to free model | Network restrictions | Ensure terminal has internet access; or set proxy `set HTTPS_PROXY=http://127.0.0.1:7890` |

## Contributing

1. Fork the repository
2. Create your feature branch (`feat/xxx`)
3. Commit your changes
4. Push and create a Pull Request

## Resources

- [Opencode Official Website](https://opencode.ai) — Open-source AI coding assistant with free models
- [Opencode GitHub](https://github.com/anomalyco/opencode) — 160K+ Stars, active community
- [Claude Code Official Docs](https://docs.anthropic.com/en/docs/claude-code)
- [CC Switch GitHub](https://github.com/farion1231/cc-switch)
- [DeepSeek Platform](https://platform.deepseek.com/)
- [DeepSeek V4 Technical Report](https://arxiv.org/abs/2512.14175)

## License

[MIT License](LICENSE)
