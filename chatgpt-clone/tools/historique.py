import json
import faiss
from .embeddings import obtenir_embedding_texte
import numpy as np

# Exemple d'initialisation de l'index FAISS
embedding_dimension = 1536  # Assurez-vous que la dimension correspond à celle des embeddings
index2 = faiss.IndexFlatL2(embedding_dimension)  # Initialise un index de type L2
embeddings = np.load("embeddings.npy")

# Fonction de sauvegarde de l'historique
def sauvegarder_historique(fichier, historique):
    try:
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(historique, f, ensure_ascii=False, indent=4)
        print(f"Historique sauvegardé dans {fichier}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'historique : {e}")

# Fonction de chargement de l'historique
def charger_historique(fichier):
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            historique = json.load(f)
        print(f"Historique chargé depuis {fichier}")
        return historique
    except FileNotFoundError:
        print(f"Fichier {fichier} non trouvé. Un nouvel historique sera créé.")
        return [{"role": "system", "content": "Tu es un assistant qui fournit des explications simples et compréhensibles."}]
    except Exception as e:
        print(f"Erreur lors du chargement de l'historique : {e}")
        return [{"role": "system", "content": "Tu es un assistant qui fournit des explications simples et compréhensibles."}]

# Ajouter chaque message de l'historique dans l'index FAISS
def add_message_to_history(history, role, content, historique_index):
    embedding = obtenir_embedding_texte(content)  # Génère un embedding pour le message
    history.append({"role": role, "content": content, "embedding": embedding})  # Ajoute l'embedding
    if len(history) > 100:
        del history[1:3]
    # Ajouter l'embedding à l'index historique
    historique_index.add(np.array([embedding], dtype=np.float32))

def rechercher_contexte_historique(embedding_requete, historique_index, history, k=5):
    # Rechercher les k messages de l'historique les plus proches
    D, I = historique_index.search(np.array([embedding_requete], dtype=np.float32), k)
    return [history[i]["content"] for i in I[0] if i < len(history)]