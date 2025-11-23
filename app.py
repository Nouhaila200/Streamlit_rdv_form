import streamlit as st
from huggingface_hub import InferenceClient
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image

# --- Configuration Hugging Face ---
HF_TOKEN = st.secrets["hf_token"]
SMTP_PASSWORD = st.secrets["smtp_password"]

# Initialize Hugging Face InferenceClient
client = InferenceClient(token=HF_TOKEN)

# --- Chargement du favicon ---
favicon = Image.open("favicon.png")
st.set_page_config(page_title="Décodage intuitif avec Estelle Viguier", page_icon=favicon)
st.markdown("<h1 style='text-align: center;'>Bienvenue chez Estelle Viguier !</h1>", unsafe_allow_html=True)

# --- Validation email ---
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# --- Fonction Hugging Face ---
def get_decoding_response(symptome):
    if not symptome.strip():
        return "Veuillez entrer un symptôme valide."

    prompt = f"""
Tu es Estelle Viguier, thérapeute spécialisée en décodage émotionnel et somatique. Quand une personne exprime un symptôme ou une difficulté, tu lui proposes avec bienveillance une piste de compréhension possible, sous forme de réponse douce, intuitive et structurée. Voici le message reçu : « {symptome} ».
Réponds directement à cette personne, comme si tu étais Estelle, en suivant strictement cette structure, sans jamais expliquer ce que tu fais ni répéter les consignes du prompt. Écris uniquement le message final à afficher à la personne.

---
1. Introduction (commence toujours par) : Merci pour ta confiance. On va explorer ensemble ce qui se joue pour toi. Je vais te poser quelques questions, pour t’aider à mettre en lumière ce que ton corps veut peut-être te dire.
2. 3 à 5 questions ouvertes adaptées à ce cas précis, pour encourager la réflexion.
3. Interprétation globale (min. 15 lignes) : Formule-la de manière douce, sans jamais affirmer une vérité absolue.
4. Phrase de clôture rassurante à la première personne.
"""

    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
            temperature=0.8,
            max_tokens=700
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
        smtp_password = SMTP_PASSWORD

        subject = f"Nouvelle demande de {name}"
        body = f"""
Nom : {name}
Email : {email}
Service : {service}
Message utilisateur : {message}

--- Interprétation générée ---
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

# --- CSS ---
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        st.markdown("""
        <style>
        .stApp { background-image: none; background-color: initial; }
        p { color: #ff00A2; font-weight: bold; margin-bottom: 1.1rem; font-size: 2.2rem; }
        button.css-18ni7ap.e8zbici2 { background-color: #ff00ff !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }
        h3 { color: #ff00A2; }
        .st-emotion-cache-r44huj { color: black; }
        .stForm > div { margin-bottom: 20px !important; }
        </style>
        """, unsafe_allow_html=True)

load_css()
