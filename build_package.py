#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_package.py
FlagOS 赛道二交付包（fanqh18.zip）自动化构建与卫生审计工具
严格遵循大赛官方提交流程与规范：
1. 文件名为“参赛队伍名.zip” (fanqh18.zip)
2. 压缩包第一层必须包含队伍名顶级目录 (fanqh18/)
3. 该顶级目录下一层必须包含：
   - readme.md (且同时兼容 README.md)
   - report.pdf
   - vllm-plugin-FL/
   - FlagGems/ (涉及算子修改)
   - benchmark/, logs_and_artifacts/, env_setup.sh, run_benchmark.sh, run_eval_accuracy.sh 等复现体系
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
PACKAGE_NAME = "fanqh18"
OUTPUT_ZIP = WORKSPACE / f"{PACKAGE_NAME}.zip"

# 官方交付包核心条目白名单 (仅打包规范交付项)
DELIVERABLE_WHITELIST = [
    "readme.md",
    "README.md",
    "report.pdf",
    "vllm-plugin-FL",
    "FlagGems",
    "src",
    "benchmark",
    "logs_and_artifacts",
    "env_setup.sh",
    "run_benchmark.sh",
    "run_eval_accuracy.sh",
    "requirements.txt",
    "report_draft.md",
    "build_package.py"
]

def clean_artifacts(target_dir: Path):
    print(f"[1/4] 清理构建垃圾与临时文件: {target_dir.name}...")
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for name in files:
            p = Path(root) / name
            if p.suffix in ['.pyc', '.pyo', '.pyd'] or p.name in ['.DS_Store', 'Thumbs.db']:
                p.unlink()
        for name in dirs:
            p = Path(root) / name
            if name in ['__pycache__', '.pytest_cache', '.ipynb_checkpoints', 'build', 'dist'] or name.endswith('.egg-info'):
                shutil.rmtree(p, ignore_errors=True)

def check_files(target_dir: Path):
    print("[2/4] 检查必备交付文件清单 (严格对照官方平台门禁规范)...")
    missing = []
    for item in DELIVERABLE_WHITELIST:
        if item in ["readme.md", "README.md"]:
            if not (target_dir / "README.md").exists() and not (target_dir / "readme.md").exists():
                missing.append("readme.md/README.md")
            continue
        p = target_dir / item
        if not p.exists():
            missing.append(item)
    if missing:
        print(f"  [警告] 缺少以下重要交付项: {missing}")
        sys.exit(1)
    else:
        print("  [OK] 所有核心文件和目录完整 (含 readme.md, report.pdf, vllm-plugin-FL, FlagGems)！")

def check_hardcoded_paths(target_dir: Path):
    print("[3/4] 静态扫描绝对路径硬编码 (防评委冷启动报错)...")
    suspicious_keywords = ["/home/", "/root/", "C:\\", "c:\\", "D:\\", "Users/"]
    found_issues = []
    
    for item in DELIVERABLE_WHITELIST:
        if item in ["readme.md", "README.md"]:
            continue
        p = target_dir / item
        if p.is_file() and p.suffix in ['.sh', '.py', '.env']:
            content = p.read_text(encoding='utf-8', errors='ignore')
            for kw in suspicious_keywords:
                if kw in content and "build_package.py" not in p.name:
                    found_issues.append((p.name, kw))
        elif p.is_dir():
            for ext in ['.sh', '.py', '.env']:
                for file in p.rglob(f"*{ext}"):
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    for kw in suspicious_keywords:
                        if kw in content:
                            found_issues.append((file.relative_to(target_dir), kw))
                
    if found_issues:
        print("  [提示] 发现疑似硬编码路径:")
        for f, kw in found_issues[:5]:
            print(f"    - {f}: 包含 '{kw}'")
    else:
        print("  [OK] 未发现明显硬编码绝对路径。")

def make_zip(source_dir: Path, output_file: Path):
    print(f"[4/4] 按照官方规范构建顶层 {PACKAGE_NAME}/ 纯净交付包: {output_file.name}...")
    if output_file.exists():
        output_file.unlink()

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. 显式写入小写 readme.md 与大写 README.md (确保 Linux 容器大小写无缝兼容)
        readme_path = source_dir / "README.md"
        if not readme_path.exists():
            readme_path = source_dir / "readme.md"
        if readme_path.exists():
            zf.write(readme_path, f"{PACKAGE_NAME}/readme.md")
            zf.write(readme_path, f"{PACKAGE_NAME}/README.md")

        # 2. 遍历其余白名单项目
        for item in DELIVERABLE_WHITELIST:
            if item in ["readme.md", "README.md"]:
                continue
            item_path = source_dir / item
            if not item_path.exists():
                continue
            if item_path.is_file():
                rel_path = item_path.relative_to(source_dir)
                archive_name = f"{PACKAGE_NAME}/{rel_path.as_posix()}"
                zf.write(item_path, archive_name)
            elif item_path.is_dir():
                for root, dirs, files in os.walk(item_path):
                    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__']]
                    for file in files:
                        p = Path(root) / file
                        if p.suffix in ['.pyc', '.pyo', '.pyd'] or p.name in ['.DS_Store', 'Thumbs.db']:
                            continue
                        rel_path = p.relative_to(source_dir)
                        archive_name = f"{PACKAGE_NAME}/{rel_path.as_posix()}"
                        zf.write(p, archive_name)

    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"=== [完成] 纯净交付包打包成功: {output_file.name} ({size_mb:.2f} MB) ===")

if __name__ == "__main__":
    clean_artifacts(WORKSPACE)
    check_files(WORKSPACE)
    check_hardcoded_paths(WORKSPACE)
    make_zip(WORKSPACE, OUTPUT_ZIP)
