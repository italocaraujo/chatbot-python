from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ZAPI_URL = "https://api.z-api.io/3E0DAD8E4FABF012B6D596870211A73F"
ZAPI_TOKEN = "6D2C25339E8916305438B2A9"
VENDEDOR_API_URL = "https://parapisos-autoatendimento-vendedores.onrender.com/proximo-vendedor"

def send_message(phone, message):
    url = f"{ZAPI_URL}/send-message"
    headers = {
        "Authorization": f"Bearer {ZAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "phone": phone,
        "message": message
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return True
    else:
        print("Erro ao enviar a mensagem:", response.text)
        return False

def get_proximo_vendedor():
    try:
        response = requests.get(VENDEDOR_API_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Erro ao buscar vendedor:", e)
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("Dados recebidos do Z-API:", data)  # Log para verificar o que foi recebido

        message = data.get("message", "").strip()
        phone = data.get("phone")

        # Verificar se os dados essenciais estão presentes
        if not phone or not message:
            print("Erro: Dados inválidos (falta de telefone ou mensagem).")
            return jsonify({"error": "Dados inválidos"}), 400

        # Processar a mensagem com base no conteúdo recebido
        if message == "1":
            vendedor = get_proximo_vendedor()
            if vendedor:
                send_message(phone, f"Você será atendido por {vendedor['nome']}.\nChame ele no WhatsApp: https://wa.me/{vendedor['numero']}")
            else:
                send_message(phone, "Nenhum vendedor disponível no momento. Tente novamente mais tarde.")
        elif message == "2":
            send_message(phone, "Aqui está o link para ver nossos produtos: https://parapisos.vercel.app/")
        elif message == "3":
            send_message(phone, "Nosso suporte técnico está online. Em que posso ajudar?")
        else:
            send_message(phone,
                "Olá! Como posso te ajudar?\n\n"
                "1 - Falar com um vendedor\n"
                "2 - Ver produtos\n"
                "3 - Suporte técnico"
            )
        
        return jsonify({"status": "ok"})
    
    except Exception as e:
        print(f"Erro no processamento do webhook: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(port=5000)
