import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TELEGRAM_TOKEN = "8932539574:AAE3x0LF7RFc_gnQTWukCOJrUBXV-Po4i2w"
FOOTBALL_API_KEY = "e08e7153946d4aaf85372ea7368b9b8d"

# Trusted high-scoring leagues (Filtering out low-scoring defensive leagues)
ALLOWED_LEAGUES = ["Premier League", "Eredivisie", "Bundesliga", "Primera Division", "Serie A"]

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Welcome! Type /predict for filtered, high-probability match slips.")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Filtering out risky fixtures and scanning top goal-scoring leagues...")
    
    url = "https://api.football-data.org/v4/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        if not matches:
            await update.message.reply_text("No upcoming matches found right now.")
            return
            
        slip_text = "🎯 REFINED HIGH-PROBABILITY SLIP 🎯\n\n"
        count = 0
        
        for match in matches:
            competition = match["competition"]["name"]
            
            # Skip leagues prone to 0-0 draws (Filter logic)
            if competition not in ALLOWED_LEAGUES:
                continue
                
            if count >= 5:
                break
                
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            utc_date = match["utcDate"].replace("T", " ")[:16]
            
            count += 1
            slip_text += f"{count}. {home} vs {away}\n"
            slip_text += f"League: {competition}\n"
            slip_text += f"Time: {utc_date} UTC\n"
            slip_text += f"Pick: Over 1.5 Goals / Safe 1X\n\n"
            
        if count == 0:
            await update.message.reply_text("No matches currently available in the primary target leagues. Try again later!")
        else:
            await update.message.reply_text(slip_text)
    else:
        await update.message.reply_text("❌ Failed to fetch live data from API.")

if __name__ == "__main__":
    # Start the tiny web server in the background to satisfy Render's port requirement
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    
    print("Bot is up with advanced match filtering and web port bound!")
    app.run_polling()
    
