import requests
from bs4 import BeautifulSoup

# URLs à surveiller et à intégrer
urls = [
    "https://www.sicaesomme.fr/souscription-en-ligne.html",
    "https://www.sicaesomme.fr/l-entreprise-sicae/nos-services.html",
    "https://www.sicaesomme.fr/l-entreprise-sicae/les-accueils.html",
    "https://www.sicaesomme.fr/nos-offres-et-services/les-conditions-generales-de-vente.html"
]

def extraire_texte_depuis_site(urls):
    contenu_total = ""
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in urls:
        try:
            print(f"📥 Extraction de : {url}")
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            for tag in soup(["script", "style", "header", "footer", "nav"]):
                tag.decompose()
            texte = soup.get_text(separator="\n", strip=True)
            contenu_total += f"\n### Contenu de la page : {url}\n{texte}\n"
        except Exception as e:
            contenu_total += f"\n[Erreur lors du chargement de {url} : {e}]\n"
    return contenu_total

# Extraire le contenu
contenu = extraire_texte_depuis_site(urls)

# Écraser le fichier utilisé par Franciscus
chemin_fichier = "base_connaissances.txt"
with open(chemin_fichier, "w", encoding="utf-8") as f:
    f.write(contenu)

print(f"✅ Mise à jour de {chemin_fichier} terminée.")
