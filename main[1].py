
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import math
import os

TOKEN = os.getenv("BOT_TOKEN")

systems = {
    'Пол': {
        'Стандарт 2 (Звукоизол Флор)': {'покрытие': 3.0, 'цена': 6500},
        'Стандарт 1 (ТЗИ)': {'покрытие': 3.0, 'цена': 8900},
        'Профи Премиум': {'покрытие': 3.0, 'цена': 11500}
    },
    'Стены': {
        'Каркасная Базовая': {'покрытие': 3.0, 'цена': 6500},
        'Каркасная Стандарт П': {'покрытие': 3.0, 'цена': 8900},
        'Каркасная Стандарт М1': {'покрытие': 3.0, 'цена': 11500}
    },
    'Потолок': {
        'Каркасная Базовая': {'покрытие': 3.0, 'цена': 6500},
        'Каркасная Стандарт П': {'покрытие': 3.0, 'цена': 8900},
        'Каркасная Стандарт М1': {'покрытие': 3.0, 'цена': 11500}
    },
    'Перегородки': {
        'Каркасная Базовая': {'покрытие': 3.0, 'цена': 6500},
        'Каркасная Стандарт П': {'покрытие': 3.0, 'цена': 8900},
        'Каркасная Стандарт М1': {'покрытие': 3.0, 'цена': 11500}
    }
}

contacts_text = (
    "📞 Телефон: +7 (909) 185-63-06\n"
    "🌐 Сайт: [tihiydom72](https://vk.link/tihiydom72)"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Пол', 'Стены'], ['Потолок', 'Перегородки'], ['Контакты']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот-калькулятор звукоизоляции «Тихий Дом».\n"
        "Выбери поверхность для расчёта:",
        reply_markup=reply_markup
    )

async def choose_surface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surface = update.message.text
    if surface in systems:
        context.user_data['surface'] = surface
        options = list(systems[surface].keys())
        keyboard = [[name] for name in options]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Выбери систему:", reply_markup=reply_markup)
    elif surface == "Контакты":
        await update.message.reply_text(contacts_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("Пожалуйста, выбери одну из предложенных опций.")

async def choose_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    system = update.message.text
    surface = context.user_data.get('surface')
    if surface and system in systems.get(surface, {}):
        context.user_data['system'] = system
        await update.message.reply_text("Введите размеры в метрах: длина ширина (например: 5.5 3.2)")
    else:
        await update.message.reply_text("Пожалуйста, выбери систему из предложенного списка.")

async def handle_dimensions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surface = context.user_data.get('surface')
    system = context.user_data.get('system')
    text = update.message.text.strip()

    try:
        length, width = map(float, text.replace(",", ".").split())
        area = length * width
        sys_data = systems[surface][system]
        packs = math.ceil(area / sys_data['покрытие'])
        cost = packs * sys_data['цена']

        await update.message.reply_text(
            f"📐 Площадь: {area:.2f} м²\n"
            f"🧱 Система: {system}\n"
            f"📦 Комплектов нужно: {packs}\n"
            f"💰 Стоимость: {cost} ₽\n\n"
            f"{contacts_text}",
            parse_mode="Markdown"
        )
        context.user_data.clear()
    except Exception:
        await update.message.reply_text("Ошибка. Введите два числа через пробел, например: 6 4")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("^(Пол|Стены|Потолок|Перегородки|Контакты)$"), choose_surface))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(Каркасная|Стандарт|Профи|Звукоизол|ТЗИ)"), choose_system))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dimensions))

app.run_polling()
