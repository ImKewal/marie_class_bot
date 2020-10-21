import logging
import warnings
import os
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
(SELECTING_HELP, BOT_HELP, COMMAND_HELP, ABOUT_ME, WHY_NEED_ME, TIMETABLE, TOMORROW,
 CURRENT, NEXT, START, HELP, WITHOUT_ARGS, WITH_ARGS, START_OVER,
 BACK, HOME, MON, TUE, WED, THU, FRI,
 SAT, SUN, NO_ARGS, SELECTING_COMMAND, SELECTING_TYPE, SELECTING_TIMETABLE, FALLBACK,
 BACK_TO_PREVIOUS) = map(chr, range(9, 38))
END = ConversationHandler.END
warnings.filterwarnings("ignore")


class Message:
    u_m: int = None
    b_m: int = None
    u_m_c: int = None
    b_m_c: int = None
    day: int = None
    
    def __eq__(self, other):
        if isinstance(other, Message):
            return (self.u_m, self.b_m, self.u_m_c, self.b_m_c, self.day) == \
                   (other.u_m, other.b_m, other.u_m_c, other.b_m_c, other.day)
        else:
            return False


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
    
    def remove(self, context: CallbackContext, cmd=None):
        if len(self.messages) > 1 and cmd is None:
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
        elif self.message_type == 'help' and len(self.messages) == 1 and cmd == 'help':
            context.bot.delete_message(self.messages[0].b_m_c, self.messages[0].b_m)
            context.bot.delete_message(self.messages[0].u_m_c, self.messages[0].u_m)
            self.messages.pop(0)
                
    def __eq__(self, other):
        if isinstance(other, Messages):
            return self.messages == other.messages
        else:
            return False


class Global:
    messages = {
        'error': Messages('error'),
        'start': Messages('start'),
        'timetable': Messages('timetable'),
        'tomorrow': Messages('tomorrow'),
        'current': Messages('current'),
        'next': Messages('next'),
        'day': Messages('day'),
        'help': Messages('help')
    }
    cmd = 'error'
    update: Update = None
    context: CallbackContext = None
    query = None
    tt = {}
    day = {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, '': None}
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
            string = {
                0: {
                    0: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    1: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    2: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    3: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    4: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    5: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    6: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    7: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None}
                },
                1: {
                    0: {'text': "No class live. \nClasses will start at 10AM.", 'keyboard': None},
                    1: {'text': "Current Class:", 'keyboard': None}, 2: {'text': "Current Class:", 'keyboard': None},
                    3: {'text': "Current Class:", 'keyboard': None}, 4: {'text': "Lunch Time", 'keyboard': None},
                    5: {'text': "Current Class:", 'keyboard': None}, 6: {'text': "Current Lab:", 'keyboard': None},
                    7: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None}
                },
                2: {
                    0: {'text': "No class live. \nClasses will start at 10AM.", 'keyboard': None},
                    1: {'text': "Current Class:", 'keyboard': None}, 2: {'text': "Current Class:", 'keyboard': None},
                    3: {'text': "Current Class:", 'keyboard': None}, 4: {'text': "Current Class:", 'keyboard': None},
                    5: {'text': "Lunch Time", 'keyboard': None}, 6: {'text': "Current Lab:", 'keyboard': None},
                    7: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None}
                },
                3: {
                    0: {'text': "No class live. \nClasses will start at 10AM.", 'keyboard': None},
                    1: {'text': "Current Class:", 'keyboard': None}, 2: {'text': "Current Class:", 'keyboard': None},
                    3: {'text': "Current Class:", 'keyboard': None}, 4: {'text': "Current Class:", 'keyboard': None},
                    5: {'text': "Lunch Time", 'keyboard': None}, 6: {'text': "Current Lab:", 'keyboard': None},
                    7: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None}
                },
                4: {
                    0: {'text': "No class live. \nClasses will start at 10AM.", 'keyboard': None},
                    1: {'text': "Current Class:", 'keyboard': None}, 2: {'text': "Current Class:", 'keyboard': None},
                    3: {'text': "Current Class:", 'keyboard': None}, 4: {'text': "Current Class:", 'keyboard': None},
                    5: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None},
                    6: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None},
                    7: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None}
                },
                5: {
                    0: {'text': "No class live. \nClasses will start at 10AM.", 'keyboard': None},
                    1: {'text': "Current Class:", 'keyboard': None}, 2: {'text': "Current Class:", 'keyboard': None},
                    3: {'text': "Current Class:", 'keyboard': None}, 4: {'text': "Lunch Time", 'keyboard': None},
                    5: {'text': "Current Class:", 'keyboard': None},
                    6: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None},
                    7: {'text': "Classes over. \nSee you tomorrow \U0001f603", 'keyboard': None}
                },
                6: {
                    0: {'text': "No class live. \nClasses will start at 10AM.", 'keyboard': None},
                    1: {'text': "Current Class:", 'keyboard': None}, 2: {'text': "Current Class:", 'keyboard': None},
                    3: {'text': "Current Class:", 'keyboard': None}, 4: {'text': "Lunch Time", 'keyboard': None},
                    5: {'text': "Current Class:", 'keyboard': None},
                    6: {'text': "Classes over. \nSee you Monday \U0001f603", 'keyboard': None},
                    7: {'text': "Classes over. \nSee you Monday \U0001f603", 'keyboard': None}
                },
            }
            return string
        elif self.cmd == 'next':
            string = {
                0: {
                    1: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    2: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    3: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    4: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    5: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    6: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None},
                    7: {'text': "No class today. Enjoy \U0001f609", 'keyboard': None}
                },
                1: {
                    1: {'text': "Next class at 10AM.", 'keyboard': None},
                    2: {'text': "Next Class:", 'keyboard': None}, 3: {'text': "Next Class:", 'keyboard': None},
                    4: {'text': "Next Class at 2 PM:", 'keyboard': None}, 5: {'text': "Next Class:", 'keyboard': None},
                    6: {'text': "Next Lab:", 'keyboard': None},
                    7: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                },
                2: {
                    1: {'text': "Next class at 10AM.", 'keyboard': None},
                    2: {'text': "Next Class:", 'keyboard': None}, 3: {'text': "Next Class:", 'keyboard': None},
                    4: {'text': "Next Class:", 'keyboard': None}, 5: {'text': "Next Lab at 3 PM:", 'keyboard': None},
                    6: {'text': "Next Lab:", 'keyboard': None},
                    7: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                },
                3: {
                    1: {'text': "Next class at 10AM.", 'keyboard': None},
                    2: {'text': "Next Class:", 'keyboard': None}, 3: {'text': "Next Class:", 'keyboard': None},
                    4: {'text': "Next Class:", 'keyboard': None}, 5: {'text': "Next Lab at 3 PM:", 'keyboard': None},
                    6: {'text': "Next Lab:", 'keyboard': None},
                    7: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                },
                4: {
                    1: {'text': "Next class at 10AM.", 'keyboard': None},
                    2: {'text': "Next Class:", 'keyboard': None}, 3: {'text': "Next Class:", 'keyboard': None},
                    4: {'text': "Next Class:", 'keyboard': None},
                    5: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                    6: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                    7: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                },
                5: {
                    1: {'text': "Next class at 10AM.", 'keyboard': None},
                    2: {'text': "Next Class:", 'keyboard': None}, 3: {'text': "Next Class:", 'keyboard': None},
                    4: {'text': "Next Class at 2 PM:", 'keyboard': None}, 5: {'text': "Next Class:", 'keyboard': None},
                    6: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                    7: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                },
                6: {
                    1: {'text': "Next class at 10AM.", 'keyboard': None},
                    2: {'text': "Next Class:", 'keyboard': None}, 3: {'text': "Next Class:", 'keyboard': None},
                    4: {'text': "Next Class at 2 PM:", 'keyboard': None}, 5: {'text': "Next Class:", 'keyboard': None},
                    6: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                    7: {'text': "No next class today.\nSee you tomorrow \U0001f603", 'keyboard': None},
                },
            }
            return string
    
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
            today, noc = day_of_week(custom_day=B.day[x])
            self.tt_day = today
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
            if self.cmd != 'day' and self.cmd != 'help':
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
                if self.cmd == 'help':
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
        if self.cmd != 'help' and len(self.messages['help'].messages) > 0:
            self.messages['help'].remove(self.context, cmd='help')
    
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

    def __eq__(self, other):
        if isinstance(other, Global):
            res = []
            for sv, ov in [(self.messages[k], other.messages[k]) for k in self.messages.keys()]:
                res.append(sv == ov)
            return not(False in res)
        else:
            return False


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


def bot_help(update: Update, context: CallbackContext):
    B.set(update, context, 'help', True)
    s = "Bot Help:\n" \
        "Select Option:"
    keyboard = [
        [
            InlineKeyboardButton("About Me", callback_data=str(ABOUT_ME)),
            InlineKeyboardButton("Why you need me?", callback_data=str(WHY_NEED_ME))
        ],
        [
            InlineKeyboardButton("Main Menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK))
        ]
    ]
    B.edit(s, keyboard)
    return BOT_HELP


def about_me(update, context):
    B.set(update, context, 'help', True)
    s = f"Hi! I am {context.bot.first_name} in your service.\nI can give you your class timetable according to your need.\n\n"\
        "My creator is Kewal Sharma.\nContact him at telegram handler: @IamKewal.\n"\
        "Want to create bot like this,\ncheck github repo mentioned below in Github button"
    keyboard = [
        [
            InlineKeyboardButton("Why you need me?", callback_data=str(WHY_NEED_ME)),
            InlineKeyboardButton("Github repo", url="https://github.com/imKewal/marie_class_bot")
            
        ],
        [
            InlineKeyboardButton("Main Menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return BOT_HELP


def why_need(update, context):
    B.set(update, context, 'help', True)
    s = f"I knew you had this question in your mind. Lets resolve this.\n\n" \
        f"This bot can be found by searching {context.bot.username}, can be used in PM or can be added to class groups.\n" \
        "It can be used to get timetable of current day, tomorrow or any other day (refer to commands help if required).\n" \
        "Without this bot you had to check timetable for every class then go to google classroom \u2192 find that class \u2192 " \
        "then only you will get google meet link.\n\nNo need to check pdf copy of timetable any more.\n" \
        "With this bot you just need to type a command and your classes with google meet link will be there according to the day"\
        " of the week.\nAlso no need to check current time, as you are provided with current and next class commands" \
        "\n\nSo enjoy this awesome bot and if you have any feedback, query or any feature request, " \
        "contact Kewal at @IamKewal handler."
    keyboard = [
        [
            InlineKeyboardButton("About me", callback_data=str(ABOUT_ME)),
        ],
        [
            InlineKeyboardButton("Main Menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00ab Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return BOT_HELP


def command_help(update, context):
    B.set(update, context, 'help', True)
    s = "For which command do you want help?"
    keyboard = [
        [
            InlineKeyboardButton("/timetable", callback_data=str(TIMETABLE)),
            InlineKeyboardButton("/tomorrow", callback_data=str(TOMORROW)),
        ],
        [
            InlineKeyboardButton("/current", callback_data=str(CURRENT)),
            InlineKeyboardButton("/next", callback_data=str(NEXT)),
        ],
        [
            InlineKeyboardButton("/start", callback_data=str(START)),
            InlineKeyboardButton("/help", callback_data=str(HELP))
        ],
        [
            InlineKeyboardButton("Main Menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK))
        ]
    ]
    B.edit(s, keyboard)
    return SELECTING_COMMAND


def timetable_help(update, context):
    B.set(update, context, 'help', True)
    s = "/timetable command has two forms, with arguments and without any argument. For which command do you want help?"
    keyboard = [
        [
            InlineKeyboardButton("/timetable with arguments", callback_data=str(WITH_ARGS))
        ],
        [
            InlineKeyboardButton("/timetable without arguments", callback_data=str(WITHOUT_ARGS))
        ],
        [
            InlineKeyboardButton("Main Menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK))
        ]
    ]
    B.edit(s, keyboard)
    return SELECTING_TYPE


def with_args(update, context):
    B.set(update, context, 'help', True)
    s = "This command has form `/timetable ddd`\nwhere `ddd` is the day you want the timetable of."
    keyboard = [
        [
            InlineKeyboardButton("/timetable mon", callback_data=str(MON)),
            InlineKeyboardButton("/timetable tue", callback_data=str(TUE))
        ],
        [
            InlineKeyboardButton("/timetable wed", callback_data=str(WED)),
            InlineKeyboardButton("/timetable thu", callback_data=str(THU)),
            InlineKeyboardButton("/timetable fri", callback_data=str(FRI))
        ],
        [
            InlineKeyboardButton("/timetable sat", callback_data=str(SAT)),
            InlineKeyboardButton("/timetable sun", callback_data=str(SUN))
        ],
        [
           InlineKeyboardButton("Main menu", callback_data=str(HOME)),
           InlineKeyboardButton("\u00AB Back", callback_data=str(BACK))
        ]
    ]
    B.edit(s, keyboard)
    return WITH_ARGS


def tt_mon(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable mon`) to get timetable of monday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tt_tue(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable tue`) to get timetable of tuesday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tt_wed(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable wed`) to get timetable of wednesday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tt_thu(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable thu`) to get timetable of thursday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tt_fri(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable fri`) to get timetable of friday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tt_sat(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable sat`) to get timetable of saturday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tt_sun(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/timetable sun`) to get timetable of sunday"
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def without_args(update, context):
    B.set(update, context, 'help', True)
    s = "This command is simple and do not take any argument (`/timetable`). This command will provide today's timetable."
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def tomorrow_help(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/tomorrow`) to get tomorrow's timetable."
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def current_help(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/current`) to get current live class."
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def next_help(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/next`) to get next class."
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def start_help(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/start`) to get interactive menu to get all the bot functionality."
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


def help_help(update, context):
    B.set(update, context, 'help', True)
    s = "Use this command (`/help`) to get the complete wiki of this bot. You are currently in this command."
    keyboard = [
        [
            InlineKeyboardButton("Main menu", callback_data=str(HOME)),
            InlineKeyboardButton("\u00AB Back", callback_data=str(BACK_TO_PREVIOUS))
        ]
    ]
    B.edit(s, keyboard)
    return FALLBACK


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
    args: dict = s[today][c]
    if today == 0 or ((today in [1, 2, 3]) and (c in [0, 4, 7])) or ((today in [4, 5, 6]) and (c in [0, 4, 6, 7])):
        args['keyboard'] = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
    else:
        tt = B.tt[today][c]
        args['keyboard'] = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
    B.edit(**args)
    return FIRST


def four(update, context):
    today, c, s = B.set(update, context, 'next', True)
    
    if c != 7:
        nc = c + 1
    else:
        nc = c
    args: dict = s[today][nc]
    if today == 0 or ((today in [1, 2, 3]) and (nc in [7])) or ((today in [4, 5, 6]) and (nc in [6, 7])):
        args['keyboard'] = [[InlineKeyboardButton("Close", callback_data=str(FIVE))]]
    elif today != 0 and nc == 4:
        tt = B.tt[today][nc + 1]
        args['keyboard'] = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Close", callback_data=str(FIVE))])
    B.edit(**args)
    return FIRST


def timetable(update, context):
    if len(context.args) > 0 and context.args[0] in B.day:
        day, s, n = B.set(update, context, 'day')
        if day == 0:
            B.send(s[1])
        else:
            tt = B.tt[day]
            keyboard = build_menu(tt, n=n)
            B.send(s[2], keyboard)
    elif len(context.args) > 0 and context.args[0] not in B.day:
        day, s, n = B.set(update, context, 'timetable')
        if day == 0:
            keyboard = [[InlineKeyboardButton("Update", callback_data=str(SIX))]]
            B.send("Check the spelling of day after /timetable command.\nType /help for help.\n\n" + s[1], keyboard)
        else:
            tt = B.tt[day]
            keyboard = build_menu(tt, n=n, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(SIX))])
            B.send("Check the spelling of day after /timetable command.\nType /help for help.\n\n" + s[2], keyboard)
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
    args: dict = s[today][c]
    if today == 0 or ((0 < today < 4) and (c in [0, 4, 7])) or ((3 < today < 7) and (c in [0, 4, 6, 7])):
        args['keyboard'] = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
    else:
        tt = B.tt[today][c]
        args['keyboard'] = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(EIGHT))])
    B.send(**args)
    return FIRST


def current_class_update(update, context):
    today, c, s = B.set(update, context, 'current', True)
    args: dict = s[today][c]
    if today == 0 or ((today in [1, 2, 3]) and (c in [0, 4, 7])) or ((today in [4, 5, 6]) and (c in [0, 4, 6, 7])):
        args['keyboard'] = [[InlineKeyboardButton("Update", callback_data=str(EIGHT))]]
    else:
        tt = B.tt[today][c]
        args['keyboard'] = build_menu(tt, c, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(EIGHT))])
    B.edit(**args)
    return FIRST


def next_class(update, context):
    today, c, s = B.set(update, context, 'next')
    
    if c != 7:
        nc = c + 1
    else:
        nc = c
    args: dict = s[today][nc]
    if today == 0 or ((today in [1, 2, 3]) and (nc in [7])) or ((today in [4, 5, 6]) and (nc in [6, 7])):
        args['keyboard'] = [[InlineKeyboardButton("Update", callback_data=str(NINE))]]
    elif today != 0 and nc == 4:
        tt = B.tt[today][nc+1]
        args['keyboard'] = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
    B.send(**args)
    return FIRST


def next_class_update(update, context):
    today, c, s = B.set(update, context, 'next', True)
    
    if c != 7:
        nc = c + 1
    else:
        nc = c
    args: dict = s[today][nc]
    if today == 0 or ((today in [1, 2, 3]) and (nc in [7])) or ((today in [4, 5, 6]) and (nc in [6, 7])):
        args['keyboard'] = [[InlineKeyboardButton("Update", callback_data=str(NINE))]]
    elif today != 0 and nc == 4:
        tt = B.tt[today][nc + 1]
        args['keyboard'] = build_menu(tt, nc, 1, footer_buttons=[InlineKeyboardButton("Update", callback_data=str(NINE))])
    B.edit(**args)
    return FIRST


def cancel(update, context):
    return END


def main():
    pp = PicklePersistence(filename='pickle')
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
                CallbackQueryHandler(why_need, pattern='^' + str(WHY_NEED_ME) + '$'),
                CallbackQueryHandler(bot_help, pattern='^' + str(BACK_TO_PREVIOUS) + '$'),
            ]
            
        },
        fallbacks=[
            CallbackQueryHandler(home, pattern='^' + str(BACK) + '$'),
            CallbackQueryHandler(home, pattern='^' + str(HOME) + '$'),
            CommandHandler('start', cancel),
            CommandHandler('help', help_command),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        map_to_parent={
            HOME: SELECTING_HELP
        },
        per_user=False,
        persistent=True,
        name='bot_help_conversation',
        per_message=True
    )
    
    with_args_help_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(with_args, pattern='^' + str(WITH_ARGS) + '$')],
        states={
            WITH_ARGS: [
                CallbackQueryHandler(tt_mon, pattern='^' + str(MON) + '$'),
                CallbackQueryHandler(tt_tue, pattern='^' + str(TUE) + '$'),
                CallbackQueryHandler(tt_wed, pattern='^' + str(WED) + '$'),
                CallbackQueryHandler(tt_thu, pattern='^' + str(THU) + '$'),
                CallbackQueryHandler(tt_fri, pattern='^' + str(FRI) + '$'),
                CallbackQueryHandler(tt_sat, pattern='^' + str(SAT) + '$'),
                CallbackQueryHandler(tt_sun, pattern='^' + str(SUN) + '$')
            ],
            FALLBACK: [
                CallbackQueryHandler(with_args, pattern='^' + str(BACK_TO_PREVIOUS) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(timetable_help, pattern='^' + str(BACK) + '$'),
            CallbackQueryHandler(home, pattern='^' + str(HOME) + '$'),
            CommandHandler('start', cancel),
            CommandHandler('help', help_command),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        map_to_parent={
            SELECTING_TYPE: SELECTING_TYPE,
            HOME: SELECTING_HELP
        },
        per_user=False,
        persistent=True,
        name='with_args_help_conversation',
        per_message=True
    )
    
    timetable_help_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(timetable_help, pattern='^' + str(TIMETABLE) + '$')],
        states={
            SELECTING_TYPE: [
                with_args_help_handler,
                CallbackQueryHandler(without_args, pattern='^' + str(WITHOUT_ARGS) + '$')
            ],
            FALLBACK: [
                CallbackQueryHandler(timetable_help, pattern='^' + str(BACK_TO_PREVIOUS) + '$'),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(command_help, pattern='^' + str(BACK) + '$'),
            CallbackQueryHandler(home, pattern='^' + str(HOME) + '$'),
            CommandHandler('start', cancel),
            CommandHandler('help', help_command),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        map_to_parent={
            SELECTING_COMMAND: SELECTING_COMMAND,
            HOME: SELECTING_HELP
        },
        per_user=False,
        persistent=True,
        name='timetable_help_conversation',
        per_message=True
    )
    
    command_help_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(command_help, pattern='^' + str(COMMAND_HELP) + '$')],
        states={
            SELECTING_COMMAND: [
                timetable_help_handler,
                CallbackQueryHandler(tomorrow_help, pattern='^' + str(TOMORROW) + '$'),
                CallbackQueryHandler(current_help, pattern='^' + str(CURRENT) + '$'),
                CallbackQueryHandler(next_help, pattern='^' + str(NEXT) + '$'),
                CallbackQueryHandler(start_help, pattern='^' + str(START) + '$'),
                CallbackQueryHandler(help_help, pattern='^' + str(HELP) + '$')
            ],
            FALLBACK: [
                CallbackQueryHandler(command_help, pattern='^' + str(BACK_TO_PREVIOUS) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(home, pattern='^' + str(BACK) + '$'),
            CallbackQueryHandler(home, pattern='^' + str(HOME) + '$'),
            CommandHandler('start', cancel),
            CommandHandler('help', help_command),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel)
        ],
        map_to_parent={
            HOME: SELECTING_HELP
        },
        per_user=False,
        persistent=True,
        name='command_help_conversation',
        per_message=True
    )
    
    help_handler = ConversationHandler(
        entry_points=[CommandHandler('help', help_command)],
        states={
            SELECTING_HELP: [
                bot_help_handler,
                command_help_handler
            ]
        },
        fallbacks=[
            CommandHandler('start', cancel),
            CommandHandler('help', help_command),
            CommandHandler('timetable', cancel),
            CommandHandler('tomorrow', cancel),
            CommandHandler('current', cancel),
            CommandHandler('next', cancel),
            CallbackQueryHandler(end, pattern='^' + str(END) + '$')
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
    if 'object' not in dispatcher.bot_data:
        dispatcher.bot_data['object'] = B.messages
    if 'object' in dispatcher.bot_data and not (B.messages == dispatcher.bot_data['object']):
        B.messages = dispatcher.bot_data['object']
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
