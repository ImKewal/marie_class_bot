import js

getTime = "http://worldtimeapi.org/api/timezone/Asia/Kolkata"


def day_of_week():
    day = js.get_json_from_url(getTime)
    return day["day_of_week"]


def curr_time():
    day = js.get_json_from_url(getTime)
    time = day['datetime']
    t = int(time[11:13])
    return t
