# PDF 取文：故障 → 原因 → 修法

本页只在 `scripts/extract_pdf.py` 的 health 行报错、或 dump 明显不对时才需要翻。
两类环境事实先记住：

- **Read 工具不读 PDF。** 它按扩展名把 `.pdf` 当二进制拒掉（`Cannot display content of
  binary file`）。取文只能靠脚本，不要反复试 Read。
- **引擎决定一切。** 同一个 PDF，PyMuPDF 抽出来是 `Provided proper attribution`，
  pdfminer 系的引擎（markitdown、pdfplumber）抽出来是 `Providedproperattribution`。

| 症状 | 原因 | 修法 |
|---|---|---|
| `Cannot display content of binary file` | Read 按扩展名判二进制 | 走 `scripts/extract_pdf.py`；不要再试 Read |
| 词粘成一片（`Providedproperattributionisprovided`、`GoogleBrain`） | 该 PDF 字体缺空格字形，pdfminer 系抽取器按字形边界拼词 | 用 PyMuPDF。本脚本默认 fitz，health 行会以「25 字母以上连写串的占比」报出来；占比 >1% 就是中招 |
| 每页平均 <200 字符 / dump 几乎为空 | 扫描件或图片型 PDF，没有文本层 | 走 OCR（`pdf` / `pdfkit-py` 技能），或向用户索取带文本层的版本。**不要靠领域知识补内容** |
| 章节号单独占一行（`3.1` 与 `Encoder and Decoder Stacks` 分行） | 版面里编号与标题是两个独立文本块 | 正常现象，读成 `§3.1`；不要为此改脚本，合并启发式会误伤脚注编号和页码 |
| 表格拆成一格一行（`Model` / `BLEU` / `ByteNet [18]` / `23.75` …） | PDF 表格只有坐标没有结构 | 正常现象。引用用表号（`Table 2`）加原文表述；要精确数值就回原 PDF 看图 |
| 双栏论文两栏串行、顺序错乱 | 分栏没有结构信息，抽取器按位置排序 | 靠 `===== PAGE n =====` 逐页读，用页码而不是"段"定位 |
| `ModuleNotFoundError: No module named 'fitz'` | 解释器没装 PyMuPDF | 换解释器。本机托管解释器（`C:\Users\admin\.workbuddy\binaries\python\...`）只有 openpyxl；**PyMuPDF 在 `D:\dev\Python\Python312\python.exe`** |
| 脚本报「PDF 已加密」 | 有打开密码 | 向用户索取无密码版本；不要试图爆破 |
| 公式变成乱码或错位 | 数学字体没有对应 Unicode 映射 | 别硬读。用周围的文字描述公式在做什么，定位到公式编号（`Eq. 3`）即可 |

## 怎么判断 dump 能不能用

三个数够了：**页数对得上 PDF 的页数**、**每页平均字符数在 1000 以上**（正常论文约 2000–3000）、
**连写串占比 <1%**。脚本把这三个都打印出来了。

拿不准就往后翻一页看正文——读起来像正常英文句子就可以开工，像电报体就不行。
