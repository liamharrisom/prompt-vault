import os
import json
import shutil
import subprocess
import re

# Pastas
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.expanduser("~/Desktop/imagens")
DEST_IMG_DIR = os.path.join(REPO_DIR, "images")
JSON_FILE = os.path.join(REPO_DIR, "prompts.json")

os.makedirs(DEST_IMG_DIR, exist_ok=True)

# Palavras-chave que o script vai caçar sozinho no texto para criar tags
KEYWORDS = [
    "BENGUS", "SHINKAWA", "SHINKIRO", "AQUARELA", "SUISAI", 
    "SUMI-E", "NANQUIM", "COPIC", "BRISTOL", "CAPCOM", 
    "1997", "1998", "STREET FIGHTER", "CHIAROSCURO", "DOUBLE EXPOSURE"
]

def extract_tags(text):
    found_tags = []
    text_upper = text.upper()
    for kw in KEYWORDS:
        if kw in text_upper:
            found_tags.append(kw)
    return found_tags if found_tags else ["ESTILO", "ARTE"]

def main():
    if not os.path.exists(SRC_DIR):
        print(f"Erro: Pasta {SRC_DIR} não encontrada!")
        return

    files = os.listdir(SRC_DIR)
    
    # Descobre todos os números de arquivos disponíveis
    ids = set()
    for f in files:
        m = re.match(r"^(\d+)", f)
        if m:
            ids.add(int(m.group(1)))

    sorted_ids = sorted(list(ids))
    prompts_data = []

    print(f"Encontrados {len(sorted_ids)} itens em {SRC_DIR}. Processando...")

    for item_id in sorted_ids:
        # Acha a imagem correspondente (.jpeg, .jpg, .png, .webp)
        img_name = None
        for ext in [".jpeg", ".jpg", ".png", ".webp", ".JPEG", ".JPG", ".PNG"]:
            if f"{item_id}{ext}" in files:
                img_name = f"{item_id}{ext}"
                break

        # Acha o arquivo de texto (com ou sem .txt)
        txt_name = None
        if f"{item_id}.txt" in files:
            txt_name = f"{item_id}.txt"
        elif str(item_id) in files and not os.path.isdir(os.path.join(SRC_DIR, str(item_id))):
            txt_name = str(item_id)

        if not img_name or not txt_name:
            print(f"Pulei o #{item_id}: precisa de imagem e texto correspondentes.")
            continue

        # Copia imagem para a pasta do repositório
        src_img = os.path.join(SRC_DIR, img_name)
        dest_img = os.path.join(DEST_IMG_DIR, img_name)
        shutil.copy2(src_img, dest_img)

        # Lê o prompt
        src_txt = os.path.join(SRC_DIR, txt_name)
        with open(src_txt, "r", encoding="utf-8", errors="ignore") as f:
            prompt_content = f.read().strip()

        tags = extract_tags(prompt_content)

        prompts_data.append({
            "id": str(item_id),
            "image": f"images/{img_name}",
            "tags": tags,
            "prompt": prompt_content
        })
        print(f"✔ Item #{item_id} processado! Tags: {tags}")

    # Salva o prompts.json
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)
    print("✔ prompts.json atualizado com sucesso!")

    # Git Add, Commit e Push automático
    try:
        print("Enviando alterações para o GitHub...")
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Auto-sync artes e prompts"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("\n🚀 SUCESSO ABSOLUTO! Tudo enviado pro GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"Aviso no Git (talvez não haja alterações novas): {e}")

if __name__ == "__main__":
    main()
