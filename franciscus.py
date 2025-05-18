
import streamlit as st
from openai import OpenAI
import os

# Configuration
st.set_page_config(page_title="Franciscus", page_icon="⚡")
st.image("franciscus.png", width=180)

st.markdown("""
# 🤖 Franciscus – Assistant IA SICAE

Posez vos questions sur :
- 🔧 Technique Gaz (sécurité, branchement, consignation…)
- 📄 Clientèle (contrat, facture, délais, souscription…)

Franciscus choisit automatiquement la bonne base documentaire.
""")

# Détection intelligente de la base
def identifier_base(question):
    mots_cles_gaz = [
        "gaz", "branchement", "intervention", "consignation", "poste", "odorisation",
        "fuite", "réseau", "piquage", "canalisation", "détendeur", "compteur gaz", "DT", "DICT"
    ]
    question_lower = question.lower()
    if any(mot in question_lower for mot in mots_cles_gaz):
        return "base_connaissances_gaz.txt"
    return "base_connaissances_client.txt"

# Chargement du contenu
def charger_connaissances(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "⚠️ Base de connaissance introuvable."

# Zone de question
question = st.text_input("❓ Posez votre question ici :")

if question:
    base_file = identifier_base(question)
    connaissances = charger_connaissances(base_file)

    with st.spinner(f"📚 Recherche dans la base {'Gaz' if 'gaz' in base_file else 'Client'}..."):
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, assistant IA de la SICAE. Tu réponds uniquement sur la base suivante :\n{connaissances}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=700
            )
            if response and hasattr(response, "choices") and response.choices:
                st.success(response.choices[0].message.content)
            else:
                st.error("❌ Réponse vide ou invalide.")
        except Exception as e:
            st.error(f"Erreur : {e}")
