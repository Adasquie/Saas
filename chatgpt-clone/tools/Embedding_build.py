import pdfplumber
import openai
import faiss
import numpy as np
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fonction pour extraire le texte du PDF
def extraire_texte_pdf(fichier_pdf):
    texte = ""
    with pdfplumber.open(fichier_pdf) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texte += page_text + "\n"
    return texte

# Fonction pour diviser le texte en sections avec une fenêtre glissante
def decouper_fenetre_glissante(texte, taille_fenetre=200, chevauchement=50):
    tokens = texte.split()
    sections = []
    for i in range(0, len(tokens), taille_fenetre - chevauchement):
        section = " ".join(tokens[i:i + taille_fenetre])
        sections.append(section)
    return sections

# Fonction pour obtenir l'embedding d'un texte
def obtenir_embedding_texte(texte):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=texte
    )
    return response.data[0].embedding

dossier_pdfs = Path("paie")

all_sections = []
all_embeddings = []

# Traiter chaque fichier PDF dans le dossier
for fichier in os.listdir(dossier_pdfs):
    if fichier.endswith(".pdf"):
        chemin_fichier = os.path.join(dossier_pdfs, fichier)
        texte_pdf = extraire_texte_pdf(chemin_fichier)
        
        # Optionnel : sauvegarder le texte extrait
        nom_fichier_texte = fichier.replace(".pdf", ".txt")
        chemin_fichier_texte = os.path.join(dossier_pdfs, nom_fichier_texte)
        
        with open(chemin_fichier_texte, 'w', encoding='utf-8') as f:
            f.write(texte_pdf)
        
        print(f"Texte extrait du fichier {fichier} et sauvegardé sous {nom_fichier_texte}")
        
        # Diviser le texte en sections
        sections = decouper_fenetre_glissante(texte_pdf)
        all_sections.extend(sections)
        
        # Générer les embeddings pour chaque section
        for section in sections:
            if section.strip():
                embedding = obtenir_embedding_texte(section)
                all_embeddings.append(embedding)

# Convertir les embeddings en un tableau NumPy
embeddings_np = np.array(all_embeddings, dtype=np.float32)

# Créer l'index FAISS
dimension = embeddings_np.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings_np)

# Sauvegarder les embeddings et les sections
np.save("embeddings.npy", embeddings_np)

with open('sections.pkl', 'wb') as f:
    pickle.dump(all_sections, f)

# Sauvegarder l'index FAISS
faiss.write_index(index, "faiss_index.idx")

print("Les embeddings, les sections et l'index FAISS ont été sauvegardés.")