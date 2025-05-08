from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ZAPI_URL = "https://api.z-api.io/3E0DAD8E4FABF012B6D596870211A73F"
ZAPI_TOKEN = "B2A86CA33AF419BB356CE4BD"  # O token agora será parte da URL
VENDEDOR_API_URL = "https://parapisos-autoatendimento-vendedores.onrender.com/proximo-vendedor"

def send_message(phone, message):
    # URL com o Client-Token diretamente na URL
    url = f"https://api.z-api.io/instances/3E0DAD8E4FABF012B6D596870211A73F/token/{ZAPI_TOKEN}/send-text"
    
    headers = {
        "Content-Type": "application/json"  # Não precisamos mais do Bearer Token no cabeçalho
    }
    
    data = {
        "phone": phone,
        "message": message
    }
    
    # Exibe o corpo da requisição para depuração
    print(f"Enviando para a API Z-API: {data}")
    
    # Envia a requisição para a API do Z-API
    response = requests.post(url, json=data, headers=headers)

    # Exibe a resposta da API para depuração
    print(f"Resposta da API Z-API: {response.status_code} - {response.text}")
    
    # Verifica se o envio foi bem-sucedido
    if response.status_code == 200:
        print(f"Mensagem enviada para {phone}: {message}")
        return True
    else:
        print(f"Erro ao enviar a mensagem para {phone}: {response.text}")
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
    data = request.json
    print("Dados recebidos do Z-API:", data)  # Log para verificar os dados recebidos
    
    # Tenta acessar o campo message ou text
    message = data.get("message", "") or data.get("text", "")
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

if __name__ == "__main__":
    app.run(port=5000)
