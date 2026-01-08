import os
import sys
import re
from google import genai
from google.genai import types

# --- 設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
REPORTS_DIR = os.path.join(BASE_DIR, "output_reports")
PLANNED_FILE = os.path.join(REPORTS_DIR, "planned_articles.md")
IDENTITY_FILE = os.path.join(REPORTS_DIR, "01_identity.md")

# 親ディレクトリのMySiteGen-Agentのユーティリティをインポートするためのパス追加
sys.path.append(os.path.dirname(BASE_DIR))
try:
    from utils.client_utils import setup_client
    from agents.agent_03_generation import generate_single_page_html
except ImportError:
    print("Error: Could not import MySiteGen-Agent utilities. Please ensure this script is inside the project directory.")
    sys.exit(1)

def main():
    client = setup_client()
    
    # ユーザーの好みに合わせてモデルを明示的に指定
    MODEL_NAME = "gemini-2.5-pro"

    if not os.path.exists(PLANNED_FILE):
        print(f"Error: {PLANNED_FILE} not found.")
        return

    # 1. 記事一覧の読み込み
    with open(PLANNED_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # テーブルから記事を抽出
    # | ファイル名 | タイトル | 概要 |
    articles = []
    lines = content.splitlines()
    for line in lines:
        if line.startswith("|") and not "ファイル名" in line and not "---" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                file_path = parts[1]
                title = parts[2]
                purpose = parts[3]
                if file_path.endswith(".html") and "/" in file_path:
                    articles.append({
                        "file_name": file_path,
                        "title": title,
                        "purpose": purpose
                    })

    if not articles:
        print("No articles found in planned_articles.md")
        return

    print(f"Found {len(articles)} planned articles.")
    
    # 2. セクションの選択
    sections = sorted(list(set([a["file_name"].split("/")[0] for a in articles])))
    print("\nAvailable sections:")
    for i, s in enumerate(sections):
        print(f"[{i}] {s}")
    
    try:
        sel = int(input("\nSelect section index: "))
        target_section = sections[sel]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    section_articles = [a for a in articles if a["file_name"].startswith(target_section + "/")]
    
    print(f"\nArticles in '{target_section}':")
    for i, a in enumerate(section_articles):
        # 存在チェック
        full_path = os.path.join(DOCS_DIR, a["file_name"])
        status = "[EXIST]" if os.path.exists(full_path) else "[MISSING]"
        print(f"[{i}] {status} {a['title']}")

    try:
        sel_art = int(input("\nSelect article index to generate: "))
        target_article = section_articles[sel_art]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # 3. 生成
    with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
        identity_content = f.read()

    print(f"\nGenerating: {target_article['title']}...")
    
    # generate_single_page_html を流用
    # Note: agent_03_generation.py 内でモデル名をハードコードしている可能性があるため、
    # 必要に応じて引数で渡せるように調整されているか確認が必要ですが、
    # ユーザー様が既に agent_03_generation.py を gemini-2.5-pro に書き換えているため、そのまま呼び出します。
    
    html = generate_single_page_html(
        client, 
        target_article, 
        identity_content, 
        None, 
        [], 
        SITE_TYPE="personal"
    )

    if html:
        output_path = os.path.join(DOCS_DIR, target_article["file_name"])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Successfully generated: {output_path}")
    else:
        print("Failed to generate HTML.")

if __name__ == "__main__":
    main()
