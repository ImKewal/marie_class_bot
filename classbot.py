import logging
import warnings
from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import error, Message as Mes
from telegram.ext import CommandHandler, Updater, ConversationHandler, PicklePersistence
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.update import Update
from Time import day_of_week, date, curr_time
from semester import Semester, timings, class_no
from config import TOKEN


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


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
FIRST = 0
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE = map(chr, range(9))
# a, b, c, d, START_OVER = map(chr, range(9, 14))
(SELECTING_HELP, BOT_HELP, COMMAND_HELP, ABOUT_ME, WHY_NEED_ME,
 TIMETABLE, TOMORROW, CURRENT, NEXT, WITHOUT_ARGS, WITH_ARGS, START_OVER, BACK, HOME) = map(chr, range(14, 28))
END = ConversationHandler.END
warnings.filterwarnings("ignore")


class Message:
    u_m: int = None
    b_m: int = None
    u_m_c: int = None
    b_m_c: int = None
    day: int = None


class Messages:
    messages: List[Message]
    
    def __init__(self, message_type):
        self.messages = []
        self.message_type = message_type
        if message_type == 'day':
            self.count = {i: 0 for i in range(7)}
            self.index = 0
    
    def insert(self, message: Message, context: CallbackContext = None):
        if message.day is not None:
            self.count[message.day] += 1
            if len(self.messages) > 0:
                context.bot.delete_message(self.messages[self.index].u_m_c, self.messages[self.index].u_m)
                self.index += 1
        self.messages.append(message)
    
    def remove(self, context: CallbackContext):
        if len(self.messages) > 1:
            if self.message_type == 'day':
                for key, value in self.count.items():
                    if value > 1:
                        for index, mess in enumerate(self.messages):
                            if mess.day == key:
                                context.bot.delete_message(mess.b_m_c, mess.b_m)
                                self.count[mess.day] -= 1
                                self.messages.pop(index)
                                self.index -= 1
                                break
            else:
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
        'next': Messages('next'),
        'day': Messages('day')
    }
    cmd = 'error'
    update: Update = None
    context: CallbackContext = None
    query = None
    tt = {}
    day = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6}
    txt = {0: ["Sunday's", "on Sunday"], 1: "Monday's",
           2: "Tuesday's", 3: "Wednesday's",
           4: "Thursday's", 5: "Friday's", 6: "Saturday's"}
    tt_day: int = None
    
    def get_string_dict(self):
        if self.cmd == 'start':
            s = "Select option:"
            return s
        elif self.cmd == 'timetable':
            s = {1: "No Class today. Enjoy : )", 2: "Today's Timetable:"}
            return s
        elif self.cmd == 'day':
            s = {1: f"No Class {self.txt[0][1]}.", 2: f"{self.txt[self.tt_day]} Timetable:"}
            return s
        elif self.cmd == 'tomorrow':
            s = {1: "No Class tomorrow   ; )", 2: "Tomorrow's Timetable:"}
            return s
        elif self.cmd == 'current':
            s = {1: "No Class today. Enjoy : )", 2: "No class live. \nClasses will start at 10AM.", 3: "Current Class:",
                 4: "Lunch Time", 5: "Current Class:", 6: "Classes over. \nSee you tomorrow : )",
                 7: "Classes over. \nSee you on Monday."}
            return s
        elif self.cmd == 'next':
            s = {1: "No Class today. Enjoy : )", 2: "Next Class at 10AM:", 3: "Next Class:", 4: "Next Class at 2PM:",
                 5: "Next Class:", 6: "No next class today"}
            return s
    
    def set(self, update: Update, context: CallbackContext, cmd='error', query=False):
        self.update = update
        self.context = context
        self.cmd = cmd
        today = day_of_week(flag=False)
        tomorrows = day_of_week(False, flag=False)
        if self.tt != Semester.get_timetable():
            self.tt = Semester.get_timetable()
        if self.cmd == 'tomorrow':
            tomorrows, noc = day_of_week(False)
        elif self.cmd == 'day':
            x = context.args[0]
            if x in B.day:
                today, noc = day_of_week(custom_day=B.day[x])
                self.tt_day = today
            else:
                today, noc = day_of_week()
                self.tt_day = today
                self.send('Check the spelling of day after /timetable command.\nType /help for help.')
        else:
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
        elif self.cmd == 'timetable':
            return today, s, n_cols
        elif self.cmd == 'day':
            return today, s, n_cols
        elif self.cmd == 'tomorrow':
            return tomorrows, s, n_cols
        elif self.cmd == 'current' or self.cmd == 'next':
            return today, c, s
    
    def make_message(self, b_m: Mes, day=None):
        m = Message()
        m.u_m_c = self.update.effective_chat.id
        m.u_m = self.update.effective_message.message_id
        m.b_m = b_m.message_id
        m.b_m_c = b_m.chat.id
        if day is not None:
            m.day = day
        return m
    
    def anti_spam(self):
        for i in self.messages.values():
            i.remove(self.context)
    
    def updated(self):
        first_name = self.update.effective_user.first_name
        last_name = self.update.effective_user.last_name
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
            if self.cmd != 'day':
                t = self.context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    reply_to_message_id=self.update.message.message_id
                )
            else:
                t = self.context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup
                )
            if self.update.effective_chat.type != 'private':
                if self.cmd == 'day':
                    self.messages['day'].insert(self.make_message(t, day=self.tt_day), self.context)
                else:
                    self.messages[self.cmd].insert(self.make_message(t))
                self.anti_spam()
        else:
            chat_id = self.update.effective_user.id
            try:
                self.context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup
                )
                if self.update.effective_chat.type == 'supergroup':
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


def help_command(update: Update, context: CallbackContext):
    s = "What help do you want?"
    keyboard = [
        [
            InlineKeyboardButton("Bot Help", callback_data=str(BOT_HELP)),
            InlineKeyboardButton("Commands Help", callback_data=str(COMMAND_HELP))
        ],
        [
            InlineKeyboardButton("Close", callback_data=str(END))
        ]
    ]
    if context.user_data.get(START_OVER):
        B.set(update, context, 'help', True)
        B.edit(s, keyboard)
    else:
        B.set(update, context, 'help')
        B.send(s, keyboard)
    context.user_data[START_OVER] = False
    return SELECTING_HELP


def end(update, context):
    update.callback_query.answer()
    update.callback_query.edit_message_text(text='See ya!')
    return END


def home(update, context):
    context.user_data[START_OVER] = True
    help_command(update, context)
    return HOME


def back(update, context):
    context.user_data[START_OVER] = True
    help_command(update, context)
    return BACK


def bot_help(update: Update, context: CallbackContext):
    B.set(update, context, 'bot_help', True)
    s = "Select Option:"
    keyboard = [
        [
            InlineKeyboardButton("About Me", callback_data=str(ABOUT_ME)),
            InlineKeyboardButton("Why you need me?", callback_data=str(WHY_NEED_ME))
        ],
        [
            InlineKeyboardButton("Close", callback_data=str(END)),
            InlineKeyboardButton("\U000000AB Back", callback_data=str(BACK))
        ]
    ]
    B.edit(s, keyboard)
    return BOT_HELP


def about_me(update, context):
    B.set(update, context, 'about_me', True)
    s = f"Hi! I am {context.bot.first_name} in your service.\nI can give you your class timetable according to your need.\n\n"\
        "My creator is Kewal Sharma.\nContact him at telegram: @IamKewal.\n"\
        "Want to create bot like me,\ncheck github repo mentioned below in Github button"
    keyboard = [
        [
            InlineKeyboardButton("Why you need me?", callback_data=str(WHY_NEED_ME)),
            InlineKeyboardButton("\U000000AB Back", callback_data=str(BACK))
        ],
        [
            InlineKeyboardButton("Github repo", url="https://github.com/imKewal/marie_class_bot")
        ]
    ]
    B.edit(s, keyboard)
    return BOT_HELP


def why_need(update, context):
    B.set(update, context, 'why_need', True)
    s = "I knew you had this question in your mind. Lets resolve this.\n\n"\
        "This bot can be used in PM by searching marie_class_bot and can also be added to class groups."\
        "It can be used to get timetable of current day or any other day if required. No need to check pdf copy of timetable " \
        "any more. For every class you had to check in timetable then go to classroom -> find class -> google meet.\n\n"\
        "But with this bot you just need to type a command and your classes will be there with google meet links.\n"\
        "Also no need to check current time and today's day, as you are provided with current and next class commands\n"\
        "So enjoy this awesome bot and provide feedback to the creator at @IamKewal if you like his work."
    keyboard = [
        [
            InlineKeyboardButton("About me", callback_data=str(ABOUT_ME)),
            InlineKeyboardButton("\U000000AB Back", callback_data=str(BACK))
        ]
    ]
    B.edit(s, keyboard)
    return BOT_HELP


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
    tom, s, n = B.set(update, context, 'tomorrow', True)
    
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
    if len(context.args) > 0:
        day, s, n = B.set(update, context, 'day')
        if day == 0:
            B.send(s[1])
        else:
            tt = B.tt[day]
            keyboard = build_menu(tt, n=n)
            B.send(s[2], keyboard)
    
    else:
        day, s, n = B.set(update, context, 'timetable')
        if day == 0:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(SIX))]]
            B.send(s[1], keyboard)
        else:
            tt = B.tt[day]
            keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SIX))])
            B.send(s[2], keyboard)
    
    return FIRST


def timetable_update(update, context):
    today, s, n = B.set(update, context, 'timetable', True)
    if context.args is not None:
        if len(context.args) > 0:
            x = context.args[0]
        else:
            x = 'today'
        if x in B.day:
            today = B.day[x]
    
    if today == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(SIX))]]
        B.edit(s[1], keyboard)
    else:
        tt = B.tt[today]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SIX))])
        B.edit(s[2], keyboard)
    
    return FIRST


def tomorrow(update, context):
    tom, s, n = B.set(update, context, 'tomorrow')
    
    if tom == 0:
        keyboard = [[InlineKeyboardButton("Update", callback_data=str(SEVEN))]]
        B.send(s[1], keyboard)
    else:
        tt = B.tt[tom]
        keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SEVEN))])
        B.send(s[2], keyboard)
    
    return FIRST


def tomorrow_update(update, context):
    tom, s, n = B.set(update, context, 'tomorrow', True)
    
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
    pp = PicklePersistence(filename='classbot')
    updater = Updater(token=TOKEN, persistence=pp, use_context=True)
    dispatcher = updater.dispatcher
    
    start_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
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
            CommandHandler('help', cancel),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        per_user=False,
        name='start_conversation',
        persistent=True
    )
    bot_help_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot_help, pattern='^' + str(BOT_HELP) + '$')],
        states={
            BOT_HELP: [
                CallbackQueryHandler(about_me, pattern='^' + str(ABOUT_ME) + '$'),
                CallbackQueryHandler(why_need, pattern='^' + str(WHY_NEED_ME) + '$')
            ],
            
        },
        fallbacks=[
            CallbackQueryHandler(back, pattern='^' + str(BACK) + '$'),
            CallbackQueryHandler(home, pattern='^' + str(HOME) + '$')
        ],
        map_to_parent={
            BACK: SELECTING_HELP
        }
    )
    
    help_handler = ConversationHandler(
        entry_points=[CommandHandler('help', help_command)],
        states={
            SELECTING_HELP: [
                bot_help_handler,
                CallbackQueryHandler(end, pattern='^' + str(END) + '$')
            ]
        },
        fallbacks=[
            CommandHandler('start', cancel),
            CommandHandler('help', help_command),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        per_user=False,
        name='help_conversation',
        persistent=True
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
        per_user=False,
        name='timetable_conversation',
        persistent=True
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
        per_user=False,
        name='tomorrow_conversation',
        persistent=True
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
        per_user=False,
        name='current_conversation',
        persistent=True
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
        per_user=False,
        name='next_conversation',
        persistent=True
    )
    
    dispatcher.add_handler(start_handler, 1)
    dispatcher.add_handler(help_handler, 2)
    dispatcher.add_handler(timetable_handler, 3)
    dispatcher.add_handler(tomorrow_handler, 4)
    dispatcher.add_handler(current_handler, 5)
    dispatcher.add_handler(next_handler, 6)
    
    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
