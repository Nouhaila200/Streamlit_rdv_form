import streamlit as st
import os
from huggingface_hub import InferenceClient
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration Hugging Face ---
HF_TOKEN = st.secrets["hf_token"]
SMTP_PASSWORD = st.secrets["smtp_password"]
client = InferenceClient(token=HF_TOKEN, provider="together")

# --- Validation email ---
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# --- Fonction Hugging Face ---
def get_decoding_response(symptome):
    if not symptome.strip():
        return "Veuillez entrer un symptôme valide."

    prompt = f"""
Tu es Estelle Viguier, thérapeute spécialisée en décodage émotionnel et somatique. Quand une personne exprime un symptôme ou une difficulté, tu lui proposes avec bienveillance une piste de compréhension possible, sous forme de réponse douce, intuitive et structurée. Voici le message reçu : « {symptome} »
Réponds directement à cette personne, comme si tu étais Estelle, en suivant **strictement cette structure**, sans jamais expliquer ce que tu fais ni répéter les consignes du prompt. Écris uniquement le message final à afficher à la personne.

---
1. **Introduction** (commence toujours par) : Merci pour ta confiance. On va explorer ensemble ce qui se joue pour toi. Je vais te poser quelques questions, pour t’aider à mettre en lumière ce que ton corps veut peut-être te dire.
2. **3 à 5 questions ouvertes adaptées à ce cas précis**, pour encourager la réflexion. Exemples à adapter :
- Depuis quand ressens-tu cela ?
- Dans quel contexte cela a-t-il commencé ?
- Est-ce qu’il y a quelque chose que tu n’arrives pas à exprimer ?
- Qu’est-ce que cela t’empêche de faire ?
- Quel événement a précédé cette sensation ?
3. **Interprétation globale brève (max. 5 lignes)** : Formule-la de manière douce, sans jamais affirmer une vérité absolue. Exemples :
- Il se pourrait que ce symptôme reflète…
- Ton corps cherche peut-être à te montrer que…
- Peut-être que tu as besoin de…
4. **Phrase de clôture rassurante à la première personne** : Exemples :
- Je suis là pour t’accompagner.
- On va éclaircir cela ensemble, je suis avec toi.
- Tu peux compter sur moi dans ce cheminement.

---
Contraintes strictes :
- Ne parle **jamais** de toi comme assistant ou intelligence artificielle.
- Parle **uniquement** au nom d’Estelle.
- Utilise **le tutoiement**.
- N’utilise jamais "chère", mais "chérie" si nécessaire.
- Adopte un **ton doux, intuitif, rassurant, chaleureux**.
Ne commence **jamais** par "Voici le message", "Je vais poser", ou une explication. Donne directement la réponse destinée à la personne.
"""

    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erreur de connexion au service de décodage : {e}"

# --- Fonction envoi email ---
def send_email_to_estelle(name, email, service, message, interpretation):
    try:
        sender_email = "contactestelleviguier@gmail.com"
        receiver_email = "nouhailaourrad0@gmail.com"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = sender_email
        smtp_password = "dhan rcbt hkxa qecc"  # mot de passe généré

        subject = f"Nouvelle demande de {name}"
        body = f"""
Nom : {name}
Email : {email}
Service : {service}
Message utilisateur : {message}

--- Interprétation générée :
{interpretation}
"""
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        st.success("Email envoyé à Estelle avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")

# --- Streamlit UI ---
st.title("Décodage intuitif avec Estelle Viguier")

with st.form("form_decodage"):
    name = st.text_input("Nom complet :")
    email = st.text_input("Email :")
    service = st.selectbox("Service souhaité :", [
        "Séance de kinésiologie",
        "Gestion du stress",
        "Accompagnement émotionnel",
        "Décodage intuitif",
        "Formation bien-être"
    ])
    symptome = st.text_area("Décris tes symptômes ou ta situation :")
    submit_button = st.form_submit_button("Envoyer et obtenir le décodage")

if submit_button:
    if not name.strip() or not email.strip() or not symptome.strip():
        st.warning("Merci de remplir tous les champs.")
    elif not validate_email(email):
        st.warning("Merci d'entrer un email valide.")
    else:
        with st.spinner("Génération du décodage en cours..."):
            interpretation = get_decoding_response(symptome)
            st.subheader("Réponse du décodage :")
            st.write(interpretation)
            send_email_to_estelle(name, email, service, symptome, interpretation)
