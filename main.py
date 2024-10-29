import json
import time
import telebot
from telebot import types
import requests
import detectlanguage
from flask import Flask, request
import logging
from config import DETECT_LANG_API_KEY, TEXT_TO_SPEECH_API_URL,BOT_TOKEN

detectlanguage.configuration.secure = True


class TextToSpeechApi:
    def __init__(self):
        self.detectlanguage = detectlanguage
        self.detectlanguage.configuration.api_key = DETECT_LANG_API_KEY
        self.detectlanguage.configuration.secure = True

    def detect_language(self, text):
        return self.detectlanguage.simple_detect(text)
    
    def text_to_speech(self, text, filename):
        url = TEXT_TO_SPEECH_API_URL
        lang = self.detect_language(text)
        params = {
            "text": text,
            "lang": lang
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            audio_file = f"./voices/{filename}.mp3"
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            return audio_file  # Return the file path
        else:
            raise Exception(f"API Error: {response.status_code}")


logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')    



# Initialize the bot with your token
bot = telebot.TeleBot(BOT_TOKEN)
WEBHOOK_URL = 'https://telebots.alwaysdata.net/text2speech/webhook'
CHAT_ID = 848696652
app = Flask(__name__)


def store_user_data(user_id, username):
    try:
        with open('user_data.json', 'r') as file:
            for line in file:
                user = json.loads(line)
                if user['user_id'] == user_id:
                    return True
                    
        with open('user_data.json', 'a') as file:
            json.dump({'user_id': user_id, 'username': username}, file)
            file.write('\n')
        return True
    except FileNotFoundError:
        with open('user_data.json', 'w') as file:
            json.dump({'user_id': user_id, 'username': username}, file)
            file.write('\n')
        return True


@bot.message_handler(commands=['start'])
def start(message):
    
    logging.info(f"User {message.from_user.username}- {message.from_user.id} started the bot")
    keyboard = types.InlineKeyboardMarkup()
    help = types.InlineKeyboardButton("🆘 Help", callback_data='help')
    about = types.InlineKeyboardButton("👥 About", callback_data='about')
    keyboard.add(help, about)
    channel = types.InlineKeyboardButton("👥 Channel", url='https://t.me/tegegndev')
    keyboard.add(channel)
    developer = types.InlineKeyboardButton("👨‍💻 Developer", url='https://t.me/yegna_tv')
    keyboard.add(developer)
    #store_user_data(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, "👋Welcome to Text-to-Speech Bot! 🎙️\n\n"
                     "I can convert any text you send me into speech. 🗣️\n\n"
                     "Just send me some text and I'll convert it to audio for you! 🔊\n\n"
                     , reply_markup=keyboard)
    try:
        store_user_data(message.from_user.id, message.from_user.username)
    except Exception as e:
        logging.error(f"User {message.from_user.username}- {message.from_user.id} has encountered an error {e}")




#handle all user messages
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.text and not message.text.startswith('/'):
        if len(message.text) > 1000:
            bot.send_message(message.chat.id, "Please send a text less than 1000 characters")
            logging.info(f"User {message.from_user.username}- {message.from_user.id} sent a text longer than 1000 characters")
        else:
            process_text(message)
    else:
        bot.send_message(message.chat.id, "Please send a text message")

# Callback function to handle language selection
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'help':
        logging.info(f"User {call.from_user.username}- {call.from_user.id} requested help")
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Text-to-Speech Bot! 🎙️\n\n"
                     "I can convert any text you send me into speech. 🗣️\n\n"
                     "Just send me some text and I'll convert it to audio for you! 🔊\n\n"
                     "if you want to suggest a feature or report a bug, please contact @yegna_tv")
    elif call.data == 'about':
        logging.info(f"User {call.from_user.username}- {call.from_user.id} requested about")
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        channel = types.InlineKeyboardButton("👥 Channel", url='https://t.me/tegegndev')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(channel)
        bot.send_message(call.message.chat.id, "This bot is developed by @yegna_tv. \nJoin channel to get updates about the bot.", reply_markup=keyboard)

def process_text(message):
    user_id = message.chat.id
    try:
        logging.info(f"User {message.from_user.username}- {message.from_user.id} is processing their text {message.text}")
        msg = bot.send_message(user_id, "processing your text...")
        api = TextToSpeechApi()
        bot.delete_message(user_id, msg.message_id)
        msg = bot.send_message(user_id, "detecting language...")
        lang = detect_language(message.text)
        bot.delete_message(user_id, msg.message_id)
        msg = bot.send_message(user_id, f"language detected: {lang}..")
        api.text_to_speech(message.text, user_id)
        with open(f"./voices/{user_id}.mp3", "rb") as audio:
            bot.send_audio(message.chat.id, audio)
        bot.delete_message(user_id, msg.message_id)
        logging.info(f"User {message.from_user.username}- {message.from_user.id} has received their audio")
    except Exception as e:
        logging.error(f"User {message.from_user.username}- {message.from_user.id} has encountered an error {e}")
        bot.send_message(message.chat.id, f"Sorry, an error occurred: {str(e)}")


def detect_language(text):
    result = detectlanguage.simple_detect(text)
    return result

def text_to_speech(text, lang):
    url = TEXT_TO_SPEECH_API_URL
    params = {
        "text": text,
        "lang": lang
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        audio_file = f"output_{lang}.mp3"
        with open(audio_file, 'wb') as f:
            f.write(response.content)
        return audio_file
    else:
        raise Exception(f"API Error: {response.status_code}")



# Webhook endpoint to handle incoming updates
@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return '', 200


# Homepage route
@app.route('/')
def home():
    return "Welcome to the TeleBot Flask app!", 200

# Set the webhook
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    if bot.set_webhook(WEBHOOK_URL):
        return "Webhook set successfully!", 200
    else:
        return "Failed to set webhook.", 400
    

   



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)