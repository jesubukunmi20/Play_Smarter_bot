import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== DATABASE (In-memory for demo - use a real DB for production) =====
users_data = {}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "points": 0,
            "streak": 0,
            "last_tip_date": None,
            "tips_received": []
        }
    return users_data[user_id]

# ===== COMMAND HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name
    
    # Initialize user data
    get_user_data(user_id)
    
    welcome_text = f"""🎮 Welcome to Play Smarter, {first_name}!

I'm here to help you level up your gaming skills — completely free.

Here's what you can do:
📅 Get a daily gaming tip
📊 Track your stats & points
🏆 Compete on the leaderboard
📂 Browse tips by category

Tap a button below to get started!"""

    keyboard = [
        [InlineKeyboardButton("📅 Daily Tip", callback_data="tip")],
        [InlineKeyboardButton("📂 Categories", callback_data="categories")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when /help is issued."""
    help_text = """📖 *Play Smarter - Help*

*Commands:*
/start - Main menu
/tip - Get daily gaming tip
/categories - Browse tip categories
/stats - Your stats
/leaderboard - Top players
/help - This message

*How it works:*
• Get daily gaming tips
• Earn points for learning
• Build streaks
• Compete with others

*Free gaming education — no gambling!*"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")


async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a daily gaming tip."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    # Simple tip rotation (replace with your actual tips)
    tips = [
        "🎯 *Aim Improvement:* Practice tracking moving targets in aim trainers for 15 minutes daily.",
        "🧠 *Mental Game:* Take a 5-minute break between matches to reset your focus.",
        "⚙️ *Settings:* Lower your sensitivity gradually for better micro-adjustments.",
        "📊 *Strategy:* Watch your replays to identify positioning mistakes.",
        "🎮 *General:* Warm up with 10 minutes of practice mode before competitive matches."
    ]
    
    tip_index = len(user_data["tips_received"]) % len(tips)
    tip = tips[tip_index]
    
    # Update user data
    user_data["points"] += 5
    user_data["streak"] += 1
    user_data["tips_received"].append(tip_index)
    
    tip_text = f"""📅 *Daily Gaming Tip*

{tip}

✨ *+5 points earned!*
📊 Points: {user_data['points']} | Streak: {user_data['streak']} days

Come back tomorrow for another tip!"""
    
    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(tip_text, reply_markup=reply_markup, parse_mode="Markdown")


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tip categories."""
    categories_text = """📂 *Choose a Category*

Get specific tips for your gaming style!"""

    keyboard = [
        [InlineKeyboardButton("🎯 Strategy Tips", callback_data="category_strategy")],
        [InlineKeyboardButton("🎮 Aim Improvement", callback_data="category_aim")],
        [InlineKeyboardButton("🧠 Mental Game", callback_data="category_mental")],
        [InlineKeyboardButton("⚙️ Settings Optimize", callback_data="category_settings")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(categories_text, reply_markup=reply_markup, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user stats."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    stats_text = f"""📊 *My Stats*

👤 Player: {update.effective_user.first_name}
⭐ Points: {user_data['points']}
🔥 Streak: {user_data['streak']} days
📚 Tips Received: {len(user_data['tips_received'])}
🏆 Rank: #{len(users_data)} on leaderboard

Keep going! Every tip makes you smarter! 🎮"""
    
    keyboard = [
        [InlineKeyboardButton("📅 Daily Tip", callback_data="tip")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show leaderboard."""
    if not users_data:
        leaderboard_text = "🏆 *Leaderboard*\n\nNo players yet! Be the first to earn points! 🎮"
    else:
        # Sort users by points (descending)
        sorted_users = sorted(users_data.items(), key=lambda x: x[1]["points"], reverse=True)
        
        leaderboard_text = "🏆 *Leaderboard*\n\n"
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            # Get username (in a real bot, you'd store this)
            name = f"Player_{user_id}"  # Placeholder
            points = data["points"]
            streak = data["streak"]
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text += f"{medal} {name} - {points} pts ({streak}d)\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(leaderboard_text, reply_markup=reply_markup, parse_mode="Markdown")


# ===== CALLBACK QUERY HANDLERS =====

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if data == "menu":
        # Return to main menu
        first_name = update.effective_user.first_name
        welcome_text = f"""🎮 Welcome back, {first_name}!

What would you like to do?"""
        
        keyboard = [
            [InlineKeyboardButton("📅 Daily Tip", callback_data="tip")],
            [InlineKeyboardButton("📂 Categories", callback_data="categories")],
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)
    
    elif data == "tip":
        # Same logic as /tip command
        tips = [
            "🎯 *Aim Improvement:* Practice tracking moving targets in aim trainers for 15 minutes daily.",
            "🧠 *Mental Game:* Take a 5-minute break between matches to reset your focus.",
            "⚙️ *Settings:* Lower your sensitivity gradually for better micro-adjustments.",
            "📊 *Strategy:* Watch your replays to identify positioning mistakes.",
            "🎮 *General:* Warm up with 10 minutes of practice mode before competitive matches."
        ]
        
        tip_index = len(user_data["tips_received"]) % len(tips)
        tip = tips[tip_index]
        
        user_data["points"] += 5
        user_data["streak"] += 1
        user_data["tips_received"].append(tip_index)
        
        tip_text = f"""📅 *Daily Gaming Tip*

{tip}

✨ *+5 points earned!*
📊 Points: {user_data['points']} | Streak: {user_data['streak']} days

Come back tomorrow for another tip!"""
        
        keyboard = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(tip_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif data == "categories":
        categories_text = """📂 *Choose a Category*

Get specific tips for your gaming style!"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Strategy Tips", callback_data="category_strategy")],
            [InlineKeyboardButton("🎮 Aim Improvement", callback_data="category_aim")],
            [InlineKeyboardButton("🧠 Mental Game", callback_data="category_mental")],
            [InlineKeyboardButton("⚙️ Settings Optimize", callback_data="category_settings")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(categories_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif data == "stats":
        stats_text = f"""📊 *My Stats*

👤 Player: {update.effective_user.first_name}
⭐ Points: {user_data['points']}
🔥 Streak: {user_data['streak']} days
📚 Tips Received: {len(user_data['tips_received'])}
🏆 Rank: #{len(users_data)} on leaderboard

Keep going! Every tip makes you smarter! 🎮"""
        
        keyboard = [
            [InlineKeyboardButton("📅 Daily Tip", callback_data="tip")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    elif data == "leaderboard":
        if not users_data:
            leaderboard_text = "🏆 *Leaderboard*\n\nNo players yet! Be the first to earn points! 🎮"
        else:
            sorted_users = sorted(users_data.items(), key=lambda x: x[1]["points"], reverse=True)
            
            leaderboard_text = "🏆 *Leaderboard*\n\n"
            for i, (uid, data_dict) in enumerate(sorted_users[:10], 1):
                name = f"Player_{uid}"  # Placeholder
                points = data_dict["points"]
                streak = data_dict["streak"]
                
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                leaderboard_text += f"{medal} {name} - {points} pts ({streak}d)\n"
        
        keyboard = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(leaderboard_text, reply_markup=reply_markup, parse_mode="Markdown")
    
    # Category handlers
    elif data.startswith("category_"):
        category = data.replace("category_", "")
        category_names = {
            "strategy": "🎯 Strategy Tips",
            "aim": "🎮 Aim Improvement", 
            "mental": "🧠 Mental Game",
            "settings": "⚙️ Settings Optimize"
        }
        
        # Sample tips for each category (replace with your actual content)
        category_tips = {
            "strategy": """🎯 *Strategy Tips*

1. Watch your replays to identify positioning mistakes.
2. Communicate with your team before the match starts.
3. Always have an escape route planned.
4. Play the objective, not just for kills.
5. Learn from your deaths — what could you have done differently?""",
            
            "aim": """🎮 *Aim Improvement*

1. Practice tracking moving targets daily.
2. Lower your sensitivity for micro-adjustments.
3. Keep crosshair at head level at all times.
4. Warm up with flick shots before matches.
5. Focus on your breathing for steady aim.""",
            
            "mental": """🧠 *Mental Game*

1. Take breaks between matches to reset.
2. Focus on what you can control, not your teammates.
3. Stay positive — tilt leads to mistakes.
4. Set small goals for each match.
5. Learn to enjoy the process, not just winning.""",
            
            "settings": """⚙️ *Settings Optimize*

1. Lower graphics for higher FPS.
2. Use a consistent sensitivity across all games.
3. Optimize crosshair color for visibility.
4. Adjust audio settings to hear footsteps clearly.
5. Find the right mouse DPI for your playstyle."""
        }
        
        category_text = f"{category_names.get(category, 'Category')}\n\n{category_tips.get(category, 'Tips coming soon!')}"
        
        keyboard = [
            [InlineKeyboardButton("📂 Back to Categories", callback_data="categories")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(category_text, reply_markup=reply_markup, parse_mode="Markdown")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send settings info."""
    settings_text = """⚙️ *Settings*

📌 Use commands or buttons:

/start - Main menu
/tip - Daily gaming tip
/categories - Browse tip categories
/stats - Your stats
/leaderboard - Top players
/help - This message

💡 Pro tip: Use the buttons below for quick access!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="Markdown")


# ===== MAIN FUNCTION =====

def main():
    """Start the bot."""
    # Create the Application
    # ⚠️ REPLACE WITH YOUR ACTUAL BOT TOKEN
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tip", tip_command))
    application.add_handler(CommandHandler("categories", categories_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Register callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))

    # Run the bot
    print("🚀 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
