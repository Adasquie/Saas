import openai
import numpy as np
import faiss
import nltk
nltk.download('punkt')  # Télécharge le tokenizer pour les phrases
from nltk.tokenize import sent_tokenize
from sklearn.cluster import DBSCAN

# Exemple d'initialisation de l'index FAISS
embedding_dimension = 1536  # Assurez-vous que la dimension correspond à celle des embeddings
index2 = faiss.IndexFlatL2(embedding_dimension)  # Initialise un index de type L2

# Fonction pour obtenir l'embedding d'un texte
def obtenir_embedding_texte(texte):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=texte
    )
    return response.data[0].embedding

# Fonction pour diviser le texte en segments (par exemple, par phrase ou paragraphe)
def segmenter_texte(texte):
    # Utilisation de NLTK pour découper le texte en phrases
    return sent_tokenize(texte)

# Fonction pour indexer chaque phrase d'un texte
def indexer_par_phrases(texte, index, sections):
    phrases = sent_tokenize(texte)  # Découpe le texte en phrases
    for i, phrase in enumerate(phrases):
        embedding = obtenir_embedding_texte(phrase)  # Génère un embedding pour chaque phrase
        index.add(np.array([embedding], dtype=np.float32))  # Ajoute l'embedding à FAISS
        sections.append((phrase, i))  # Stocke la phrase et sa position

# Fonction de recherche pour trouver les sections similaires à une requête
def rechercher_similaires(embedding_recherche, index, sections, k=5):
    D, I = index2.search(np.array([embedding_recherche], dtype=np.float32), k)
    return [(sections[i], D[0][j]) for j, i in enumerate(I[0])]