# dxp-skills

A personal [Claude Code](https://claude.com/claude-code) Skills repository covering thesis review, code development, teaching, and research scenarios.

## Table of Contents

- [Skills](#skills)
- [Environment Setup](#environment-setup)
  - [Install Claude Code CLI](#install-claude-code-cli)
  - [Install & Switch Node.js Versions](#install--switch-nodejs-versions)
- [Using Skills](#using-skills)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
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

### Install Claude Code CLI

**Option 1: Global npm install (recommended)**

```bash
npm install -g @anthropic-ai/claude-code
```

**Option 2: Run directly (no install required)**

```bash
npx @anthropic-ai/claude-code
```

**First-time setup & authentication:**

```bash
claude
```

The first run will guide you through Anthropic account login or API key configuration. You can also manually log in:

```bash
claude login
```

**Update Claude Code:**

```bash
npm update -g @anthropic-ai/claude-code
```

### Install & Switch Node.js Versions

Claude Code requires Node.js 18+. Using a version manager is recommended.

**Option 1: nvm (Node Version Manager) — Recommended**

Windows (nvm-windows):

```powershell
# Download and install: https://github.com/coreybutler/nvm-windows/releases
# After installation:
nvm install 20        # Install Node.js 20 LTS
nvm use 20            # Switch to Node.js 20
nvm list              # List installed versions
```

macOS / Linux:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# Restart terminal, then:
nvm install --lts     # Install LTS version
nvm use --lts         # Use LTS version
nvm alias default lts/* # Set as default
```

**Option 2: fnm (Fast Node Manager)**

```bash
# macOS / Linux
curl -fsSL https://fnm.vercel.app/install | bash

# Windows (PowerShell)
winget install Schniz.fnm

# Install and use Node
fnm install 20
fnm use 20
fnm default 20
```

**Option 3: Direct Node.js install**

Download the LTS version from [nodejs.org](https://nodejs.org/).

**Verify installation:**

```bash
node --version    # Should be >= v18.0.0
npm --version
```

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
│           ├── append_summary.py    # Append red summary to doc
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

## Contributing

1. Fork the repository
2. Create your feature branch (`feat/xxx`)
3. Commit your changes
4. Push and create a Pull Request

## License

[MIT License](LICENSE)
