import os
import bs4
import re

DOCS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

def fix_links():
    print(f"Fixing links in {DOCS_ROOT}...")
    html_files = []
    for root, dirs, files in os.walk(DOCS_ROOT):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))

    modified_count = 0
    for file_path in html_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        soup = bs4.BeautifulSoup(content, "html.parser")
        rel_dir = os.path.relpath(os.path.dirname(file_path), DOCS_ROOT)
        
        # Determine depth
        if rel_dir == ".":
            depth = 0
        else:
            depth = len(rel_dir.split(os.sep))

        made_changes = False
        
        # 1. Handle cases like href="../index.html" in the root directory
        if depth == 0:
            for a in soup.find_all("a", href=True):
                old_href = a["href"]
                if old_href.startswith("../index.html"):
                    a["href"] = old_href.replace("../index.html", "index.html")
                    print(f"  Fixing root link: {file_path} -> {old_href} to {a['href']}")
                    made_changes = True
                elif old_href == "..":
                    a["href"] = "index.html"
                    print(f"  Fixing root link: {file_path} -> .. to index.html")
                    made_changes = True

        if made_changes:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(soup))
            modified_count += 1

    print(f"\n--- Repair Complete ---")
    print(f"Files modified: {modified_count}")

if __name__ == "__main__":
    fix_links()
