from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8766775527:AAG-qpeP0QcgMY4cJjA8cxPhoa9037FldgQ"
ADMIN_ID = 7421345767

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return
    await update.message.reply_text(
        "🛡 <b>Бот-модератор AnonMka</b>\n\n"
        "Команды:\n"
        "/dialogs — активные диалоги\n"
        "/ban [id] [срок] — бан\n"
        "/unban [id] — разбан\n"
        "/banlist — список банов\n"
        "/monitor on/off — трансляция",
        parse_mode="HTML"
    )

async def dialogs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "📋 <b>Активные диалоги:</b>\n\n"
        "Пока диалогов нет или функция в разработке.\n"
        "Диалоги отслеживаются через основной бот — все сообщения приходят в этот чат.",
        parse_mode="HTML"
    )

async def monitor_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Использование: /monitor on или /monitor off")
        return
    global moder_monitoring
    if context.args[0].lower() == "on":
        moder_monitoring = True
        await update.message.reply_text("✅ Трансляция диалогов включена")
    elif context.args[0].lower() == "off":
        moder_monitoring = False
        await update.message.reply_text("🔕 Трансляция диалогов выключена")
    else:
        await update.message.reply_text("Использование: /monitor on или /monitor off")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dialogs", dialogs_cmd))
    app.add_handler(CommandHandler("monitor", monitor_cmd))
    
    print("Бот-модератор запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
