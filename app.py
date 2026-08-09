#!/usr/bin/env python3
"""
🔐 FF JWT TOKEN GENERATOR - RENDER WEB SERVICE
"""

import os
import telebot
from telebot import types
import requests
import urllib3
from flask import Flask, request
from threading import Thread

urllib3.disable_warnings()

# Flask Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>FF JWT Generator</title>
    <style>
        body { background: #0a0a0a; color: #fff; font-family: Arial; text-align: center; padding: 50px; }
        h1 { color: #00ff88; }
        .status { color: #00ff88; font-size: 24px; }
    </style></head>
    <body>
        <h1>🔥 FF JWT TOKEN GENERATOR 🔥</h1>
        <p class="status">✅ Bot Running!</p>
        <p>Use Telegram Bot: @YourBot</p>
    </body>
    </html>
    """

# BOT
BOT_TOKEN = "8669711044:AAEJqfiT1aaTVcZy2VF7JgW6HhoHtZtH_Xc"
ADMIN_ID = 769051183
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

bot = telebot.TeleBot(BOT_TOKEN)

E = {
    "crown": "👑", "check": "✅", "cross": "❌", "load": "🔄",
    "key": "🔑", "id": "🆔", "pass": "🔒", "ticket": "🎫",
    "time": "⏰", "bolt": "⚡", "diamond": "💎", "star": "🌟",
    "rocket": "🚀", "globe": "🌐", "lock": "🔐", "msg": "💬",
    "fire": "🔥", "target": "🎯", "shield": "🛡️",
}

INFO_TEXT = f"""
{E['star']} <b>ᴊᴏɪɴ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ</b> {E['star']}

{E['msg']} <b>ᴅᴍ</b> ➜ @CRACKAxxFATHER
{E['globe']} <b>ɢʀᴏᴜᴘ</b> ➜ t.me/+c0N-hu7QF9IzYzM1
{E['fire']} <b>ᴄʜᴀɴɴᴇʟ</b> ➜ t.me/+7h2aMq3RcOQ0YzI1
{E['rocket']} <b>ʏᴏᴜᴛᴜʙᴇ</b> ➜ shorturl.at/5shO6
"""

def community_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 ɢʀᴏᴜᴘ", url="https://t.me/+c0N-hu7QF9IzYzM1"),
        types.InlineKeyboardButton("♦️ ᴄʜᴀɴɴᴇʟ", url="https://t.me/+7h2aMq3RcOQ0YzI1"),
    )
    markup.add(
        types.InlineKeyboardButton("💌 ᴅᴍ", url="https://t.me/CRACKAxxFATHER"),
        types.InlineKeyboardButton("🎬 ʏᴏᴜᴛᴜʙᴇ", url="https://shorturl.at/5shO6"),
    )
    return markup

def get_jwt(uid, password):
    try:
        resp = requests.post(
            "https://100067.connect.garena.com/oauth/guest/token/grant",
            data={"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_secret": HEX_KEY, "client_id": "100067"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15, verify=False
        )
        data = resp.json()
        if "access_token" in data:
            return True, data["access_token"], data.get("expires_in", 0)
        return False, data.get("error", "Unknown"), 0
    except Exception as e:
        return False, str(e), 0

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name or "User"
    
    if uid == ADMIN_ID:
        txt = f"{E['crown']}╔══════════════════════╗\n║   {E['diamond']} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {E['diamond']}   ║\n╚══════════════════════╝\n\n{E['star']} Welcome Admin {name}!\n\nSend <code>UID:Password</code>\n\n{INFO_TEXT}"
        bot.send_message(uid, txt, parse_mode="HTML", reply_markup=community_buttons())
        return
    
    txt = f"{E['fire']}╔══════════════════════╗\n║   {E['crown']} ғғ ᴊᴡᴛ ɢᴇɴ {E['crown']}   ║\n╚══════════════════════╝\n\n{E['rocket']} Welcome {name}!\n\n{E['lock']} Send <code>UID:Password</code>\n\n{E['star']} Example: <code>6267873771:Test123</code>\n\n{INFO_TEXT}"
    bot.send_message(uid, txt, parse_mode="HTML", reply_markup=community_buttons())

@bot.message_handler(func=lambda m: m.text and ":" in m.text)
def handle_uid_pass(message):
    uid = message.from_user.id
    parts = message.text.strip().split(":", 1)
    uid_input = parts[0].strip().replace(" ", "")
    password = parts[1].strip()
    
    if not uid_input.isdigit() or not password:
        return
    
    load = bot.reply_to(message, f"{E['load']} <i>Generating...</i>", parse_mode="HTML")
    success, result, expires = get_jwt(uid_input, password)
    
    if success:
        hours = expires // 3600
        jwt = result
        txt = f"{E['check']}╔══════════════════════╗\n║   {E['crown']} ᴊᴡᴛ ʀᴇᴀᴅʏ {E['crown']}   ║\n╚══════════════════════╝\n\n{E['id']} UID: <code>{uid_input}</code>\n{E['pass']} Pass: <code>{password[:40]}</code>\n\n{E['ticket']} JWT: <code>{jwt[:80]}...</code>\n\n{E['time']} Expires: {hours}h\n{E['bolt']} Status: ACTIVE\n\n{E['lock']} Full token below ↓"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton(f"{E['key']} ɴᴇᴡ", callback_data="new_gen"), types.InlineKeyboardButton(f"{E['msg']} sʜᴀʀᴇ", callback_data="share"))
        bot.edit_message_text(txt, uid, load.message_id, parse_mode="HTML", reply_markup=markup)
        bot.send_message(uid, f"{E['ticket']} <b>Full JWT:</b>\n\n<code>{jwt}</code>", parse_mode="HTML")
    else:
        txt = f"{E['cross']}╔══════════════════════╗\n║   {E['cross']} ғᴀɪʟᴇᴅ {E['cross']}   ║\n╚══════════════════════╝\n\n{E['cross']} Error: <code>{result}</code>\n\n{E['star']} Check UID/Password"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"{E['key']} ᴛʀʏ ᴀɢᴀɪɴ", callback_data="new_gen"))
        bot.edit_message_text(txt, uid, load.message_id, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "new_gen")
def new_gen(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, f"{E['star']} Send <code>UID:Password</code>:", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "share")
def share(call):
    bot.answer_callback_query(call.id, "✅ Share @CRACKAxxFATHER", show_alert=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Flask thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    
    # Bot
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)