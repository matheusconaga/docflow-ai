import os
import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

resend.api_key = os.getenv("RESEND_API_KEY", "re_123456789")

# Define onde os templates estão salvos
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "emails"))
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(["html", "xml"])
)
def get_welcome_email_html():
    template = env.get_template("welcome_preregistration.html")
    return template.render()

def send_welcome_email(to_email: str):
    try:
        html_content = get_welcome_email_html()

        # Usar e-mail de envio padrão ou um fictício caso não tenha domínio verificado no Resend
        from_email = os.getenv("RESEND_FROM_EMAIL", "contato@educassist.com.br")

        params = {
            "from": f"EducAssist <{from_email}>",
            "to": [to_email],
            "subject": "Confirmação de Pré-Registro no EducAssist 🚀",
            "html": html_content,
        }
        
        # Só tenta enviar se tiver uma API key configurada
        if "re_" in resend.api_key and resend.api_key != "re_123456789":
            email = resend.Emails.send(params)
            print(f"E-mail enviado para {to_email}. ID: {email['id']}")
            return True
        else:
            print(f"Modo DEV: E-mail não enviado para {to_email} (sem chave do Resend configurada).")
            return False

    except Exception as e:
        print(f"Erro ao enviar e-mail via Resend: {e}")
        return False
