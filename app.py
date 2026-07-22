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

app = Flask(__name__)

# ========== FIREBASE - ENVIRONMENT VARIABLE SE LOAD ==========
service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

if not service_account_json:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT environment variable not set!")

service_account_dict = json.loads(service_account_json)
cred = credentials.Certificate(service_account_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://videohostvip-default-rtdb.firebaseio.com'
})

# ========== API ROUTES ==========

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "api": "SMS Admin API v1.0",
        "project": "videohostvip",
        "endpoints": {
            "/send/<folder>": "POST - Send data",
            "/showdata/<folder>": "GET - Get all data",
            "/clear/<folder>": "DELETE - Clear folder",
            "/clear/<folder>/<item>": "DELETE - Delete item",
            "/health": "GET - Health check"
        }
    })

@app.route('/send/<folder>', methods=['POST'])
def send_data(folder):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data"}), 400
        ref = db.reference(f'/{folder}')
        new_ref = ref.push(data)
        return jsonify({"status": "success", "key": new_ref.key}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/showdata/<folder>', methods=['GET'])
def show_data(folder):
    try:
        ref = db.reference(f'/{folder}')
        data = ref.get()
        return jsonify({"status": "success", "data": data if data else {}, "count": len(data) if data else 0}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear/<folder>', methods=['DELETE'])
def clear_folder(folder):
    try:
        ref = db.reference(f'/{folder}')
        ref.delete()
        return jsonify({"status": "success", "message": f"Folder {folder} cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear/<folder>/<item>', methods=['DELETE'])
def clear_item(folder, item):
    try:
        ref = db.reference(f'/{folder}/{item}')
        ref.delete()
        return jsonify({"status": "success", "message": f"Item {item} deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "time": str(datetime.now())}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
