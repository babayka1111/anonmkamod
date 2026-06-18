from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
from datetime import datetime, timedelta

BOT_TOKEN = "8766775527:AAG-qpeP0QcgMY4cJjA8cxPhoa9037FldgQ"
ADMIN_ID = 7421345767

def ban_user(user_id: int, reason: str, days: int = None):
    conn = sqlite3.connect("/opt/render/project/src/bot.db")
    c = conn.cursor()
    banned_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banned_until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S") if days else "forever"
    c.execute("INSERT OR REPLACE INTO bans VALUES (?, ?, ?, ?)", (user_id, reason, banned_until, banned_at))
    conn.commit()
    conn.close()

def unban_user(user_id: int):
    conn = sqlite3.connect("/opt/render/project/src/bot.db")
    c = conn.cursor()
    c.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "🛡 <b>Бот-модератор AnonMka</b>\n\n"
        "/dialogs — список активных диалогов\n"
        "/ban [id] [срок] — бан\n"
        "/unban [id] — разбан\n"
        "/banlist — список банов",
        parse_mode="HTML"
    )

async def dialogs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("/opt/render/project/src/bot.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT dialog_id FROM messages ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Нет активных диалогов.")
        return
    keyboard = []
    for (dialog_id,) in rows[-10:]:
        keyboard.append([InlineKeyboardButton(f"📋 {dialog_id}", callback_data=f"view_{dialog_id}")])
    await update.message.reply_text("📋 <b>Последние диалоги:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        return

    if data.startswith("view_"):
        dialog_id = data.replace("view_", "")
        msgs = []
        conn = sqlite3.connect("/opt/render/project/src/bot.db")
        c = conn.cursor()
        c.execute("SELECT user_id, msg_text, timestamp FROM messages WHERE dialog_id = ? ORDER BY timestamp", (dialog_id,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            await query.edit_message_text("Диалог пуст.")
            return
        text = f"📋 <b>Диалог {dialog_id}:</b>\n\n"
        for uid, msg, ts in rows:
            text += f"<a href='tg://user?id={uid}'>{uid}</a>: {msg}\n"
        await query.edit_message_text(text, parse_mode="HTML")

    elif data.startswith("ban_"):
        parts = data.split("_")
        target_id = int(parts[1])
        action = parts[2]
        if action == "no":
            await query.edit_message_text("✅ Жалоба отклонена.")
            return
        days_map = {"1": 1, "7": 7, "30": 30, "0": None}
        days = days_map.get(action)
        ban_user(target_id, "Жалоба от пользователя", days)
        reason_text = f"на {days} дн." if days else "навсегда"
        await query.edit_message_text(f"⛔ Пользователь <a href='tg://user?id={target_id}'>{target_id}</a> забанен ({reason_text}).", parse_mode="HTML")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("/ban [user_id] [срок]\nПримеры: 1d, 7d, 30d, 1y, forever")
        return
    try:
        target = int(context.args[0])
    except:
        await update.message.reply_text("Неверный ID.")
        return
    duration = context.args[1].lower()
    if duration in ["forever", "0"]:
        days = None
        reason_text = "навсегда"
    elif duration.endswith("d"):
        days = int(duration[:-1])
        reason_text = f"на {days} дн."
    elif duration.endswith("y"):
        days = int(duration[:-1]) * 365
        reason_text = f"на {int(duration[:-1])} год/лет"
    else:
        await update.message.reply_text("Неверный формат.")
        return
    ban_user(target, "Бан от администратора", days)
    await update.message.reply_text(f"⛔ <a href='tg://user?id={target}'>{target}</a> забанен ({reason_text}).", parse_mode="HTML")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("/unban [user_id]")
        return
    try:
        target = int(context.args[0])
        unban_user(target)
        await update.message.reply_text(f"✅ Пользователь {target} разбанен.")
    except:
        await update.message.reply_text("Неверный ID.")

async def banlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("/opt/render/project/src/bot.db")
    c = conn.cursor()
    c.execute("SELECT user_id, reason, banned_until FROM bans")
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Список банов пуст.")
        return
    text = "📋 <b>Забаненные:</b>\n\n"
    for uid, reason, until in rows:
        text += f"<a href='tg://user?id={uid}'>{uid}</a> — {reason} — {until}\n"
    await update.message.reply_text(text, parse_mode="HTML")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dialogs", dialogs_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("banlist", banlist_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern="^(view_|ban_).*"))
    print("Бот-модератор запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
