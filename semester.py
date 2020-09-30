subjects = [
    ["Java", "https://meet.google.com/lookup/dkohkc6aee?authuser=1&hs=179"],
    ["DAA", "https://meet.google.com/lookup/hjtsucjvft?authuser=1&hs=179"],
    ["Graphics", "https://meet.google.com/lookup/chx53hcrzu?authuser=1&hs=179"],
    ["C.Net.", "https://meet.google.com/lookup/ffxcy7tjsc?authuser=1&hs=179"],
    ["Cloud", "https://meet.google.com/lookup/d4rlhrurw3?authuser=1&hs=179"],
    ["MP", "https://meet.google.com/lookup/ad7c5qekkz?authuser=1&hs=179"],
    ["Java Lab", "https://meet.google.com/lookup/dkohkc6aee?authuser=1&hs=179"],
    ["Cloud Lab", "https://meet.google.com/lookup/d4rlhrurw3?authuser=1&hs=179"],
    ["MP Lap", "https://meet.google.com/lookup/ad7c5qekkz?authuser=1&hs=179"],
    ["Project", "https://www.google.com"]
]
codes = ['BCE-C501', 'BCE-C502', 'BCE-C503', 'BCE-C504', 'BCE-C505', 'BET-C505', 'BCE-C551', 'BCE-C552', 'BET-C553', 'BCE-C560']
timings = {1: '10-11  ', 2: '11-12  ', 3: '12-1  ', 4: '1-2  ', 5: '2-3  ', 6: '3-4  '}


def import_timetable(file):
    tt = []
    for line in file:
        x = line.split()
        tt.append(x)
    file.close()
    for index, value in enumerate(tt):
        tt[index] = tt[index][1:6]
    for di, day in enumerate(tt):
        for ci, code in enumerate(day):
            for i in range(10):
                if code == codes[i]:
                    tt[di][ci] = subjects[i]
                    break
            if 0 <= ci <= 1:
                lower_timing = f"{ci + 10}"
                upper_timing = f"{ci + 11}:30"
                if code in codes[6:10]:
                    timings[ci + 1] = f"{lower_timing}-{upper_timing}  "
            elif ci == 2:
                lower_timing = f"{ci + 10}"
                upper_timing = f"{ci - 1}:30"
                if code in codes[6:10]:
                    timings[ci + 1] = f"{lower_timing}-{upper_timing}  "
            else:
                lower_timing = f"{ci - 1}"
                upper_timing = f"{ci}:30"
                if code in codes[6:10]:
                    timings[ci + 2] = f"{lower_timing}-{upper_timing}  "
    ttd = {}
    for day, day_tt in enumerate(tt):
        day_dictionary = {}
        for cn, cl in enumerate(day_tt):
            if 0 <= cn <= 2:
                day_dictionary[cn + 1] = cl
            else:
                day_dictionary[cn + 2] = cl
        ttd[day + 1] = day_dictionary
    return ttd


def class_no(t):
    cn = 0
    if t < 10:
        cn = 0
    elif 10 <= t < 15:
        for i in range(10, 16):
            if t == i:
                cn = i - 9
    elif 15 <= t < 17:
        cn = 6
    else:
        cn = 7
    return cn


class Semester:
    @staticmethod
    def get_timetable():
        file = open("tt.txt", 'r')
        tt = import_timetable(file)
        return tt
