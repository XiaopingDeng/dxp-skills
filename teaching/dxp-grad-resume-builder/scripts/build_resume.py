#!/usr/bin/env python3
"""
build_resume.py — 简历 / 学习路线图 / 评审报告 渲染引擎

读取一份「模型」JSON（由WorkBuddy 在分析用户基本信息 / 目标岗位 / 岗位要求 /
培养方案后生成；评审分支则由简历原件 + JD 推出），渲染为：
  - resume.md      标准 Markdown 简历
  - resume.html    单页可打印 HTML 简历
  - roadmap.md     学习路线图文档
  - review.md      评审报告 Markdown
  - review.html    评审报告 HTML（可打印）

用法:
  python build_resume.py <model.json> [--out <输出目录>]

JSON 模型字段（缺失字段会被安全跳过）:
{
  "name": "姓名",
  "contact": "电话 · 邮箱 · 城市 · [GitHub] · [政治面貌]",
  "intent": "目标岗位",
  "education": {
    "school": "...", "college": "...", "major": "...", "degree": "本科",
    "period": "2022.09 – 2026.06", "gpa": "3.7/4.0", "rank": "前 10%",
    "courses": ["课程1", "课程2"], "extra": "可选补充"
  },
  "skills": [ {"category":"编程语言","items":["..."],"gap":false}, ... ],
  "sections": [ {"type":"projects","title":"项目经历","items":[
      {"name":"项目","role":"角色","period":"时间","bullets":["..."]}
  ]}, ... ],
  "awards": ["奖项1","奖项2"],
  "summary": "自我评价 ...",

  # 学习路线图（可选）
  "roadmap": {
    "total_months": 3, "weekly_hours": 12,
    "timeline": [ {"phase":"L0 入门","weeks":"1-3","skills":"...","milestone":"..."} ],
    "cards": [ {"skill":"技能","why":"...","levels":[
        {"level":"L0 入门","weeks":"2 周","goal":"...","resources":"...","check":"..."}
    ]} ],
    "gap_table": [ {"gap":"...","card":"...","eta":"X 周"} ]
  },

  # 评审报告（可选，评审分支专用；含此字段即渲染 review.*）
  "review": {
    "target": "嵌入式软件工程师",              # 被评审简历的目标岗位
    "subject": "姓名 · 学校 · 专业 · 届别",     # 抬头行
    "verdict": "综合评分 78 / 100 —— 一句话结论",
    "scores": [ {"dim":"项目含金量","score":"22/25","note":"判分依据"} ],
    "verdict_paragraphs": ["总体结论段落..."],
    "sections": [ {"level":"P0","title":"...","items":[
        {"title":"问题标题", "where":"位置（哪个板块）",
         "why":"为什么扣分", "before":"现", "after":"建议",
         "pending": ["需本人核实的事项"]}
    ]} ],
    "questions": [ {"q":"追问问题", "a":"该准备的答案要点"} ],
    "actions": [ {"order":1,"action":"动作","hours":"20 分钟","value":"最高"} ],
    "checklist": ["自查项1"],
    "disclaimer": "文末声明，默认给出未修改原简历的措辞"
  }
}
"""
import sys
import json
import html
import argparse
from pathlib import Path

CSS = """
:root{--ink:#1f2329;--sub:#5b6168;--line:#e3e6eb;--accent:#2f6df6;--bg:#fff;--soft:#f5f7fa;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:#eceff3;line-height:1.6;padding:24px;}
.page{max-width:820px;margin:0 auto;background:var(--bg);padding:40px 48px;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.08);}
header{border-bottom:2px solid var(--accent);padding-bottom:14px;margin-bottom:18px;}
.name{font-size:28px;font-weight:700;letter-spacing:2px;}
.contact{color:var(--sub);font-size:13px;margin-top:6px;}
.intent{color:var(--accent);font-size:14px;margin-top:6px;font-weight:600;}
section{margin:18px 0;}
h2{font-size:16px;color:var(--accent);border-left:4px solid var(--accent);padding-left:8px;margin-bottom:10px;letter-spacing:1px;}
.edu-title{font-weight:600;}
.meta{color:var(--sub);font-size:13px;}
ul{list-style:none;padding-left:2px;}
li{position:relative;padding-left:16px;margin:6px 0;font-size:14px;}
li::before{content:"•";color:var(--accent);position:absolute;left:2px;}
.skill-cat{font-weight:600;display:inline-block;min-width:84px;}
.tag{display:inline-block;background:var(--soft);color:var(--sub);font-size:12px;padding:1px 8px;border-radius:10px;margin:2px 4px 2px 0;}
.exp-head{font-weight:600;}
.exp-meta{color:var(--sub);font-size:13px;}
.gap{color:#c0392b;font-size:13px;}
footer{margin-top:24px;color:#9aa0a8;font-size:12px;text-align:center;}
@media print{body{background:#fff;padding:0;}.page{box-shadow:none;border-radius:0;max-width:100%;padding:0 8mm;}}

/* ---- 评审报告样式 ---- */
.rv-head{border-bottom:3px solid var(--ink);padding-bottom:12px;margin-bottom:16px;}
.rv-title{font-size:21px;font-weight:700;letter-spacing:.5px;}
.rv-sub{color:var(--sub);font-size:13px;margin-top:5px;line-height:1.7;}
.rv-verdict{display:inline-block;margin-top:9px;padding:4px 12px;border-radius:3px;
  background:#eef2ff;color:#1d4ed8;font-weight:700;font-size:13px;}
.rv-h2{font-size:16px;font-weight:700;margin:26px 0 10px;padding-left:10px;
  border-left:5px solid var(--ink);}
.rv-h3{font-size:14px;font-weight:700;margin:16px 0 7px;color:#3d4557;}
.rv-cards{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0;}
.rv-card{flex:1 1 140px;border:1px solid var(--line);border-radius:4px;
  padding:10px 13px;background:var(--soft);}
.rv-card b{display:block;font-size:23px;line-height:1.25;font-weight:700;}
.rv-card span{font-size:12px;color:var(--sub);}
.rv-item{border:1px solid var(--line);border-left:4px solid var(--line);
  border-radius:3px;padding:10px 14px;margin:10px 0;}
.rv-item.p0{border-left-color:#b3261e;background:#fdecea;}
.rv-item.p1{border-left-color:#9a6200;background:#fdf3e0;}
.rv-item.p2{border-left-color:#0f7b52;background:#e8f6ef;}
.rv-item h4{margin:0 0 5px;font-size:14px;font-weight:700;}
.rv-item p{margin:4px 0;}
.rv-lv{display:inline-block;font-size:11.5px;font-weight:700;color:#fff;
  padding:1px 7px;border-radius:2px;margin-right:7px;vertical-align:2px;}
.rv-lv.p0{background:#b3261e;} .rv-lv.p1{background:#9a6200;} .rv-lv.p2{background:#0f7b52;}
.rv-before{background:#fdecea;border-left:3px solid #b3261e;padding:6px 11px;
  margin:6px 0;font-size:13px;}
.rv-after{background:#e8f6ef;border-left:3px solid #0f7b52;padding:6px 11px;
  margin:6px 0;font-size:13px;}
.rv-lbl{font-weight:700;font-size:11.5px;letter-spacing:1px;display:block;margin-bottom:2px;}
.rv-before .rv-lbl{color:#b3261e;} .rv-after .rv-lbl{color:#0f7b52;}
.rv-pending{background:var(--soft);border:1px dashed var(--sub);border-radius:3px;
  padding:6px 11px;margin:6px 0;font-size:13px;}
.rv-qa{border:1px solid var(--line);border-radius:3px;margin:8px 0;}
.rv-qa .q{background:var(--ink);color:#fff;padding:5px 12px;font-weight:700;font-size:13px;}
.rv-qa .a{padding:8px 12px;font-size:13px;}
.rv-foot{margin-top:26px;padding-top:11px;border-top:1px solid var(--line);
  font-size:11.5px;color:var(--sub);line-height:1.7;}
.rv-table{width:100%;border-collapse:collapse;margin:11px 0;font-size:13px;}
.rv-table th,.rv-table td{border:1px solid var(--line);padding:6px 9px;
  text-align:left;vertical-align:top;}
.rv-table th{background:var(--soft);font-weight:700;}
.rv-num{text-align:center;font-weight:700;white-space:nowrap;}
.rv-checks{list-style:none;padding-left:2px;}
.rv-checks li{padding-left:20px;position:relative;margin:5px 0;font-size:13px;}
.rv-checks li::before{content:"□";position:absolute;left:0;color:var(--accent);font-weight:700;}
"""


def esc(x):
    return html.escape(str(x), quote=True)


def render_md(m):
    L = []
    L.append(f"# {m.get('name','姓名')}")
    if m.get('contact'):
        L.append(m['contact'])
    if m.get('intent'):
        L.append(f"\n**求职意向：{m['intent']}**")
    L.append("\n---")

    edu = m.get('education') or {}
    if edu:
        L.append("\n## 教育背景")
        title = " · ".join(filter(None, [edu.get('school'), edu.get('college'),
                                          edu.get('major'), edu.get('degree')]))
        L.append(f"**{title}**  {edu.get('period','')}")
        meta = []
        if edu.get('gpa'):
            meta.append(f"GPA：{edu['gpa']}")
        if edu.get('rank'):
            meta.append(f"专业排名：{edu['rank']}")
        if meta:
            L.append("- " + " ｜ ".join(meta))
        if edu.get('courses'):
            L.append(f"- 核心课程（与岗位相关）：{'、'.join(edu['courses'])}")
        if edu.get('extra'):
            L.append(f"- {edu['extra']}")

    if m.get('skills'):
        L.append("\n## 专业技能")
        for s in m['skills']:
            cat = s.get('category', '技能')
            items = s.get('items', [])
            if s.get('gap'):
                L.append(f"- **{cat}（待补强）**：" + "；".join(items))
            else:
                L.append(f"- **{cat}**：" + "；".join(items))

    for sec in m.get('sections', []):
        L.append(f"\n## {sec.get('title','经历')}")
        for it in sec.get('items', []):
            head = " · ".join(filter(None, [it.get('name'), it.get('role'), it.get('period')]))
            L.append(f"**{head}**")
            for b in it.get('bullets', []):
                L.append(f"- {b}")

    if m.get('awards'):
        L.append("\n## 获奖与证书")
        for a in m['awards']:
            L.append(f"- {a}")

    if m.get('summary'):
        L.append("\n## 自我评价")
        L.append(f"- {m['summary']}")

    return "\n".join(L) + "\n"


def render_html(m):
    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>简历 · {esc(m.get('name',''))}</title><style>{CSS}</style></head>
<body><div class="page"><header>""")
    parts.append(f'<div class="name">{esc(m.get("name","姓名"))}</div>')
    if m.get('contact'):
        parts.append(f'<div class="contact">{esc(m["contact"])}</div>')
    if m.get('intent'):
        parts.append(f'<div class="intent">求职意向：{esc(m["intent"])}</div>')
    parts.append("</header>")

    edu = m.get('education') or {}
    if edu:
        parts.append("<section><h2>教育背景</h2>")
        title = " · ".join(filter(None, [edu.get('school'), edu.get('college'),
                                          edu.get('major'), edu.get('degree')]))
        parts.append(f'<div class="edu-title">{esc(title)}</div>')
        meta = []
        if edu.get('period'):
            meta.append(esc(edu['period']))
        if edu.get('gpa'):
            meta.append(f"GPA：{esc(edu['gpa'])}")
        if edu.get('rank'):
            meta.append(f"专业排名：{esc(edu['rank'])}")
        if meta:
            parts.append(f'<div class="meta">{" ｜ ".join(meta)}</div>')
        if edu.get('courses'):
            parts.append(f'<div class="meta">核心课程（与岗位相关）：{esc("、".join(edu["courses"]))}</div>')
        if edu.get('extra'):
            parts.append(f'<div class="meta">{esc(edu["extra"])}</div>')
        parts.append("</section>")

    if m.get('skills'):
        parts.append("<section><h2>专业技能</h2><ul>")
        for s in m['skills']:
            cat = esc(s.get('category', '技能'))
            items = "；".join(esc(i) for i in s.get('items', []))
            if s.get('gap'):
                parts.append(f'<li><span class="skill-cat">{cat}（待补强）</span> <span class="gap">{items}</span></li>')
            else:
                parts.append(f'<li><span class="skill-cat">{cat}</span> {items}</li>')
        parts.append("</ul></section>")

    for sec in m.get('sections', []):
        parts.append(f'<section><h2>{esc(sec.get("title","经历"))}</h2>')
        for it in sec.get('items', []):
            head = " · ".join(filter(None, [it.get('name'), it.get('role'), it.get('period')]))
            parts.append(f'<div class="exp-head">{esc(head)}</div><ul>')
            for b in it.get('bullets', []):
                parts.append(f'<li>{esc(b)}</li>')
            parts.append("</ul></section>")

    if m.get('awards'):
        parts.append("<section><h2>获奖与证书</h2><ul>")
        for a in m['awards']:
            parts.append(f'<li>{esc(a)}</li>')
        parts.append("</ul></section>")

    if m.get('summary'):
        parts.append(f'<section><h2>自我评价</h2><ul><li>{esc(m["summary"])}</li></ul></section>')

    parts.append('<footer>本简历由 dxp-grad-resume-builder 技能生成 · 所有内容须真实可核</footer>')
    parts.append("</div></body></html>")
    return "\n".join(parts)


def render_roadmap(m):
    rm = m.get('roadmap') or {}
    if not rm:
        return None
    L = []
    L.append(f"# 学习路线图：{m.get('name','姓名')} · 目标岗位 {m.get('intent','')}")
    meta = []
    if rm.get('total_months'):
        meta.append(f"求职倒计时：{rm['total_months']} 个月")
    if rm.get('weekly_hours'):
        meta.append(f"每周投入：{rm['weekly_hours']} 小时")
    if meta:
        L.append("> " + " ｜ ".join(meta))
    L.append("")

    if rm.get('timeline'):
        L.append("## 总览时间线")
        L.append("| 阶段 | 时间 | 主攻技能 | 里程碑（可写进简历的产出） |")
        L.append("|------|------|----------|----------------------------|")
        for t in rm['timeline']:
            L.append(f"| {t.get('phase','')} | {t.get('weeks','')} | {t.get('skills','')} | {t.get('milestone','')} |")
        L.append("")

    if rm.get('cards'):
        L.append("## 逐技能学习卡")
        for c in rm['cards']:
            L.append(f"\n### {c.get('skill','技能')}")
            if c.get('why'):
                L.append(f"- **为什么需要**：{c['why']}")
            for lv in c.get('levels', []):
                L.append(f"\n- **{lv.get('level','')}（{lv.get('weeks','')}）**")
                if lv.get('goal'):
                    L.append(f"  - 目标：{lv['goal']}")
                if lv.get('resources'):
                    L.append(f"  - 资源：{lv['resources']}")
                if lv.get('check'):
                    L.append(f"  - 验收：{lv['check']}")

    if rm.get('gap_table'):
        L.append("\n## 缺口 → 路线图 对照表")
        L.append("| 简历缺口 | 对应路线图条目 | 预计补齐时间 |")
        L.append("|----------|----------------|--------------|")
        for g in rm['gap_table']:
            L.append(f"| {g.get('gap','')} | {g.get('card','')} | {g.get('eta','')} |")

    return "\n".join(L) + "\n"


def render_review_md(m, rv):
    """渲染评审报告 Markdown。"""
    L = []
    L.append("# 简历评价报告")
    if rv.get('subject'):
        L.append(f"> {rv['subject']}")
    if rv.get('target'):
        L.append(f"> 目标岗位：{rv['target']}")
    L.append("")
    if rv.get('verdict'):
        L.append(f"**{rv['verdict']}**")
        L.append("")

    if rv.get('verdict_paragraphs'):
        for p in rv['verdict_paragraphs']:
            L.append(p)
            L.append("")

    if rv.get('scores'):
        L.append("## 分项评分")
        L.append("| 维度 | 得分 | 判分依据 |")
        L.append("|------|------|----------|")
        for s in rv['scores']:
            L.append(f"| **{s.get('dim','')}** | {s.get('score','')} | {s.get('note','')} |")
        L.append("")

    order = {'P0': 0, 'P1': 1, 'P2': 2}
    secs = sorted(rv.get('sections', []), key=lambda x: order.get(x.get('level', 'P2'), 3))
    titles = {'P0': 'P0 — 投递前必修', 'P1': 'P1 — 显著影响通过率', 'P2': 'P2 — 加分项'}
    for sec in secs:
        lv = sec.get('level', '')
        head = titles.get(lv, lv)
        L.append(f"## {head}")
        # title 是该级别的可选主题行；与级别标题重复时省略，避免输出两遍同样的字
        if sec.get('title') and sec['title'] != head:
            L.append(f"**{sec['title']}**")
            L.append("")
        for it in sec.get('items', []):
            L.append(f"### [{lv}] {it.get('title','')}")
            if it.get('where'):
                L.append(f"- **位置**：{it['where']}")
            if it.get('why'):
                L.append(f"- **为什么扣分**：{it['why']}")
            if it.get('before'):
                L.append(f"\n  现：{it['before']}")
            if it.get('after'):
                L.append(f"\n  建议：{it['after']}")
            for p in it.get('pending', []):
                L.append(f"- **待核实**：{p}")
            L.append("")

    if rv.get('questions'):
        L.append("## 面试官大概率追问的地方")
        L.append("每个量化指标都要经得起追问。")
        L.append("")
        for q in rv['questions']:
            L.append(f"**{q.get('q','')}**")
            L.append(f"{q.get('a','')}")
            L.append("")

    if rv.get('actions'):
        L.append("## 修改优先级与工时")
        L.append("| 顺序 | 动作 | 工时 | 预期收益 |")
        L.append("|------|------|------|----------|")
        for a in rv['actions']:
            L.append(f"| {a.get('order','')} | {a.get('action','')} | {a.get('hours','')} | {a.get('value','')} |")
        L.append("")

    if rv.get('checklist'):
        L.append("## 交付前自查")
        for c in rv['checklist']:
            L.append(f"- [ ] {c}")
        L.append("")

    L.append("---")
    L.append(rv.get('disclaimer') or
             "本报告基于简历原件逐项核对，**未修改原简历任何内容**；所有建议均需学生本人核实真实数据后执行，"
             "任何量化数字不得凭空填写。")
    return "\n".join(L) + "\n"


def render_review_html(m, rv):
    """渲染评审报告 HTML（可打印）。"""
    parts = [f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>简历评价报告 · {esc(rv.get('subject', m.get('name','')))}</title><style>{CSS}</style></head>
<body><div class="page"><div class="rv-head">
<div class="rv-title">简历评价报告</div>"""]
    if rv.get('subject'):
        parts.append(f'<div class="rv-sub">{esc(rv["subject"])}</div>')
    if rv.get('target'):
        parts.append(f'<div class="rv-sub">目标岗位：{esc(rv["target"])}</div>')
    if rv.get('verdict'):
        parts.append(f'<div class="rv-verdict">{esc(rv["verdict"])}</div>')
    parts.append("</div>")

    if rv.get('verdict_paragraphs'):
        parts.append("<section>")
        for p in rv['verdict_paragraphs']:
            parts.append(f"<p>{esc(p)}</p>")
        parts.append("</section>")

    if rv.get('scores'):
        parts.append('<h2 class="rv-h2">分项评分</h2><table class="rv-table">'
                     '<tr><th>维度</th><th style="width:76px">得分</th><th>判分依据</th></tr>')
        for s in rv['scores']:
            parts.append(f'<tr><td><b>{esc(s.get("dim",""))}</b></td>'
                         f'<td class="rv-num">{esc(s.get("score",""))}</td>'
                         f'<td>{esc(s.get("note",""))}</td></tr>')
        parts.append("</table>")

    order = {'P0': 0, 'P1': 1, 'P2': 2}
    titles = {'P0': 'P0 — 投递前必修', 'P1': 'P1 — 显著影响通过率', 'P2': 'P2 — 加分项'}
    for sec in sorted(rv.get('sections', []), key=lambda x: order.get(x.get('level', 'P2'), 3)):
        lv = sec.get('level', '')
        head = titles.get(lv, lv)
        parts.append(f'<h2 class="rv-h2">{esc(head)}</h2>')
        # 主题行与级别标题重复时省略，避免同一句话输出两遍
        if sec.get('title') and sec['title'] != head:
            parts.append(f'<h3 class="rv-h3">{esc(sec["title"])}</h3>')
        for it in sec.get('items', []):
            parts.append(f'<div class="rv-item {esc(lv.lower())}">')
            parts.append(f'<h4><span class="rv-lv {esc(lv.lower())}">{esc(lv)}</span>{esc(it.get("title",""))}</h4>')
            if it.get('where'):
                parts.append(f'<p><b>位置</b>：{esc(it["where"])}</p>')
            if it.get('why'):
                parts.append(f'<p><b>为什么扣分</b>：{esc(it["why"])}</p>')
            if it.get('before'):
                parts.append(f'<div class="rv-before"><span class="rv-lbl">现</span>{esc(it["before"])}</div>')
            if it.get('after'):
                parts.append(f'<div class="rv-after"><span class="rv-lbl">建议</span>{esc(it["after"])}</div>')
            for p in it.get('pending', []):
                parts.append(f'<div class="rv-pending"><b>待核实</b>：{esc(p)}</div>')
            parts.append("</div>")

    if rv.get('questions'):
        parts.append('<h2 class="rv-h2">面试官大概率追问的地方</h2>')
        parts.append("<p>技术细节密是优势，但每个数字都要经得起追问。以下各处学生必须有准备。</p>")
        for q in rv['questions']:
            parts.append(f'<div class="rv-qa"><div class="q">{esc(q.get("q",""))}</div>'
                         f'<div class="a">{esc(q.get("a",""))}</div></div>')

    if rv.get('actions'):
        parts.append('<h2 class="rv-h2">修改优先级与工时</h2>')
        parts.append("<p>按收益/工时排序，标出当天必须完成的组合。</p>")
        parts.append('<table class="rv-table"><tr><th>顺序</th><th>动作</th>'
                     '<th style="width:88px">工时</th><th style="width:96px">预期收益</th></tr>')
        for a in rv['actions']:
            parts.append(f'<tr><td class="rv-num">{esc(a.get("order",""))}</td>'
                         f'<td>{esc(a.get("action",""))}</td><td>{esc(a.get("hours",""))}</td>'
                         f'<td>{esc(a.get("value",""))}</td></tr>')
        parts.append("</table>")

    if rv.get('checklist'):
        parts.append('<h2 class="rv-h2">交付前自查</h2><ul class="rv-checks">')
        for c in rv['checklist']:
            parts.append(f'<li>{esc(c)}</li>')
        parts.append("</ul>")

    parts.append(f'<div class="rv-foot">{esc(rv.get("disclaimer") or
        "本报告基于简历原件逐项核对，未修改原简历任何内容；所有建议均需学生本人核实真实数据后执行，任何量化数字不得凭空填写。")}</div>')
    parts.append("</div></body></html>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model', help='简历/评审模型 JSON 文件路径')
    ap.add_argument('--out', default='.', help='输出目录（默认当前目录）')
    args = ap.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ 找不到模型文件: {model_path}")
        sys.exit(1)
    try:
        m = json.loads(model_path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")
        sys.exit(1)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rv = m.get('review')

    if rv:
        rmd = render_review_md(m, rv)
        (out / 'review.md').write_text(rmd, encoding='utf-8')
        print(f"✅ 已生成 review.md（{len(rmd)} 字符）")

        rhtml = render_review_html(m, rv)
        (out / 'review.html').write_text(rhtml, encoding='utf-8')
        print(f"✅ 已生成 review.html（{len(rhtml)} 字符）")
    else:
        md = render_md(m)
        (out / 'resume.md').write_text(md, encoding='utf-8')
        print(f"✅ 已生成 resume.md（{len(md)} 字符）")

        htm = render_html(m)
        (out / 'resume.html').write_text(htm, encoding='utf-8')
        print(f"✅ 已生成 resume.html（{len(htm)} 字符）")

        rm = render_roadmap(m)
        if rm:
            (out / 'roadmap.md').write_text(rm, encoding='utf-8')
            print(f"✅ 已生成 roadmap.md（{len(rm)} 字符）")
        else:
            print("ℹ️  模型中无 roadmap 字段，跳过路线图生成")

    print(f"\n📁 输出目录：{out.resolve()}")


if __name__ == '__main__':
    main()
