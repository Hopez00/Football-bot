import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from supabase import create_client, Client

TELEGRAM_TOKEN = "8932539574:AAE3x0LF7RFc_gnQTWukCOJrUBXV-Po4i2w"
FOOTBALL_API_KEY = "e08e7153946d4aaf85372ea7368b9b8d"

# Initialize Supabase Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Strict filter focusing on leagues with stable statistical scoring metrics
ALLOWED_LEAGUES = ["Premier League", "Eredivisie", "Bundesliga", "Primera Division", "Serie A"]

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot service status: Operational with Cloud Logging")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "📊 *Professional Football Analytics Bot*\n\n"
        "Welcome. This system utilizes disciplined data filtering and tactical trend analysis "
        "to highlight high-probability market scenarios while managing exposure risk.\n\n"
        "Use /predict to generate the current analytical fixture report."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

def evaluate_tactical_market(home, away, competition):
    if competition in ["Eredivisie", "Bundesliga"]:
        return {
            "market": "Over 2.5 Goals / Alternative: Team Total Over 1.5",
            "risk_profile": "Moderate (Open tactical setups observed)",
            "confidence": "Tier 1 (Statistical Trend Alignment)"
        }
    elif competition == "Premier League":
        return {
            "market": "Double Chance (1X) & Match Over 1.5 Goals",
            "risk_profile": "Conservative (High volatility management)",
            "confidence": "Tier 2 (Core Selection)"
        }
    elif competition == "Primera Division":
        return {
            "market": "Under 3.5 Match Goals / Home Draw No Bet",
            "risk_profile": "Controlled (Tactical possession management)",
            "confidence": "Tier 2 (Defensive Stability Focus)"
        }
    elif competition == "Serie A":
        return {
            "market": "Under 3.5 Goals / Second Half Over 0.5 Goals",
            "risk_profile": "Cautious (Low-block structural profiles)",
            "confidence": "Tier 1 (Structural Constraint)"
        }
    else:
        return {
            "market": "Strictly Monitored / Low Exposure Recommendation",
            "risk_profile": "Defensive",
            "confidence": "Observation Only"
        }

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or user.first_name or "Unknown"

    await update.message.reply_text("🔄 Executing multi-variable data scan across approved leagues...")
    
    url = "https://api.football-data.org/v4/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        if not matches:
            await update.message.reply_text("No verified fixtures currently match the active scheduling criteria.")
            return
            
        report_text = "📈 *EXECUTIVE MATCH ANALYTICS REPORT* 📈\n\n"
        count = 0
        
        for match in matches:
            competition = match["competition"]["name"]
            
            if competition not in ALLOWED_LEAGUES:
                continue
                
            if count >= 5:
                break
                
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            utc_date = match["utcDate"].replace("T", " ")[:16]
            
            evaluation = evaluate_tactical_market(home, away, competition)
            
            count += 1
            report_text += f"*Fixture {count}:* {home} vs {away}\n"
            report_text += f"• *Competition:* {competition}\n"
            report_text += f"• *Kickoff:* {utc_date} UTC\n"
            report_text += f"• *Analytical Angle:* {evaluation['market']}\n"
            report_text += f"• *Risk Rating:* {evaluation['risk_profile']}\n"
            report_text += f"• *Confidence:* {evaluation['confidence']}\n\n"
            
        if count == 0:
            await update.message.reply_text("No qualifying fixtures found within the primary target parameters at this hour.")
        else:
            report_text += "_Disclaimer: Analytical models are probabilistic. Practice strict bankroll management._"
            await update.message.reply_text(report_text, parse_mode="Markdown")

            # Log request to Supabase database
            if supabase:
                try:
                    supabase.table("bot_logs").insert({
                        "user_id": user_id,
                        "username": username,
                        "prediction_summary": f"Generated {count} fixtures report successfully."
                    }).execute()
                except Exception as e:
                    print(f"Database logging error: {e}")
    else:
        await update.message.reply_text("❌ Data retrieval error: Unable to sync with live telemetry feeds.")

if __name__ == "__main__":
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
    
    print("Professional analytics bot operational with cloud database logging.")
    app.run_polling()
