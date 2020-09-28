##     marie_class_bot
Telegram bot to get timetable classes and their meet links

* This project requires following python modules installed:
    1. `requests`
    2. `python-telegram-bot`

####    Configuring bot according to your timetable:

- First of all add timetable in [`tt.txt`](tt.txt) in this format:
    1. First word of each line == day.
    2. next words separated with spaces indicating each subject code

- Now configure [`semester.py`](semester.py) according to the [`tt.txt`](tt.txt)
    * sub-codes, 
    * subjects in same sequence of sub-codes and their meet links, 
    * class no (0 for before classes, 1-6 for 6 classes, 7 for after classes}), 
    * and change import_timetable() to make timetable dictionary 
        ```
        {   
            day_no:
                {
                    class_no: [subject, "meetlink], 
                    class_no: [sub, "meetlink"], 
                    ...
                }, 
            day_no:
                {
                    ... 
                },
        }
        ```
        here day_no = 1 for Monday, 2 for Tuesday, ... 6 for saturday
        and class_no = 1 for 1st class, 2 for 2nd, ...

- change number of classes (`noc`) in [`Time.py`](Time.py).`day_of_week()` for each day (0==sunday, ... 6==saturday)

- Rename [`tempelate-config.ini`](TempelateConfig.ini) to config.ini and insert your bot token in the renamed [`config.ini`](TempelateConfig.ini) file in place of `<bot-token>`

- crosscheck code to work with your timetable

#### Running your bot
- Run [`classbot.py`](classbot.py) with `python3` and viola your bot is running.
- This bot will change timetable automatically as you replace [`tt.txt`](tt.txt) with new [`tt.txt`](tt.txt) timetable file. No need to restart bot. Please use update button to update current message timetables.

refer to the [`cmds.txt`](cmds.txt) for the current supported commands
