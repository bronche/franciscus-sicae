
import streamlit as st
import openai
import os

# Configuration du projet
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

# Récupération de la clé API depuis les secrets Streamlit
openai.api_key = os.getenv("OPENAI_API_KEY")

# Nouvelle configuration de client pour OpenAI v1.x
client = openai.OpenAI()

# Chargement de la base de connaissances
with open("base_connaissances.txt", "r", encoding="utf-8") as f:
    connaissances = f.read()

# Interface utilisateur
question = st.text_input("❓ Votre question ici :")

if question:
    with st.spinner("Franciscus rédige sa réponse..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, un assistant client pour la SICAE. Tu réponds de façon claire, concise et conviviale en t'appuyant sur ces données : {connaissances}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=500
            )
            reponse_text = response.choices[0].message.content
            st.success(reponse_text)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")
