# 导出 Word：JSON 结构、口吻与校验

把问题清单写成 JSON，交给 `scripts/build_review_docx.js` 生成 docx。

```
node scripts/build_review_docx.js review.json 输出.docx
```

依赖：`npm i -g docx`（本机已装于全局 node_modules）。若 `require("docx")` 失败，先设
`NODE_PATH` 指向全局 node_modules，例如：

```powershell
$env:NODE_PATH="$(npm root -g)"; node scripts/build_review_docx.js review.json 输出.docx
```

## JSON 结构

```json
{
  "title": "关于你投稿稿件的修改意见",
  "meta": ["论文：<题名>", "稿件：<文件名>（N 页，<模板>）｜作者：<列表>", "日期：YYYY 年 M 月 D 日"],
  "note": "说明：每一条问题后面我都用红字写了怎么改，你照着一条条过。",
  "tone": "mentor",
  "blocks": [
    { "type": "h1", "text": "你这篇的整体思路（我先复述一遍）" },
    { "type": "p",  "text": "一段话复述……" },
    { "type": "bullets", "items": ["场景与矛盾：……", "问题建模：……"] },
    { "type": "table",
      "widths": [3000, 6026],
      "header": ["项目", "数值"],
      "rows": [["空域", "500 × 500 × 100"], ["速度", "0.6 ~ 1.0 unit / step"]] },
    { "type": "issue",
      "heading": "1. 标题和正文对不上（这条最要紧）",
      "paras": ["问题正文第一段", "问题正文第二段"],
      "bullets": ["§1：“……”", "Remark 1：“……”"],
      "suggest": ["修改建议第一段（自动加红色标签）", "修改建议续段"] }
  ]
}
```

字段说明：

| 字段 | 作用 |
|---|---|
| `tone` | `"reviewer"` 或 `"mentor"`，决定红字标签用词 |
| `blocks[].type` | `h1` / `h2` / `p` / `bullets` / `table` / `issue` |
| `issue.paras` | 问题陈述，可多段 |
| `issue.bullets` | 问题陈述里的引文或子项，可省略 |
| `issue.suggest` | **红字**修改建议；第一段自动带标签，其余为续段 |

排版参数已内置：A4、1 英寸页边距、正文 Microsoft YaHei 10.5pt、1.5 倍行距、标题深蓝
（`1F3864` / `2E5C8A`）、建议红字 `FF0000`、页脚居中页码。`table.widths` 会按内容宽度
（9026 DXA）自动等比缩放，无需手算。

## 两种口吻

口吻只改措辞，不改事实与结论。同一份 JSON 换 `tone` 即得另一版；也可复制成两个 JSON，
分别写两套措辞、生成两个文件。

| | 审稿人 `reviewer` | 导师 `mentor` |
|---|---|---|
| 文档标题 | 关于投稿稿件的审阅意见 | 关于你投稿稿件的修改意见 |
| 思路概括标题 | 论文整体思路概括 | 你这篇的整体思路（我先复述一遍） |
| 首节标题 | 总体判断 | 先说整体印象 |
| 章节标题 | 一、致命问题／二、方法层面／三、实验与统计／四、写作与格式 | 一、最要紧的问题／二、方法设计上还要补的地方／三、实验和统计上要补的地方／四、写作和格式上的问题 |
| 清单标题 | 五、优先修改清单 | 五、咱们的修改顺序 |
| 末节标题 | 结论 | 最后交代几句 |
| 红字标签 | 【修改建议】 | 【我建议】 |
| 人称 | 本文／作者／该问题 | 你这篇／你／咱们 |
| 判词 | 客观直陈（"标题与内容不符"） | 先肯定底子再点问题（"标题和正文对不上，这条最要紧"） |
| 开头 | 直接给总评 | 先说好的地方，再给三条硬伤 |

导师口吻的两条硬要求：**先说底子**（题目/模型/局限陈述中值得肯定的部分），**把判词说软但问题一条不减**（"我猜是表 1 写错了" 而非 "属于虚假承诺"）。

## 校验

生成后必跑一遍：

```python
import zipfile, re, xml.etree.ElementTree as ET
z = zipfile.ZipFile(out)
for n in z.namelist():                      # 1) XML 全部可解析
    if n.endswith(('.xml', '.rels')):
        ET.fromstring(z.read(n))
d = z.read('word/document.xml').decode('utf-8')
txt = re.sub(r'<[^>]+>', '', d)
assert txt.count('【修改建议】') or txt.count('【我建议】')   # 2) 标签数 == 问题数
assert not [c for c in txt if ord(c) > 0xFFFF]               # 3) 无 BMP 外字符（易缺字形）
```

检查项：

1. 所有 `.xml` / `.rels` 可被 `ElementTree` 解析
2. 红字标签数 == 问题条数
3. 无 BMP 外字符——数学花体（𝒦 / 𝔼 / 𝒩）在 Microsoft YaHei 中缺字形，会渲染成方框，
   一律换成 ASCII（`K_c` / `E` / `N`）
4. 一级标题数 == 章节数 + 1（思路概括）；二级标题数 == 问题条数

## 完整示例

一份可运行的最小样例见 `assets/example_review.json`：

```
node scripts/build_review_docx.js assets/example_review.json /tmp/demo.docx
```
