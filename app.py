#!/usr/bin/env python3
"""
🔐 FF JWT TOKEN GENERATOR - RENDER READY
Premium UI + Optional Join + Space Handle
"""

import os
import telebot
from telebot import types
import requests
import urllib3
from flask import Flask
from threading import Thread

urllib3.disable_warnings()

# Flask for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ FF JWT Bot Running!"

# ========== CONFIG ==========
BOT_TOKEN = "8669711044:AAEJqfiT1aaTVcZy2VF7JgW6HhoHtZtH_Xc"
ADMIN_ID = 769051183
HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

bot = telebot.TeleBot(BOT_TOKEN)

# ========== PREMIUM EMOJIS ==========
E = {
    "crown": "👑", "check": "✅", "cross": "❌", "load": "🔄",
    "key": "🔑", "id": "🆔", "pass": "🔒", "ticket": "🎫",
    "time": "⏰", "bolt": "⚡", "diamond": "💎", "star": "🌟",
    "rocket": "🚀", "globe": "🌐", "lock": "🔐", "msg": "💬",
    "fire": "🔥", "hearts": "💖", "target": "🎯", "shield": "🛡️",
}

# ========== INFO LINKS (Optional) ==========
INFO_TEXT = """
{star} <b>ᴊᴏɪɴ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ</b> {star}

{msg} <b>ᴅᴍ</b> ➜ @CRACKAxxFATHER
{globe} <b>ɢʀᴏᴜᴘ</b> ➜ <a href='https://t.me/+c0N-hu7QF9IzYzM1'>Join Group</a>
{fire} <b>ᴄʜᴀɴɴᴇʟ</b> ➜ <a href='https://t.me/+7h2aMq3RcOQ0YzI1'>Join Channel</a>
{rocket} <b>ʏᴏᴜᴛᴜʙᴇ</b> ➜ <a href='https://shorturl.at/5shO6'>Subscribe</a>
""".format(**E)

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

# ========== JWT GENERATOR ==========
def get_jwt(uid, password):
    try:
        resp = requests.post(
            "https://100067.connect.garena.com/oauth/guest/token/grant",
            data={
                "uid": uid,
                "password": password,
                "response_type": "token",
                "client_type": "2",
                "client_secret": HEX_KEY,
                "client_id": "100067"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)",
            },
            timeout=15,
            verify=False
        )
        data = resp.json()
        if "access_token" in data:
            return True, data["access_token"], data.get("expires_in", 0)
        return False, data.get("error", "Unknown"), 0
    except Exception as e:
        return False, str(e), 0

# ========== START ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    name = message.from_user.first_name or "User"
    
    if uid == ADMIN_ID:
        txt = f"""
{ E['crown']}╔══════════════════════╗
║   {E['diamond']} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {E['diamond']}   ║
╚══════════════════════╝

{E['star']} <b>Welcome Admin {name}!</b>
{E['shield']} All restrictions bypassed

{E['bolt']} <b>Send UID:Password</b>
<code>6267873771:Test123</code>

{INFO_TEXT}
"""
        bot.send_message(uid, txt, parse_mode="HTML", reply_markup=community_buttons())
        return
    
    txt = f"""
{E['fire']}╔══════════════════════╗
║   {E['crown']} ғғ ᴊᴡᴛ ɢᴇɴ {E['crown']}   ║
╚══════════════════════╝

{E['rocket']} <b>Welcome {name}!</b>

{E['lock']} <b>Send UID & Password:</b>
<code>UID:Password</code>

{E['star']} <b>Example:</b>
<code>6267873771:Test123</code>

{E['target']} <b>Get instant JWT Token!</b>

{INFO_TEXT}
"""
    bot.send_message(uid, txt, parse_mode="HTML", reply_markup=community_buttons())

# ========== HANDLE UID:PASSWORD ==========
@bot.message_handler(func=lambda m: m.text and ":" in m.text)
def handle_uid_pass(message):
    uid = message.from_user.id
    
    # Clean input - remove extra spaces
    text = message.text.strip()
    
    # Split on first ":" only
    parts = text.split(":", 1)
    
    uid_input = parts[0].strip().replace(" ", "")
    password = parts[1].strip()
    
    # Validate UID
    if not uid_input or not uid_input.isdigit():
        # Silent ignore - user ko pata nahi chalega
        return
    
    if not password:
        return
    
    # Loading message
    load = bot.reply_to(
        message,
        f"{E['load']} <i>Generating JWT Token...</i>",
        parse_mode="HTML"
    )
    
    # Generate JWT
    success, result, expires = get_jwt(uid_input, password)
    
    if success:
        hours = expires // 3600
        jwt = result
        
        txt = f"""
{E['check']}╔══════════════════════╗
║   {E['crown']} ᴊᴡᴛ ʀᴇᴀᴅʏ {E['crown']}   ║
╚══════════════════════╝

{E['id']} <b>UID:</b> <code>{uid_input}</code>
{E['pass']} <b>Password:</b> <code>{password[:40]}</code>

{E['ticket']} <b>JWT Token:</b>
<code>{jwt[:80]}...</code>

{E['time']} <b>Expires in:</b> {hours} hours
{E['bolt']} <b>Status:</b> <code>ACTIVE</code>

{E['lock']} <i>Full token below ↓</i>
"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"{E['key']} ɴᴇᴡ ɢᴇɴ", callback_data="new_gen"),
            types.InlineKeyboardButton(f"{E['msg']} sʜᴀʀᴇ", callback_data="share"),
        )
        
        bot.edit_message_text(txt, uid, load.message_id, parse_mode="HTML", reply_markup=markup)
        
        # Send full JWT separately
        bot.send_message(
            uid,
            f"{E['ticket']} <b>Full JWT Token:</b>\n\n<code>{jwt}</code>",
            parse_mode="HTML"
        )
    else:
        txt = f"""
{E['cross']}╔══════════════════════╗
║   {E['cross']} ғᴀɪʟᴇᴅ {E['cross']}   ║
╚══════════════════════╝

{E['cross']} <b>Error:</b> <code>{result}</code>

{E['star']} <b>Try:</b>
• Check UID & Password
• Use different account
• Wait & try again

{INFO_TEXT}
"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"{E['key']} ᴛʀʏ ᴀɢᴀɪɴ", callback_data="new_gen"))
        bot.edit_message_text(txt, uid, load.message_id, parse_mode="HTML", reply_markup=markup)

# ========== OTHER MESSAGES (Silent) ==========
@bot.message_handler(func=lambda m: True)
def other_messages(message):
    # Koi reply nahi - sirf UID:Password format pe response
    pass

# ========== CALLBACKS ==========
@bot.callback_query_handler(func=lambda call: call.data == "new_gen")
def new_gen_callback(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)
    bot.send_message(
        uid,
        f"{E['star']} <b>Send new UID:Password:</b>\n<code>UID:Password</code>",
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data == "share")
def share_callback(call):
    bot.answer_callback_query(call.id, "✅ Share @CRACKAxxFATHER", show_alert=True)

# ========== START BOT ==========
if __name__ == "__main__":
    # Render port
    port = int(os.environ.get("PORT", 10000))
    
    print(f"""
{E['fire']}══════════════════════════
{E['crown']} FF JWT GEN BOT
{E['bolt']} @CRACKAxxFATHER
{E['check']} Render Ready
{E['fire']}══════════════════════════
""")
    
    # Flask in background
    Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    
    # Telegram bot
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)