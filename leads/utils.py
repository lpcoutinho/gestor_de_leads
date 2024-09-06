import requests
from .models import Lead
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

BASE_URL = os.getenv('BASE_URL')
INSTANCIA = os.getenv('INSTANCIA')

def send_message(phone_number, text_message, api_key):
    url = f'{BASE_URL}/message/sendText/{INSTANCIA}'
    headers = {
        'Content-Type': 'application/json',
        'apikey': api_key
    }
    data = {
        "number": phone_number,
        "options": {
            "delay": 1200,
            "presence": "composing",
            "linkPreview": True
        },
        "textMessage": {
            "text": text_message
        }
    }

    print("URL:", url)
    print("Headers:", headers)
    print("Data:", data)

    response = requests.post(url, json=data, headers=headers)
    return response

def update_lead_status(lead_id, new_status):
    try:
        lead = Lead.objects.get(pk=lead_id)
        lead.status_lead = new_status
        lead.save()
        return True
    except Lead.DoesNotExist:
        return False
