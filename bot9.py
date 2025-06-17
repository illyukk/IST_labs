# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET           #Импорт модулей
import telebot
from telebot import types
import random

TOKEN = "8169042976:AAGhhrGM-gAxPFXBEWlZnv3O4g9WXyI-Bds" 
bot = telebot.TeleBot(TOKEN)

# Глобальный флаг (словарь) для режима гадания: если для chat.id установлен True, бот ожидает вопрос
expect_question = {}

# Inline меню главного уровня
main_menu_options = ["Гороскоп", "Гадание"]

# Список знаков зодиака
zodiac_list = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев", 
    "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", 
    "Водолей", "Рыбы"
]

# Возможные ответы для гадания
divination_answers = ["Да", "Нет", "Возможно", "Скорее да чем нет", "Скорее нет чем да"]

def get_horoscope_from_xml(sign): #Считывает файл horoscopes.xml и возвращает текст
    try:
        tree = ET.parse('horoscopes1.xml')
        root = tree.getroot()
        for horoscope in root.findall('horoscope'):
            if horoscope.get('zodiac') == sign:
                return horoscope.text.strip()
    except Exception as e:
        print("Ошибка чтения XML:", e)
    return "Гороскоп для вашего знака недоступен."

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    expect_question[message.chat.id] = False  # сброс режима гадания
    markup = types.InlineKeyboardMarkup()
    btn_goroscope = types.InlineKeyboardButton(text="Гороскоп", callback_data="menu_goroscope")
    btn_divination = types.InlineKeyboardButton(text="Гадание", callback_data="menu_divination")
    markup.add(btn_goroscope, btn_divination)
    bot.send_message(message.chat.id, "Привет! Выбери, что бы ты хотел получить:", reply_markup=markup)

# Обработка главного inline меню
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def menu_handler(call):
    if call.data == "menu_goroscope":
        # Выводим меню выбора знака зодиака
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [types.InlineKeyboardButton(text=sign, callback_data=f"zodiac_{sign}") for sign in zodiac_list]
        markup.add(*buttons)
        bot.send_message(call.message.chat.id, "Хорошо, выбери пожалуйста свой знак зодиака:", reply_markup=markup)
    elif call.data == "menu_divination":
        # Включаем режим гадания
        expect_question[call.message.chat.id] = True
        bot.send_message(call.message.chat.id, "Хорошо, задай свой вопрос!")

# Обработка выбора знака зодиака (гороскоп)
@bot.callback_query_handler(func=lambda call: call.data.startswith("zodiac_"))
def zodiac_handler(call):
    sign = call.data.split("_", 1)[1]
    horoscope = get_horoscope_from_xml(sign)
    response = f"Ваш знак зодиака: *{sign}*\n\nВаш гороскоп на сегодня:\n\"{horoscope}\""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Главное меню", callback_data="menu_main"))
    bot.send_message(call.message.chat.id, response, parse_mode="Markdown", reply_markup=markup)

# Обработка возврата в главное меню
@bot.callback_query_handler(func=lambda call: call.data == "menu_main")
def main_menu_handler(call):
    expect_question[call.message.chat.id] = False
    markup = types.InlineKeyboardMarkup()
    btn_goroscope = types.InlineKeyboardButton(text="Гороскоп", callback_data="menu_goroscope")
    btn_divination = types.InlineKeyboardButton(text="Гадание", callback_data="menu_divination")
    markup.add(btn_goroscope, btn_divination)
    bot.send_message(call.message.chat.id, "Выбери, что бы ты хотел получить:", reply_markup=markup)

# Обработка текстовых сообщений в режиме гадания
@bot.message_handler(func=lambda m: expect_question.get(m.chat.id, False) == True, content_types=["text"])
def divination_handler(message):
    # Выбираем случайный ответ
    answer = random.choice(divination_answers)
    # Отправляем только ответ
    bot.send_message(message.chat.id, answer)
    # Выключаем режим гадания
    expect_question[message.chat.id] = False

# Обработка любых других текстовых сообщений
@bot.message_handler(content_types=["text"])
def default_handler(message):
    if not expect_question.get(message.chat.id, False):
        bot.send_message(message.chat.id, "Пожалуйста, используй меню для выбора опций.")

bot.polling(none_stop=True)
