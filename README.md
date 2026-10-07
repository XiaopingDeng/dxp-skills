# dxp-skills

自用技能仓库，涵盖论文审核、代码开发、教学研究等场景。

## 目录

* [技能列表](#技能列表)
* [安装与注册技能](#step-4-安装与注册技能)
* [Skills 管理与移除](#skills-管理与移除)
* [许可证](#许可证)

## 技能列表

|技能名称|分类|说明|
|-|-|-|
|**dxp-thesis-reviewer**|`teaching/`|本科毕业论文审核与批注(v2.1)：自动体检 + 三档批注密度 + AI幻觉术语检测 + OOXML 批注写入 + 答辩问题及参考答案独立文档生成，支持 .doc/.docx|
|**dxp-syllabus-creator**|`teaching/`|高校课程教学大纲智能编制（配套 2026 版培养方案）：理论课/课程设计/实习实训/毕业论文（设计）四类模板自动识别；理论课使用含完整评分标准表的示例大纲作模板、替换内容生成 docx 并配套生成课程简介，其余三类按对应模板填充，输出格式合规的 .docx|
|**dxp-paper-reviewer**|`researching/`|投稿论文体检（v1.0）：四本账系统性对账（承诺 vs 交付 / 数字 / 量纲 / 符号）+ 五维排查（归因 / 复现 / 基线 / 呈现），输出按严重度分级的编号问题清单（P0 硬伤 / P1·P2 软伤），每条附可执行改法；支持导出 Word（审稿人 / 导师两种口吻），输入 .pdf/.docx|
|**dxp-resume-doc-to-personal-homepage**|`researching/`|简历文档（.doc/.docx/.wps）→ 可部署的 GitHub Pages 个人主页：自包含静态站点（index.html + styles.css + images/ + files/cv.pdf），可选中英文一键切换，逐宽度数值化验证无横向溢出，默认隐私处理（手机号 / 群照不发布）|
|**dxp-paper-reading**|`researching/`|PDF 论文 → 逐篇结构化阅读笔记：按 Griswold《How to Read an Engineering Research Paper》八问框架（动机 / 方案 / 评估 / 你的分析 / 贡献 / 未来方向 / 遗留问题 / take-away）逐篇输出 Markdown 笔记，每个答案落回原文定位，缺失内容标注「原文未提供」，支持多篇批量|
|**dxp-grad-resume-builder**|`teaching/`|本科应届生简历撰写与评审双分支：撰写分支按目标岗位与 JD 生成可投递简历（Markdown + 可打印 HTML）与配套技能学习路线图；评审分支以学业指导老师角色对已有简历（PDF/图片/文本）逐项定级（P0/P1/P2）并给出改写示范与面试追问预判，原文档零改动|
|**dxp-engineering-major-four-year-plan**|`teaching/`|工科专业新生教育双交付：先取「口径」（学校层次 / 保研率 / 雇主圈层 / 地域产业）再读培养方案，产出《XX专业四年行动表（YYYY级）.html》（A4 横向可打印，逐年逐学期规划，学生用）与《XX专业开学第一课.md》（一级标题=一页，导入飞书以演示模式播放，专业主任用），两份共用同一事实底座；输入专业名称 + 培养方案（docx / 课程体系示意图 / PDF / 文本）即可触发|

更多技能正在开发中。分类目录：

* `coding/` — 编码相关技能
* `researching/` — 研究相关技能
* `teaching/` — 教学相关技能

### 安装与注册技能

将此仓库克隆到本地后，在仓库根目录执行注册：

```bash
# 注册所有技能
npx skills add .

# 或注册单个技能
npx skills add ./teaching/dxp-thesis-reviewer
npx skills add ./teaching/dxp-syllabus-creator
npx skills add ./researching/dxp-paper-reviewer
npx skills add ./researching/dxp-resume-doc-to-personal-homepage
npx skills add ./researching/dxp-paper-reading
npx skills add ./teaching/dxp-grad-resume-builder
npx skills add ./teaching/dxp-engineering-major-four-year-plan
```

查看已注册技能：

```bash
npx skills list
```

### Skills 管理与移除

&#x20;AI智能体支持 Skills 管理：

* 在交互界面中，输入 `/skill` 即可浏览和安装社区 Skills
* 或使用命令行：`npx skills add .` 注册本地技能
* 已注册的技能即可通过 `/skill-name` 直接触发

移除技能：

```bash
npx skills remove dxp-thesis-reviewer
npx skills remove dxp-syllabus-creator
npx skills remove dxp-paper-reviewer
npx skills remove dxp-resume-doc-to-personal-homepage
npx skills remove dxp-paper-reading
npx skills remove dxp-grad-resume-builder
npx skills remove dxp-engineering-major-four-year-plan
```

## 许可证

[MIT License](LICENSE)

