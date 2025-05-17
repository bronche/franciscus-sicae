import streamlit as st
from openai import OpenAI
import os

# Configuration de la page Streamlit
st.set_page_config(page_title="Franciscus - Assistant SICAE", page_icon="⚡")

# Affichage d'accueil
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

# Initialisation du client OpenRouter (compatible OpenAI)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Chargement de la base de connaissances
try:
    with open("base_connaissances.txt", "r", encoding="utf-8") as f:
        connaissances = f.read()
except FileNotFoundError:
    st.error("⚠️ Fichier base_connaissances.txt introuvable.")
    connaissances = ""

# Champ de saisie utilisateur
question = st.text_input("❓ Posez votre question ici :")

# Génération de la réponse
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
            st.success(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
