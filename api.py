import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

VK_ACCESS_TOKEN = "vk1.a.Mlc5bXSun4Kw2wOgwiEakFJYquXmcfAGN1y4AzdWQAwv7GQXuUtWZ7joFM54I5ZRR4tfcUYGCC9uPht2nsUfFz7pdWPbc_J0DSvFD3O-L-pzTgZcmPMPJs-U6LN7jWrytR3KrfIR2EyET1AgmQ6vidJiINfwZPY1AhMSCvnZLTUMutP6DWWkqMZ4bnbRFFiLs7NBqAjZciMCwIy7sLmCbQ"
VK_API_VERSION = "5.131"

def set_vk_status(text: str) -> dict:
    """
    Функция для установки статуса во ВКонтакте.
    
    Согласно методичке, отправляем GET-запрос к методу status.set с параметрами:
    - access_token
    - text (текст статуса)
    - v (версия API)
    """
    url = "https://api.vk.com/method/status.set"
    params = {
        "access_token": VK_ACCESS_TOKEN,
        "text": text,
        "v": VK_API_VERSION
    }
    response = requests.get(url, params=params)
    return response.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с предложением ввести новый статус.
    """
    await update.message.reply_text("Привет! Напиши новый статус для ВК")

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовых сообщений.
    Получает текст от пользователя и устанавливает его как статус во ВКонтакте.
    """
    user_status = update.message.text
    result = set_vk_status(user_status)
    
    # Проверяем наличие ошибок в ответе от API ВКонтакте
    if "error" in result:
        await update.message.reply_text("Произошла ошибка при установке статуса во ВК.")
    else:
        await update.message.reply_text("Статус успешно установлен!")

if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    
    # Токен вашего Telegram-бота (из вашего сообщения)
    TELEGRAM_BOT_TOKEN = "7692417878:AAFlX9tt2YfHQsvfZCpk-e4PGtp4mOM640M"
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_status))
    
    app.run_polling()
