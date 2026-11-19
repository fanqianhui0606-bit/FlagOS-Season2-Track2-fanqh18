import markdown
import subprocess
from pathlib import Path

md_path = Path("report_draft.md")
html_path = Path("report.html")
pdf_path = Path("report.pdf")

text = md_path.read_text(encoding="utf-8")

body = markdown.markdown(text, extensions=["tables", "fenced_code"])

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>FlagOS 赛道二技术报告 - fanqh18</title>
<style>
@page {{
    size: A4;
    margin: 20mm 15mm;
}}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
    line-height: 1.6;
    color: #24292e;
    font-size: 14px;
}}
h1 {{ font-size: 24px; text-align: center; border-bottom: 2px solid #0969da; padding-bottom: 8px; margin-bottom: 15px; }}
h2 {{ font-size: 18px; border-bottom: 1px solid #eaecef; padding-bottom: 6px; margin-top: 25px; color: #0969da; }}
h3 {{ font-size: 15px; margin-top: 15px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 13px; }}
th, td {{ border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }}
th {{ background-color: #f6f8fa; font-weight: 600; }}
pre {{ background-color: #f6f8fa; padding: 10px; border-radius: 4px; overflow: auto; font-family: monospace; font-size: 12px; }}
code {{ font-family: monospace; background-color: #eff1f3; padding: 2px 4px; border-radius: 3px; font-size: 12px; }}
pre code {{ background-color: transparent; padding: 0; }}
blockquote {{ border-left: 4px solid #0969da; margin: 10px 0; padding-left: 12px; color: #57606a; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

html_path.write_text(html, encoding="utf-8")
print("Generated report.html")

# Find edge path
edge_candidates = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

edge_exe = None
for p in edge_candidates:
    if Path(p).exists():
        edge_exe = p
        break

if edge_exe:
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path.resolve()}",
        str(html_path.resolve())
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if pdf_path.exists():
        print(f"SUCCESS: report.pdf generated! Size: {pdf_path.stat().st_size} bytes")
    else:
        print(f"Edge run returned: {res.returncode}, but PDF not created")
else:
    print("Edge not found, using reportlab fallback")
