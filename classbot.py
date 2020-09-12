import configparser as cfg
import logging

import telegram
from semester import Semester, timings, class_no
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Updater, ConversationHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from Time import day_of_week, curr_time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

FIRST, SECOND, THIRD, FOURTH, FIFTH = range(5)
ONE, TWO, THREE, FOUR, FIVE = range(5)


def get_token(config):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', 'token')


TOKEN = get_token("config.ini")
tt = Semester.get_timetable()
bot = telegram.Bot(token=TOKEN)


# def edit_message(update, context, query, text, reply_markup)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Today Timetable", callback_data=str(ONE)),
            InlineKeyboardButton("Tomorrow Timetable", callback_data=str(TWO))
        ],
        [
            InlineKeyboardButton("Current Class", callback_data=str(THREE)),
            InlineKeyboardButton("Next Class", callback_data=str(FOUR))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.message.from_user['id'],
        text="Select option:",
        reply_markup=reply_markup
    )
    return FIRST


def start_over(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Today Timetable", callback_data=str(ONE)),
            InlineKeyboardButton("Tomorrow Timetable", callback_data=str(TWO))
        ],
        [
            InlineKeyboardButton("Current Class", callback_data=str(THREE)),
            InlineKeyboardButton("Next Class", callback_data=str(FOUR))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Select option:",
        reply_markup=reply_markup
    )
    return FIRST


def one(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    button_list = []
    if today == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="No Class today. Enjoy : )", reply_markup=reply_markup)
        return FIRST
    tt_ = tt[today - 1]
    
    for i, each in enumerate(tt_):
        button_list.append(InlineKeyboardButton(timings[i] + ' ' + each[0], url=each[1]))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3,
                                                   footer_buttons=[
                                                       InlineKeyboardButton("Close", callback_data=str(FIVE))]))
    query.edit_message_text(
        text="Today's Timetable:",
        reply_markup=reply_markup
    )
    return FIRST


def two(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    button_list = []
    if today == 6:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="No Class tomorrow   ; )", reply_markup=reply_markup)
        return FIRST
    tt_ = tt[today]
    for i, each in enumerate(tt_):
        button_list.append(InlineKeyboardButton(timings[i] + ' ' + each[0], url=each[1]))
    reply_markup = InlineKeyboardMarkup(
        build_menu(button_list, n_cols=3, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
    query.edit_message_text(
        text="Tomorrow's Timetable:",
        reply_markup=reply_markup
    )
    return FIRST


def three(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    button_list = []
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="No Class today. Enjoy : )", reply_markup=reply_markup)
    elif c == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="No class live. Classes will start at 10AM.", reply_markup=reply_markup)
    elif 1 <= c <= 3:
        tt_ = tt[c - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="Current Class:",
            reply_markup=reply_markup
        )
    elif c == 4:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Lunch Time", reply_markup=reply_markup
        )
    elif 5 <= c <= 6:
        tt_ = tt[c - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="Current Class:",
            reply_markup=reply_markup
        )
    elif c == 7 and today != 6:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Classes over. See you tomorrow : )", reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Classes over. See you on Monday.", reply_markup=reply_markup
        )
    return FIRST


def four(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    if c != 7:
        c += 1
    button_list = []
    if today == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="No Class today. Enjoy : )", reply_markup=reply_markup)
    elif c == 1:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="Next Class at 10AM:",
            reply_markup=reply_markup
        )
    elif 2 <= c <= 3:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="Next Class:",
            reply_markup=reply_markup
        )
    elif c == 4:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="Next Class at 2PM:",
            reply_markup=reply_markup
        )
    elif 5 <= c <= 6:
        tt_ = tt[today - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="Next Class:",
            reply_markup=reply_markup
        )
    elif c == 7 and today != 6:
        tt_ = tt[today][0]
        button_list.append(InlineKeyboardButton(timings[0] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="No next class today. Next Class tomorrow at 10AM:",
            reply_markup=reply_markup
        )
    else:
        tt_ = tt[1][0]
        button_list.append(InlineKeyboardButton(timings[0] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))]))
        query.edit_message_text(
            text="No next class today. Next Class on Monday at 10AM:",
            reply_markup=reply_markup
        )
    return FIRST


def timetable(update, context):
    today = day_of_week()
    button_list = []
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(ONE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.from_user['id'], text="No Class today. Enjoy : )",
                                 reply_markup=reply_markup)
    else:
        tt_ = tt[today - 1]
        for i, each in enumerate(tt_):
            button_list.append(InlineKeyboardButton(timings[i] + ' ' + each[0], url=each[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=3, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(ONE))]))
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Today's Timetable:",
            reply_markup=reply_markup
        )
    bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message['message_id'])
    return SECOND


def timetable_update(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    button_list = []
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(ONE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="No Class today. Enjoy : )", reply_markup=reply_markup)
        except:
            print("Timetable Updated without change")
    else:
        tt_ = tt[today - 1]
        
        for i, each in enumerate(tt_):
            button_list.append(InlineKeyboardButton(timings[i] + ' ' + each[0], url=each[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3,
                                                       footer_buttons=[
                                                           InlineKeyboardButton("Update", callback_data=str(ONE))]))
        try:
            query.edit_message_text(
                text="Today's Timetable:",
                reply_markup=reply_markup
            )
        except:
            print("Timetable Updated without change")
    return SECOND


def tomorrow(update, context):
    today = day_of_week()
    button_list = []
    if today == 6:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(TWO))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.from_user['id'], text="No Class tomorrow   ; )",
                                 reply_markup=reply_markup)
    else:
        tt_ = tt[today]
        for i, each in enumerate(tt_):
            button_list.append(InlineKeyboardButton(timings[i] + ' ' + each[0], url=each[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=3, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(TWO))]))
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Tomorrow's Timetable:",
            reply_markup=reply_markup
        )
    bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message['message_id'])
    return SECOND


def tomorrow_update(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    button_list = []
    if today == 6:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(TWO))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="No Class tomorrow   ; )", reply_markup=reply_markup)
        except:
            print("Tomorrow updated without change")
    else:
        tt_ = tt[today]
        for i, each in enumerate(tt_):
            button_list.append(InlineKeyboardButton(timings[i] + ' ' + each[0], url=each[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=3, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(TWO))]))
        try:
            query.edit_message_text(
                text="Tomorrow's Timetable:",
                reply_markup=reply_markup
            )
        except:
            print("Tomorrow updated without change")
    return SECOND


def currentclass(update, context):
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    button_list = []
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.from_user['id'], text="No Class today. Enjoy : )",
                                 reply_markup=reply_markup)
    elif c == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.from_user['id'],
                                 text="No class live. Classes will start at 10AM.",
                                 reply_markup=reply_markup)
    elif 1 <= c <= 3:
        tt_ = tt[c - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1, footer_buttons=[
            InlineKeyboardButton("Update", callback_data=str(THREE))]))
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Current Class:",
            reply_markup=reply_markup
        )
    elif c == 4:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Lunch Time",
            reply_markup=reply_markup
        )
    elif 5 <= c <= 6:
        tt_ = tt[c - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1, footer_buttons=[
            InlineKeyboardButton("Update", callback_data=str(THREE))]))
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Current Class:",
            reply_markup=reply_markup
        )
    elif c == 7 and today != 6:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Classes over. See you tomorrow : )",
            reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(
            chat_id=update.message.from_user['id'],
            text="Classes over. See you on Monday.",
            reply_markup=reply_markup
        )
    bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message['message_id'])
    return SECOND


def currentclass_update(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    button_list = []
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="No Class today. Enjoy : )", reply_markup=reply_markup)
        except:
            print("Currentclass updated without change")
    elif c == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="No class live. Classes will start at 10AM.", reply_markup=reply_markup)
        except:
            print("Currentclass updated without change")
    elif 1 <= c <= 3:
        tt_ = tt[c - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1,
                       footer_buttons=[InlineKeyboardButton("Update", callback_data=str(THREE))]))
        try:
            query.edit_message_text(
                text="Current Class:",
                reply_markup=reply_markup
            )
        except:
            print("Currentclass updated without change")
    elif c == 4:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(
                text="Lunch Time", reply_markup=reply_markup
            )
        except:
            print("Currentclass updated without change")
    elif 5 <= c <= 6:
        tt_ = tt[c - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1,
                       footer_buttons=[InlineKeyboardButton("Update", callback_data=str(THREE))]))
        try:
            query.edit_message_text(
                text="Current Class:",
                reply_markup=reply_markup
            )
        except:
            print("Currentclass updated without change")
    elif c == 7 and today != 6:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(
                text="Classes over. See you tomorrow : )", reply_markup=reply_markup
            )
        except:
            print("Currentclass updated without change")
    else:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(THREE))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(
                text="Classes over. See you on Monday.", reply_markup=reply_markup
            )
        except:
            print("Currentclass updated without change")
    return SECOND


def nextclass(update, context):
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    if c != 7:
        c += 1
    button_list = []
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(FOUR))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="No Class today. Enjoy : )",
                                 reply_markup=reply_markup)
    elif c == 1:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Next Class at 10AM:",
            reply_markup=reply_markup
        )
    elif 2 <= c <= 3:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Next Class:",
            reply_markup=reply_markup
        )
    elif c == 4:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Next Class at 2PM:",
            reply_markup=reply_markup
        )
    elif 5 <= c <= 6:
        tt_ = tt[today - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Next Class:",
            reply_markup=reply_markup
        )
    elif c == 7 and today != 6:
        tt_ = tt[today][0]
        button_list.append(InlineKeyboardButton(timings[0] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No next class today. Next Class tomorrow at 10AM:",
            reply_markup=reply_markup
        )
    else:
        tt_ = tt[1][0]
        button_list.append(InlineKeyboardButton(timings[0] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="No next class today. Next Class on Monday at 10AM:",
            reply_markup=reply_markup
        )
    bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message['message_id'])
    return SECOND


def nextclass_update(update, context):
    query = update.callback_query
    query.answer()
    today = day_of_week()
    c = curr_time()
    c = class_no(c)
    if c != 7:
        c += 1
    button_list = []
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(FOUR))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            query.edit_message_text(text="No Class today. Enjoy : )", reply_markup=reply_markup)
        except:
            print("Nextclass updated without change")
    elif c == 1:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        try:
            query.edit_message_text(
                text="Next Class at 10AM:",
                reply_markup=reply_markup
            )
        except:
            print("Nextclass updated without change")
    elif 2 <= c <= 3:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        try:
            query.edit_message_text(
                text="Next Class:",
                reply_markup=reply_markup
            )
        except:
            print("Nextclass updated without change")
    elif c == 4:
        tt_ = tt[today - 1][c - 1]
        button_list.append(InlineKeyboardButton(timings[c - 1] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        try:
            query.edit_message_text(
                text="Next Class at 2PM:",
                reply_markup=reply_markup
            )
        except:
            print("Nextclass updated without change")
    elif 5 <= c <= 6:
        tt_ = tt[today - 1][c - 2]
        button_list.append(InlineKeyboardButton(timings[c - 2] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        try:
            query.edit_message_text(
                text="Next Class:",
                reply_markup=reply_markup
            )
        except:
            print("Nextclass updated without change")
    elif c == 7 and today != 6:
        tt_ = tt[today][0]
        button_list.append(InlineKeyboardButton(timings[0] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        try:
            query.edit_message_text(
                text="No next class today. Next Class tomorrow at 10AM:",
                reply_markup=reply_markup
            )
        except:
            print("Nextclass updated without change")
    else:
        tt_ = tt[1][0]
        button_list.append(InlineKeyboardButton(timings[0] + ' ' + tt_[0], url=tt_[1]))
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(FOUR))]))
        try:
            query.edit_message_text(
                text="No next class today. Next Class on Monday at 10AM:",
                reply_markup=reply_markup
            )
        except:
            print("Nextclass updated without change")
    return SECOND


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('help', start),
                      CommandHandler('timetable', timetable),
                      CommandHandler('tomorrow', tomorrow),
                      CommandHandler('currentclass', currentclass),
                      CommandHandler('nextclass', nextclass)
                      ],
        states={
            FIRST: [CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                    CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                    CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                    CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                    CallbackQueryHandler(start_over, pattern='^' + str(FIVE) + '$')
                    ],
            SECOND: [CallbackQueryHandler(timetable_update, pattern='^' + str(ONE) + '$'),
                     CallbackQueryHandler(tomorrow_update, pattern='^' + str(TWO) + '$'),
                     CallbackQueryHandler(currentclass_update, pattern='^' + str(THREE) + '$'),
                     CallbackQueryHandler(nextclass_update, pattern='^' + str(FOUR) + '$')
                     ]
        },
        fallbacks=[CommandHandler('start', start),
                   CommandHandler('help', start),
                   CommandHandler('timetable', timetable),
                   CommandHandler('tomorrow', tomorrow),
                   CommandHandler('currentclass', currentclass),
                   CommandHandler('nextclass', nextclass)]
    )
    
    # timetable_handler = ConversationHandler(
    #     entry_points=[CommandHandler('timetable', timetable)],
    #     states={
    #         FIRST: [CallbackQueryHandler(timetable_update, pattern='^' + str(UPDATE) + '$')]
    #     },
    #     fallbacks=[CommandHandler('timetable', timetable)]
    # )
    # tomorrow_handler = ConversationHandler(
    #     entry_points=[CommandHandler('tomorrow', tomorrow)],
    #     states={
    #         FIRST: [CallbackQueryHandler(tomorrow_update, pattern='^' + str(UPDATE) + '$')]
    #     },
    #     fallbacks=[CommandHandler('tomorrow', tomorrow)]
    # )
    # all_msgs =
    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(timetable_handler)
    # dispatcher.add_handler(tomorrow_handler)
    # dispatcher.add_handler(CommandHandler('timetable', timetable))
    # dispatcher.add_handler(CommandHandler('tomorrow', tomorrow))
    # dispatcher.add_handler(CommandHandler('currentclass', currentclass))
    # dispatcher.add_handler(CommandHandler('nextclass', nextclass))
    updater.start_polling()


if __name__ == '__main__':
    main()
