# dxp-skills

A personal Skills repository covering thesis review, code development, teaching, and research scenarios. **Opencode** (open ecosystem, native Windows support) is recommended as the driver; model priority: **DeepSeek-V4-Flash** (primary).

## Table of Contents

- [Skills](#skills)
- [Environment Setup](#environment-setup)
   - [Prerequisites](#prerequisites)
   - [Step 1: Install Node.js & npm](#step-1-install-nodejs--npm)
   - [Install Python (Required by Skill Scripts)](#install-python-required-by-skill-scripts)
   - [Step 2: Install Opencode](#step-2-install-opencode)
   - [Step 3: Configure Models](#step-3-configure-models)
   - [Step 4: Install & Register Skills](#step-4-install--register-skills)
- [Using Skills](#using-skills)
   - [dxp-thesis-reviewer Usage](#dxp-thesis-reviewer-usage)
   - [dxp-syllabus-creator Usage](#dxp-syllabus-creator-usage)
   - [dxp-paper-reviewer Usage](#dxp-paper-reviewer-usage)
   - [resume-doc-to-personal-homepage Usage](#resume-doc-to-personal-homepage-usage)
   - [Customization](#customization)
   - [Skills Management & Removal](#skills-management--removal)
- [Repository Structure](#repository-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Resources](#resources)
- [License](#license)

## Skills

| Skill | Category | Description |
|-------|----------|-------------|
| **dxp-thesis-reviewer** | `teaching/` | Undergrad thesis review & annotation (v2.1): auto health-check + 3-level comment density + AI hallucination term detection + OOXML annotation + defense Q&A reference document generation, supports .doc/.docx |
| **dxp-syllabus-creator** | `teaching/` | University course syllabus/outline intelligent generator (aligned with the 2026 training plan): auto-detects one of 4 template types (theory / course design / internship / graduation thesis); theory courses use a sample syllabus with a complete grading rubric as the template, replacing content to produce .docx plus a companion course-introduction document; the other three types are filled from their respective templates — outputs compliant .docx |
| **dxp-paper-reviewer** | `researching/` | Submission paper health check (v1.0): systematic cross-audit across four ledgers (claims vs. delivery / numbers / units / symbols) + five-dimension review (attribution / reproducibility / baselines / presentation), outputting a severity-tiered numbered issue list (P0 fatal / P1·P2 soft) with an actionable fix per item; optional Word export (reviewer / advisor voices), accepts .pdf/.docx |
| **resume-doc-to-personal-homepage** | `researching/` | Resume document (.doc/.docx/.wps) → deployable GitHub Pages personal homepage: a self-contained static site (index.html + styles.css + images/ + files/cv.pdf), optional one-click Chinese/English toggle, per-width numeric overflow verification, privacy-by-default (phone number / group photos not published) |

More skills are in development. Categories:

- `coding/` — Code-related skills
- `researching/` — Research-related skills
- `teaching/` — Teaching-related skills

## Environment Setup

> 🚀 This guide is tailored for **Windows 11**. **Opencode** is recommended (open ecosystem, native Windows support); model priority: **DeepSeek-V4-Flash** (primary, built-in & free) → **DeepSeek-V4-Pro** → **GLM-5.2**. See Step 3.

### Prerequisites

| Item | Requirement | Notes |
|------|-------------|-------|
| OS | Windows 11 (22H2+) | WSL2 recommended (optional) |
| Node.js | ≥ 18.0.0 | LTS version recommended |
| Python | ≥ 3.10 | Runtime for skill scripts |
| Git | ≥ 2.40 | Optional |
| Model API Key | DeepSeek-V4-Flash (primary) need keys | See Step 3; Opencode's built-in free models need no key |

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

> ⚠️ **Important**: Most skills rely on a Python runtime (`dxp-thesis-reviewer` and `dxp-syllabus-creator` core scripts, `dxp-paper-reviewer` full-text extraction, `resume-doc-to-personal-homepage` file & image handling). Install Python before using these skills.

1. Visit [python.org](https://www.python.org/downloads/) and download Python 3.10+ (`.exe`)
2. Run the installer — **make sure to check** `Add python.exe to PATH`
3. Verify in terminal:

```bash
python --version   # Should output Python 3.10.x or higher
pip --version      # Should output a pip version number
```

4. Install required Python packages:

```bash
pip install python-docx pywin32 pymupdf pillow
```

| Package | Purpose | Used By |
|---------|---------|---------|
| `python-docx` | Generate/manipulate .docx files | dxp-thesis-reviewer, dxp-syllabus-creator, dxp-paper-reviewer |
| `pywin32` | .doc → .docx conversion (Word COM automation) | dxp-thesis-reviewer |
| `pymupdf` (fitz) | Extract plain text from PDF files | dxp-paper-reviewer |
| `pillow` | Image processing (resume photo crop/resize, screenshot scan) | resume-doc-to-personal-homepage |

> 💡 **Node dependency**: `dxp-paper-reviewer` needs the node `docx` package to export a Word issue list: `npm i -g docx` (the script handles a global node_modules; if `require("docx")` fails, set `NODE_PATH` — see the troubleshooting table).

> 💡 **Tip**: If `pip` is not recognized, verify that you checked "Add python.exe to PATH" during installation. You can re-run the installer and choose "Modify" to add it.

### Step 2: Install Opencode

[Opencode](https://opencode.ai) is an open-source, free AI coding assistant CLI with significant advantages:

- ✅ **Completely Free**: Built-in limited free models (no API Key needed); also supports 75+ providers including GLM-5.2, DeepSeek, GPT, Gemini
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

> 💡 **Zero-cost start**: Run `opencode` right after installation — the built-in limited free models (incl. the primary `deepseek-v4-flash`) work without any API Key! For stronger models, follow Step 3 to connect `deepseek-v4-pro` or `glm-5.2`.

### Step 3: Configure Models

Recommended model priority (highest first):

| Priority | Model | Notes | How to obtain |
|:---:|:---|:---|:---|
| 1 | `deepseek-v4-flash` | **Primary**, fast mode, Chinese-friendly |  bring your own key via the [DeepSeek Platform](https://platform.deepseek.com/) |
| 2 | `deepseek-v4-pro` | Secondary, 1.6T expert mode, stronger deep reasoning | Get an API Key from the [DeepSeek Platform](https://platform.deepseek.com/) |
| 3 | `glm-5.2` | Alternative, long context, Chinese-friendly | See the [GLM API docs](https://open.bigmodel.cn/dev/api); add as an OpenAI-compatible provider in Opencode |

> 💡 **How to connect**: Select a configured model via `/model` in Opencode. The primary `deepseek-v4-flash` is a built-in free model and needs no API Key. For each model's Base URL / API Key and other parameters, refer to its official API docs (DeepSeek via its platform, GLM-5.2 via the link above).

### Step 4: Install & Register Skills

After cloning this repository, register skills from the repository root:

```bash
# Register all skills
npx skills add .

# Or register a single skill
npx skills add ./teaching/dxp-thesis-reviewer
npx skills add ./teaching/dxp-syllabus-creator
npx skills add ./researching/dxp-paper-reviewer
npx skills add ./researching/resume-doc-to-personal-homepage
```

List registered skills:

```bash
npx skills list
```

> 💡 Once registered, trigger a skill in the Opencode interface via `/skill-name` (TAB to autocomplete) or natural language. See the next section for usage.

## Using Skills

In the Opencode interface, first run `/model` to select a model (the primary `deepseek-v4-flash` is recommended; `deepseek-v4-pro` / `glm-5.2` also work), then trigger a skill via `/skill-name` or natural language. Usage for each skill is described separately below.

### dxp-thesis-reviewer Usage

Undergraduate thesis review & annotation; produces a reviewed Word document with comments embedded.

1. **Create a new folder as the working directory** and place the thesis to be reviewed (supports .doc/.docx; PDF not supported) into it
2. Open a terminal in that folder: in File Explorer, click the address bar, type `cmd` and press Enter, then:

```cmd
opencode
```

3. Inside the interactive interface, run `/model` and select a model (recommend `deepseek-v4-flash`)
4. Trigger the skill (slash command + TAB autocomplete, or natural language):

```bash
/dxp-thesis-reviewer Review the thesis xxxx.docx in this folder
```

5. The process requires multiple authorizations along the way. When finished, a reviewed Word document with comments embedded will be generated in the working directory

### dxp-syllabus-creator Usage

University course syllabus generator; auto-detects the course type, matches one of 4 templates, and produces Markdown + .docx syllabi (theory courses also generate a course introduction).

1. **Create a new folder as the working directory**
2. ⚠️ **Before running the skill**, place the **training plan containing engineering-accreditation support relationships** (`.docx`) into the working directory (the skill scans the working directory, parses the training plan, and extracts course metadata and graduation-requirement indicator support relationships)
3. Open a terminal in that folder: in File Explorer, click the address bar, type `cmd` and press Enter, then:

```cmd
opencode
```

4. Inside the interactive interface, run `/model` and select a model (recommend `deepseek-v4-flash`)
5. Trigger the skill (slash command + TAB autocomplete, or natural language):

```bash
/dxp-syllabus-creator Major: Mechanical Engineering, Course: Mechanical Principles, write the syllabus based on the training plan.docx in this folder
```

6. The skill first confirms the textbook and assessment weights, then generates the syllabus; multiple authorizations are required, and a compliant .docx syllabus is output in the working directory

> 💡 The training plan should include the engineering-accreditation matrix between graduation-requirement indicators and courses. If you have a separate engineering-accreditation matrix xlsx, place it in the working directory too — the skill will preferentially extract fine-grained indicators from it.

### dxp-paper-reviewer Usage

Submission paper health check: systematically cross-audits a manuscript (four ledgers — claims vs. delivery / numbers & units / symbols — plus the five-dimension review of attribution / reproducibility / baselines / presentation) and outputs a severity-tiered numbered issue list (P0 fatal / P1·P2 soft) with an actionable fix for each item.

1. **Create a new folder as the working directory** and place the manuscript to check (supports .pdf / .docx) into it
2. Open a terminal in that folder: in File Explorer, click the address bar, type `cmd` and press Enter, then:

```cmd
opencode
```

3. Inside the interactive interface, run `/model` and select a model (recommend `deepseek-v4-flash`)
4. Trigger the skill (slash command + TAB autocomplete, or natural language):

```bash
/dxp-paper-reviewer Review article.pdf in this folder
```

5. The default full check outputs a tiered issue list; ask for a Word export (reviewer / advisor voice) when you need a document:

```bash
/dxp-paper-reviewer Review article.pdf and export the issue list as a Word doc in the reviewer voice
```

> 💡 Single-dimension queries are supported — e.g., "only check the statistics" or "focus on baseline fairness" — the skill jumps straight to that dimension. Word export requires `npm i -g docx` (see the Node dependency note under "Install Python").

### resume-doc-to-personal-homepage Usage

Turns a resume document into a deployable GitHub Pages personal homepage (self-contained static site: index.html + styles.css + images/ + files/cv.pdf, with an optional one-click Chinese/English toggle).

1. **Create a new folder as the working directory** and place the resume into it (supports .doc / .docx / .wps; no resume at hand? fill in the skill's bundled `resume-template.docx`)
2. Open a terminal in that folder: in File Explorer, click the address bar, type `cmd` and press Enter, then:

```cmd
opencode
```

3. Inside the interactive interface, run `/model` and select a model (recommend `deepseek-v4-flash`), then trigger the skill (slash command + TAB autocomplete, or natural language):

```bash
/resume-doc-to-personal-homepage Turn this resume.docx into my personal homepage and deploy it to GitHub Pages
```

4. Optionally provide a reference homepage URL (the skill reproduces its layout system, never its content); mention it if you want a Chinese/English toggle
5. After building and verifying the site at every tested width (zero horizontal overflow), the skill delivers a `homepage/` folder + deployment instructions (`<username>.github.io` or a project repo + Settings → Pages); it omits phone numbers, group photos, etc. by default — uncomment them if you really want them published

> 💡 Reading the resume relies on the local Office / document-reading toolchain (lark-cli doc tools) — follow the authorization prompts on first run; render verification needs Chrome on this machine.

### Customization

Iterate on and customize the skills using `/skill-creator` (installable from GitHub community repos with one click) based on a review / generation session. For example:

```bash
# Slash command — TAB to select
/skill-creator Based on this review session, improve dxp-thesis-reviewer to support xxxx, add xxxx checks...
```

### Skills Management & Removal

Opencode natively supports Skills management:

- Type `/skill` in the Opencode interface to browse and install community Skills
- Or use the CLI: `npx skills add .` to register local skills
- Registered skills are available via `/skill-name` immediately

Remove a skill:

```bash
npx skills remove dxp-thesis-reviewer
npx skills remove dxp-syllabus-creator
npx skills remove dxp-paper-reviewer
npx skills remove resume-doc-to-personal-homepage
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
│   └── dxp-syllabus-creator/        # University syllabus generator (2026 training plan)
│       ├── SKILL.md                 # Skill definition
│       ├── scripts/
│       │   └── generate_syllabus_docx.py # docx generator (with helpers)
│       ├── references/
│       │   ├── 培养方案解析指南.md   # Training plan parsing guide
│       │   └── docx_generation_guide.md # Detailed docx generation rules
│       ├── 示例：机械原理 课程教学大纲.docx # Primary theory template (full grading rubric)
│       ├── 1. 理论课程教学大纲的格式.docx  # Theory template (lite, fallback)
│       ├── 2. 课程设计教学大纲的格式.docx  # Course design template
│       ├── 3. 实习教学大纲的格式.docx      # Internship template
│       ├── 4. 毕业论文（设计）教学大纲的格式.docx # Thesis template
│       ├── 附件2：课程简介模板.doc   # Course-intro structure reference
│       ├── 附件4：实验项目汇总表.xlsx # Lab project summary reference
│       └── eval_set.json            # Evaluation dataset
├── researching/                     # Research-related skills
│   ├── dxp-paper-reviewer/          # Submission paper health check
│   │   ├── SKILL.md                 # Skill definition
│   │   ├── scripts/
│   │   │   ├── extract_manuscript.py # PDF/DOCX full-text extraction (with metadata)
│   │   │   └── build_review_docx.js  # Issue-list JSON → Word export
│   │   ├── references/
│   │   │   └── docx-export.md        # Word export rules (reviewer/advisor voices)
│   │   └── assets/
│   │       └── example_review.json   # Sample issue list
│   └── resume-doc-to-personal-homepage/ # Resume → GitHub Pages personal homepage
│       ├── SKILL.md                 # Skill definition
│       ├── references/
│       │   ├── reading-the-doc.md   # Reading the resume (extension routing/handshake/polling)
│       │   ├── building-the-site.md # Building the site (design tokens/photo component)
│       │   ├── verifying-render.md  # Render verification (numeric overflow probe/tall shots)
│       │   ├── shipping-pages.md    # GitHub Pages deployment (HTTPS + PAT recipe)
│       │   ├── bilingual.md         # Chinese/English toggle implementation
│       │   └── windows-gotchas.md   # Windows environment trap lookup table
│       └── assets/
│           └── resume-template.docx # Resume template (fill in when no resume at hand)
├── .gitignore
├── LICENSE
├── README.md
└── README.en.md
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `python` / `pip` command not found | Python not installed or not in PATH | Reinstall Python with "Add python.exe to PATH" checked; or manually add Python directory to system environment variables |
| `opencode` command not found | npm global path not in PATH | Restart terminal; or reinstall Node.js with "Add to PATH" checked |
| Scripts fail with `ModuleNotFoundError` | Missing Python dependencies | Run `pip install python-docx pywin32` |
| Connection timeout / 401 | Wrong API Key or network issue | Verify the key; ensure Base URL has no trailing `/v1` |
| GLM-5.2 call fails (model not found / 404) | Wrong model name or provider config | Confirm model name is `glm-5.2`; verify Base URL and auth against the [GLM API docs](https://open.bigmodel.cn/dev/api) |
| Error after model switch | Old session cached the old model name | Run `/model` inside Opencode to reselect; or exit and restart |
| Chinese text garbled | Windows terminal encoding issue | Run `chcp 65001` to switch to UTF-8 encoding |
| Opencode can't connect to free model | Network restrictions | Ensure terminal has internet access; or set proxy `set HTTPS_PROXY=http://127.0.0.1:7890` |
| dxp-syllabus-creator can't find training plan | No training plan .docx in the working directory | Place a training plan containing engineering-accreditation support relationships into the working directory before running the skill |
| dxp-thesis-reviewer can't recognize the thesis | The thesis is a PDF or not placed in the working directory | Only .doc/.docx are supported; place the thesis into the working directory before running |
| dxp-paper-reviewer Word export fails with `Cannot find module 'docx'` | The node `docx` package is missing or unresolved | Run `npm i -g docx`; if it still fails, set `$env:NODE_PATH="$(npm root -g)"` and re-run |
| dxp-paper-reviewer PDF extraction fails with `ModuleNotFoundError` | Missing PDF parsing library | Run `pip install pymupdf` (or pdfplumber / pypdf) |
| resume-doc-to-personal-homepage reading .wps/.dot reports `Unknown sheet tool` | Extension mis-routed to the sheet category | Copy the file and save the copy as .doc before reading (never modify the original) |

## Contributing

1. Fork the repository
2. Create your feature branch (`feat/xxx`)
3. Commit your changes
4. Push and create a Pull Request

## Resources

- [Opencode Official Website](https://opencode.ai) — Open-source AI coding assistant with free models
- [Opencode GitHub](https://github.com/anomalyco/opencode) — 160K+ Stars, active community
- [DeepSeek Platform](https://platform.deepseek.com/) — Primary model deepseek-v4-flash and expert-mode deepseek-v4-pro integration platform
- [GLM API Docs](https://open.bigmodel.cn/dev/api) — Alternative model GLM-5.2 integration guide

## License

[MIT License](LICENSE)
