from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os

app = Flask(__name__)

# ========== FIREBASE CONFIG ==========
firebase_config = {
    "apiKey": "AIzaSyCswByaGkpUUzIFkXfvVZuhD4Aokrbg-mg",
    "authDomain": "tournament-78d9c.firebaseapp.com",
    "databaseURL": "https://tournament-78d9c-default-rtdb.firebaseio.com",
    "projectId": "tournament-78d9c",
    "storageBucket": "tournament-78d9c.firebasestorage.app",
    "messagingSenderId": "803296956926",
    "appId": "1:803296956926:web:26f686438e7e775e1c30af",
    "measurementId": "G-260M66TC2C"
}

# Initialize Firebase
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "tournament-78d9c",
    "private_key_id": "your-key-id",
    "private_key": "your-private-key",
    "client_email": "firebase-adminsdk@tournament-78d9c.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40tournament-78d9c.iam.gserviceaccount.com"
})

firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_config['databaseURL']
})

# ========== API ROUTES ==========

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "api_version": "1.0",
        "endpoints": {
            "/send/<folder>": "POST - Send data",
            "/showdata/<folder>": "GET - Show all data",
            "/clear/<folder>": "DELETE - Clear folder data",
            "/clear/<folder>/<item>": "DELETE - Clear specific item"
        }
    })

# ========== SEND DATA ==========
@app.route('/send/<folder>', methods=['POST'])
def send_data(folder):
    try:
        data = request.get_json()
        ref = db.reference(f'/{folder}')
        ref.push(data)
        return jsonify({"status": "success", "message": f"Data sent to {folder}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ========== SHOW DATA ==========
@app.route('/showdata/<folder>', methods=['GET'])
def show_data(folder):
    try:
        ref = db.reference(f'/{folder}')
        data = ref.get()
        if data:
            return jsonify({"status": "success", "data": data}), 200
        return jsonify({"status": "success", "data": {}, "message": "No data found"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ========== CLEAR ALL DATA IN FOLDER ==========
@app.route('/clear/<folder>', methods=['DELETE'])
def clear_folder(folder):
    try:
        ref = db.reference(f'/{folder}')
        ref.delete()
        return jsonify({"status": "success", "message": f"Folder {folder} cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ========== CLEAR SPECIFIC ITEM ==========
@app.route('/clear/<folder>/<item>', methods=['DELETE'])
def clear_item(folder, item):
    try:
        ref = db.reference(f'/{folder}/{item}')
        ref.delete()
        return jsonify({"status": "success", "message": f"Item {item} deleted from {folder}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ========== HEALTH CHECK ==========
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "time": str(datetime.now())}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)