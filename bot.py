import telebot
import json
import os
import random

# 🔑 توکن رباتت
API_TOKEN = "7996298266:AAHhLDEFnCns9FNBav0_AMzfS-g9IUE9zEc"

# 📢 آیدی کانالت با @
CHANNEL_USERNAME = "@enzo_pubgm"

bot = telebot.TeleBot(API_TOKEN)

# بارگذاری یا ساخت دیتابیس
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

def get_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {"points": 1, "refs": 0}
    return users[str(user_id)]

def generate_ip(version="v4"):
    if version == "v4":
        return ".".join(str(random.randint(0, 255)) for _ in range(4))
    else:
        return ":".join(''.join(random.choices("0123456789abcdef", k=4)) for _ in range(8))

def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    args = message.text.split()
    user = get_user(uid)

    # ثبت زیرمجموعه
    if len(args) > 1:
        ref_id = args[1]
        if ref_id != str(uid) and ref_id in users:
            users[ref_id]["points"] += 1
            users[ref_id]["refs"] += 1

    if not is_member(uid):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(uid, "❗️اول عضو کانال شو و بعد /start رو بزن", reply_markup=markup)
        return

    save_users()
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📥 دریافت IP", callback_data="get_ip"))
    markup.add(telebot.types.InlineKeyboardButton("🔗 لینک دعوت من", callback_data="my_ref"))
    bot.send_message(uid, "به ربات خوش اومدی 👇 یکی از دکمه‌ها رو انتخاب کن:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    user = get_user(uid)

    if not is_member(uid):
        bot.answer_callback_query(call.id, "اول عضو کانال شو")
        return

    if call.data == "get_ip":
        if user["points"] <= 0:
            bot.send_message(uid, "❌ امتیاز نداری. با دعوت از دوستانت امتیاز بگیر.")
        else:
            ipv4 = generate_ip("v4")
            ipv6 = generate_ip("v6")
            user["points"] -= 1
            save_users()
            bot.send_message(uid, f"🌐 IP شما:\nIPv4: `{ipv4}`\nIPv6: `{ipv6}`", parse_mode="Markdown")

    elif call.data == "my_ref":
        ref_link = f"https://t.me/{bot.get_me().username}?start={uid}"
        msg = f"🔗 لینک دعوت شما:\n{ref_link}\n📊 زیرمجموعه‌ها: {user['refs']}\n🎁 امتیاز: {user['points']}"
        bot.send_message(uid, msg)

print("🤖 ربات روشنه...")
bot.infinity_polling()