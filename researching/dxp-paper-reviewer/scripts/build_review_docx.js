#!/usr/bin/env node
/**
 * 由 JSON 生成论文体检 docx。
 *
 * 用法:
 *   node build_review_docx.js review.json out.docx
 *
 * 依赖 docx（npm i -g docx）。若 require 失败，设置 NODE_PATH 指向全局 node_modules。
 *
 * JSON 结构见 references/docx-export.md。
 */
const fs = require("fs");
const path = require("path");

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Footer,
} = require("docx");

const FONT = "Microsoft YaHei";
const BODY = 21;         // 10.5pt
const RED = "FF0000";
const H1_COLOR = "1F3864";
const H2_COLOR = "2E5C8A";
const CONTENT_W = 9026;  // A4，1 英寸页边距

const SUGGEST_LABEL = { reviewer: "【修改建议】", mentor: "【我建议】" };

/* ---------------- helpers ---------------- */
function run(text, o = {}) {
  return new TextRun({
    text: String(text),
    font: FONT,
    size: o.size ?? BODY,
    bold: !!o.bold,
    italics: !!o.italics,
    color: o.color ?? "000000",
  });
}

function para(content, o = {}) {
  const children = typeof content === "string" ? [run(content, o)] : content;
  return new Paragraph({
    children,
    heading: o.heading,
    alignment: o.alignment,
    numbering: o.numbering,
    spacing: { before: o.before ?? 0, after: o.after ?? 120, line: 300 },
  });
}

function bullet(content) {
  return para(content, { numbering: { reference: "bul", level: 0 }, after: 60 });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [run(text, { size: 30, bold: true, color: H1_COLOR })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [run(text, { size: 24, bold: true, color: H2_COLOR })],
  });
}

const BORDER = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };

function cell(text, o) {
  return new TableCell({
    borders: BORDERS,
    width: { size: o.width, type: WidthType.DXA },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({
      spacing: { before: 20, after: 20, line: 260 },
      children: [run(text, { size: 20, bold: !!o.bold })],
    })],
  });
}

function buildTable(spec) {
  const raw = spec.widths && spec.widths.length ? spec.widths : spec.header.map(() => 1);
  const sum = raw.reduce((a, b) => a + b, 0);
  const widths = raw.map((w) => Math.round((w / sum) * CONTENT_W));
  // 修正四舍五入误差，保证列宽之和 == 表宽
  widths[widths.length - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);

  const mkRow = (vals, isHeader) => new TableRow({
    tableHeader: !!isHeader,
    children: vals.map((v, i) => cell(v, {
      width: widths[i],
      bold: isHeader,
      fill: isHeader ? "D5E8F0" : undefined,
    })),
  });

  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [mkRow(spec.header, true), ...spec.rows.map((r) => mkRow(r, false))],
  });
}

/* ---------------- block renderers ---------------- */
function renderBlocks(blocks, tone) {
  const out = [];
  const label = SUGGEST_LABEL[tone] || SUGGEST_LABEL.reviewer;

  for (const b of blocks) {
    switch (b.type) {
      case "h1":
        out.push(h1(b.text));
        break;
      case "h2":
        out.push(h2(b.text));
        break;
      case "p":
        out.push(para(b.text));
        break;
      case "bullets":
        (b.items || []).forEach((t) => out.push(bullet(t)));
        break;
      case "table":
        out.push(buildTable(b));
        out.push(para("", { after: 60 }));
        break;
      case "issue": {
        if (b.heading) out.push(h2(b.heading));
        (b.paras || []).forEach((t) => out.push(para(t)));
        (b.bullets || []).forEach((t) => out.push(bullet(t)));
        const sg = b.suggest || [];
        sg.forEach((t, i) => {
          if (i === 0) {
            out.push(new Paragraph({
              indent: { left: 300 },
              spacing: { before: 60, after: 180, line: 300 },
              children: [run(label, { bold: true, color: RED }), run(t, { color: RED })],
            }));
          } else {
            out.push(new Paragraph({
              indent: { left: 300 },
              spacing: { before: 0, after: 180, line: 300 },
              children: [run(t, { color: RED })],
            }));
          }
        });
        break;
      }
      default:
        throw new Error("unknown block type: " + b.type);
    }
  }
  return out;
}

/* ---------------- document ---------------- */
function buildDocument(spec) {
  const tone = spec.tone === "mentor" ? "mentor" : "reviewer";
  const children = [];

  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
    children: [run(spec.title, { size: 40, bold: true, color: H1_COLOR })],
  }));
  (spec.meta || []).forEach((line, i, arr) => {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: i === arr.length - 1 ? 120 : 60 },
      children: [run(line, { size: 19, color: "595959" })],
    }));
  });
  if (spec.note) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
      children: [run(spec.note, { size: 19, italics: true, color: "595959" })],
    }));
  }

  children.push(...renderBlocks(spec.blocks || [], tone));

  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: BODY } } },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, bold: true, font: FONT, color: H1_COLOR },
          paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 0 },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: H2_COLOR },
          paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 1 },
        },
      ],
    },
    numbering: {
      config: [{
        reference: "bul",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      }],
    },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "第 ", font: FONT, size: 18, color: "808080" }),
              new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "808080" }),
              new TextRun({ text: " 页", font: FONT, size: 18, color: "808080" }),
            ],
          })],
        }),
      },
      children,
    }],
  });
}

/* ---------------- main ---------------- */
function main() {
  const [jsonPath, outPath] = process.argv.slice(2);
  if (!jsonPath || !outPath) {
    console.error("usage: node build_review_docx.js review.json out.docx");
    process.exit(1);
  }
  const spec = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
  Packer.toBuffer(buildDocument(spec)).then((buf) => {
    fs.writeFileSync(outPath, buf);
    console.log("WROTE " + path.resolve(outPath) + " (" + buf.length + " bytes)");
  });
}

main();
