import os
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
# Pega a chave do Gemini das configurações do servidor
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Prompt de Sistema (A Alma do Azul)
SYSTEM_PROMPT = """
Você é o Azul 💙. Seu objetivo é organizar a vida financeira de trabalhadores brasileiros.
- Se receber TEXTO: Responda curto, com gíria leve e apoio emocional.
- Se receber ÁUDIO (descrito): Acolha o desabafo e extraia os valores.
- Se receber IMAGEM (descrita): Identifique qual é a conta e o valor.
Sempre termine com uma pergunta fácil ou uma frase de esperança.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

@app.route("/", methods=["GET"])
def home():
    return "O Azul Híbrido está Online! 💙🧢"

# --- VERIFICAÇÃO DO WHATSAPP (Obrigatório) ---
@app.route("/webhook", methods=["GET"])
def verify():
    verify_token = "azul123" # Senha de verificação
    
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
    return "Erro de verificação", 403

# --- RECEBIMENTO DE MENSAGENS (O Fluxo Híbrido) ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"Recebido: {data}") # Log para debug

    try:
        # Navega no JSON do WhatsApp para achar a mensagem
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' in value:
            message = value['messages'][0]
            tipo = message['type'] # Aqui descobrimos se é text, audio ou image
            
            resposta_azul = ""

            # CASO 1: TEXTO (O usuário digitou)
            if tipo == 'text':
                texto_usuario = message['text']['body']
                print(f"📝 Texto recebido: {texto_usuario}")
                response = model.generate_content(texto_usuario)
                resposta_azul = response.text

            # CASO 2: ÁUDIO (O usuário mandou voz)
            elif tipo == 'audio':
                print("🎤 Áudio recebido.")
                # No MVP Básico, não baixamos o arquivo ainda (precisa de Token Extra).
                # Vamos simular que o Azul ouviu para validar o fluxo.
                response = model.generate_content("O usuário mandou um áudio de desabafo financeiro. Responda dizendo que ouviu e peça para ele falar o valor se não ficou claro.")
                resposta_azul = response.text

            # CASO 3: IMAGEM (O usuário mandou foto/boleto)
            elif tipo == 'image':
                print("📸 Imagem recebida.")
                response = model.generate_content("O usuário mandou uma foto de uma conta. Diga que viu a imagem e pergunte qual o dia do vencimento.")
                resposta_azul = response.text
            
            else:
                resposta_azul = "Opa, esse formato eu ainda não entendo 😅. Manda áudio, texto ou foto!"

            print(f"💙 Azul Respondeu: {resposta_azul}")
            
            # Aqui entra a função de ENVIAR de volta para o Zap (Fase avançada)
            
        return jsonify({"status": "recebido"}), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"status": "erro"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
