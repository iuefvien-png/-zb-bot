import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8925613520:AAG-EL7MdNA2oizhxIwHxKC3QkT4Ldg_Up8"
ADMIN_ID = 898174079

logging.basicConfig(level=logging.INFO)

NAME, PHONE, ADDRESS, ITEMS, TIME, CONFIRM = range(6)

MENU = """
🥭 *Манго* — Пакистан/Индия
🍓 *Клубника* — Краснодар
🍇 *Виноград* — Узбекистан
🍑 *Персик* — Испания
🍒 *Черешня* — Крым
🥝 *Киви* — Новая Зеландия
🍊 *Мандарин* — Абхазия
🌺 *Маракуйя* — Бразилия
🍋 *Лимон* — Турция
🍍 *Ананас* — Коста-Рика
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🛒 Сделать заказ"], ["🍓 Ассортимент", "📞 Контакты"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привет! Добро пожаловать в *Zemly & Barboss Fruits Co.*\n\n"
        "🏠 Доставка по Крылатскому\n"
        "⏱ Время доставки: 1–2 часа\n"
        "✅ Только отборные фрукты\n\n"
        "Выбери что тебя интересует 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍉 *Наш ассортимент:*\n" + MENU + "\nМинимальный заказ — 1 кг\nДоставка по Крылатскому 🏠",
        parse_mode="Markdown"
    )

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Контакты Z&B Fruits Co.*\n\n"
        "📍 Район: Крылатское, Москва\n"
        "🕐 Работаем: 8:00 — 22:00\n"
        "👨‍💼 CEO: Володя Яковлев\n"
        "👨‍💼 COO: Гриша Измайлов\n\n"
        "Для заказа нажми 👉 *Сделать заказ*",
        parse_mode="Markdown"
    )

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🛒 *Оформление заказа*\n\nШаг 1/5\n\n👤 Как вас зовут?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True)
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отменить":
        return await cancel(update, context)
    context.user_data['name'] = update.message.text
    kb = ReplyKeyboardMarkup([[KeyboardButton("📱 Отправить номер", request_contact=True)], ["❌ Отменить"]], resize_keyboard=True)
    await update.message.reply_text(
        f"✅ Отлично, *{update.message.text}*!\n\nШаг 2/5\n\n📱 Укажите номер телефона:",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отменить":
        return await cancel(update, context)
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
    else:
        context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "Шаг 3/5\n\n📍 Укажите адрес доставки в Крылатском:",
        reply_markup=ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True)
    )
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отменить":
        return await cancel(update, context)
    context.user_data['address'] = update.message.text
    await update.message.reply_text(
        "Шаг 4/5\n\n🍓 Что хотите заказать?\n\n" + MENU + "\nПример: *Манго 2кг, Клубника 1 лоток, Черешня 500г*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True)
    )
    return ITEMS

async def get_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отменить":
        return await cancel(update, context)
    context.user_data['items'] = update.message.text
    keyboard = [
        ["⚡️ Как можно скорее (1–2 ч)"],
        ["🌆 Сегодня вечером 18:00–21:00"],
        ["🌅 Завтра утром 9:00–13:00"],
        ["📞 Договоримся при звонке"],
        ["❌ Отменить"]
    ]
    await update.message.reply_text(
        "Шаг 5/5\n\n🕐 Когда удобно доставить?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отменить":
        return await cancel(update, context)
    context.user_data['time'] = update.message.text
    d = context.user_data
    summary = (
        f"📋 *Проверьте заказ:*\n\n"
        f"👤 Имя: {d['name']}\n"
        f"📱 Телефон: {d['phone']}\n"
        f"📍 Адрес: {d['address']}\n"
        f"🍓 Заказ: {d['items']}\n"
        f"🕐 Время: {d['time']}\n\n"
        f"Всё верно?"
    )
    keyboard = [["✅ Подтвердить заказ"], ["❌ Отменить"]]
    await update.message.reply_text(summary, parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отменить":
        return await cancel(update, context)
    d = context.user_data
    user = update.message.from_user
    admin_msg = (
        f"🔔 *НОВЫЙ ЗАКАЗ!*\n\n"
        f"👤 Клиент: {d['name']}\n"
        f"📱 Телефон: {d['phone']}\n"
        f"📍 Адрес: {d['address']}\n"
        f"🍓 Заказ: {d['items']}\n"
        f"🕐 Время: {d['time']}\n\n"
        f"💬 Telegram: @{user.username or 'нет'}\n"
        f"🆔 ID: {user.id}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
    keyboard = [["🛒 Сделать заказ"], ["🍓 Ассортимент", "📞 Контакты"]]
    await update.message.reply_text(
        "✅ *Заказ принят!*\n\n"
        "Мы свяжемся с вами в течение 15 минут для подтверждения.\n\n"
        "🙏 Спасибо что выбрали *Z&B Fruits Co.*!",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🛒 Сделать заказ"], ["🍓 Ассортимент", "📞 Контакты"]]
    await update.message.reply_text(
        "❌ Заказ отменён. Возвращайся когда будешь готов! 🍓",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🛒 Сделать заказ"], ["🍓 Ассортимент", "📞 Контакты"]]
    await update.message.reply_text(
        "Нажми кнопку ниже 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛒 Сделать заказ$"), order_start)],
        states={
            NAME: [MessageHandler(filters.TEXT, get_name)],
            PHONE: [MessageHandler(filters.TEXT | filters.CONTACT, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT, get_address)],
            ITEMS: [MessageHandler(filters.TEXT, get_items)],
            TIME: [MessageHandler(filters.TEXT, get_time)],
            CONFIRM: [MessageHandler(filters.TEXT, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^🍓 Ассортимент$"), menu_cmd))
    app.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT, unknown))
    print("✅ ZBFruitsBot запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
