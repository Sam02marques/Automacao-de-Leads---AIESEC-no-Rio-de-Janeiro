import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import urllib3

# Carrega o .env com as variáveis
load_dotenv()


# Desativa avisos de segurança por causa do verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURAÇÕES ---
CLIENT_ID = os.getenv('PODIO_CLIENT_ID')
CLIENT_SECRET = os.getenv('PODIO_CLIENT_SECRET')
USERNAME = os.getenv('PODIO_USERNAME')
PASSWORD = os.getenv('PODIO_PASSWORD')
EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
SENHA_APP_GOOGLE = os.getenv('SENHA_APP_GOOGLE')
APP_ID = 29772898


LOG_FILE = 'leads_enviados.txt'
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()

def enviar_email(nome, email_destino):
    msg = EmailMessage()
    msg['Subject'] = '🌍 Seu interesse na AIESEC Rio de Janeiro!'
    msg['From'] = f"Samuel da AIESEC no Rio de Janeiro <{EMAIL_REMETENTE}>"
    msg['To'] = email_destino
    
    corpo = f"""Olá, {nome}! Tudo bem?

Vi que você demonstrou interesse em nossos programas de intercâmbio recentemente e apareceu aqui no meu sistema da AIESEC no Rio de Janeiro. 

Como somos a maior organização gerida por jovens do mundo, nosso objetivo é desenvolver sua liderança através de experiências internacionais práticas. Seja no Voluntário Global ou no Talento Global, temos o projeto certo para o seu perfil!

Gostaria de agendar uma conversa rápida para tirarmos suas dúvidas? 

Você pode responder a este e-mail diretamente ou, se preferir, entrar em contato conosco pelo nosso formulário oficial de atendimento:
👉 https://aiesec.org.br/forms-de-atendimento/

Estamos ansiosos para te ajudar a dar o próximo passo na sua carreira e impacto no mundo!

Atenciosamente,

Samuel Marques de Araujo
Equipe da AIESEC no Rio de Janeiro"""

    msg.set_content(corpo)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_APP_GOOGLE)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"   ❌ Erro SMTP: {e}")
        return False

print(">>> SCRIPT INICIADO <<<")

try:
    # 1. Autenticação
    auth_data = {'grant_type': 'password', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'username': USERNAME, 'password': PASSWORD}
    auth_res = requests.post('https://podio.com/oauth/token', data=auth_data, verify=False).json()
    token = auth_res['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Autenticado!")

    # 2. Busca de Leads
    items_url = f'https://api.podio.com/item/app/{APP_ID}/filter/'
    # Aumentamos o limite para 200 para garantir que pegamos leads recentes
    payload = {"limit": 500}
    response = requests.post(items_url, headers=headers, json=payload, verify=False).json()
    
    lista_leads = response.get('items', [])
    print(f"📊 Leads recebidos do Podio: {len(lista_leads)}")

    if len(lista_leads) == 0:
        print("⚠️ A API retornou uma lista vazia. Verifique se o App ID 29772898 tem itens.")

    with open(LOG_FILE, 'r+') as f:
        enviados = f.read().splitlines()
        
        for item in lista_leads:
            item_id = str(item['item_id'])
            
            # Mapeamento de campos
            fields = {}
            for f_data in item.get('fields', []):
                label = f_data.get('label')
                values = f_data.get('values', [])
                if label and values:
                    val = values[0].get('value')
                    fields[label] = val['text'] if isinstance(val, dict) and 'text' in val else val

            # Captura de valores para o filtro
            regiao = str(fields.get('Qual é a AIESEC mais próxima de você?', '')).strip()
            status = str(fields.get('[INTERNO] Status', '')).strip().upper()

            # ESTE PRINT É A CHAVE: Ele vai mostrar o que o script está vendo
            if regiao != "" or status != "":
                 print(f"🔎 Analisando ID {item_id}: Região='{regiao}' | Status='{status}'")

            if regiao == 'AIESEC no Rio de Janeiro' and status == 'OPEN':
                if item_id not in enviados:
                    nome = fields.get('Nome ', 'Interessado(a)')
                    
                    # Ajustado para buscar apenas 'Email'
                    email_raw = fields.get('Email') 
                    
                    email_destino = None
                    if isinstance(email_raw, dict):
                        email_destino = email_raw.get('value')
                    elif isinstance(email_raw, str):
                        email_destino = email_raw

                    if email_destino:
                        print(f"📧 Lead qualificado encontrado! Enviando para: {nome} ({email_destino})")
                        if enviar_email(nome, email_destino):
                            f.write(f"{item_id}\n")
                            print(f"🚀 SUCESSO: Email disparado e ID {item_id} salvo no log.")
                    else:
                        print(f"⚠️ Alerta: Lead {item_id} ({nome}) não tem dados no campo 'Email'.")
                        
except Exception as e:
    # 2. O 'except' captura qualquer erro e impede o script de travar
    print(f"❌ Ocorreu um erro durante a execução: {e}")

finally:
    # Executa sempre, dando um feedback final
    print(">>> Fim da tentativa de processamento <<<")
