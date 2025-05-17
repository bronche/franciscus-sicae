
import streamlit as st
from openai import OpenAI
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Chargement des connaissances
def charger_texte(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Chargement de l'index Gaz découpé
def charger_index_gaz():
    try:
        with open("index_gaz.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def rechercher_blocs(question, index, top_n=3):
    docs = [bloc['contenu'] for bloc in index]
    titres = [bloc['titre'] for bloc in index]
    vect = TfidfVectorizer().fit_transform([question] + docs)
    cos_sim = cosine_similarity(vect[0:1], vect[1:]).flatten()
    indices = cos_sim.argsort()[-top_n:][::-1]
    return [f"### {titres[i]}\n{docs[i]}" for i in indices]

# Interface
st.set_page_config(page_title="Franciscus - SICAE", page_icon="⚡")
st.image("logo-sicae.png", width=200)

st.markdown("""
# 🤖 Franciscus
Bienvenue ! Je suis **Franciscus**, l'assistant virtuel de la SICAE.
Posez-moi vos questions :
- 📱 Clientèle (abonnement, facture, horaires…)
- 🔧 Technique Gaz (intervention, sécurité, branchement…)
""")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

connaissances_client = charger_texte("base_connaissances.txt")
index_gaz = charger_index_gaz()

def identifier_sujet(question):
    mots_cles_gaz = ["gaz", "branchement", "intervention", "consignation", "fuite", "réseau", "détendeur", "odorisation", "canalisation", "compteur", "piquage"]
    question_lower = question.lower()
    if any(mot in question_lower for mot in mots_cles_gaz):
        return "gaz"
    return "client"

if "historique" not in st.session_state:
    st.session_state.historique = []

if st.button("🔄 Réinitialiser l'historique"):
    st.session_state.historique = []

with st.expander("📜 Historique des questions posées"):
    if st.session_state.historique:
        for i, q in enumerate(st.session_state.historique, 1):
            st.markdown(f"**{i}.** {q}")
    else:
        st.info("Aucune question posée pour le moment.")

question = st.text_input("❓ Posez votre question ici :")

if question:
    sujet = identifier_sujet(question)
    if sujet == "gaz":
        context = "\n\n".join(rechercher_blocs(question, index_gaz, top_n=4))
    else:
        context = connaissances_client

    with st.spinner("Franciscus rédige sa réponse..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, un assistant SICAE. Voici les données :\n{context}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=600
            )
            if response and hasattr(response, "choices") and response.choices:
                st.success(response.choices[0].message.content)
                st.session_state.historique.append(question)
            else:
                st.error("❌ Réponse vide ou invalide.")
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
