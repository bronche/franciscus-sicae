
import streamlit as st
from openai import OpenAI
import os

# Configuration de la page
st.set_page_config(page_title="Franciscus", page_icon="⚡")
st.image("franciscus.png", width=180)

st.markdown("""
# 🤖 Franciscus – Assistant IA SICAE

Posez vos questions liées à :
- 📂 La relation client (contrats, factures, délais…)
- 🔧 La technique Gaz (interventions, sécurité, consignation…)

Cochez la base que vous souhaitez interroger :
""")

# Choix de la base à interroger
base_client = st.checkbox("📄 Base Client (documents SICAE)", value=True)
base_gaz = not base_client

# Charger la base texte correspondante
def charger_connaissances(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Base de connaissance introuvable."

base_path = "base_connaissances_client.txt" if base_client else "base_connaissances_gaz.txt"
connaissances = charger_connaissances(base_path)

# Zone de question
question = st.text_input("❓ Posez votre question ici :")

if question:
    with st.spinner("✍️ Franciscus rédige sa réponse..."):
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, assistant IA de la SICAE. Tu réponds en t'appuyant uniquement sur la base suivante :\n{connaissances}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=700
            )
            st.success(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Erreur : {e}")
