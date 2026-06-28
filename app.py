#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║           🔑 KURO ONLINE KEY SYSTEM - BACKEND API               ║
║           by Sumit x mods                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  Features:                                                      ║
║  • Generate One-Day / Custom Time Keys                          ║
║  • Format: SUMIT-ONLINE-KEY-XXXX (last 4 random)               ║
║  • Firebase Realtime Database Storage                           ║
║  • Verify, Expire, List, Delete Keys                            ║
║  • MAX USES LIMIT - Set how many users can use a key           ║
║  • ONE-TIME USE - Single use keys option                       ║
║  • 2 Secret Endpoints (not guessable)                           ║
║  • Render.com / Termux Compatible                               ║
║  • CORS enabled for frontend                                   ║
╚══════════════════════════════════════════════════════════════════╝

Setup:
    pip install flask requests gunicorn
    
Run Local:
    python kuro_backend.py
    
Deploy on Render:
    - Build Command: pip install flask requests gunicorn
    - Start Command: gunicorn kuro_backend:app
    - Port: 10000

Endpoints (Secret 1 - Generate/Verify):
    POST [BASE]/api/k7x9m2p4/generate
    POST [BASE]/api/k7x9m2p4/verify

Endpoints (Secret 2 - List/Delete):
    GET  [BASE]/api/v3r8n1q5/list
    POST [BASE]/api/v3r8n1q5/delete
"""

import os
import sys
import json
import random
import string
import time
import datetime
import requests
from functools import wraps

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("[!] Install: pip install flask flask-cors requests")
    sys.exit(1)

# ─── FIREBASE CONFIG ──────────────────────────────────────
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDafBvUDXJw31NT1Wmir7_uEOlU_GtahjM",
    "authDomain": "videohostvip.firebaseapp.com",
    "databaseURL": "https://videohostvip-default-rtdb.firebaseio.com",
    "projectId": "videohostvip",
    "storageBucket": "videohostvip.firebasestorage.app",
    "messagingSenderId": "259835288841",
    "appId": "1:259835288841:web:847fa82fd591ddf79887d8",
    "measurementId": "G-Q8DXDVY58V"
}

DB_URL = FIREBASE_CONFIG["databaseURL"]

# ─── SECRET ENDPOINTS ─────────────────────────────────────
# Inhe badal sakte ho! Koi bhi random string daalo
ENDPOINT_GEN_VERIFY = "k7x9m2p4"  # Generate + Verify ke liye
ENDPOINT_LIST_DELETE = "v3r8n1q5"  # List + Delete ke liye

# ─── Flask App ────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Frontend ko allow karo

# ─── FIREBASE REST HELPERS ────────────────────────────────

def fb_get(path):
    url = f"{DB_URL}/{path}.json"
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def fb_put(path, data):
    url = f"{DB_URL}/{path}.json"
    try:
        r = requests.put(url, json=data, timeout=10)
        return r.json() if r.status_code in (200, 201) else None
    except: return None

def fb_patch(path, data):
    url = f"{DB_URL}/{path}.json"
    try:
        r = requests.patch(url, json=data, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def fb_delete(path):
    url = f"{DB_URL}/{path}.json"
    try:
        r = requests.delete(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None


# ─── KEY ENGINE ───────────────────────────────────────────

def generate_key():
    """Format: SUMIT-ONLINE-KEY-ABCD"""
    chars = string.ascii_uppercase + string.digits
    rand = ''.join(random.choices(chars, k=4))
    return f"SUMIT-ONLINE-KEY-{rand}"

def calc_expiry(value, unit):
    """Expiry calculate karo"""
    now = datetime.datetime.utcnow()
    if unit == 'hours':
        expiry = now + datetime.timedelta(hours=int(value))
    elif unit == 'days':
        expiry = now + datetime.timedelta(days=int(value))
    elif unit == 'minutes':
        expiry = now + datetime.timedelta(minutes=int(value))
    else:
        expiry = now + datetime.timedelta(hours=24)
    
    return int(expiry.timestamp()), expiry.strftime("%Y-%m-%d %H:%M:%S UTC")

def get_status(key_data):
    """Key ka current status do"""
    if not key_data: return "not_found"
    
    # Check max uses limit
    max_uses = key_data.get('max_uses', 1)
    used_count = key_data.get('used_count', 0)
    
    if used_count >= max_uses:
        return "used"
    if int(time.time()) > key_data.get('expiry_ts', 0):
        return "expired"
    return "active"


# ─── HELPER: Secret check ────────────────────────────────

def check_secret(req, expected):
    """Check karo secret sahi hai"""
    s = (req.args.get('secret') or 
         (req.json or {}).get('secret') or 
         req.headers.get('X-Secret-Key', ''))
    return s == expected


# ═══════════════════════════════════════════════════════════
# ENDPOINT 1: GENERATE KEY
# ═══════════════════════════════════════════════════════════

@app.route(f'/api/{ENDPOINT_GEN_VERIFY}/generate', methods=['POST'])
def api_generate():
    """🔑 Key Generate karo"""
    
    # Secret check
    if not check_secret(request, ENDPOINT_GEN_VERIFY):
        return jsonify({'success': False, 'error': 'Invalid secret'}), 403
    
    data = request.get_json() or {}
    
    duration = int(data.get('duration', 1))
    unit = data.get('unit', 'days')
    max_uses = int(data.get('max_uses', 1))  # 🔥 NEW: Max users limit
    
    if duration < 1: duration = 1
    if duration > 365: duration = 365
    if unit not in ('minutes', 'hours', 'days'): unit = 'days'
    if max_uses < 1: max_uses = 1
    if max_uses > 999: max_uses = 999
    
    # Unique key generate (max 10 attempts)
    key = None
    for _ in range(10):
        k = generate_key()
        if not fb_get(f"keys/{k}"):
            key = k
            break
    
    if not key:
        return jsonify({'success': False, 'error': 'Failed to generate unique key'})
    
    expiry_ts, expiry_read = calc_expiry(duration, unit)
    
    # 🔥 Determine key type
    key_type = "one_time" if max_uses == 1 else "multi_use"
    
    key_data = {
        'key': key,
        'created_ts': int(time.time()),
        'created_at': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        'expiry_ts': expiry_ts,
        'expires_at': expiry_read,
        'duration': f"{duration} {unit}",
        'duration_value': duration,
        'duration_unit': unit,
        'used': False,
        'used_count': 0,  # 🔥 NEW: Current use count
        'max_uses': max_uses,  # 🔥 NEW: Max allowed uses
        'key_type': key_type,  # 🔥 NEW: Key type
        'used_by': [],
        'used_at': [],
        'used_ip': [],
        'active': True
    }
    
    saved = fb_put(f"keys/{key}", key_data)
    
    if not saved:
        return jsonify({'success': False, 'error': 'Failed to save to database'})
    
    return jsonify({
        'success': True,
        'key': key,
        'format': 'SUMIT-ONLINE-KEY-XXXX',
        'expires_at': expiry_read,
        'expiry_ts': expiry_ts,
        'duration': f"{duration} {unit}",
        'max_uses': max_uses,
        'key_type': key_type,
        'note': 'Last 4 characters are randomly generated'
    })


# ═══════════════════════════════════════════════════════════
# ENDPOINT 2: VERIFY KEY
# ═══════════════════════════════════════════════════════════

@app.route(f'/api/{ENDPOINT_GEN_VERIFY}/verify', methods=['POST'])
def api_verify():
    """✅ Key Verify karo"""
    
    if not check_secret(request, ENDPOINT_GEN_VERIFY):
        return jsonify({'success': False, 'valid': False, 'error': 'Invalid secret'}), 403
    
    data = request.get_json() or {}
    key = data.get('key', '').strip().upper()
    mark_used = data.get('mark_used', True)
    
    if not key:
        return jsonify({'success': False, 'valid': False, 'error': 'No key provided'})
    
    if not key.startswith('SUMIT-ONLINE-KEY-'):
        return jsonify({
            'success': False, 'valid': False,
            'error': 'Invalid format. BUY ON TG:@CRACKAxxFATHER'
        })
    
    key_data = fb_get(f"keys/{key}")
    
    if not key_data:
        return jsonify({
            'success': False, 'valid': False,
            'key': key,
            'error': 'Key not found in database'
        })
    
    status = get_status(key_data)
    
    if status == 'expired':
        return jsonify({
            'success': False, 'valid': False,
            'key': key,
            'status': 'expired',
            'error': f"Key expired at {key_data.get('expires_at', 'unknown')}"
        })
    
    if status == 'used':
        max_u = key_data.get('max_uses', 1)
        used_u = key_data.get('used_count', 0)
        return jsonify({
            'success': False, 'valid': False,
            'key': key,
            'status': 'used',
            'error': f"Key fully used ({used_u}/{max_u} uses)"
        })
    
    # Mark as used (if requested)
    if mark_used:
        user_ip = request.remote_addr or 'unknown'
        used_by_list = key_data.get('used_by', [])
        used_at_list = key_data.get('used_at', [])
        used_ip_list = key_data.get('used_ip', [])
        used_count = key_data.get('used_count', 0) + 1
        
        used_by_list.append(user_ip)
        used_at_list.append(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        used_ip_list.append(user_ip)
        
        max_uses = key_data.get('max_uses', 1)
        fully_used = (used_count >= max_uses)
        
        fb_patch(f"keys/{key}", {
            'used': fully_used,
            'used_count': used_count,
            'used_by': used_by_list,
            'used_at': used_at_list,
            'used_ip': used_ip_list,
            'active': not fully_used
        })
    
    remaining = max(0, key_data.get('expiry_ts', 0) - int(time.time()))
    max_u = key_data.get('max_uses', 1)
    used_u = key_data.get('used_count', 0) + (1 if mark_used else 0)
    remaining_uses = max(0, max_u - used_u)
    
    return jsonify({
        'success': True,
        'valid': True,
        'key': key,
        'status': 'verified',
        'message': f'✅ Key valid ({remaining_uses} uses left)',
        'created': key_data.get('created_at'),
        'expires': key_data.get('expires_at'),
        'duration': key_data.get('duration'),
        'max_uses': max_u,
        'used_count': used_u,
        'remaining_uses': remaining_uses,
        'remaining_seconds': remaining,
        'key_type': key_data.get('key_type', 'unknown'),
        'consumed': mark_used
    })


# ═══════════════════════════════════════════════════════════
# ENDPOINT 3: LIST ALL KEYS
# ═══════════════════════════════════════════════════════════

@app.route(f'/api/{ENDPOINT_LIST_DELETE}/list', methods=['GET'])
def api_list():
    """📋 Saare keys dikhao"""
    
    if not check_secret(request, ENDPOINT_LIST_DELETE):
        return jsonify({'success': False, 'error': 'Invalid secret'}), 403
    
    keys_data = fb_get('keys')
    
    if not keys_data:
        return jsonify({
            'success': True,
            'keys': [],
            'total': 0, 'active': 0, 'expired': 0, 'used': 0
        })
    
    keys_list = []
    for kid, kinfo in keys_data.items():
        if isinstance(kinfo, dict):
            kinfo['_id'] = kid
            kinfo['status'] = get_status(kinfo)
            # Ensure backwards compatibility
            if 'max_uses' not in kinfo:
                kinfo['max_uses'] = 1
            if 'used_count' not in kinfo:
                kinfo['used_count'] = 1 if kinfo.get('used') else 0
            if 'key_type' not in kinfo:
                kinfo['key_type'] = 'one_time'
            keys_list.append(kinfo)
    
    keys_list.sort(key=lambda k: k.get('created_ts', 0), reverse=True)
    
    total = len(keys_list)
    active = sum(1 for k in keys_list if k['status'] == 'active')
    expired = sum(1 for k in keys_list if k['status'] == 'expired')
    used = sum(1 for k in keys_list if k['status'] == 'used')
    
    return jsonify({
        'success': True,
        'total': total,
        'active': active,
        'expired': expired,
        'used': used,
        'keys': keys_list
    })


# ═══════════════════════════════════════════════════════════
# ENDPOINT 4: DELETE KEY
# ═══════════════════════════════════════════════════════════

@app.route(f'/api/{ENDPOINT_LIST_DELETE}/delete', methods=['POST'])
def api_delete():
    """🗑️ Key delete karo"""
    
    if not check_secret(request, ENDPOINT_LIST_DELETE):
        return jsonify({'success': False, 'error': 'Invalid secret'}), 403
    
    data = request.get_json() or {}
    key = data.get('key', '').strip().upper()
    del_all = data.get('delete_all', False)
    
    if del_all:
        fb_delete('keys')
        return jsonify({'success': True, 'message': 'All keys deleted'})
    
    if not key:
        return jsonify({'success': False, 'error': 'No key provided'})
    
    existing = fb_get(f"keys/{key}")
    if not existing:
        return jsonify({'success': False, 'error': 'Key not found'})
    
    fb_delete(f"keys/{key}")
    
    return jsonify({
        'success': True,
        'deleted': True,
        'key': key,
        'message': f'Key {key} deleted'
    })


# ═══════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════

@app.route('/health')
def health():
    return jsonify({'status': 'alive', 'time': datetime.datetime.utcnow().isoformat()})


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"""
╔═══════════════════════════════════════════════════╗
║     🔑 KURO KEY SYSTEM - BACKEND RUNNING          ║
╠═══════════════════════════════════════════════════╣
║  Port: {port:<5}                                     ║
║                                                   ║
║  Endpoints:                                       ║
║  POST /api/{ENDPOINT_GEN_VERIFY}/generate  ║
║  POST /api/{ENDPOINT_GEN_VERIFY}/verify    ║
║  GET  /api/{ENDPOINT_LIST_DELETE}/list      ║
║  POST /api/{ENDPOINT_LIST_DELETE}/delete    ║
║                                                   ║
║  Features:                                        ║
║  🔑 One-Time & Multi-Use Keys                     ║
║  👥 Max Uses Limit Configurable                   ║
╚═══════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False)