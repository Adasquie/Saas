from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import openai
import faiss
import pickle
import numpy as np

load_dotenv()

app = Flask(__name__)

# Charger la clé API de manière sécurisée
openai.api_key = os.getenv("OPENAI_API_KEY")

from tools import sauvegarder_historique, charger_historique, add_message_to_history, rechercher_contexte_historique, obtenir_embedding_texte, rechercher_similaires, indexer_par_phrases

# Charger l'index FAISS et les sections
index = faiss.read_index("faiss_index.idx")
print(type(index))

with open('sections.pkl', 'rb') as f:
    sections = pickle.load(f)

# Charger les embeddings et l'historique
embeddings = np.load("embeddings.npy")
fichier_historique = "historique_conversation.json"
conversation_history = charger_historique(fichier_historique)

# Initialisation d'un index FAISS pour l'historique
embedding_dimension = 1536
historique_index = faiss.IndexFlatL2(embedding_dimension)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    # Obtenir l'embedding de la requête
    embedding_requete = obtenir_embedding_texte(user_message)

    # Recherche des informations pertinentes
    resultats = rechercher_similaires(embedding_requete, index, sections)
    textes_combines = "\n\n".join([section for section, _ in resultats])

    # Recherche des messages pertinents dans l'historique
    contexte_historique = rechercher_contexte_historique(embedding_requete, historique_index, conversation_history)
    textes_combines_historique = "\n\n".join(contexte_historique)

    # Ajouter le message utilisateur et les résultats à l’historique
    add_message_to_history(conversation_history, "user", user_message, historique_index)
    # add_message_to_history(conversation_history, "assistant", f"Voici les informations pertinentes : {textes_combines}")

    # Créer le contexte global en combinant les deux sources
    contexte = f"Historique pertinent :\n\n{textes_combines_historique}\n\n" \
               f"Informations externes :\n\n{textes_combines}"
    
    # Ajouter le contexte en tant que message système
    conversation_with_context = conversation_history + [{"role": "system", "content": contexte}]

    # Créer la réponse en utilisant le modèle GPT avec l'historique
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_with_context,
        max_tokens=150,
        temperature=0.7,
        stream=True
    )

    assistant_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            assistant_response += content

    # Ajouter la réponse de l'assistant à l’historique
    add_message_to_history(conversation_history, "assistant", assistant_response, historique_index)

    # Sauvegarder l'historique après chaque interaction
    sauvegarder_historique(fichier_historique, conversation_history)

    # Retourner la réponse au frontend
    return jsonify({"response": assistant_response})

if __name__ == '__main__':
    app.run(debug=True)