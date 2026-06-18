import zipfile
from pathlib import Path

skill_path = Path("G:/AI4ALL/dxp-skills/teaching/dxp-syllabus-creator")
skill_filename = skill_path / "dxp-syllabus-creator.skill"

EXCLUDE = {"workspace", "__pycache__", ".git"}
EXCLUDE_FILES = {"eval_set.json", ".DS_Store", "optimization_report.html"}

with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file_path in sorted(skill_path.rglob("*")):
        if not file_path.is_file():
            continue
        parts = list(file_path.relative_to(skill_path.parent).parts)
        if len(parts) > 1 and parts[1] in EXCLUDE:
            continue
        if parts[-1] in EXCLUDE_FILES or parts[-1].endswith(".pyc"):
            continue
        arcname = file_path.relative_to(skill_path.parent)
        zipf.write(file_path, arcname)

print(f"OK: {skill_filename}")
