import os
import re
import datetime
from googletrans import Translator

README = "README.md"
MANIFEST = "repo_manifest.txt"
INDEX = "INDEX.md"
LANGUAGES = {'en': 'English', 'fr': 'Français', 'ru': 'Русский', 'ja': '日本語'}

def get_manifest_stats():
    try:
        with open(MANIFEST, "r", encoding="utf-8") as f:
            files = [l.strip() for l in f if l.strip()]
        total = len(files)
        return total, files
    except Exception:
        return 0, []

def make_stats_block(total, files, lang='en'):
    block = {
        'en': f"### 📊 LUFT Repo Manifest\n\n- **Total files:** {total}\n- **Last update:** {datetime.datetime.utcnow().isoformat()}Z\n",
        'fr': f"### 📊 Manifest du dépôt LUFT\n\n- **Fichiers totaux :** {total}\n- **Dernière mise à jour :** {datetime.datetime.utcnow().isoformat()}Z\n",
        'ru': f"### 📊 Манифест репозитория LUFT\n\n- **Всего файлов:** {total}\n- **Последнее обновление:** {datetime.datetime.utcnow().isoformat()}Z\n",
        'ja': f"### 📊 LUFTリポジトリマニフェスト\n\n- **総ファイル数:** {total}\n- **最終更新:** {datetime.datetime.utcnow().isoformat()}Z\n",
    }
    return block.get(lang, block['en'])

def insert_or_replace_block(readme, new_block, marker):
    if marker in readme:
        # Replace between special markers
        pattern = re.compile(rf"(<!-- {marker} START -->).*?(<!-- {marker} END -->)", re.DOTALL)
        replacement = rf"\1\n{new_block}\n\2"
        return pattern.sub(replacement, readme)
    else:
        # Insert at top if marker not found
        return f"<!-- {marker} START -->\n{new_block}\n<!-- {marker} END -->\n\n" + readme

def main():
    total, files = get_manifest_stats()
    try:
        with open(README, "r", encoding="utf-8") as f:
            readme = f.read()
    except Exception:
        readme = ""

    for lang in LANGUAGES:
        block = make_stats_block(total, files, lang)
        marker = f"LUFT_MANIFEST_{lang.upper()}"
        readme = insert_or_replace_block(readme, block, marker)

    with open(README, "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
