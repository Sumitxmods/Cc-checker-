#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║   🌐 SUMIT X MODS — TRAFFIC BOT API v4.0 (STABLE)          ║
║   ✅ FIXED: Self-loop prevention | Memory cleanup           ║
║   ✅ RATE LIMITED | ERROR HANDLED | AUTO-HEAL               ║
╚═══════════════════════════════════════════════════════════════╝
"""

import requests
import random
import time
import json
import os
import threading
import uuid
import sys
import gc
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

# ============================================
# 🔥 CONFIG
# ============================================
app = Flask(__name__)
CORS(app)

DATA_FILE = "traffic_logs.json"
CONFIG_FILE = "campaign_config.json"
MAX_LOGS = 500  # Limit logs to prevent memory bloat
MAX_THREADS = 10  # Reduced for Render free tier
BOT_SELF_URL = "https://traffic-bot-xfsz.onrender.com"  # Block self-target

# ============================================
# 🛡️ RATE LIMITER (Simple)
# ============================================
class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def allow(self, ip, limit=10, window=60):
        now = time.time()
        if ip not in self.requests:
            self.requests[ip] = []
        # Clean old entries
        self.requests[ip] = [t for t in self.requests[ip] if now - t < window]
        if len(self.requests[ip]) >= limit:
            return False
        self.requests[ip].append(now)
        return True

rate_limiter = RateLimiter()

# ============================================
# 📊 DATABASE
# ============================================
class TrafficDB:
    @staticmethod
    def load():
        try:
            if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"logs": [], "stats": {"total": 0, "success": 0, "failed": 0}}
    
    @staticmethod
    def save(data):
        try:
            # Limit logs to prevent bloat
            if len(data.get("logs", [])) > MAX_LOGS:
                data["logs"] = data["logs"][-MAX_LOGS:]
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    @staticmethod
    def add_log(entry):
        data = TrafficDB.load()
        data["logs"].append(entry)
        data["stats"]["total"] = data["stats"].get("total", 0) + 1
        if entry.get("status") == "success":
            data["stats"]["success"] = data["stats"].get("success", 0) + 1
        else:
            data["stats"]["failed"] = data["stats"].get("failed", 0) + 1
        TrafficDB.save(data)
        return data

# ============================================
# 🎯 CAMPAIGN MANAGER
# ============================================
class CampaignManager:
    @staticmethod
    def load_config():
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "active": False,
            "target_url": "",
            "total_goal": 10000,
            "start_date": None,
            "end_date": None,
            "visits_done": 0,
            "started_at": None
        }
    
    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def get_progress():
        config = CampaignManager.load_config()
        if not config.get("active", False) or config.get("total_goal", 0) == 0:
            return 0
        done = config.get("visits_done", 0)
        goal = config.get("total_goal", 1)
        return round((done / goal) * 100, 2)
    
    @staticmethod
    def get_remaining_time():
        config = CampaignManager.load_config()
        if not config.get("active", False) or not config.get("end_date"):
            return None
        try:
            end = datetime.fromisoformat(config["end_date"])
            now = datetime.now()
            if now > end:
                return "Expired"
            diff = end - now
            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"

# ============================================
# 🧠 FAKE DATA GENERATOR
# ============================================
class FakeDataGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 Chrome/126.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 Chrome/126.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    ]
    
    LOCATIONS = [
        {"country": "US", "city": "New York", "state": "NY"},
        {"country": "US", "city": "Los Angeles", "state": "CA"},
        {"country": "US", "city": "Chicago", "state": "IL"},
        {"country": "UK", "city": "London", "state": "England"},
        {"country": "CA", "city": "Toronto", "state": "ON"},
        {"country": "AU", "city": "Sydney", "state": "NSW"},
        {"country": "DE", "city": "Berlin", "state": "Berlin"},
        {"country": "FR", "city": "Paris", "state": "Île-de-France"},
        {"country": "JP", "city": "Tokyo", "state": "Tokyo"},
        {"country": "IN", "city": "Mumbai", "state": "MH"},
        {"country": "IN", "city": "Delhi", "state": "DL"},
        {"country": "BR", "city": "São Paulo", "state": "SP"},
    ]
    
    @staticmethod
    def get_ip():
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    @staticmethod
    def get_user_agent():
        return random.choice(FakeDataGenerator.USER_AGENTS)
    
    @staticmethod
    def get_location():
        return random.choice(FakeDataGenerator.LOCATIONS)
    
    @staticmethod
    def get_headers(target_url):
        location = FakeDataGenerator.get_location()
        return {
            "User-Agent": FakeDataGenerator.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-For": FakeDataGenerator.get_ip(),
            "Client-IP": FakeDataGenerator.get_ip(),
            "X-Real-IP": FakeDataGenerator.get_ip(),
            "X-Geo-Country": location["country"],
            "X-Geo-City": location["city"],
            "X-Geo-State": location["state"],
            "Referer": random.choice([
                "https://www.google.com/search?q=",
                "https://www.bing.com/search?q=",
                "https://in.search.yahoo.com/search?p=",
                "https://www.facebook.com/",
                "https://twitter.com/",
            ]) + random.choice(["best+website", "top+website", "learn+online"]),
        }

# ============================================
# 🚀 TRAFFIC BOT ENGINE (FIXED)
# ============================================
class TrafficBot:
    def __init__(self):
        self.running = False
        self.thread = None
        self.paused = False
        self.visits_done = 0
        self.lock = threading.Lock()
    
    def is_self_target(self, url):
        """Prevent bot from targeting itself"""
        if not url:
            return True
        url_lower = url.lower()
        self_urls = [
            "traffic-bot-xfsz.onrender.com",
            "127.0.0.1",
            "localhost",
            "0.0.0.0"
        ]
        for bad in self_urls:
            if bad in url_lower:
                return True
        return False
    
    def visit(self, target_url, visit_id):
        """Simulate one visitor with proper error handling"""
        if self.is_self_target(target_url):
            return {
                "id": str(uuid.uuid4()),
                "visit_id": visit_id,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": "Self-target blocked"
            }
        
        headers = FakeDataGenerator.get_headers(target_url)
        time.sleep(random.uniform(0.5, 2.5))  # Human-like delay
        
        try:
            resp = requests.get(target_url, headers=headers, timeout=8)
            success = resp.status_code == 200
            
            entry = {
                "id": str(uuid.uuid4()),
                "visit_id": visit_id,
                "timestamp": datetime.now().isoformat(),
                "url": target_url,
                "ip": headers.get("X-Forwarded-For", "0.0.0.0"),
                "user_agent": headers.get("User-Agent", "Unknown"),
                "location": {
                    "country": headers.get("X-Geo-Country", "Unknown"),
                    "city": headers.get("X-Geo-City", "Unknown"),
                    "state": headers.get("X-Geo-State", "Unknown")
                },
                "status": "success" if success else "failed",
                "status_code": resp.status_code,
            }
            
            TrafficDB.add_log(entry)
            
            with self.lock:
                self.visits_done += 1
                config = CampaignManager.load_config()
                if config.get("active", False):
                    config["visits_done"] = self.visits_done
                    CampaignManager.save_config(config)
            
            return entry
            
        except requests.exceptions.Timeout:
            entry = {
                "id": str(uuid.uuid4()),
                "visit_id": visit_id,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": "Timeout",
                "ip": headers.get("X-Forwarded-For", "0.0.0.0")
            }
            TrafficDB.add_log(entry)
            return entry
            
        except Exception as e:
            entry = {
                "id": str(uuid.uuid4()),
                "visit_id": visit_id,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)[:50],
                "ip": headers.get("X-Forwarded-For", "0.0.0.0")
            }
            TrafficDB.add_log(entry)
            return entry
    
    def start_campaign(self, target_url, total_visits, days):
        """Start campaign with self-target prevention"""
        if self.running:
            return {"status": "already_running"}
        
        if self.is_self_target(target_url):
            return {"status": "error", "message": "Cannot target bot's own URL"}
        
        # Calculate end date
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        # Save campaign config
        config = {
            "active": True,
            "target_url": target_url,
            "total_goal": total_visits,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "visits_done": 0,
            "started_at": start_date.isoformat()
        }
        CampaignManager.save_config(config)
        
        self.running = True
        self.visits_done = 0
        self.thread = threading.Thread(target=self._run_bot, args=(target_url, total_visits))
        self.thread.daemon = True
        self.thread.start()
        
        return {
            "status": "started",
            "target_url": target_url,
            "total_visits": total_visits,
            "end_date": end_date.isoformat()
        }
    
    def _run_bot(self, target_url, total_visits):
        """Main bot loop with safe execution"""
        visited = 0
        
        try:
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                while visited < total_visits and self.running:
                    # Check if campaign is still active
                    config = CampaignManager.load_config()
                    if not config.get("active", False):
                        self.running = False
                        break
                    
                    batch = min(20, total_visits - visited)
                    futures = [executor.submit(self.visit, target_url, visited + i) for i in range(batch)]
                    
                    for future in futures:
                        try:
                            future.result(timeout=10)
                        except:
                            pass
                        visited += 1
                        with self.lock:
                            self.visits_done = visited
                            config = CampaignManager.load_config()
                            if config.get("active", False):
                                config["visits_done"] = visited
                                CampaignManager.save_config(config)
                        
                        # Small delay between requests
                        time.sleep(0.5)
                        
                        # Periodic cleanup
                        if visited % 50 == 0:
                            gc.collect()
                    
                    # Pause between batches
                    time.sleep(1)
        except Exception as e:
            print(f"Bot error: {e}")
        finally:
            self.running = False
            config = CampaignManager.load_config()
            config["active"] = False
            CampaignManager.save_config(config)
    
    def stop(self):
        """Stop the bot gracefully"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        config = CampaignManager.load_config()
        config["active"] = False
        CampaignManager.save_config(config)
        return {"status": "stopped"}

# Initialize bot
bot = TrafficBot()

# ============================================
# 🌐 API ENDPOINTS
# ============================================

@app.route('/')
def home():
    return jsonify({
        "name": "SUMIT X MODS - Traffic Bot API",
        "version": "4.0",
        "status": "online",
        "endpoints": [
            "/api/status",
            "/api/start",
            "/api/stop",
            "/api/logs",
            "/api/stats",
            "/api/config",
            "/api/reset"
        ]
    })

@app.route('/api/status')
def api_status():
    """Get current bot status"""
    # Rate limit check
    if not rate_limiter.allow(request.remote_addr):
        return jsonify({"error": "Rate limited"}), 429
    
    config = CampaignManager.load_config()
    stats = TrafficDB.load().get("stats", {})
    
    return jsonify({
        "running": bot.running,
        "active": config.get("active", False),
        "target_url": config.get("target_url", ""),
        "total_goal": config.get("total_goal", 0),
        "visits_done": config.get("visits_done", 0),
        "progress": CampaignManager.get_progress(),
        "remaining_time": CampaignManager.get_remaining_time(),
        "start_date": config.get("start_date"),
        "end_date": config.get("end_date"),
        "started_at": config.get("started_at"),
        "stats": stats,
        "uptime": time.time() - start_time if 'start_time' in globals() else 0
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start a new campaign"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    target_url = data.get('url', '').strip()
    total_visits = data.get('visits', 10000)
    days = data.get('days', 1)
    
    if not target_url:
        return jsonify({"error": "URL is required"}), 400
    
    if bot.is_self_target(target_url):
        return jsonify({"error": "Cannot target bot's own URL"}), 400
    
    # Validate URL format
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    result = bot.start_campaign(target_url, total_visits, days)
    return jsonify(result)

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the bot"""
    result = bot.stop()
    return jsonify(result)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset all data"""
    config = CampaignManager.load_config()
    config["active"] = False
    config["visits_done"] = 0
    CampaignManager.save_config(config)
    
    data = TrafficDB.load()
    data["logs"] = []
    data["stats"] = {"total": 0, "success": 0, "failed": 0}
    TrafficDB.save(data)
    
    return jsonify({"status": "reset"})

@app.route('/api/logs')
def api_logs():
    """Get logs with limit"""
    if not rate_limiter.allow(request.remote_addr):
        return jsonify({"error": "Rate limited"}), 429
    
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)  # Cap at 100
    
    data = TrafficDB.load()
    logs = data.get("logs", [])
    total = len(logs)
    
    return jsonify({
        "total": total,
        "limit": limit,
        "logs": logs[-limit:] if logs else []
    })

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    data = TrafficDB.load()
    stats = data.get("stats", {})
    config = CampaignManager.load_config()
    
    return jsonify({
        "total_visits": stats.get("total", 0),
        "success": stats.get("success", 0),
        "failed": stats.get("failed", 0),
        "success_rate": round((stats.get("success", 0) / max(stats.get("total", 1), 1)) * 100, 2),
        "campaign_progress": CampaignManager.get_progress(),
        "campaign_active": config.get("active", False),
        "remaining_time": CampaignManager.get_remaining_time()
    })

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update config"""
    if request.method == 'POST':
        data = request.get_json()
        if data:
            config = CampaignManager.load_config()
            config.update(data)
            CampaignManager.save_config(config)
            return jsonify({"status": "updated"})
    config = CampaignManager.load_config()
    return jsonify(config)

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============================================
# 🚀 STARTUP
# ============================================
start_time = time.time()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    # Clear any stale config on startup
    config = CampaignManager.load_config()
    config["active"] = False
    CampaignManager.save_config(config)
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║   🌐 SUMIT X MODS — TRAFFIC BOT API v4.0                    ║
║   ✅ SELF-LOOP PREVENTED | RATE LIMITED | AUTO-HEAL         ║
║   🚀 Running on port {port}                                    ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)