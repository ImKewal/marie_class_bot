# marie_class_bot
Telegram bot to get timetable classes and their meet links

-This project requires following python modules installed:
    1. requests
    2. python-telegram-bot

# configuring bot acc to you:

-First of all add timetable in `tt.txt` in this format:
    1. First word of each line == day.
    2. next words separated with spaces indicating each subject code

-now configure `semester.py` according to the `tt.txt` 
    * sub-codes, 
    * subjects in same sequence of sub-codes and their meet links, 
    * class no (0 for before classes, 1-6 for 6 classes, 7 for after classes}), 
    * and change import_timetable() to make timetable dictionary 
        {day_no:{class_no:[subject, "meetlink], [sub, "meetlink"], ...}, 
        day_no: ...} 
        here day_no = 1 for Monday, 2 for Tuesday, ... 6 for saturday.

-change number of classes (`noc`) in Time.py/.`day_of_week()` for each day (0==sunday, ... 6==saturday)

-insert your bot token in the `config.ini` in place of `<bot-token>`

-crosscheck code to work with your timetable

run `classbot.py` with `python3` and viola your bot is running
This bot will change timetable automatically as you replace `tt.txt` with new `tt.txt` timetable file. No need to restart bot. Please use update button to update current message timetables.

refer to the `commands.txt` for the current supported commands
