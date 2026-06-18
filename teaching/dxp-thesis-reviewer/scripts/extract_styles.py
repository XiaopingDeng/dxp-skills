"""
从学校论文模板中提取样式信息，输出为 JSON 格式的 Style_Rules.json。
"""
import sys
import os
import json
import docx
from jsonschema import validate, ValidationError

TEMPLATE_PATH = "F:/playground/skills/论文模板.docx"

def get_json_schema():
    """返回样式规则的JSON Schema"""
    return {
        "type": "object",
        "properties": {
            "_default": {
                "type": "object",
                "properties": {
                    "font_name": {"type": "string"},
                    "font_size_pt": {"type": ["number", "null"]},
                    "description": {"type": "string"}
                },
                "required": ["font_name", "font_size_pt", "description"],
                "additionalProperties": True
            }
        },
        "patternProperties": {
            "^((?!_default$).)*$": {
                "type": "object",
                "properties": {
                    "font_name": {"type": "string"},
                    "font_size_pt": {"type": "number"},
                    "font_size_cn": {"type": "string"},
                    "bold": {"type": "boolean"},
                    "italic": {"type": "boolean"},
                    "color": {"type": "string"},
                    "alignment": {"type": "string"},
                    "line_spacing": {"type": "number"},
                    "space_before_pt": {"type": "number"},
                    "space_after_pt": {"type": "number"},
                    "first_line_indent_pt": {"type": "number"}
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": True
    }

def extract_styles(docx_path):
    doc = docx.Document(docx_path)

    style_rules = {}

    # 遍历文档中定义的样式
    for style in doc.styles:
        # 只提取段落样式（忽略字符样式、表格样式等）
        if style.type != docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
            continue

        # 跳过内置默认样式以外的非自定义样式
        if not style.name:
            continue

        font = style.font
        pf = style.paragraph_format

        style_info = {}

        # 字体信息
        if font.name:
            style_info["font_name"] = font.name
        if font.size:
            # 字号转换为中文字号描述（小四、三号等）
            style_info["font_size_pt"] = font.size.pt
            style_info["font_size_cn"] = pt_to_cn(font.size.pt)
        if font.bold is not None:
            style_info["bold"] = font.bold
        if font.italic is not None:
            style_info["italic"] = font.italic
        if font.color and font.color.rgb:
            style_info["color"] = str(font.color.rgb)

        # 段落格式
        if pf.alignment is not None:
            style_info["alignment"] = str(pf.alignment)
        if pf.line_spacing is not None:
            style_info["line_spacing"] = pf.line_spacing
        if pf.space_before is not None:
            style_info["space_before_pt"] = pf.space_before.pt
        if pf.space_after is not None:
            style_info["space_after_pt"] = pf.space_after.pt
        if pf.first_line_indent is not None:
            style_info["first_line_indent_pt"] = pf.first_line_indent.pt

        if style_info:
            style_rules[style.name] = style_info

    # 也提取默认段落字体（用于未指定样式的正文）
    default_font = doc.styles["Normal"].font
    if default_font.name:
        style_rules["_default"] = {
            "font_name": default_font.name,
            "font_size_pt": default_font.size.pt if default_font.size else None,
            "description": "默认正文样式，用于未显式指定样式的段落"
        }

    return style_rules

def pt_to_cn(pt):
    """将磅值(pt)转换为中文字号描述"""
    mapping = {
        42: "初号", 36: "小初", 26: "一号", 24: "小一",
        22: "二号", 18: "小二", 16: "三号", 15: "小三",
        14: "四号", 12: "小四", 10.5: "五号", 9: "小五",
        7.5: "六号", 6.5: "小六", 5.5: "七号", 5: "八号"
    }
    return mapping.get(pt, f"{pt}pt")

def validate_json(data):
    """验证JSON数据是否符合Schema"""
    schema = get_json_schema()
    try:
        validate(instance=data, schema=schema)
        return True, "JSON格式验证通过"
    except ValidationError as e:
        return False, f"JSON验证失败: {e.message}"

def save_json_file(data, filename="Style_Rules.json"):
    """保存JSON数据到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, f"成功保存到文件: {filename}"
    except Exception as e:
        return False, f"保存文件时出错: {str(e)}"

if __name__ == "__main__":
    # 1. 检查是否传入了命令行参数
    if len(sys.argv) < 2:
        print("用法: python extract_styles.py <docx文件的绝对路径>")
        sys.exit(1)
    
    # 2. 获取命令行传入的路径
    template_path = sys.argv[1]
    
    # 3. 检查文件是否真实存在（提前拦截路径错误）
    if not os.path.exists(template_path):
        print(f"❌ 错误: 找不到文件 '{template_path}'")
        print("请检查文件路径是否正确，或文件是否被其他程序占用。")
        sys.exit(1)

    # 4. 尝试读取并提取样式
    try:
        print(f"🔄 正在读取模板: {template_path}")
        rules = extract_styles(template_path)
        
        # 验证JSON格式
        is_valid, validation_msg = validate_json(rules)
        if not is_valid:
            print(f"❌ {validation_msg}")
            sys.exit(1)
        
        print("✅ 样式提取成功！")
        print(validation_msg)
        
        # 保存到文件
        save_success, save_msg = save_json_file(rules, "Style_Rules.json")
        if save_success:
            print(save_msg)
            print("📋 提取的样式规则:")
            print(json.dumps(rules, ensure_ascii=False, indent=2))
        else:
            print(f"❌ {save_msg}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 提取过程中发生错误: {e}")
        sys.exit(1)
