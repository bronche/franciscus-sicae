
import streamlit as st
from openai import OpenAI
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Affichage de l'image
st.set_page_config(page_title="Franciscus", page_icon="⚡")
st.image("franciscus.png", width=180)

st.markdown("""
# 🤖 Franciscus – Assistant IA SICAE

Posez vos questions liées à :
- 📂 La relation client (contrats, factures, délais…)
- 🔧 La technique Gaz (interventions, sécurité, consignation…)

Cochez la base que vous souhaitez interroger :
""")

# Case à cocher : base client ou gaz
base_client = st.checkbox("📄 Base Client (documents SICAE)", value=True)
base_gaz = not base_client

# Charger les index
def charger_index(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Recherche contextuelle dans un index
def rechercher_blocs(question, index, top_n=4):
    docs = [bloc["contenu"] for bloc in index]
    titres = [bloc["titre"] for bloc in index]
    vect = TfidfVectorizer().fit_transform([question] + docs)
    cos_sim = cosine_similarity(vect[0:1], vect[1:]).flatten()
    indices = cos_sim.argsort()[-top_n:][::-1]
    return [f"### {titres[i]}\n{docs[i]}" for i in indices]

# Chargement index selon choix
index_path = "index_client_affine.json" if base_client else "index_gaz_affine.json"
index = charger_index(index_path)

# Zone de question
question = st.text_input("❓ Posez votre question ici :")

if question:
    blocs = rechercher_blocs(question, index)
    contexte = "\n\n".join(blocs)

    st.markdown("### 🔍 Documents utilisés :")
    for bloc in blocs:
        st.markdown(bloc)

    with st.spinner("✍️ Franciscus rédige sa réponse..."):
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es Franciscus, assistant de la SICAE. Voici les extraits documentaires à disposition :\n{contexte}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.4,
                max_tokens=700
            )
            st.success(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Erreur : {e}")
