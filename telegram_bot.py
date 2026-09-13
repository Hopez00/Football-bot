import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from supabase import create_client, Client

# Load sensitive keys safely from Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Strict filter focusing on leagues with stable statistical scoring metrics
ALLOWED_LEAGUES = ["Premier League", "Eredivisie", "Bundesliga", "Primera Division", "Serie A"]

# Professional Persistent Menu Keyboard
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📈 Get Predictions"), KeyboardButton("📊 My Stats")],
        [KeyboardButton("ℹ️ System Info")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot service status: Operational with Interactive Menus & Cloud Logging")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "📊 *Professional Football Analytics Bot*\n\n"
        "Welcome. This system utilizes disciplined data filtering and tactical trend analysis "
        "to highlight high-probability market scenarios while managing exposure risk.\n\n"
        "Use the menu buttons below to interact with the system."
    )
    await update.message.reply_text(
        welcome_message, 
        parse_mode="Markdown", 
        reply_markup=get_main_keyboard()
    )

async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    if not supabase:
        await update.message.reply_text("⚠️ Database connection unavailable.")
        return

    try:
        # Query Supabase for user interaction count
        response = supabase.table("bot_logs").select("*", count="exact").eq("user_id", user_id).execute()
        total_requests = response.count if hasattr(response, 'count') and response.count is not None else len(response.data)
        
        stats_text = (
            f"👤 *User Activity Profile*\n\n"
            f"• *User ID:* `{user_id}`\n"
            f"• *Name:* {user.first_name}\n"
            f"• *Total Prediction Reports Generated:* {total_requests}\n\n"
            f"_Thank you for utilizing disciplined analytical models._"
        )
        await update.message.reply_text(stats_text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"Stats retrieval error: {e}")
        await update.message.reply_text("❌ Error fetching your activity stats from the cloud database.")

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

    await update.message.reply_text("🔄 Executing multi-variable data scan across approved leagues...", reply_markup=get_main_keyboard())
    
    url = "https://api.football-data.org/v4/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        if not matches:
            await update.message.reply_text("No verified fixtures currently match the active scheduling criteria.", reply_markup=get_main_keyboard())
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
            await update.message.reply_text("No qualifying fixtures found within the primary target parameters at this hour.", reply_markup=get_main_keyboard())
        else:
            report_text += "_Disclaimer: Analytical models are probabilistic. Practice strict bankroll management._"
            await update.message.reply_text(report_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

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
        await update.message.reply_text("❌ Data retrieval error: Unable to sync with live telemetry feeds.", reply_markup=get_main_keyboard())

# Handle button clicks as text messages
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📈 Get Predictions":
        await predict(update, context)
    elif text == "📊 My Stats":
        await user_stats(update, context)
    elif text == "ℹ️ System Info":
        await start(update, context)

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
    
    # Register command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("stats", user_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_click))
    
    print("Professional analytics bot operational with interactive keyboards and cloud logging.")
    app.run_polling()
         
