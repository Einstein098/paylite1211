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
    return url, token

def get_status(session_id):
    url, token = get_env_vars()
    if url and token and session_id:
        endpoint = f"{url.rstrip('/')}/get/{session_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            r = requests.get(endpoint, headers=headers)
            if r.status_code == 200:
                val = r.json().get("result")
                return val or "pending"
            else:
                print(f"[Upstash Status] Error: {r.status_code} {r.text}")
        except Exception as e:
            print(f"[Upstash Status] Exception: {e}")
    return "pending"

@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/api/status', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/status', methods=['GET', 'POST'], strict_slashes=False)
def status_handler():
    session_id = request.args.get('session_id') or (request.json or {}).get('session_id')
    current_status = get_status(session_id) or "pending"
    resp = jsonify({"status": current_status})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
