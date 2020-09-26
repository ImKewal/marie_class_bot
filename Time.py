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


def date():
    day = js.get_json_from_url(getTime)
    time = day['datetime']
    d = time[8:10]
    m = time[5:7]
    y = time[2:4]
    a = ['AM', 'PM']
    H = str(int(time[11:13]) % 12)
    M = time[14:16]
    ampm = a[int(time[11:13]) // 12]
    return f"{d}.{m}.{y} - {H}:{M} {ampm}"
