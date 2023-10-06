from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
import random
import time

API_ID = '23601851'
API_HASH = '122209a9c58d40ab8947ed409cc49ecd'
BOT_TOKEN = '6547349199:AAEHYX6dD2R1kdS7lehxq0JzY7YLXhQuYuc'
MANAGEMENT_CHAT_ID = -1001893099740
GIVEAWAY_CHAT_ID = -1001862011009
ALLOWED_USER_IDS = [42094194, 1069032545]

participants = []
is_giveaway_active = False

app = Client("giveawayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def is_user_allowed(user_id):
    return user_id in ALLOWED_USER_IDS

@app.on_message(filters.command("start_giveaway") & filters.chat(MANAGEMENT_CHAT_ID))
def start_giveaway(client, message):
    global is_giveaway_active
    try:
        if not is_user_allowed(message.from_user.id):
            return
        if is_giveaway_active:
            app.send_message(MANAGEMENT_CHAT_ID, "يوجد سحب نشط حاليًا. يرجى إنهاء أو إلغاء السحب الحالي قبل بدء سحب جديد.")
            return

        is_giveaway_active = True
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("انضم الى السحب", callback_data="join_giveaway")]]
        )
        app.send_message(GIVEAWAY_CHAT_ID, "تم بدء سحب جديد! انقر على الزر أدناه للانضمام.", reply_markup=markup)
    except FloodWait as e:
        print(f"Rate limit exceeded. Please wait for {e.x} seconds.")
        time.sleep(e.x)

@app.on_callback_query(filters.regex("^join_giveaway$"))
def join_giveaway(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in participants:
        participants.append(user_id)
        callback_query.answer("لقد انضممت للسحب!")
    else:
        callback_query.answer("لقد انضممت بالفعل للسحب!")

@app.on_message(filters.command("list_participants") & filters.chat(MANAGEMENT_CHAT_ID))
def list_participants(client, message):
    if not is_user_allowed(message.from_user.id):
        return

    if not participants:
        app.send_message(MANAGEMENT_CHAT_ID, "لا يوجد مشاركين حتى الآن.")
        return

    participants_links = []
    for idx, user_id in enumerate(participants, 1):
        user = app.get_users(user_id)
        if user.username:
            user_link = f"@{user.username}"
        else:
            user_link = f"[{user.first_name}](tg://user?id={user_id})"
        participants_links.append(f"{idx}- {user_link}")

    app.send_message(MANAGEMENT_CHAT_ID, "\n".join(participants_links))

@app.on_message(filters.command("draw_winner") & filters.chat(MANAGEMENT_CHAT_ID))
def draw_winner(client, message):
    if not is_user_allowed(message.from_user.id):
        return

    if not participants:
        app.send_message(MANAGEMENT_CHAT_ID, "لا يوجد مشاركين للاختيار من بينهم.")
        return

    winner_id = random.choice(participants)
    winner = app.get_users(winner_id)
    winner_mention = f"[{winner.first_name}](tg://user?id={winner.id})"

    app.send_message(GIVEAWAY_CHAT_ID, f"مبروووكك 😍الفائز هو: {winner_mention}!")

@app.on_message(filters.command("cancel_giveaway") & filters.chat(MANAGEMENT_CHAT_ID))
def cancel_giveaway(client, message):
    global is_giveaway_active
    if not is_user_allowed(message.from_user.id):
        return
    if not is_giveaway_active:
        app.send_message(MANAGEMENT_CHAT_ID, "لا يوجد سحب نشط حاليًا لإلغائه.")
        return

    is_giveaway_active = False
    participants.clear()
    app.send_message(GIVEAWAY_CHAT_ID, "تم انهاء السحب.")

@app.on_message(filters.command("end_giveaway") & filters.chat(MANAGEMENT_CHAT_ID))
def end_giveaway(client, message):
    global is_giveaway_active
    if not is_user_allowed(message.from_user.id):
        return
    if not is_giveaway_active:
        app.send_message(MANAGEMENT_CHAT_ID, "لا يوجد سحب نشط حاليًا لإنهائه.")
        return

    is_giveaway_active = False
    app.send_message(GIVEAWAY_CHAT_ID, "تم اغلاق السحب")
    
if __name__ == '__main__':
    while True:
        try:
            app.run()
            break  # If successful, break out of the loop
        except FloodWait as e:
            print(f"Rate limit exceeded. Please wait for {e.seconds} seconds.")
            time.sleep(e.seconds)  # Wait for the required duration
