# 第 2 步：四年行动表 HTML

产出：`XX专业四年行动表（YYYY级）.html` —— **单文件**，双击可开，Ctrl+P 直接出 A4 横向 PDF。不引外部 CSS/JS/字体，不依赖网络。

## 骨架：十节，顺序不可乱

顺序本身就是论证：先摆事实 → 再给主线 → 再落学期 → 再选方向 → 再选路径 → 再给工具 → 再划红线 → 最后避坑。

| 节 | 标题 | 形态 | 回答什么问题 |
|---|---|---|---|
| 首屏 | 专业名 + 一行定位 + facts 栏（6 格）+ 打印说明 | `.hd` + `.facts` | 这个专业是什么体量 |
| 特色 | 行业特色警示块 | `.warn` | 我们的求职坐标和计算机院不一样（见 `plan-intake.md`） |
| 一 | 四年主线：四个阶段，一条因果链 | `.phases` 四卡 + 因果链一行 | 四年怎么分段 |
| 二 | 逐学期行动表（对照培养方案课程顺序） | 8 行 × 5 列大表 | 每学期具体做什么 |
| 三 | 白名单科创竞赛计划 | ~14 行 × 6 列表 + 月份轴 | 竞赛只打这两条线 |
| 四 | 方向选择：大三上结束前必须做完的决定 | 4 卡 | 将来做嵌入式/后端/行业方向/边缘AI |
| 五 | 路径选择：保研/考研/就业 | 5.1 保研 · 5.2 考研 · 5.3 决策判据表 | 三条路在哪里撞车 |
| 六 | 用 AI 学习 | 6.1~6.6 | 把能力溢出的模型变成杠杆 |
| 七 | 网络自学 | 7.1~7.4 | 免费顶尖课程怎么排进课表 |
| 八 | 红线时间节点（错过即永久损失） | `.tl` 4 列表 + `.legend` | 哪几个时点不可逆 |
| 九 | 四年里最容易踩的坑 | 16 行 × 4 列表 + 配额协议 + 自查 | 具体避开什么行为 |
| 十 | 五条不可让步的原则 | 编号列表 | 一句话底线 |
| 页脚 | 数据来源 + 免责 | `footer` | 学分口径来自培养方案、赛程以当年通知为准 |

**首屏 facts 栏六个格子**（从培养方案直接取，是整份文档的可信度锚点）：
专业代码 / 总学分 / 课程学时 / 实践教学占比 / 学制 / 授予学位。

**逐学期表的 5 列固定为**：

| 学期 | 培养方案重点课程 | 技能与证书目标 | 项目·竞赛·实习 | 学期末验收标准 |
|---|---|---|---|---|

第 2 列是培养方案的**原文课程名**（这一列的存在就是「对照培养方案」的证据），第 5 列必须是**可判定真假的一句话**（例：「能用 C 独立写出 500 行以上的程序」），不能写成「打好基础」。

## 设计系统（直接复制，勿另起风格）

深色蓝为主体、四色语义标签、无阴影无圆角渐变，气质是「工程文档」不是「营销落地页」。

```css
:root{
  --ink:#16202b; --ink2:#48566a; --ink3:#7b8798;
  --line:#dfe4ea; --line2:#eef1f5; --bg:#ffffff; --soft:#f7f9fb;
  --blue:#2563eb;   --blue-bg:#eef4ff;
  --violet:#7c3aed; --violet-bg:#f4efff;
  --orange:#d95f18; --orange-bg:#fff2e9;
  --green:#0f8a5f;  --green-bg:#eaf7f1;
  --red:#cf3333;    --red-bg:#fdeeee;
  --navy:#1f4e79;
}
body{
  font-family:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Source Han Sans SC","Noto Sans CJK SC",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  color:var(--ink); background:var(--bg); font-size:12px; line-height:1.62;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
.page{max-width:1220px;margin:0 auto;padding:26px 30px 40px;}
```

组件类（骨架里用到的全部）：

| 类 | 用于 | 要点 |
|---|---|---|
| `.hd` / `.hd h1` / `.hd .sub` | 首屏标题区 | 下边框 2px navy |
| `.facts` / `.fact` | 六格数字 | `grid-template-columns:repeat(6,1fr)` |
| `h2` | 一级节标题 | `border-left:4px solid navy` + 左侧内缩 |
| `.phases` / `.ph` / `.ph1~.ph4` | 四阶段卡 | `.ph1~4` 只是不同颜色的 `border-top:3px` |
| `.sem` / `.sem small` | 学期单元格 | `white-space:nowrap` |
| `.key` | 关键课程 | 红色加粗 |
| `.tag` + `.t-blue/.t-violet/.t-orange/.t-green/.t-red/.t-gray` | 内联标签 | 用于竞赛类别、课程类型 |
| `.pri` + `.p-s/.p-a/.p-b/.p-c` | 竞赛优先级 | S/A/B/C，S=红 A=橙 B=绿 C=灰 |
| `.tl` + `tr.u-red/.u-orange/.u-blue` | 红线时间轴 | `td:first-child` 左边框随严重度变色 |
| `.dt` / `.dt-sub` / `.nd` / `.lbl` / `.legend` | 时间轴单元格 | 时间在左列内分行，备注与被标内容同格 |
| `.note` / `.warn` | 提示 / 警示 | 左 3px 边条 |
| `.two` / `.three` / `.card` | 多栏卡片 | 方向、路径、AI 三节 |
| `.pb` | 强制分页 | `page-break-before:always` |
| `.no-print` | 仅在屏幕上出现 | 打印说明用 |

**红线时间轴必须四列 `时间轴 | 节点 | 代价 | 对策`，且备注不能堆在时间列里。** 时间列内用 `.dt`（主时间）+ `.dt-sub`（副说明，如「约 6 月中旬」「以当年通知为准」）分行；节点列用 `.nd` 打头、`.lbl` 挂标签。这是被用户明确要求优化过的一处，别退回去。

**时间轴顺序按「季节」排，不按重要性排**：把夏令营、实习投递、保研资格公示、秋招、考研报名、毕设开题按自然年重新串一遍，否则学生看不出「同一段时间有三件事撞车」。

## 打印 CSS（整块照抄）

```css
@page{size:A4 landscape;margin:9mm;}
@media print{
  body{font-size:9.5px;}
  .page{max-width:none;padding:0;}
  h2{font-size:11.5px;margin:12px 0 6px;}
  h3{font-size:10.5px;}
  .hd h1{font-size:16px;} .hd .sub{font-size:9.5px;}
  .fact b{font-size:11px;} .fact span{font-size:8.5px;}
  table{page-break-inside:auto;}
  tr{page-break-inside:avoid;page-break-after:auto;}
  th,td{padding:4px 5px;font-size:8.5px;line-height:1.45;}
  th{font-size:8.5px;}
  .sem{font-size:9px;}
  .card,.ph,.note,.warn{page-break-inside:avoid;}
  .sec{page-break-inside:avoid;}
  .pb{page-break-before:always;}
  .tag{font-size:8px;line-height:12px;}
  .pri{font-size:8px;line-height:12px;width:30px;}
  .dt{font-size:9px;} .dt-sub{font-size:7.5px;margin-top:0;}
  .nd{font-size:9px;margin-bottom:1px;}
  .lbl{font-size:7px;line-height:10px;padding:0 3px;margin-right:3px;}
  .tl td:first-child{border-left-width:3px;}
  .legend{font-size:8px;gap:10px;}
  .no-print{display:none;}
}
```

三个关键点，少一个打印就废：
1. `@page{size:A4 landscape}` —— 逐学期表 5 列、竞赛表 6 列，纵向放不下。
2. `print-color-adjust:exact`（含 `-webkit-` 前缀）—— 不写，浏览器默认**不打印背景色**，所有标签和底纹全变白。
3. `tr{page-break-inside:avoid}` —— 不写，一行会从中间劈开，跨页断行。

## 自检清单（写完必过）

- [ ] 十节齐全，顺序与上表一致。
- [ ] 首屏 facts 六格的每个数字都能在 `plan-intake.md` 的提取结果里找到出处。
- [ ] 培养方案里每门带学分的课，都出现在某一学期的「重点课程」列里；没有课被漏掉，也没有课被安到错误学期。
- [ ] 每条「验收标准」都是可真可假的断言，没有「打好基础」「认真学习」这类软话。
- [ ] 红线时间轴的顺序按自然时间先后，不按严重度。
- [ ] 同一事实（保研率、各时点、总学分）在本文件内多次出现时数值一致。
- [ ] 文件中无外部资源引用（`http` 开头的 `src`/`href` 应只出现在文字里，不作为加载项）。
- [ ] 标签闭合：用一次正则或者浏览器打开控制台看有无解析错误。
- [ ] **修改既有 HTML 前先重读文件**——预览注入的 `data-page-node-id` 会让旧字符串失配（见 `plan-intake.md` 已知坑）。
