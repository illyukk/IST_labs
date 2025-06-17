import telebot
import requests
import xml.dom.minidom
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

TOKEN_TELEGRAM = '7615552909:AAE2gSTSrIIpOaeaZ_SkFTgaIaC6l0BJfOs'
bot = telebot.TeleBot(TOKEN_TELEGRAM)

selected_currency = {}
user_data = {}
#Функция, которая считывает все валюты с сайта ЦБ
def get_available_currencies(date='09/05/2023'):
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, timeout=5, headers=headers)  # Запрос на сайт
        if response.status_code == 200:  # Если ответ успешный
            dom = xml.dom.minidom.parseString(response.text)  # Разбираем XML
            currencies = []  # Список для хранения валют
            # Проходим по всем валютам в ответе
            for currency in dom.getElementsByTagName('Valute'):
                char_code = currency.getElementsByTagName('CharCode')[0].childNodes[0].nodeValue  # Получаем код валюты
                name = currency.getElementsByTagName('Name')[0].childNodes[0].nodeValue  # Получаем название валюты
                currencies.append((char_code, name))  # Добавляем валюту в список. кортеж
            return currencies
    except Exception as e:
        print(f"Ошибка при получении списка валют: {e}")
    return []

def get_currency_rate_raw(currency_code, date):
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code == 200:
            dom = xml.dom.minidom.parseString(response.text)
            for currency in dom.getElementsByTagName('Valute'):
                code = currency.getElementsByTagName('CharCode')[0].childNodes[0].nodeValue
                if code == currency_code:
                    nominal = int(currency.getElementsByTagName('Nominal')[0].childNodes[0].nodeValue)
                    value = currency.getElementsByTagName('Value')[0].childNodes[0].nodeValue.replace(',', '.')
                    return float(value) / nominal
    except Exception as e:
        print(f"Ошибка при запросе курса: {e}")
    return None

def get_currency_rate(currency_code, date):
    raw_rate = get_currency_rate_raw(currency_code, date)
    if raw_rate is not None:
        return f"Курс {currency_code} на {date} составляет {raw_rate:.4f} RUB"
    else:
        return "Курс не найден или ошибка в вводе даты."

def get_currency_rates_range(currency_code, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
    current_date = start_date
    dates = []
    rates = []
    while current_date <= end_date:
        date_formatted = current_date.strftime('%d/%m/%Y')
        rate = get_currency_rate_raw(currency_code, date_formatted)
        if rate is not None:
            dates.append(current_date)
            rates.append(rate)
        current_date += timedelta(days=1)
    return dates, rates

def plot_currency_rates(currency_code, start_date, end_date):
    dates, rates = get_currency_rates_range(currency_code, start_date, end_date)
    if not dates or not rates:
        return None
    plt.figure()
    plt.plot(dates, rates, marker='o')
    plt.xlabel("Дата")
    plt.ylabel("Курс (RUB)")
    plt.title(f"Курс {currency_code} с {start_date} по {end_date}")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    filename = 'currency_plot.png'
    plt.savefig(filename)
    plt.close()
    return filename
#получение списка валют
@bot.message_handler(commands=['start'])
def start(message):
    currencies = get_available_currencies()  # Получаем список валют
    if not currencies:
        bot.send_message(message.chat.id, "Не удалось получить список валют. Попробуйте позже.")
        return
    markup = telebot.types.InlineKeyboardMarkup()  # Создаём инлайн клавиатуру

    # Добавляем каждую валюту в клавиатуру как кнопку
    for code, name in currencies:
        markup.add(telebot.types.InlineKeyboardButton(f'{name} ({code})', callback_data=f'currency_{code}'))

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выберите валюту:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
def handle_currency_selection(call):
    currency_code = call.data.split('_')[1]
    selected_currency[call.message.chat.id] = currency_code
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Курс на дату", callback_data="action_rate"))
    markup.add(telebot.types.InlineKeyboardButton("Курсовая разница", callback_data="action_diff"))
    markup.add(telebot.types.InlineKeyboardButton("График курса", callback_data="action_chart"))
    bot.send_message(call.message.chat.id, f"Вы выбрали валюту: {currency_code}\nТеперь выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('action_'))
def handle_action(call):
    action = call.data.split('_')[1]
    currency = selected_currency.get(call.message.chat.id, 'не выбрана')
    if action == "rate":
        bot.send_message(call.message.chat.id, f"Вы выбрали: Курс на дату для {currency}\nВведите дату в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(call.message, process_rate)
    elif action == "diff":
        bot.send_message(call.message.chat.id, f"Вы выбрали: Курсовая разница для {currency}\nВведите первую дату в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(call.message, process_diff1)
    elif action == "chart":
        bot.send_message(call.message.chat.id, f"Вы выбрали: График курса для {currency}\nПожалуйста, подождите — график генерируется после ввода дат.\nВведите начальную дату в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(call.message, process_chart1)

def process_rate(message):
    try:
        date_input = message.text
        dt = datetime.strptime(date_input, "%d.%m.%Y")
        date_formatted = dt.strftime("%d/%m/%Y")
        currency_code = selected_currency.get(message.chat.id)
        if not currency_code:
            bot.send_message(message.chat.id, "Ошибка: валюта не выбрана.")
            return
        result = get_currency_rate(currency_code, date_formatted)
        bot.send_message(message.chat.id, result)
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат даты. Используйте ДД.ММ.ГГГГ")

def process_diff1(message):
    try:
        date_input = message.text
        dt = datetime.strptime(date_input, "%d.%m.%Y")
        date1 = dt.strftime("%d/%m/%Y")
        user_data[message.chat.id] = {"date1": date1}
        bot.send_message(message.chat.id, "Введите вторую дату в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(message, process_diff2)
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат даты. Используйте ДД.ММ.ГГГГ")

def process_diff2(message):
    try:
        date_input = message.text
        dt = datetime.strptime(date_input, "%d.%m.%Y")
        date2 = dt.strftime("%d/%m/%Y")
        currency_code = selected_currency.get(message.chat.id)
        if not currency_code:
            bot.send_message(message.chat.id, "Ошибка: валюта не выбрана.")
            return
        date1 = user_data.get(message.chat.id, {}).get("date1")
        if not date1:
            bot.send_message(message.chat.id, "Ошибка: отсутствует первая дата.")
            return
        rate1 = get_currency_rate_raw(currency_code, date1)
        rate2 = get_currency_rate_raw(currency_code, date2)
        if rate1 is None or rate2 is None:
            bot.send_message(message.chat.id, "Не удалось получить курс для одной из дат.")
            return
        diff = rate2 - rate1
        diff_text = f"+{diff:.4f}" if diff >= 0 else f"{diff:.4f}"
        bot.send_message(message.chat.id, f"Курсовая разница {currency_code}: {diff_text} RUB")
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат даты. Используйте ДД.ММ.ГГГГ")

def process_chart1(message):
    try:
        date_input = message.text
        dt = datetime.strptime(date_input, "%d.%m.%Y")
        start_date = dt.strftime("%d/%m/%Y")
        user_data[message.chat.id] = {"start_date": start_date}
        bot.send_message(message.chat.id, "Введите конечную дату в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(message, process_chart2)
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат даты. Используйте ДД.ММ.ГГГГ")

def process_chart2(message):
    try:
        date_input = message.text
        dt = datetime.strptime(date_input, "%d.%m.%Y")
        end_date = dt.strftime("%d/%m/%Y")
        currency_code = selected_currency.get(message.chat.id)
        if not currency_code:
            bot.send_message(message.chat.id, "Ошибка: валюта не выбрана.")
            return
        start_date = user_data.get(message.chat.id, {}).get("start_date")
        if not start_date:
            bot.send_message(message.chat.id, "Ошибка: отсутствует начальная дата.")
            return
        bot.send_message(message.chat.id, "График строится, подождите...")
        filename = plot_currency_rates(currency_code, start_date, end_date)
        if filename:
            with open(filename, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, "Не удалось построить график.")
    except Exception:
        bot.send_message(message.chat.id, "Неверный формат даты. Используйте ДД.ММ.ГГГГ")

bot.polling(none_stop=True)
