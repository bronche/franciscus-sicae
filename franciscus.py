import streamlit as st
from openai import OpenAI
import os
from fpdf import FPDF
from io import BytesIO

# Configuration
st.set_page_config(page_title="Franciscus - Assistant SICAE", page_icon="⚡")
st.image("logo-sicae.png", width=200)

st.markdown("""
# 🤖 Franciscus
Bienvenue ! Je suis **Franciscus**, l'assistant virtuel de la SICAE.
Posez-moi vos questions :
- 📱 Clientèle (abonnement, facture, horaires…)
- 🔧 Technique Gaz (intervention, sécurité, branchement…)
""")

# Initialisation OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Chargement des deux bases de connaissance
def charger_texte(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

connaissances_client = charger_texte("base_connaissances.txt")
connaissances_gaz = charger_texte("base_connaissances_gaz.txt")

# Fonction de routage selon mots-clés
def identifier_sujet(question):
    mots_cles_gaz = ["gaz", "branchement", "intervention", "consignation", "fuite", "réseau", "détendeur", "odorisation", "canalisation", "compteur gaz"]
    question_lower = question.lower()
    if any(mot in question_lower for mot in mots_cles_gaz):
        return "gaz"
    return "client"

# Historique
if "historique" not in st.session_state:
    st.session_state.historique = []

if st.button("🔄 Réinitialiser l'historique"):
    st.session_state.historique = []

with st.expander("📜 Historique des questions posées"):
    if st.session_state.historique:
        for index, q in enumerate(st.session_state.historique, 1):
            st.markdown(f"**{index}.** {q}")
    else:
        st.info("Aucune question posée pour le moment.")

# Zone de question
question = st.text_input("❓ Posez votre question ici :")

if question:
    sujet = identifier_sujet(question)
    base = connaissances_gaz if sujet == "gaz" else connaissances_client

    with st.spinner(f"Franciscus recherche dans la base {'gaz' if sujet == 'gaz' else 'clientèle'}..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, un assistant IA pour la SICAE. Tu réponds aux questions liées à la {'partie Gaz technique' if sujet == 'gaz' else 'relation clientèle'} en t’appuyant sur les documents suivants : {base}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=600
            )
            reponse_text = response.choices[0].message.content
            st.session_state.historique.append(question)
            st.success(reponse_text)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
