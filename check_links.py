import os
import bs4

DOCS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

def check_links():
    print(f"Scanning files in {DOCS_ROOT}...")
    html_files = []
    for root, dirs, files in os.walk(DOCS_ROOT):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.relpath(os.path.join(root, file), DOCS_ROOT))

    broken_links = []
    total_links = 0
    for rel_path in html_files:
        full_path = os.path.join(DOCS_ROOT, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f, "html.parser")
            
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("http", "mailto", "#")):
                continue
            
            total_links += 1
            # Check if internal link exists
            target_path = os.path.normpath(os.path.join(os.path.dirname(full_path), href))
            if not os.path.exists(target_path):
                broken_links.append({
                    "source": rel_path,
                    "href": href,
                    "target": target_path
                })

    print(f"\n--- Scan Complete ---")
    print(f"Files checked: {len(html_files)}")
    print(f"Total internal links checked: {total_links}")

    if broken_links:
        print(f"\n[ERROR] Found {len(broken_links)} broken links:")
        for link in broken_links:
            print(f"  Source: {link['source']}")
            print(f"  Href:   {link['href']}")
            print(f"  Reason: Target not found at {link['target']}")
            print("-" * 20)
    else:
        print("\n[SUCCESS] No broken internal links found!")

if __name__ == "__main__":
    check_links()
