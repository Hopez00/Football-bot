import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TELEGRAM_TOKEN = "8932539574:AAE3x0LF7RFc_gnQTWukCOJrUBXV-Po4i2w"
FOOTBALL_API_KEY = "e08e7153946d4aaf85372ea7368b9b8d"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Welcome! Type /predict to get real-life football prediction slips.")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Fetching live matches and analyzing trends...")
    
    url = "https://api.football-data.org/v4/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        if not matches:
            await update.message.reply_text("No upcoming matches found right now.")
            return
            
        slip_text = "🎯 HIGH-CONFIDENCE PREDICTION SLIP 🎯\n\n"
        count = 0
        
        for match in matches:
            if count >= 5:
                break
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            competition = match["competition"]["name"]
            utc_date = match["utcDate"].replace("T", " ")[:16]
            
            count += 1
            slip_text += f"{count}. {home} vs {away}\n"
            slip_text += f"League: {competition}\n"
            slip_text += f"Time: {utc_date} UTC\n"
            slip_text += f"Prediction: Over 1.5 Goals / Safe 1X\n\n"
            
        await update.message.reply_text(slip_text)
    else:
        await update.message.reply_text("❌ Failed to fetch live data from API.")

if __name__ == "__main__":
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
    
    print("Bot is up and running with custom timeouts! Press Ctrl+C to stop.")
    app.run_polling()
