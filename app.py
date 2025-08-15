import streamlit as st
import os
from huggingface_hub import InferenceClient
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_lottie import st_lottie
import requests

# --- Configuration de la page ---
st.set_page_config(
    page_title="Décodage intuitif avec Estelle Viguier",
    page_icon="💫",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Configuration Hugging Face et SMTP ---
HF_TOKEN = st.secrets["hf_token"]
SMTP_PASSWORD = st.secrets["smtp_password"]

client = InferenceClient(token=HF_TOKEN, provider="together")

# --- Fonction pour charger Lottie ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- Validation email ---
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# --- Fonction Hugging Face ---
def get_decoding_response(symptome):
    if not symptome.strip():
        return "Veuillez entrer un symptôme valide."
    
    prompt = f"""
Tu es Estelle Viguier, thérapeute spécialisée en décodage émotionnel et somatique...
(Ton prompt complet ici)
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
        smtp_password = SMTP_PASSWORD  # Utiliser le secret

        subject = f"Nouvelle demande de {name}"
        body = f"""
Nom : {name}
Email : {email}
Service : {service}
Message utilisateur :
{message}

---

Interprétation générée :
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

# --- Exemple d'animation Lottie ---
lottie_decodage = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")
st_lottie(lottie_decodage, speed=1, width=300, height=300, key="decodage")

# --- Interface ---
st.title("Décodage intuitif avec Estelle Viguier")

with st.form("form_decodage"):
    name = st.text_input("Nom complet :")
    email = st.text_input("Email :")
    service = st.selectbox("Service souhaité :", ["Séance de kinésiologie", "Gestion du stress", "Accompagnement émotionnel", "Décodage intuitif", "Formation bien-être"])
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
