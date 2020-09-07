import configparser as cfg
import json
import logging
import requests

from timetable import Semester
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove


def get_token(config):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', 'token')


TOKEN = get_token("config.ini")
getTime = "http://worldtimeapi.org/api/timezone/Asia/Kolkata"
subjects = Semester.get_subjects()
tt = Semester.get_timetable()
timings = ['10-11: ', '11-12: ', '12-01: ', '02-03: ', '03-04: ']


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def day_of_week():
    day = get_json_from_url(getTime)
    return day["day_of_week"]


def curr_time():
    day = get_json_from_url(getTime)
    time = day['datetime']
    t = int(time[11:13])
    return t


def class_no(t):
    global cn
    if t < 10:
        cn = 0
    elif 10 <= t <= 15:
        for i in range(10, 16):
            if t == i:
                cn = i - 9
    else:
        cn = 7
    return cn


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def start(update, context):
    kbd_layout = [["/timetable", "/tomorrow"],
                  ['/currentclass', '/nextclass'],
                  ['/close']]
    kbd = ReplyKeyboardMarkup(kbd_layout, resize_keyboard=True)
    update.message.reply_text(
        text="Select option:\n"
             "1. /timetable      - for today's classes\n"
             "2. /tomorrow     - for tomorrow classes\n"
             "3. /currentclass - for current live class\n"
             "4. /nextclass       - for next class\n"
             "5. /close               - to switch back to typing",
        reply_markup=kbd
    )


def close(update, context):
    reply_markup = ReplyKeyboardRemove()
    update.message.reply_text(text="Ok! Send commands by typing.", reply_markup=reply_markup)
    pass


def timetable(update, context):
    today = day_of_week()
    button_list = []
    if today == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No Class today. Enjoy : )")
        return
    tt_ = tt[today - 1]
    for i, each in enumerate(tt_):
        button_list.append(InlineKeyboardButton(timings[i]+'  '+each[0], url=each[1]))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Today's Timetable:",
                             reply_markup=reply_markup)


def tomorrow(update, context):
    today = day_of_week()
    button_list = []
    if today == 6:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No Class tomorrow   ; )")
        return
    tt_ = tt[today]
    for i, each in enumerate(tt_):
        button_list.append(InlineKeyboardButton(timings[i]+'  '+each[0], url=each[1]))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Tomorrow's Timetable:",
        reply_markup=reply_markup
    )


def currentclass(update, context):
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    button_list = []
    if today == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No Class today. Enjoy : )")
        return
    elif c == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No class live. Classes will start at 10AM.")
        return
    elif 1 <= c <= 3:
        tt_ = tt[today-1][c-1]
        button_list.append(InlineKeyboardButton(timings[c-1] + '  ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Current Class:",
            reply_markup=reply_markup
        )
        return
    elif c == 4:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Lunch Time"
        )
        return
    elif 5 <= c <= 6:
        tt_ = tt[today - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + '  ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Current Class:",
            reply_markup=reply_markup
        )
        return
    elif c == 7 and today != 6:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Classes over. See you tomorrow : )"
        )
        return
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Classes over. See you on Monday."
        )


def nextclass(update, context):
    today = day_of_week()
    c = curr_time()
    c = class_no(c) + 1
    button_list = []
    if today == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No Class today. Enjoy : )")
        return
    elif 1 <= c <= 3:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + '  ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Next Class:",
            reply_markup=reply_markup
        )
        return
    elif c == 4:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No next class. Lunch time."
        )
        return
    elif 5 <= c <= 6:
        tt_ = tt[today - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + '  ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Next Class:",
            reply_markup=reply_markup
        )
        return
    elif 7 <= c <=8 and today != 6:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No next class. See you tomorrow : )"
        )
        return
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No next class. See you on Monday."
        )


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('timetable', timetable))
    dispatcher.add_handler(CommandHandler('tomorrow', tomorrow))
    dispatcher.add_handler(CommandHandler('currentclass', currentclass))
    dispatcher.add_handler(CommandHandler('nextclass', nextclass))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("close", close))
    dispatcher.add_handler(CommandHandler("help", start))
    updater.start_polling()


if __name__ == '__main__':
    main()
