import os
from chatgpt_test import pergunta_chatgpt
from flask import Flask, request
import requests
from unidecode import unidecode
from dotenv import load_dotenv
app = Flask(__name__)


load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
tokenmeta = os.getenv('tokenmeta')
numero = os.getenv('numero')
numerozap = os.getenv('numerozap')
API_URL = os.getenv('API_URL')

def arruma_texto(text):
    return unidecode(text).lower()

def pega_nome(item_name):
    url = f"https://api.weirdgloop.org/exchange/history/osrs/latest?name={item_name}"
    response = requests.get(url)
    print(f' tentando consultar {item_name} na {url}')
    if response.status_code == 200:
        data = response.json()
        print(f"Resposta da API: {data}")
        if data:
            first_item_name = list(data.keys())[0]
            first_item_data = data[first_item_name]
            return first_item_name, first_item_data
    return None, None
def formata_extenso(valor):
    return f"{valor:,}".replace(",", ".")

def formata_preco(valor):
    if valor >= 1_000_000_000:
        return f"{valor / 1_000_000_000:.1f}B"
    elif valor >= 1_000_000:
        return f"{valor / 1_000_000:.1f}M"
    elif valor >= 1_000:
        return f"{valor / 1_000:.1f}K"
    else:
        return f"{valor:,}"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        verify_token = tokenmeta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == verify_token:
                print("VERIFICADO")
                return challenge, 200
            else:
                return "Token de verificação inválido", 403
        else:
            return "Parâmetros ausentes", 400

    if request.method == "POST":
        data = request.get_json()

        if data:
            entry = data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])
            if messages:
                message = messages[0]
                from_number = message['from']

                text = message['text']['body']
                texto_normalizado = arruma_texto(text)

                if texto_normalizado.startswith('!price '):
                    item_name = text[len('!price '):].strip()
                    item_name_retorno, item_data = pega_nome(item_name)

                    if item_name_retorno:
                        item_price = item_data['price']
                        preco_formatado = formata_preco(item_price)

                        preco_extenso = formata_extenso(item_price)
                        response_message = f"O preço do {item_name_retorno} é {preco_extenso}, {preco_formatado}."
                    else:
                        response_message = "Item não encontrado."

                    send_whatsapp_message(from_number, response_message)
                    #sempre comentar essa linha quando parar de testar, lembre-se que gasta TOKEN na openai.
                else:
                    resposta_chatgpt = pergunta_chatgpt(text)
                    send_whatsapp_message(from_number, resposta_chatgpt)

        return "OK", 200

def send_whatsapp_message(to, body):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numerozap,  # Número do destinatário no formato: 'whatsapp:+<número>'
        "type": "text",
        "text": {"body": body}
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Mensagem enviada com sucesso: {body}")
    else:

        print(f"Erro ao enviar a mensagem: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(port=5000)
