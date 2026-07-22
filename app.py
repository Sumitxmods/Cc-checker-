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

# ========== FIREBASE INIT - SERVICE ACCOUNT JSON SE ==========
# Service account JSON ko string mein store karo
service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')

if service_account_json:
    # Environment variable se load
    service_account_dict = json.loads(service_account_json)
    cred = credentials.Certificate(service_account_dict)
else:
    # Local file se load (development ke liye)
    cred = credentials.Certificate('serviceAccountKey.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tournament-78d9c-default-rtdb.firebaseio.com'
})

# ========== API ROUTES ==========

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "api": "SMS Admin API v1.0",
        "endpoints": {
            "/send/<folder>": "POST - Send SMS data",
            "/showdata/<folder>": "GET - Get all data",
            "/clear/<folder>": "DELETE - Clear folder"
        }
    })

@app.route('/send/<folder>', methods=['POST'])
def send_data(folder):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
        ref = db.reference(f'/{folder}')
        ref.push(data)
        return jsonify({"status": "success", "message": f"Data saved in {folder}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/showdata/<folder>', methods=['GET'])
def show_data(folder):
    try:
        ref = db.reference(f'/{folder}')
        data = ref.get()
        return jsonify({"status": "success", "data": data if data else {}}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear/<folder>', methods=['DELETE'])
def clear_folder(folder):
    try:
        ref = db.reference(f'/{folder}')
        ref.delete()
        return jsonify({"status": "success", "message": f"Folder {folder} deleted"}), 200
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
