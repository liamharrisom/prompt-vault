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

    # 1. Carrega dados existentes para manter o #1 (Junji Ito) intacto
    existing_data = {}
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    existing_data[str(item.get("id"))] = item
        except Exception:
            pass

    files = os.listdir(SRC_DIR)
    ids = sorted(list({int(m.group(1)) for f in files if (m := re.match(r"^(\d+)", f))}))
    
    final_prompts = []

    # Protege o #1
    if "1" in existing_data:
        final_prompts.append(existing_data["1"])
        print("✔ #1 (Junji Ito original) protegido!")

    print(f"\nIniciando sincronização em massa de {len(ids)} itens...")

    for item_id in ids:
        if item_id == 1:
            continue

        # Acha a imagem
        img_name = next((f"{item_id}{ext}" for ext in [".jpeg", ".jpg", ".png", ".webp", ".JPEG", ".JPG", ".PNG"] if f"{item_id}{ext}" in files), None)
        
        # Acha o texto
        txt_name = f"{item_id}.txt" if f"{item_id}.txt" in files else (str(item_id) if str(item_id) in files else None)

        if not img_name or not txt_name:
            print(f"⚠ Pulei o #{item_id}: falta imagem ou texto correspondente.")
            continue

        # Copia imagem para a pasta do repositório
        shutil.copy2(os.path.join(SRC_DIR, img_name), os.path.join(DEST_IMG_DIR, img_name))

        # Lê prompt
        with open(os.path.join(SRC_DIR, txt_name), "r", encoding="utf-8", errors="ignore") as f:
            prompt_content = f.read().strip()

        final_prompts.append({
            "id": str(item_id),
            "image": f"images/{img_name}",
            "prompt": prompt_content
        })
        print(f"✔ Arte #{item_id} processada!")

    # Ordena todos numericamente de 1 a 68
    final_prompts.sort(key=lambda x: int(x["id"]) if x["id"].isdigit() else 9999)

    # Salva prompts.json
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(final_prompts, f, ensure_ascii=False, indent=2)

    print(f"\n✨ Total de {len(final_prompts)} artes catalogadas com sucesso!")

    # Git push
    try:
        print("\nEnviando o caminhão de artes pro GitHub...")
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", f"Adiciona lote completo até a arte #{max(ids)}"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("\n🚀 SUCESSO TOTAL! Todas as artes já estão voando pro site!")
    except subprocess.CalledProcessError as e:
        print(f"\nAviso no Git: {e}")

if __name__ == "__main__":
    main()
