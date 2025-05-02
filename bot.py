import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import init_db, populate_data, get_masters, get_services, get_branches, add_booking
import requests
from datetime import datetime, timedelta

# Настроим логирование, чтобы видеть ошибки и инфо
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7661488307:AAHD1b3zHygTe1ccDsSEdpnLpRSIYtoe4xw'
FLASK_URL = 'http://127.0.0.1:5000/booking'

bot = TeleBot(API_TOKEN)

# Инициализация БД
init_db()
populate_data()


def main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛒 Заказать пиццу", callback_data="book"),
        InlineKeyboardButton("📜 Меню",       callback_data="price"),
        InlineKeyboardButton("📍 Филиалы",    callback_data="branches")
    )
    return markup


@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в «Нашу Пиццу»!\nВыберите действие:",
        reply_markup=main_menu()
    )


@bot.callback_query_handler(lambda c: c.data == 'book')
def handle_book(call):
    # Шаг 1: показываем "мастеров" (у вас — виды пиццы)
    markup = InlineKeyboardMarkup(row_width=1)
    masters = get_masters()
    for idx, (name, rating) in enumerate(masters):
        markup.add(InlineKeyboardButton(f"{name} (Рейтинг: {rating})", callback_data=f"master_{idx}"))
    bot.edit_message_text(
        "🍕 Выберите пиццу:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(lambda c: c.data == 'price')
def handle_price(call):
    services = get_services()
    text = "📋 Наши услуги и цены:\n\n" + "\n".join(f"{s[0]} — {s[1]} тг" for s in services)
    bot.answer_callback_query(call.id)  # без этого может крутиться «часики»
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(lambda c: c.data == 'branches')
def handle_branches(call):
    branches = get_branches()
    text = "🏢 Наши филиалы:\n\n" + "\n".join(f"{b[0]} — [На карте]({b[1]})" for b in branches)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


@bot.callback_query_handler(lambda c: c.data.startswith('master_'))
def handle_master(call):
    # Шаг 2: выбираем способ доставки (у вас — услуги)
    master_id = call.data.split('_')[1]
    services = get_services()
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, (srv, price) in enumerate(services):
        markup.add(InlineKeyboardButton(f"{srv} — {price} тг", callback_data=f"service_{master_id}_{idx}"))
    bot.edit_message_text(
        "🚚 Выберите тип доставки:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(lambda c: c.data.startswith('service_'))
def handle_service(call):
    # Шаг 3: дата
    _, master_id, service_id = call.data.split('_')
    markup = InlineKeyboardMarkup(row_width=2)
    for i in range(7):
        d = (datetime.now() + timedelta(days=i)).strftime("%d-%m-%Y")
        markup.add(InlineKeyboardButton(d, callback_data=f"date_{master_id}_{service_id}_{d}"))
    bot.edit_message_text(
        "📅 Выберите дату:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(lambda c: c.data.startswith('date_'))
def handle_date(call):
    # Шаг 4: время
    parts = call.data.split('_')  # ['date', master, service, 'DD-MM-YYYY']
    master_id, service_id, date = parts[1], parts[2], parts[3]
    markup = InlineKeyboardMarkup(row_width=3)
    for hour in range(10, 23):
        t = f"{hour}:00"
        markup.add(InlineKeyboardButton(t, callback_data=f"time_{master_id}_{service_id}_{date}_{t}"))
    bot.edit_message_text(
        "⏰ Выберите время:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(lambda c: c.data.startswith('time_'))
def handle_time(call):
    # Шаг 5: филиал
    parts = call.data.split('_')  # ['time', master, service, date, 'HH:MM']
    master_id, service_id, date, time_slot = parts[1], parts[2], parts[3], parts[4]
    branches = get_branches()
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, (bname, _) in enumerate(branches):
        markup.add(InlineKeyboardButton(bname, callback_data=f"branch_{master_id}_{service_id}_{date}_{time_slot}_{idx}"))
    bot.edit_message_text(
        "🏠 Выберите филиал:",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(lambda c: c.data.startswith('branch_'))
def handle_branch(call):
    # Шаг 6: спрашиваем имя и телефон
    parts = call.data.split('_')
    master_id, service_id, date, time_slot, branch_id = parts[1:]
    msg = bot.send_message(call.message.chat.id, "👤 Введите ваше имя:")
    bot.register_next_step_handler(msg, get_phone, master_id, service_id, date, time_slot, branch_id)


def get_phone(message, master_id, service_id, date, time_slot, branch_id):
    name = message.text
    msg = bot.send_message(message.chat.id, "📞 Теперь введите номер телефона:")
    bot.register_next_step_handler(msg, save_booking, master_id, service_id, date, time_slot, branch_id, name)


def save_booking(message, master_id, service_id, date, time_slot, branch_id, name):
    phone = message.text
    masters = get_masters()
    services = get_services()
    branches = get_branches()

    master = masters[int(master_id)][0]
    service = services[int(service_id)][0]
    branch  = branches[int(branch_id)][0]

    # Сохраняем в базу
    add_booking(name, phone, master, service, date, time_slot, branch)
    # Отправляем на Flask
    try:
        requests.post(FLASK_URL, json={
            "name": name, "phone": phone,
            "master": master, "service": service,
            "date": date, "time": time_slot,
            "branch": branch
        }, timeout=5)
    except Exception as e:
        logging.warning(f"Не удалось отправить на Flask: {e}")

    # Подтверждаем пользователю
    bot.send_message(
        message.chat.id,
        f"✅ Заказ подтверждён!\n\n"
        f"Пицца: {master}\n"
        f"Доставка: {service}\n"
        f"Дата: {date}\n"
        f"Время: {time_slot}\n"
        f"Филиал: {branch}"
    )
    bot.send_message(message.chat.id, "Спасибо за обращение!", reply_markup=main_menu())


if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
