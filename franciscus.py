import streamlit as st
from openai import OpenAI
import os

# Configuration de la page Streamlit
st.set_page_config(page_title="Franciscus - Assistant SICAE", page_icon="⚡")

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

# Initialisation du client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chargement de la base de connaissances
with open("base_connaissances.txt", "r", encoding="utf-8") as f:
    connaissances = f.read()

# Champ de saisie de la question utilisateur
question = st.text_input("❓ Votre question ici :")

# Traitement de la question
if question:
    with st.spinner("Franciscus rédige sa réponse..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Tu es Franciscus, un assistant client pour la SICAE. Tu réponds de façon claire, concise et conviviale en t'appuyant sur ces données : {connaissances}"
                    },
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=500
            )
            st.success(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
