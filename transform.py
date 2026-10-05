import os
import re
from pathlib import Path

# Configuration
LOCAL_DIR = Path("scripts")
REPO_URL = "https://github.com/devdinc/skripts"
DRY_RUN = True  # Set to False only when you are ready to apply changes

def scan_requirements(content: str) -> list:
    requires = ["skript >= 2.6"]
    content_lower = content.lower()

    if "import:" in content or "reflect" in content_lower or "java." in content:
        requires.append("skript-reflect >= 2.4")
    if "skquery" in content_lower:
        requires.append("skquery")
    if "tuske" in content_lower:
        requires.append("tuske")

    return requires

def extract_defined_functions(content: str) -> set:
    pattern = r'^\s*function\s+([a-zA-Z0-9_:]+)\s*\('
    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
    return {m.lower().split('::')[-1] for m in matches}

def analyze_local_files():
    if not LOCAL_DIR.exists():
        raise FileNotFoundError(f"Directory {LOCAL_DIR.resolve()} does not exist.")

    sk_files = {}
    file_contents = {}
    file_functions = {}

    for sk_file in LOCAL_DIR.glob("**/*.sk"):
        if ".git" in sk_file.parts:
            continue

        rel_path = sk_file.relative_to(LOCAL_DIR.parent)

        try:
            with open(sk_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = ""

        sk_files[sk_file.stem] = rel_path
        file_contents[rel_path] = content
        file_functions[rel_path] = extract_defined_functions(content)

    func_to_file = {}
    for rel_path, funcs in file_functions.items():
        for func in funcs:
            func_to_file[func] = rel_path

    return sk_files, file_contents, file_functions, func_to_file

def simulate_transformation():
    sk_files, file_contents, file_functions, func_to_file = analyze_local_files()
    print(f"=== DRY RUN MODE ({len(sk_files)} files found under '{LOCAL_DIR}') ===\n")

    for rel_path, content in file_contents.items():
        full_path = LOCAL_DIR.parent / rel_path
        parent_dir = full_path.parent
        pkg_dir = parent_dir / full_path.stem
        new_sk_path = pkg_dir / full_path.name

        requires = scan_requirements(content)

        # Dependency detection
        dependencies = set()
        current_file_funcs = file_functions[rel_path]

        # 1. Cross-file function calls
        for func_name, defining_file in func_to_file.items():
            if defining_file == rel_path:
                continue
            if func_name not in current_file_funcs:
                call_pattern = r'\b' + re.escape(func_name) + r'\s*\('
                if re.search(call_pattern, content, re.IGNORECASE):
                    subfolder_path = defining_file.parent / defining_file.stem
                    dep_url = f"{REPO_URL}#{subfolder_path.as_posix()}"
                    dependencies.add(dep_url)

        # 2. Include / file references
        for other_stem, other_rel_path in sk_files.items():
            if other_rel_path == rel_path:
                continue
            include_pattern = rf'(?:include|load|import)\s+["\']?[^"\']*?\b{re.escape(other_stem)}\b'
            if re.search(include_pattern, content, re.IGNORECASE):
                subfolder_path = other_rel_path.parent / other_rel_path.stem
                dep_url = f"{REPO_URL}#{subfolder_path.as_posix()}"
                dependencies.add(dep_url)

        # Build simulated package.txt
        package_txt_content = [
            f"name: {full_path.stem}",
            "version: 1.0.0",
            f"description: Skript package for {full_path.stem}"
        ]

        if requires:
            package_txt_content.append(f"requires: {', '.join(requires)}")

        if dependencies:
            package_txt_content.append(f"packages: {', '.join(sorted(dependencies))}")

        # Print Preview for this file
        print(f"--------------------------------------------------")
        print(f"[SIMULATE MOVE] {rel_path}  -->  {new_sk_path.as_posix()}")
        print(f"[SIMULATE CREATE] {pkg_dir / 'package.txt'}")
        print(f"--- Generated package.txt Content ---")
        print("\n".join(package_txt_content))
        print(f"------------------------------------------------..\n")

    print("=== Dry run complete. No files were modified. ===")

if __name__ == "__main__":
    simulate_transformation()
