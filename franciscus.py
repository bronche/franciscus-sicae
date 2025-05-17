import streamlit as st
from openai import OpenAI
import os
import json
import csv
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Config
st.set_page_config(page_title="Franciscus - SICAE", page_icon="⚡")
st.image("logo-sicae.png", width=200)

st.markdown("""
# 🤖 Franciscus
Bienvenue ! Je suis **Franciscus**, l'assistant IA de la SICAE.
Posez-moi vos questions :
- 📱 Clientèle (abonnement, facture…)
- 🔧 Technique Gaz (procédures, consignation…)
""")

# Initialisation OpenAI / OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Chargement des textes
def charger_texte(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def charger_index_gaz():
    try:
        with open("index_gaz_affine.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def rechercher_blocs(question, index, top_n=4):
    docs = [bloc['contenu'] for bloc in index]
    titres = [bloc['titre'] for bloc in index]
    vect = TfidfVectorizer().fit_transform([question] + docs)
    cos_sim = cosine_similarity(vect[0:1], vect[1:]).flatten()
    indices = cos_sim.argsort()[-top_n:][::-1]
    return [{"titre": titres[i], "contenu": docs[i]} for i in indices]

# 📂 Sélection de questions précédentes par thème
options_combinees = [""]
try:
    historique_df = pd.read_csv("historique_questions.csv", names=["datetime", "sujet", "question"], encoding="utf-8")
    historique_df.drop_duplicates(subset=["question"], inplace=True)
    options_client = [f"Client : {q}" for q in historique_df[historique_df["sujet"] == "client"]["question"].tolist()]
    options_gaz = [f"Gaz : {q}" for q in historique_df[historique_df["sujet"] == "gaz"]["question"].tolist()]
    options_combinees += options_client + options_gaz
except FileNotFoundError:
    pass

with st.expander("📂 Questions précédentes (sélectionnable par thème)"):
    selection = st.selectbox("📜 Choisir une question à réutiliser :", options_combinees)
    if selection and ": " in selection:
        st.session_state.question_predefinie = selection.split(": ", 1)[1]

# Initialiser question cliquée
if "question_predefinie" not in st.session_state:
    st.session_state.question_predefinie = ""

# Enregistrer question posée
def enregistrer_historique_csv(question, sujet):
    ligne = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sujet, question]
    with open("historique_questions.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(ligne)

# Base client + index gaz
connaissances_client = charger_texte("base_connaissances.txt")
index_gaz = charger_index_gaz()

# Reconnaissance auto + option manuelle
def identifier_sujet(question):
    mots_cles_gaz = ["gaz", "branchement", "intervention", "consignation", "fuite", "réseau", "détendeur", "odorisation", "canalisation", "piquage", "poste", "HTA", "compteur"]
    question_lower = question.lower()
    if any(mot in question_lower for mot in mots_cles_gaz):
        return "gaz"
    return "client"

use_force_gaz = st.checkbox("🔧 Forcer la base technique Gaz")

# Champ question
question = st.text_input("❓ Posez votre question ici :", value=st.session_state.question_predefinie)

if question and st.session_state.question_predefinie:
    st.session_state.question_predefinie = ""

# Historique session
if "historique" not in st.session_state:
    st.session_state.historique = []

if st.button("🔄 Réinitialiser l'historique"):
    st.session_state.historique = []

with st.expander("📜 Historique des questions posées (session actuelle)"):
    if st.session_state.historique:
        for i, q in enumerate(st.session_state.historique, 1):
            st.markdown(f"**{i}.** {q}")
    else:
        st.info("Aucune question posée pour le moment.")

# Traitement
if question:
    sujet = "gaz" if use_force_gaz else identifier_sujet(question)

    if sujet == "gaz":
        blocs = rechercher_blocs(question, index_gaz)
        context = "\n\n".join([f"### {b['titre']}\n{b['contenu']}" for b in blocs])
        with st.expander("🔍 Blocs utilisés (base Gaz)"):
            for b in blocs:
                st.markdown(f"**{b['titre']}**\n{b['contenu']}")
    else:
        context = connaissances_client

    with st.spinner("Franciscus rédige sa réponse..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, assistant IA de la SICAE. Voici les documents à disposition :\n{context}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=700
            )
            if response and hasattr(response, "choices") and response.choices:
                reponse_text = response.choices[0].message.content
                st.success(reponse_text)
                st.session_state.historique.append(question)
                enregistrer_historique_csv(question, sujet)
            else:
                st.error("❌ Réponse vide ou invalide.")
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
