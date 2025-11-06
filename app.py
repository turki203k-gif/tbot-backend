from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS   # ✅ السماح بالاتصال من أي موقع

app = Flask(__name__)
CORS(app)  # ✅ تفعيل CORS لجميع الطلبات

# قراءة التوكن من المتغير البيئي في Render
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("⚠️ لم يتم العثور على متغير HF_TOKEN، أضفه في إعدادات Render.")

# رابط نموذج Mistral 7B
MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

@app.route("/")
def home():
    return "🚀 TBot AI Proxy is running successfully with CORS enabled!"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    language = data.get("lang", "ar")

    if not user_message.strip():
        return jsonify({"reply": "⚠️ أرسل رسالة صحيحة."}), 400

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # إعداد الـ prompt بطريقة ودّية وإنسانية
    prompt = f"""You are TBot, a friendly and smart AI assistant developed by Turki Alzahrani.
You speak fluently in {language}.
You always give accurate, natural, human-like answers without repeating phrases.
Answer the following user message naturally:

User: {user_message}
TBot:"""

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300, "temperature": 0.8}
    }

    try:
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        # استخراج الرد من النموذج
        if isinstance(result, list) and len(result) > 0:
            reply = result[0].get("generated_text", "").split("TBot:")[-1].strip()
        else:
            reply = "🤖 لم أتمكن من فهم سؤالك."

        return jsonify({"reply": reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"reply": f"⚠️ حدث خطأ في الاتصال: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
