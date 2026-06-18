# dxp-skills

A personal [Claude Code](https://claude.com/claude-code) Skills repository covering thesis review, code development, teaching, and research scenarios. Supports one-click API Provider switching via **CC Switch**, powered by **DeepSeek V4**.

## Table of Contents

- [Skills](#skills)
- [Environment Setup](#environment-setup)
  - [Prerequisites](#prerequisites)
  - [Step 1: Install Node.js & npm](#step-1-install-nodejs--npm)
  - [Step 2: Install Claude Code](#step-2-install-claude-code)
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
| **dxp-thesis-reviewer** | `teaching/` | Undergrad thesis review & annotation: auto health-check report + OOXML comment injection, supports .doc/.docx |

More skills are in development. Categories:

- `coding/` — Code-related skills
- `researching/` — Research-related skills
- `teaching/` — Teaching-related skills

## Environment Setup

> 🚀 This guide is tailored for **Windows 11**. It uses **CC Switch** to swap the API Provider to **DeepSeek V4** with a single click — no manual editing of environment variables or config files.

### Prerequisites

| Item | Requirement | Notes |
|------|-------------|-------|
| OS | Windows 11 (22H2+) | WSL2 recommended (optional) |
| Node.js | ≥ 18.0.0 | LTS version recommended |
| Git | ≥ 2.40 | Required by Claude Code |
| DeepSeek Account | Verified identity | Must have available credits |

> ⚠️ **Note**: Claude Code is a CLI tool. On Windows, run PowerShell or CMD as **Administrator** for installation and initial configuration.

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

### Step 2: Install Claude Code

Run in an **Administrator** terminal:

```bash
npm install -g @anthropic-ai/claude-code
```

Verify:

```bash
claude --version
```

> 💡 **Tip**: Do NOT run `claude` to log into an official account yet. We will use CC Switch to bypass official auth and connect directly to DeepSeek API.

### Step 3: Get DeepSeek API Key

1. Visit the [DeepSeek Platform](https://platform.deepseek.com/) and log in
2. Go to **"API Keys"** → click **"Create New Key"**
3. Copy the generated key (format: `sk-xxxxxxxx`) and store it safely
4. Ensure your account has sufficient credits (DeepSeek V4 pricing: ¥1/1M input tokens, ¥3/1M output tokens)

**DeepSeek V4 Model Reference:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Base URL | `https://api.deepseek.com` | Official endpoint |
| Expert Mode | `deepseek-v4-pro` | 1.6T parameters |
| Fast Mode | `deepseek-v4-flash` | 284B parameters |
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

1. Open a terminal (regular permissions are fine) and run:

```bash
claude
```

2. Once inside the interactive interface, run the `/model` command to confirm the model shows `deepseek-v4-pro` (or your configured model name)
3. Send a test prompt:

```
> Hi.
```

If you get back a response without errors, you're all set! 🎉

## Using Skills

### Register Skills

After cloning this repository, run from the repository root:

```bash
# Register all skills
npx skills add .

# Or register a single skill
npx skills add ./teaching/dxp-thesis-reviewer
```

### List Registered Skills

```bash
npx skills list
```

### Trigger a Skill

In the Claude Code interactive interface, trigger a skill via slash command or natural language:

```bash
# Slash command
/dxp-thesis-reviewer

# Natural language
Please review my_thesis.docx
Review this thesis
```

### Skills Management (CC Switch)

CC Switch also provides unified Skills management:

- In the **"Skills"** tab of CC Switch, install community Skills (e.g., baoyu-skills) from GitHub repos with one click
- Import custom Skills from local ZIP files
- Skills take effect in Claude Code immediately — no extra configuration needed

### Remove a Skill

```bash
npx skills remove dxp-thesis-reviewer
```

## Repository Structure

```
dxp-skills/
├── coding/                          # Code-related skills
├── researching/                     # Research-related skills
├── teaching/                        # Teaching-related skills
│   └── dxp-thesis-reviewer/         # Undergrad thesis review & annotation
│       ├── SKILL.md                 # Skill definition
│       └── scripts/                 # Supporting scripts
│           ├── append_summary.py    # Append red summary
│           ├── batch_comment.py     # Batch comment injection
│           ├── convert_doc_to_docx.py # .doc → .docx conversion
│           ├── extract_structure.py # Extract document structure
│           ├── extract_styles.py    # Extract document styles
│           ├── pack_docx.py         # Re-pack .docx
│           ├── unpack_docx.py       # Unpack .docx
│           ├── validate_keywords.py # Pre-validate keywords
│           └── verify_comments.py   # Verify comment integrity
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `claude` command not found | npm global path not in PATH | Restart terminal; or reinstall Node.js with "Add to PATH" checked |
| Connection timeout / 401 | Wrong API Key or network issue | Verify the key; ensure Base URL has no trailing `/v1` |
| Error after model switch | Old session cached the old model name | Run `/model` inside Claude Code to reselect; or exit and restart |
| CC Switch enable not working | Insufficient permissions to write config | Try running CC Switch as Administrator |
| Chinese text garbled | Windows terminal encoding issue | Run `chcp 65001` to switch to UTF-8 encoding |

## Contributing

1. Fork the repository
2. Create your feature branch (`feat/xxx`)
3. Commit your changes
4. Push and create a Pull Request

## Resources

- [Claude Code Official Docs](https://docs.anthropic.com/en/docs/claude-code)
- [CC Switch GitHub](https://github.com/farion1231/cc-switch)
- [DeepSeek Platform](https://platform.deepseek.com/)
- [DeepSeek V4 Technical Report](https://arxiv.org/abs/2512.14175)

## License

[MIT License](LICENSE)
