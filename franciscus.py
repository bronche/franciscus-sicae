
import streamlit as st
from openai import OpenAI
import os

# ──────────────────────────────
#  Configuration de la page
# ──────────────────────────────
st.set_page_config(page_title="Franciscus", page_icon="⚡")
st.image("franciscus.png", width=180)

st.markdown(
    """
# 🤖 Franciscus – Assistant IA SICAE

Pose ta question, puis clique sur **« 💬 Poser la question »**.  
Franciscus choisit automatiquement la bonne base documentaire :

- 📄 *Base Client* (CGV, souscription, factures…)  
- 🔧 *Base Gaz* (branchements, sécurité, DT/DICT…)

---
"""
)

# ──────────────────────────────
#  Fonctions utilitaires
# ──────────────────────────────
def identifier_base(question: str) -> str:
    """Retourne le fichier de base à interroger selon des mots-clés gaz."""
    mots_cles_gaz = [
        "gaz", "branchement", "intervention", "consignation", "poste",
        "odorisation", "fuite", "réseau", "piquage", "canalisation",
        "détendeur", "compteur gaz", "dt", "dict"
    ]
    q = question.lower()
    return "base_connaissances_gaz.txt" if any(m in q for m in mots_cles_gaz) else "base_connaissances_client.txt"


def charger_connaissances(fichier: str) -> str:
    """Charge le contenu texte de la base de connaissances."""
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "⚠️ Base de connaissance introuvable."


# ──────────────────────────────
#  Interface de question
# ──────────────────────────────
question = st.text_input("❓ Posez votre question ici :")
clicked = st.button("💬 Poser la question")

if clicked and question.strip():
    base_file = identifier_base(question)
    connaissances = charger_connaissances(base_file)

    with st.spinner(f"📚 Recherche dans la base {'Gaz' if 'gaz' in base_file else 'Client'}…"):
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )

            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Tu es Franciscus, assistant IA de la SICAE. "
                            "Réponds uniquement à partir de la base suivante :\n"
                            f"{connaissances}"
                        )
                    },
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=700
            )

            if response and getattr(response, "choices", None):
                st.success(response.choices[0].message.content)
            else:
                st.error("❌ Réponse vide ou invalide.")
        except Exception as e:
            st.error(f"Erreur : {e}")
