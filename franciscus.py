
import streamlit as st
from openai import OpenAI
import os

# Configuration de la page
st.set_page_config(page_title="Franciscus - Assistant SICAE", page_icon="⚡")

# Chargement de l'image de Franciscus
st.image("https://www.sicaesomme.fr/assets/custom/img/logo.png", width=200)

# Titre et présentation
st.markdown("""
# 🤖 Franciscus
Bienvenue ! Je suis **Franciscus**, l'assistant virtuel de la SICAE de la Somme et du Cambraisis.

Posez-moi une question sur :
- La souscription ou la résiliation
- Votre facture ou le paiement
- Les services aux collectivités ou aux pros
- Le raccordement ou les coupures
- Les Conditions Générales de Vente
""")

# Initialisation du client OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Chargement des connaissances
try:
    with open("base_connaissances.txt", "r", encoding="utf-8") as f:
        connaissances = f.read()
except FileNotFoundError:
    st.error("⚠️ Fichier base_connaissances.txt introuvable.")
    connaissances = ""

# Initialisation de l'historique
if "historique" not in st.session_state:
    st.session_state.historique = []

# Réinitialisation
if st.button("🔄 Réinitialiser l'historique"):
    st.session_state.historique = []

# Affichage de l'historique
with st.expander("📜 Historique des questions posées"):
    if st.session_state.historique:
        for i, q in enumerate(st.session_state.historique, 1):
            st.markdown(f"**{i}.** {q}")
    else:
        st.info("Aucune question posée pour le moment.")

# Champ de question
question = st.text_input("❓ Posez votre question ici :")

# Traitement
if question:
    with st.spinner("Franciscus rédige sa réponse..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Tu es Franciscus, un assistant client pour la SICAE. Tu réponds de manière claire, concise et accessible en t'appuyant sur les informations suivantes : {connaissances}"
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.4,
                max_tokens=500
            )
            reponse_text = response.choices[0].message.content
            st.session_state.historique.append(question)
            st.success(reponse_text)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
