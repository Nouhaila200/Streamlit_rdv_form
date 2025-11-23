import streamlit as st
from huggingface_hub import InferenceClient
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image

# --- Configuration Hugging Face ---
HF_TOKEN = st.secrets["hf_token"]
client = InferenceClient(token=HF_TOKEN)

# --- Chargement favicon ---
favicon = Image.open("favicon.png")
st.set_page_config(page_title="Décodage intuitif", page_icon=favicon)
st.markdown("<h1 style='text-align: center;'>Bienvenue chez Estelle Viguier !</h1>", unsafe_allow_html=True)

# --- Validation email ---
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# --- Fonction LLM ---
def get_decoding_response(symptome):
    if not symptome.strip():
        return "Veuillez entrer un symptôme valide."
    
    prompt = f"""
Tu es Estelle Viguier, thérapeute spécialisée en décodage émotionnel. Voici le message : « {symptome} » 
Réponds de manière douce, intuitive et rassurante, comme si tu parlais directement à la personne.
"""
    try:
        response = client.text_generation(
            model="TheBloke/WizardLM-7B-uncensored-GPTQ",
            inputs=prompt,
            max_new_tokens=700,
            temperature=0.8
        )
        return response[0].generated_text
    except Exception as e:
        return f"Erreur de connexion au service de décodage : {e}"

# --- Envoi email ---
def send_email_to_estelle(name, email, service, message, interpretation):
    try:
        sender_email = "contactestelleviguier@gmail.com"
        receiver_email = "nouhailaourrad0@gmail.com"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = sender_email
        smtp_password = st.secrets["smtp_password"]

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

# --- Formulaire Streamlit ---
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
