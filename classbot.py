import configparser as cfg
import logging
import warnings
from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import error, Message as Mes
from telegram.ext import CommandHandler, Updater, ConversationHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.update import Update
from Time import day_of_week, date, curr_time
from semester import Semester, timings, class_no


def build_menu(tt, c=0, n=3, header_buttons=None, footer_buttons=None):
    button_list = []
    if c == 0:
        for key, value in tt.items():
            button_list.append(InlineKeyboardButton(timings[key] + ' ' + value[0], url=value[1]))
    elif 1 <= c <= 3 or 5 <= c <= 6:
        button_list.append(InlineKeyboardButton(timings[c] + ' ' + tt[0], url=tt[1]))
    buttons = button_list
    menu = [buttons[i:i + n] for i in range(0, len(buttons), n)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_token(config):
    parser = cfg.ConfigParser()
    parser.read(config)
    return parser.get('creds', 'token')


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
FIRST = 0
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE = range(9)
TOKEN = get_token("config.ini")
warnings.filterwarnings("ignore")


class Message:
    u_m: int = None
    b_m: int = None
    u_m_c: int = None
    b_m_c: int = None


class Messages:
    messages: List[Message]
    
    def __init__(self, message_type):
        self.messages = []
        self.message_type = message_type
    
    def insert(self, message: Message):
        self.messages.append(message)
    
    def remove(self, context: CallbackContext):
        if len(self.messages) > 1:
            context.bot.delete_message(self.messages[0].b_m_c, self.messages[0].b_m)
            context.bot.delete_message(self.messages[0].u_m_c, self.messages[0].u_m)
            self.messages.pop(0)


class Global:
    messages = {
        'error': Messages('error'),
        'start': Messages('start'),
        'timetable': Messages('timetable'),
        'tomorrow': Messages('tomorrow'),
        'current': Messages('current'),
        'next': Messages('next')
    }
    cmd = 'error'
    update: Update = None
    context: CallbackContext = None
    query = None
    tt = {}
    
    def get_string_dict(self):
        if self.cmd == 'start':
            s = "Select option:"
            return s
        elif self.cmd == 'timetable':
            s = {1: "No Class today. Enjoy : )", 2: "Today's Timetable:"}
            return s
        elif self.cmd == 'tomorrow':
            s = {1: "No Class tomorrow   ; )", 2: "Tomorrow's Timetable:"}
            return s
        elif self.cmd == 'current':
            s = {1: "No Class today. Enjoy : )", 2: "No class live. Classes will start at 10AM.", 3: "Current Class:",
                 4: "Lunch Time", 5: "Current Class:", 6: "Classes over. See you tomorrow : )",
                 7: "Classes over. See you on Monday."}
            return s
        elif self.cmd == 'next':
            s = {1: "No Class today. Enjoy : )", 2: "Next Class at 10AM:", 3: "Next Class:", 4: "Next Class at 2PM:",
                 5: "Next Class:", 6: "No next class today"}
            return s
    
    def set(self, update: Update, context: CallbackContext, cmd='error', query=False):
        self.update = update
        self.context = context
        self.cmd = cmd
        if self.tt != Semester.get_timetable():
            self.tt = Semester.get_timetable()
        today, noc = day_of_week()
        c = class_no(curr_time())
        s = self.get_string_dict()
        if noc < 5:
            n_cols = 2
        else:
            n_cols = 3
        
        if query is True:
            self.query = self.update.callback_query
            self.query.answer()
        
        if self.cmd == 'start':
            return s
        elif self.cmd == 'timetable' or self.cmd == 'tomorrow':
            return today, s, n_cols
        elif self.cmd == 'current' or self.cmd == 'next':
            return today, c, s
    
    def make_message(self, b_m: Mes):
        m = Message()
        m.u_m_c = self.update.message.chat.id
        m.u_m = self.update.message.message_id
        m.b_m = b_m.message_id
        m.b_m_c = b_m.chat.id
        return m
    
    def anti_spam(self):
        for i in self.messages.values():
            i.remove(self.context)
    
    def updated(self):
        first_name = self.update.callback_query.from_user.first_name
        last_name = self.update.callback_query.from_user.last_name
        if last_name is None:
            last_name = '\b'
        if self.cmd == 'current':
            command = 'Current Class'
        elif self.cmd == 'next':
            command = 'Next Class'
        else:
            command = self.cmd.capitalize()
        print(command, "updated without change -", first_name, last_name, f"- {date()}")
    
    def send(self, text, keyboard=None, to_user=False):
        
        if keyboard is not None:
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None
        
        if to_user is False:
            chat_id = self.update.effective_chat.id
            t = self.context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                reply_to_message_id=self.update.message.message_id
            )
            if self.update.message.chat.type != 'private':
                self.messages[self.cmd].insert(self.make_message(t))
                self.anti_spam()
        else:
            chat_id = self.update.message.from_user.id
            try:
                self.context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup
                )
                if self.update.message.chat.type == 'supergroup':
                    t = self.context.bot.send_message(
                        chat_id=self.update.effective_chat.id,
                        text=f'Click on @{self.context.bot.username} to go to PM',
                        reply_to_message_id=self.update.message.message_id
                    )
                    self.messages[self.cmd].insert(self.make_message(t))
                    self.anti_spam()
            except error.Unauthorized:
                self.cmd = 'error'
                m = self.context.bot.send_message(
                    chat_id=self.update.effective_chat.id,
                    text=f"You have not initiated conversation with me.\n"
                         f"Click on @{self.context.bot.username} and click on button at bottom.",
                    reply_to_message_id=self.update.message.message_id
                )
                self.messages[self.cmd].insert(self.make_message(m))
                self.anti_spam()
    
    def edit(self, text, keyboard):
        if keyboard is None:
            reply_markup = None
        else:
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            self.query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
        except error.BadRequest:
            self.updated()


B = Global()


def start(update: Update, context: CallbackContext):
    s = B.set(update, context, 'start')
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
    B.send(s, keyboard)
    
    return FIRST


def start_over(update: Update, context: CallbackContext):
    s = B.set(update, context, 'start', query=True)
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
    B.edit(s, keyboard)
    
    return FIRST


def one(update, context):
    today, s, n = B.set(update, context, 'timetable', True)
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        B.edit(s[1], keyboard)
    else:
        tt = B.tt[today]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
        B.edit(s[2], keyboard)
    
    return FIRST


def two(update, context):
    today, s, n = B.set(update, context, 'tomorrow', True)
    
    if today != 6:
        tom = today + 1
    else:
        tom = 0
    
    if tom == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        B.edit(s[1], keyboard)
    else:
        tt = B.tt[tom]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
        B.edit(s[2], keyboard)
    
    return FIRST


def three(update, context):
    today, c, s = B.set(update, context, 'current', True)
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        B.edit(s[1], keyboard)
    else:
        if c == 0:
            keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
            B.edit(s[2], keyboard)
        elif 1 <= c <= 3:
            tt = B.tt[today][c]
            keyboard = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
            B.edit(s[3], keyboard)
        elif c == 4:
            keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
            B.edit(s[4], keyboard)
        elif 5 <= c <= 6:
            tt = B.tt[today][c]
            keyboard = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
            B.edit(s[5], keyboard)
        elif c == 7 and today != 6:
            keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
            B.edit(s[6], keyboard)
        else:
            keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
            B.edit(s[7], keyboard)
    
    return FIRST


def four(update, context):
    today, c, s = B.set(update, context, 'next', True)
    
    if c != 7:
        nc = c + 1
    else:
        nc = c
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
        B.edit(s[1], keyboard)
    else:
        if nc == 1:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
            B.edit(s[2], keyboard)
        elif 2 <= nc <= 3:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
            B.edit(s[3], keyboard)
        elif nc == 4:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
            B.edit(s[4], keyboard)
        elif 5 <= nc <= 6:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
            B.edit(s[5], keyboard)
        elif nc == 7:
            keyboard = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
            B.edit(s[6], keyboard)
    
    return FIRST


def timetable(update, context):
    today, s, n = B.set(update, context, 'timetable')
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(SIX))]]
        B.send(s[1], keyboard)
    else:
        tt = B.tt[today]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SIX))])
        B.send(s[2], keyboard)
    
    return FIRST


def timetable_update(update, context):
    today, s, n = B.set(update, context, 'timetable', True)
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(SIX))]]
        B.edit(s[1], keyboard)
    else:
        tt = B.tt[today]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SIX))])
        B.edit(s[2], keyboard)
    
    return FIRST


def tomorrow(update, context):
    today, s, n = B.set(update, context, 'tomorrow')
    
    if today != 6:
        tom: int = today + 1
    else:
        tom: int = 0
    
    if tom == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(SEVEN))]]
        B.send(s[1], keyboard)
    else:
        tt = B.tt[tom]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SEVEN))])
        B.send(s[2], keyboard)
    
    return FIRST


def tomorrow_update(update, context):
    today, s, n = B.set(update, context, 'tomorrow', True)
    
    if today != 6:
        tom: int = today + 1
    else:
        tom: int = 0
    
    if tom == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(SEVEN))]]
        B.edit(s[1], keyboard)
    else:
        tt = B.tt[tom]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SEVEN))])
        B.edit(s[2], keyboard)
    
    return FIRST


def current_class(update, context):
    today, c, s = B.set(update, context, 'current')
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
        B.send(s[1], keyboard)
    else:
        if c == 0:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.send(s[2], keyboard)
        elif 1 <= c <= 3:
            tt = B.tt[today][c]
            keyboard = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(EIGHT))])
            B.send(s[3], keyboard)
        elif c == 4:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.send(s[4], keyboard)
        elif 5 <= c <= 6:
            tt = B.tt[today][c]
            keyboard = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(EIGHT))])
            B.send(s[5], keyboard)
        elif c == 7 and today != 6:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.send(s[6], keyboard)
        else:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.send(s[7], keyboard)
    
    return FIRST


def current_class_update(update, context):
    today, c, s = B.set(update, context, 'current', True)
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
        B.edit(s[1], keyboard)
    else:
        if c == 0:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.edit(s[2], keyboard)
        elif 1 <= c <= 3:
            tt = B.tt[today][c]
            keyboard = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(EIGHT))])
            B.edit(s[3], keyboard)
        elif c == 4:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.edit(s[4], keyboard)
        elif 5 <= c <= 6:
            tt = B.tt[today][c]
            keyboard = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(EIGHT))])
            B.edit(s[5], keyboard)
        elif c == 7 and today != 6:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.edit(s[6], keyboard)
        else:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
            B.edit(s[7], keyboard)
    
    return FIRST


def next_class(update, context):
    today, c, s = B.set(update, context, 'next')
    
    if c != 7:
        nc = c + 1
    else:
        nc = c
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(NINE))]]
        B.send(s[1], keyboard)
    else:
        if nc == 1:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.send(s[2], keyboard)
        elif 2 <= nc <= 3:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.send(s[3], keyboard)
        elif nc == 4:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.send(s[4], keyboard)
        elif 5 <= nc <= 6:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.send(s[5], keyboard)
        elif nc == 7:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(NINE))]]
            B.send(s[6], keyboard)
    
    return FIRST


def next_class_update(update, context):
    today, c, s = B.set(update, context, 'next', True)
    
    if c != 7:
        nc = c + 1
    else:
        nc = c
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(NINE))]]
        B.edit(s[1], keyboard)
    else:
        if nc == 1:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.edit(s[2], keyboard)
        elif 2 <= nc <= 3:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.edit(s[3], keyboard)
        elif nc == 4:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.edit(s[4], keyboard)
        elif 5 <= nc <= 6:
            tt = B.tt[today][nc]
            keyboard = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
            B.edit(s[5], keyboard)
        elif nc == 7:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(NINE))]]
            B.edit(s[6], keyboard)
    
    return FIRST


def cancel(update, context):
    return ConversationHandler.END


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    start_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('help', start)
        ],
        states={
            FIRST: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(timetable_update, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(tomorrow_update, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(current_class_update, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(next_class_update, pattern='^' + str(NINE) + '$')
            ]
        },
        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('help', start),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        per_user=False
    )
    
    timetable_handler = ConversationHandler(
        entry_points=[CommandHandler('timetable', timetable)],
        states={
            FIRST: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(timetable_update, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(tomorrow_update, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(current_class_update, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(next_class_update, pattern='^' + str(NINE) + '$')
            ]
        },
        fallbacks=[
            CommandHandler('start', cancel),
            CommandHandler('help', cancel),
            CommandHandler('timetable', timetable),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        per_user=False
    )
    
    tomorrow_handler = ConversationHandler(
        entry_points=[CommandHandler('tomorrow', tomorrow)],
        states={
            FIRST: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(timetable_update, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(tomorrow_update, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(current_class_update, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(next_class_update, pattern='^' + str(NINE) + '$')
            ]
        },
        fallbacks=[
            CommandHandler('start', cancel),
            CommandHandler('help', cancel),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', tomorrow),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        per_user=False
    )
    
    current_handler = ConversationHandler(
        entry_points=[CommandHandler('current', current_class)],
        states={
            FIRST: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(timetable_update, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(tomorrow_update, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(current_class_update, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(next_class_update, pattern='^' + str(NINE) + '$')
            ]
        },
        fallbacks=[
            CommandHandler('start', cancel),
            CommandHandler('help', cancel),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', current_class),
            CommandHandler('next', cancel)
        ],
        per_user=False
    )
    
    next_handler = ConversationHandler(
        entry_points=[CommandHandler('next', next_class)],
        states={
            FIRST: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(timetable_update, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(tomorrow_update, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(current_class_update, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(next_class_update, pattern='^' + str(NINE) + '$')
            ]
        },
        fallbacks=[
            CommandHandler('start', cancel),
            CommandHandler('help', cancel),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', next_class_update)
        ],
        per_user=False
    )
    
    dispatcher.add_handler(start_handler, 1)
    dispatcher.add_handler(timetable_handler, 2)
    dispatcher.add_handler(tomorrow_handler, 3)
    dispatcher.add_handler(current_handler, 4)
    dispatcher.add_handler(next_handler, 5)
    
    updater.start_polling(clean=True)


if __name__ == '__main__':
    main()
