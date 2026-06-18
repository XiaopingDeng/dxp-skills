from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("F:/playground/skills/论文模板.docx")

with open("Template_Structure.md", "w", encoding="utf-8") as f:
    f.write(result.text_content)

print("结构提取完成 > Template_Structure.md")