# Attention Is All You Need

|  |  |
|---|---|
| **原文** | `1706.03762.pdf`（arXiv:1706.03762v7，15 页） |
| **出处** | 31st Conference on Neural Information Processing Systems (NIPS 2017), Long Beach, CA, USA |
| **作者** | Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin（Google Brain / Google Research / University of Toronto） |
| **读于** | 2026-10-07 |

## 1. 动机：它要解决什么问题

**people problem** — 机器翻译质量要好，同时训练要便宜。引言的开场不是"翻译不够好"，而是"翻译好但太贵"：当时的 SOTA 靠循环网络堆出来，要更多质量就得更多算力与时间，长序列上尤其贵。省的是**训练时间和算力**。

**technical problem** — 循环网络把计算沿着符号位置展开，第 *t* 步的隐状态依赖第 *t−1* 步，**这个串行性在单个训练样本内部就阻断了并行**；序列越长越严重，因为显存限制会进一步压缩跨样本的批大小。作者点明了关键：已有工作（因式分解技巧 [21]、条件计算 [32]）确实提升了效率，但 *"The fundamental constraint of sequential computation, however, remains."* 也就是说**不是"循环能不能更快"，而是"顺序计算这个约束本身能不能不要"**。

**research question** — 能否**完全去掉循环与卷积**，只用注意力在输入与输出之间建立全局依赖，同时做到质量更好、并行度更高、训练更省？

**已有的方案为什么不够** — 两条路线都不够：① 卷积替代（Extended Neural GPU [16]、ByteNet [18]、ConvS2S [9]）确实能并行，但把两个位置关联起来所需的操作数正比于它们的距离（ConvS2S 线性、ByteNet 对数），长程依赖依然难学（§2、Table 1）；② 注意力机制本身早已存在，但 *"In all but a few cases [27], however, such attention mechanisms are used in conjunction with a recurrent network."* —— 注意力一直是循环的**配件**，从没当过主体。

> 定位：§1（PAGE 2）、§2（PAGE 2）、Table 1（PAGE 6）

## 2. 方案：它给出的答案是什么

**核心机制** — Transformer：编码器与解码器各由 N = 6 个相同层堆叠，每层是「multi-head self-attention + position-wise 全连接前馈」两个子层，每个子层外面套残差连接和 LayerNorm，所有子层与嵌入层输出维度统一为 d_model = 512；解码器多插一个对编码器输出做注意力的子层，并用掩码（softmax 输入置 −∞）阻断向左的信息流以保持自回归性。**循环和卷积一个不留**；顺序信息靠加在输入嵌入上的正弦位置编码注入（§3.1、§3.2.3、§3.5）。

**为什么相信它可行、且更好** —— 这是全文最扎实的一段，理由分四层：

1. **长程依赖的路径最短**。每层三种候选的「任意两位置间最大路径长度」：循环 O(n)、卷积 O(log_k n)、自注意力 **O(1)**；而路径越短越容易学长程依赖（§4、Table 1）。
2. **并行度最高**。每层「最少顺序操作数」：循环 O(n)，自注意力 **O(1)**（Table 1）。这正是技术问题的正解。
3. **在当时的实际数据规模下反而更便宜**。自注意力每层复杂度 O(n²·d)、循环 O(n·d²)，所以当序列长度 n < 表示维度 d 时自注意力更划算——而当时 SOTA 用的 word-piece [38]、BPE [31] 表示恰好让 n 远小于 d（§4）。
4. **两个必要修正**。scaled dot-product：dk 大时点积量级增大，会把 softmax 推进梯度极小的区域（脚注 4 用独立随机变量假设算出点积方差为 dk），故除以 √dk；multi-head：单个 head 会把不同表示子空间的信息平均掉，故投影到 h = 8 个子空间分别做注意力再拼接，每个 head 维度降到 d_model/h = 64，使总计算量与全维单头相当（§3.2.1、§3.2.2）。

**关键取舍与代价** — ① 丢掉循环意味着 O(n²) 的注意力开销随序列长度平方增长，作者提出 restricted self-attention（只看半径 r 的邻域）作为缓解，但代价是最大路径长度退化为 O(n/r)（§4）；② 顺序信息没有被消掉，只是**从架构移到了输入特征**（位置编码），且正弦与 learned 版本效果几乎相同（Table 3 行 E）；③ 位置编码用固定正弦而非学习的，作者的理由是"可能外推到比训练更长的序列"（§3.5）。

> 定位：§3.1（PAGE 3）、§3.2.1–3.2.2（PAGE 4–5）、§3.5（PAGE 6）、§4（PAGE 6–7）、Table 1（PAGE 6）

## 3. 评估：它怎么证明这个答案成立

**三种方式都有**：论证（§4 的复杂度与路径长度分析）、实现（开源 tensor2tensor，§7）、实验（§6）。

**数据集** — WMT 2014 英德（约 4.5M 句对，byte-pair，37000 共享词表）；WMT 2014 英法（36M 句对，word-piece 32000 词表）；测试集 newstest2014；消融在 newstest2013 dev 上做。另加一个非翻译任务：Penn Treebank 的 WSJ 部分（约 40K 句）做成分句法分析，以及 17M 句的半监督设置（§5.1、§6.2、§6.3）。

**baseline** — 翻译：ByteNet [18]、Deep-Att + PosUnk [39]、GNMT + RL [38]、ConvS2S [9]、MoE [32]，以及其中三个的 ensemble（Table 2）。句法分析：Vinyals & Kaiser [37]、Petrov [29]、Zhu [40]、Dyer [26→8]、McClosky [26]、Luong [23]（Table 4）。

**指标** — 翻译用 BLEU；消融用 per-wordpiece perplexity（明确声明**不可**与 per-word perplexity 比较，Table 3）；句法分析用 WSJ Section 23 的 F1；训练成本用 FLOPs 估算（训练时间 × GPU 数 × 每卡持续单精度算力，脚注 5 假设 K80 2.8 / K40 3.7 / M40 6.0 / P100 9.5 TFLOPS）。

**关键数字（用原文表述）** — 英德：big 模型 **28.4 BLEU**，比此前最好结果（含 ensemble）高 **2.0 BLEU 以上**，训练 3.5 天 / 8×P100；base 模型 27.3 BLEU，仍超过所有已发表的单模型与 ensemble，成本只有竞争对手的一个零头。英法：摘要与 Table 2 给 **41.8**，正文 §6.1 给 **41.0**（见 Q4）。成本：base 3.3·10¹⁸、big 2.3·10¹⁹ FLOPs，对比 GNMT+RL Ensemble 的 1.8·10²⁰、ConvS2S Ensemble 的 1.2·10²¹。句法分析：4 层、d_model = 1024，WSJ-only 91.3 F1、半监督 92.7 F1，除 RNN Grammar 外超过所有已报告模型（Table 4）。

**作者自己承认的收益与问题** — 收益：质量与训练成本同时占优。问题：① 单头注意力比最佳设置差 0.9 BLEU，head 数过多质量反而下降；② 减小 dk 损害质量，作者据此推测「确定兼容性并不容易，比点积更复杂的兼容函数可能有帮助」；③ label smoothing 会**损害** perplexity（模型学会更不确定），但提升 accuracy 和 BLEU（§6.2、§5.4）；④ 长序列上的 O(n²) 代价未解决（§4）；⑤ 句法分析仍不如 RNN Grammar（§6.3）。

> 定位：§5.1（PAGE 7）、§5.4（PAGE 8）、§6.1–6.3（PAGE 8–10）、Table 2（PAGE 8）、Table 3（PAGE 9）、Table 4（PAGE 10）、脚注 5（PAGE 8）

## 4. 我的分析

**判断：好 idea，而且是「减法」型的。** 论文的说服力不来自任何新发明的零件——注意力、残差、LayerNorm、前馈层全是已有的——而来自把一件长期被默认必需的东西（循环）整体拿掉，并用「复杂度 / 顺序操作数 / 路径长度」这三把尺子论证为什么可以拿掉。相比之下，同期大量工作是往架构里**加**模块，用涨点来论证价值；这篇是用一个可读的表（Table 1）证明"加"的原因本来就不成立。**先立判据再选方案**，这比结论本身更值得学。

**作者没有明说的：**

1. **同一篇论文里英法结果有两个数**。§6.1 正文写 *"our big model achieves a BLEU score of 41.0, outperforming all of the previously published single models"*，而摘要与 Table 2 都是 **41.8**。全文没有解释差异，也没有作为勘误或口径说明提出。可能来自 checkpoint averaging / 超参差异，但读者无法判断——这直接让"41.8 是新的单模型 SOTA"这一主张的支撑变模糊。
2. **最大胆的主张是全篇验证范围最窄的一条**。摘要说"the Transformer generalizes well to other tasks"，但支撑它的**只有一个**句法分析任务，而且**输给了** RNN Grammar。§6.3 原文的措辞其实很谨慎（"in contrast to RNN sequence-to-sequence models... outperforms the BerkeleyParser"），是相对于"RNN seq2seq 在小数据下做不到 SOTA"这个**较低的比较对象**成立的。摘要把它抬到了"泛化到其他任务"的高度。
3. **位置编码的选择理由从未被验证**。§3.5 说选正弦版是因为"may allow the model to extrapolate to sequence lengths longer than the ones encountered during training"；但 Table 3 行 E 显示 learned 版本结果几乎相同，而**全文没有任何长度外推实验**。这是一个被写进设计理由、却零证据支撑的取舍。
4. **跨模型的训练成本比较是混合口径**。Table 2 里 Transformer 的 FLOPs 是自估的，baseline 的 FLOPs 是**本文用统一的 TFLOPS 假设重算的**（脚注 5），而非各 baseline 原论文自报值。换算误差有多大、换回原口径结论是否仍成立，论文没有交代。成本优势的量级（1–2 个数量级）应该稳健，但"small fraction"这类措辞的精确度没有支撑。
5. **消融的统计强度未见说明**。§6.2 的消融只在 newstest2013 dev 上、只用 base 模型、未提多 seed 重复，却给出了"单头差 0.9 BLEU""head 太多质量下降"这类 0.1–1 BLEU 量级的结论。论文没有给出 dev 集规模或方差，无法判断这些差异是否在噪声内。

**最有意思的点：架构选择被一个数据规模的事实选定，而不是被直觉选定。** §4 先立三个 desiderata（每层复杂度、可并行的顺序操作数、长程依赖路径长度），再把三种层类型并排放进 Table 1，于是 O(n²·d) vs O(n·d²) 的比较落在了一个二项式上：**n < d 时自注意力更便宜**。而当时 SOTA 用的 word-piece / BPE 表示恰好保证 n 远小于 d（§4 原文）。同一条论证在今天会得出相反结论——长上下文场景下 n ≥ d，O(n²) 变成主导项，后来的稀疏/线性注意力全都在还这笔账。**这篇论文的辩护是"当 n < d 时"，不是"永远"。**

**最有争议的点：论文声称消掉了序列结构，但只是把它搬了个位置。** 模型去掉了循环与卷积这两条**天然携带顺序**的结构，然后**手工**把顺序信息作为正弦位置编码加回输入端（§3.5）。也就是说序列结构没有被消除，只是从架构移进了输入特征——那些本来需要靠结构学到的位置关系，现在变成了人为指定的函数。争议正在这里：如果位置编码的形式如此关键（论文自己承认正弦与 learned 的差异"几乎相同"，却仍选正弦），那"attention is all you need"里的 all 到底成不成立？论文把这件事放在 Table 3 的一行里一笔带过，**没有把它当作需要论证的洞见**，但它后来成了整个方向的核心问题（相对位置、旋转位置编码等一整条支线都是从这里长出来的）。

**能否落地：** 已经落地，而且落地门槛不在模型本身。§7 给出开源实现（tensor2tensor），此后成为大模型的基础架构。论文自己给出的最低条件很清楚：**8 张 P100 卡 + 12 小时**就能训出 base 模型（§5.2）。所以真正的门槛是算力、平行语料规模和一套成熟的 BLEU 评测流程——而不是架构复杂度。这也是它能迅速被复现、被替换掉循环的原因之一。

> 定位：§6.1 的 41.0（PAGE 8）与摘要 / Table 2 的 41.8（PAGE 1、PAGE 8）；"generalizes well" 摘要（PAGE 1）vs §6.3 与 Table 4（PAGE 9–10）；§3.5 的外推理由与 Table 3 行 (E)（PAGE 6、PAGE 9）；脚注 5 的 TFLOPS 假设（PAGE 8）；§6.2 消融（PAGE 8–9）；§4 的 n < d 论证（PAGE 6–7）；§3.5 位置编码（PAGE 6）

## 5. 贡献

**洞见 / idea** — 完全由注意力构成、不含循环与卷积的编码器-解码器架构（Transformer）；scaled dot-product attention；multi-head attention。

**软件** — 开源实现 tensor2tensor（§7 给出仓库地址）。

**实验技术 / 评测方法** — ① 用「每层复杂度 / 最少顺序操作数 / 最大路径长度」三元组横向比较层类型（Table 1、§4）——这个比较框架本身就是可复用资产，不只适用于本文的架构；② 以固定算力预算（8×P100、3.5 / 0.5 天）报告 SOTA 的实证范式。

**领域综述** — §2 Background 对循环、卷积替代方案、自注意力、记忆网络四条线的梳理，以及"注意力此前一直是循环的配件"这一判断。

**声称与实做是否一致：**

- **高度一致**：两个翻译任务上 base 与 big 都超过所有已发表单模型，big 在英德上还超过 ensemble；成本低 1–2 个数量级；给出的三个具体机制（scaled dot-product、multi-head、正弦位置编码）都有对应的消融或论证。
- **打折**：摘要的 "generalizes well to other tasks" 只有单个任务支撑，且在该任务上未达 SOTA（见 Q4-2）。更准确的说法是"在没有任务专用调参的情况下**接近**领域 SOTA"，这一点 §6.3 正文其实写对了。
- **是工具而非复现包**：§7 说的是"We used to train and evaluate"的代码，不是完整复现脚本。对复现者而言这是个需要留意的边界。

> 定位：§2（PAGE 2）、§4 与 Table 1（PAGE 6）、§7 与代码链接（PAGE 10）、抽象主张（PAGE 1）

## 6. 未来方向

**作者指出的：** ① 把注意力限制到局部邻域以高效处理大输入输出（§4 提出 neighborhood r，路径长度 O(n/r)；§7 重申要研究 local / restricted attention）；② 扩展到文本以外的模态：图像、音频、视频（§7）；③ 让生成过程更少串行（§7）；④ §6.2 提出「更复杂的兼容函数可能优于点积」这条线索。

> 定位：§4 末与 §7（PAGE 7、PAGE 10）、§6.2（PAGE 9）

**我读出来的：**

- **位置编码的外推性**：作者选正弦版的唯一理由是"可能外推到更长序列"，但完全没做实验。这是现成的、代价极低的验证（用超过训练长度的推理测质量衰减）。
- **O(n²) 的账怎么还**：restricted attention 把复杂度换成 O(n·r)，但 Table 1 显示路径长度同时退化到 O(n/r)。论文没给出 r 的取值与质量损失曲线——这一步空着，而它正是所有后续高效注意力工作的起点。
- **成本口径统一**：把 Table 2 里 baseline 的成本换回各自原论文自报口径重算，才能知道成本优势的可比性边界（见 Q4-4）。
- **消融缺统计**：base 模型架构超参之外，训练层面的选择（warmup 4000 步、label smoothing、dropout）与模型大小的交互完全没有交叉消融，而 warmup 公式（Eq. 3）本身就是个强假设。
- **从"层间比较"到"输入表示"**：Table 1 的比较框架只看层类型，没有把序列长度与表示维度的关系（n vs d）作为变量做实验——而 §4 的整条论证恰恰建立在这个不等式上。

## 7. 遗留问题

1. **英法结果到底是 41.0 还是 41.8？** §6.1 正文与摘要 / Table 2 不一致，且没有说明是 checkpoint averaging 还是超参差异造成的。哪个是最终报告值？（针对 §6.1 与 Table 2、摘要）
2. **0.9 BLEU 这类结论落在噪声里吗？** §6.2 称 "single-head attention is 0.9 BLEU worse than the best setting"，但消融只在 newstest2013 dev 上、单次运行。dev 集多大？同配置多 seed 的方差是多少？（针对 §6.2 与 Table 3 行 A）
3. **restricted self-attention 的折中曲线在哪里？** §4 说把邻域限制到 r 可降低计算量，但路径长度退化为 O(n/r)，且没给 r 的取值与相应质量损失。r 取多少时这个退化开始吃掉长程依赖的收益？（针对 §4 与 Table 1 的 restricted 行）
4. **Table 2 的跨模型成本比较成立吗？** baseline 的 FLOPs 是用本文的统一 TFLOPS 假设重算的（脚注 5），不是各自原论文的自报值。换算误差量级多大？换回原口径后 1–2 个数量级的优势是否仍然成立？（针对 Table 2 与脚注 5）
5. **正弦位置编码的外推优势有没有证据？** Table 3 行 (E) 显示 learned 版本结果几乎相同（4.92/25.7 vs 4.92/25.8），而选择正弦的理由是"可能外推到更长序列"。有没有做过超过训练长度的推理实验？（针对 §3.5 与 Table 3 行 E）
6. **"泛化到其他任务"依赖多少偶然配置？** §6.3 明确说 "we performed only a small number of experiments to select the dropout... all other parameters remained unchanged"——即句法分析的超参几乎直接从翻译模型搬来。换一套专门调过的超参，结论会变吗？（针对 §6.3）

## 8. Take-away

它把「序列必须按顺序处理」从架构的必需品降级成了一个可以塞进输入特征的选择——一旦顺序信息变成位置编码，模型剩下的约束就只有算力和数据。

> 复核：Q1 三层齐全且给了已有方案的不足；Q2 的可行性与「为什么更好」落到 Table 1 的三项指标并列出代价；Q3 的 baseline / 数据集 / 指标全部落名并给出原文数字；Q4 五条均为作者未明说项，含一处数据不一致、一处主张与证据范围不匹配；Q6 两条线都在；Q7 六条各带指向且与 Q4 不重复；Q8 单句且未引用标题或摘要原句。
