
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
Bienvenue ! Je suis **Franciscus**, l'assistant virtuel de la SICAE de la Somme et du Cambraisis.
Posez-moi vos questions :
- Souscription / Résiliation
- Facture ou Paiement
- Coupures, travaux, raccordement
- Conditions Générales de Vente
""")

# Initialisation OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Chargement base de connaissances
def charger_connaissances():
    try:
        with open("base_connaissances.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("⚠️ base_connaissances.txt introuvable.")
        return ""

connaissances = charger_connaissances()

# Franciscus - Assistant IA
st.subheader("💬 Posez votre question à Franciscus")

if "historique" not in st.session_state:
    st.session_state.historique = []

if st.button("🔄 Réinitialiser l'historique"):
    st.session_state.historique = []

with st.expander("📜 Historique des questions posées"):
    if st.session_state.historique:
        for index, question_hist in enumerate(st.session_state.historique, 1):
            st.markdown(f"**{index}.** {question_hist}")
    else:
        st.info("Aucune question posée pour le moment.")

question = st.text_input("❓ Posez votre question ici :")

if question:
    with st.spinner("Franciscus rédige sa réponse..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, un assistant client pour la SICAE. Tu réponds de manière claire, concise et accessible en t'appuyant sur les informations suivantes : {connaissances}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=500
            )
            reponse_text = response.choices[0].message.content
            st.session_state.historique.append(question)
            st.success(reponse_text)
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")

# Séparation
st.markdown("---")
st.markdown("## 💰 Assistant tarifaire personnalisé")

# Assistant tarifaire
puissances = ["3", "6", "9", "12", "15", "18", "24", "30", "36"]
options = ["Base", "Heures Pleines / Heures Creuses", "Tempo"]

tarifs = {
    "Base": {"3": "103,20 €", "6": "134,16 €", "9": "167,88 €", "12": "202,08 €", "15": "233,76 €", "18": "263,52 €", "24": "319,08 €", "30": "373,32 €", "36": "426,24 €"},
    "Heures Pleines / Heures Creuses": {"3": "137,76 €", "6": "172,80 €", "9": "206,76 €", "12": "238,44 €", "15": "270,12 €", "18": "303,60 €", "24": "365,28 €", "30": "420,84 €", "36": "477,00 €"},
    "Tempo": {"3": "169,92 €", "6": "203,28 €", "9": "233,76 €", "12": "264,36 €", "15": "297,72 €", "18": "329,40 €", "24": "390,00 €", "30": "444,24 €", "36": "502,80 €"}
}

col1, col2 = st.columns(2)
with col1:
    p = st.selectbox("Puissance souscrite (kVA)", puissances, index=1)
with col2:
    o = st.selectbox("Option tarifaire", options)

if p and o:
    st.success(f"💡 Abonnement annuel pour {p} kVA en option {o} : **{tarifs[o][p]} HT/an**")

    # Affichage des prix du kWh
    if o == "Base":
        st.info("💡 **Option Base** : Prix unique de l'énergie : **0,2276 €/kWh** HT")
    elif o == "Heures Pleines / Heures Creuses":
        st.info("💡 **Option HP/HC** : Heures Pleines : **0,2516 €/kWh** HT – Heures Creuses : **0,1828 €/kWh** HT")
    elif o == "Tempo":
        with st.expander("🔎 Détail des prix Tempo (jours bleus, blancs, rouges)"):
            st.markdown("""
            **Jours Bleus**  
            - Heures Pleines : 0,1618 €/kWh  
            - Heures Creuses : 0,1334 €/kWh

            **Jours Blancs**  
            - Heures Pleines : 0,2002 €/kWh  
            - Heures Creuses : 0,1498 €/kWh

            **Jours Rouges**  
            - Heures Pleines : 0,7518 €/kWh  
            - Heures Creuses : 0,1379 €/kWh
            """)

    # Génération du PDF
    if st.button("📄 Télécharger un résumé PDF de ma sélection"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Résumé tarifaire personnalisé - SICAE", ln=1, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Puissance souscrite : {p} kVA", ln=1)
        pdf.cell(200, 10, txt=f"Option tarifaire : {o}", ln=1)
        pdf.cell(200, 10, txt=f"Abonnement annuel : {tarifs[o][p]} HT/an", ln=1)
        pdf.ln(5)

        if o == "Base":
            pdf.multi_cell(0, 10, "Prix unique de l'énergie : 0,2276 €/kWh HT")
        elif o == "Heures Pleines / Heures Creuses":
            pdf.multi_cell(0, 10, "HP : 0,2516 €/kWh HT, HC : 0,1828 €/kWh HT")
        elif o == "Tempo":
            pdf.multi_cell(0, 10, "Tempo :
"
                                  "- Bleus : HP 0,1618 € / HC 0,1334 €
"
                                  "- Blancs : HP 0,2002 € / HC 0,1498 €
"
                                  "- Rouges : HP 0,7518 € / HC 0,1379 €")
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("📥 Télécharger le PDF", data=pdf_output.getvalue(), file_name="tarif_sicae.pdf", mime="application/pdf")
