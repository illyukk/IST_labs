# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import telebot
from telebot import types
from telebot import apihelper

TOKEN = "8169042976:AAGhhrGM-gAxPFXBEWlZnv3O4g9WXyI-Bds" 
bot = telebot.TeleBot(TOKEN)

# Список знаков зодиака
zodiac_list = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев",
    "Дева", "Весы", "Скорпион", "Стрелец", "Козерог",
    "Водолей", "Рыбы"
]

# Счётчики нажатий для каждой кнопки
button_counts = { zodiac: 0 for zodiac in zodiac_list }

def get_horoscope_from_xml(zodiac):
    """
    Читает XML-файл horoscopes.xml и возвращает текст гороскопа для заданного знака.
    """
    try:
        tree = ET.parse('horoscopes.xml')
        root = tree.getroot()
        for horoscope in root.findall('horoscope'):
            if horoscope.get('zodiac') == zodiac:
                return horoscope.text.strip()
    except Exception as e:
        print("Ошибка чтения XML:", e)
    return "Гороскоп для вашего знака недоступен."

@bot.message_handler(commands=['start'])
def start_handler(message):
    # Создаем клавиатуру с кнопками для выбора знака зодиака
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for i, zodiac in enumerate(zodiac_list, start=1):
        row.append(types.KeyboardButton(zodiac))
        if i % 3 == 0:
            markup.row(*row)
            row = []
    if row:
        markup.row(*row)
    bot.send_message(message.chat.id, "Привет! Выбери свой знак зодиака:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in zodiac_list)
def zodiac_handler(message):
    zodiac = message.text
    button_counts[zodiac] += 1
    horoscope = get_horoscope_from_xml(zodiac)
    response = (f"Ваш знак зодиака: *{zodiac}*\n\n"
                f"Ваш гороскоп на сегодня:\n\"{horoscope}\"\n\n")
    # Создаем клавиатуру с опциями "Главное меню" и "Счётчик нажатий"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(types.KeyboardButton("Главное меню"), types.KeyboardButton("Счётчик нажатий"))
    bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Главное меню")
def main_menu_handler(message):
    # Возвращаем основную клавиатуру с выбором знаков зодиака
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for i, zodiac in enumerate(zodiac_list, start=1):
        row.append(types.KeyboardButton(zodiac))
        if i % 3 == 0:
            markup.row(*row)
            row = []
    if row:
        markup.row(*row)
    bot.send_message(message.chat.id, "Выбери свой знак зодиака:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Счётчик нажатий")
def counter_handler(message):
    # Выводим статистику нажатий для каждого знака
    stats = "\n".join([f"{zodiac}: {button_counts[zodiac]}" for zodiac in zodiac_list])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(types.KeyboardButton("Главное меню"))
    bot.send_message(message.chat.id, f"Счётчик нажатий:\n{stats}", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def default_handler(message):
    # Если введён текст не соответствует ожидаемым значениям, выводим подсказку
    if message.text not in zodiac_list and message.text not in ["/start", "Главное меню", "Счётчик нажатий"]:
        bot.send_message(message.chat.id, "Пожалуйста, выберите свой знак зодиака с помощью клавиатуры.")

bot.polling(none_stop=True)
