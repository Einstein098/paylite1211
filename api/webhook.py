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

def get_env_vars():
    url = os.environ.get("UPSTASH_REDIS_REST_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    tg_token = os.environ.get("TELEGRAM_TOKEN")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID")
    return url, token, tg_token, tg_chat

def set_status(session_id, status):
    url, token, _, _ = get_env_vars()
    if url and token and session_id:
        endpoint = f"{url.rstrip('/')}/set/{session_id}/{status}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            r = requests.post(endpoint, headers=headers)
            print(f"[Upstash Webhook] Set status {status} for {session_id}: {r.status_code} {r.text}")
        except Exception as e:
            print(f"[Upstash Webhook] Exception setting status: {e}")

@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/api/webhook', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/webhook', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/telegram-webhook', methods=['GET', 'POST'], strict_slashes=False)
def webhook_handler():
    if request.method == 'GET':
        return jsonify({"status": "webhook active", "ok": True})
        
    data = request.json or {}
    print(f"[Telegram Webhook] Payload: {data}")
    
    if 'callback_query' in data:
        query = data['callback_query']
        callback_data = query.get('data', '')
        callback_id = query.get('id')
        message = query.get('message')
        chat_id = message['chat']['id'] if message else None
        message_id = message['message_id'] if message else None
        _, _, token, _ = get_env_vars()

        if callback_data.startswith("approve_") or callback_data.startswith("reject_"):
            action, session_id = callback_data.split('_', 1)
            status_val = "approved" if action == "approve" else "rejected"
            
            # 1. Update Upstash status
            set_status(session_id, status_val)
            print(f"[Telegram Webhook] Session {session_id} set to {status_val}")
            
            if token and callback_id:
                # 2. Answer callback query immediately to stop the button spinning
                ans_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                toast_text = "✅ Demande approuvée !" if action == "approve" else "❌ Demande refusée !"
                try:
                    requests.post(ans_url, json={
                        "callback_query_id": callback_id,
                        "text": toast_text,
                        "show_alert": False
                    })
                except Exception as e:
                    print(f"[Telegram Webhook] Error answering callback: {e}")

            # 3. Edit Telegram message to show decision
            if token and chat_id and message_id:
                new_text = message.get('text', '') if message else ''
                decision_badge = "\n\n✅ <b>APPROUVÉ</b>" if action == "approve" else "\n\n❌ <b>REFUSÉ</b>"
                new_text += decision_badge
                    
                edit_url = f"https://api.telegram.org/bot{token}/editMessageText"
                try:
                    requests.post(edit_url, json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": new_text,
                        "parse_mode": "HTML"
                    })
                except Exception as e:
                    print(f"[Telegram Webhook] Error editing message: {e}")
                
    return jsonify({"status": "success", "ok": True})
