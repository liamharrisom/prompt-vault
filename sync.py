import os
import json
import shutil
import subprocess
import re

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.expanduser("~/Desktop/imagens")
DEST_IMG_DIR = os.path.join(REPO_DIR, "images")
JSON_FILE = os.path.join(REPO_DIR, "prompts.json")

os.makedirs(DEST_IMG_DIR, exist_ok=True)

def main():
    if not os.path.exists(SRC_DIR):
        print(f"Pasta {SRC_DIR} não encontrada!")
        return

    files = os.listdir(SRC_DIR)
    ids = sorted(list({int(m.group(1)) for f in files if (m := re.match(r"^(\d+)", f))}))
    prompts_data = []

    print(f"Processando {len(ids)} itens...")

    for item_id in ids:
        img_name = next((f"{item_id}{ext}" for ext in [".jpeg", ".jpg", ".png", ".webp", ".JPEG", ".JPG", ".PNG"] if f"{item_id}{ext}" in files), None)
        txt_name = f"{item_id}.txt" if f"{item_id}.txt" in files else (str(item_id) if str(item_id) in files else None)

        if not img_name or not txt_name:
            continue

        shutil.copy2(os.path.join(SRC_DIR, img_name), os.path.join(DEST_IMG_DIR, img_name))

        with open(os.path.join(SRC_DIR, txt_name), "r", encoding="utf-8", errors="ignore") as f:
            prompt_content = f.read().strip()

        prompts_data.append({
            "id": str(item_id),
            "image": f"images/{img_name}",
            "prompt": prompt_content
        })
        print(f"✔ Arte #{item_id} sincronizada!")

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)

    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Auto-clean: remove tags e sincroniza"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("\n🚀 SUCESSO! Tudo corrigido e enviado pro GitHub!")
    except subprocess.CalledProcessError:
        print("\nSem novas alterações para enviar.")

if __name__ == "__main__":
    main()
