tt = []
noc = 5
subjects = [
	["Java", "https://meet.google.com/lookup/dkohkc6aee?authuser=1&hs=179"],
	["DAA", "https://meet.google.com/lookup/hjtsucjvft?authuser=1&hs=179"],
	["Graphics", "https://meet.google.com/lookup/chx53hcrzu?authuser=1&hs=179"],
	["C.Net.", "https://meet.google.com/lookup/ffxcy7tjsc?authuser=1&hs=179"],
	["Cloud", "https://meet.google.com/lookup/gwndu7gz3q?authuser=1&hs=179"],
	["Microprocessor", "https://meet.google.com/lookup/ad7c5qekkz?authuser=1&hs=179"]
]
codes = ['BCE-C501', 'BCE-C502', 'BCE-C503', 'BCE-C504', 'BCE-C505', 'BET-C505']
timings = ['10-11: ', '11-12: ', '12-01: ', '02-03: ', '03-04: ']


def import_timetable(file):
	for line in file:
		x = line.split()
		tt.append(x)
	file.close()
	
	for index, value in enumerate(tt):
		tt[index] = tt[index][1:(noc + 1)]
	
	for di, day in enumerate(tt):
		for ci, code in enumerate(day):
			for i in range(6):
				if code == codes[i]:
					tt[di][ci] = subjects[i]
					break


class Semester:
	@staticmethod
	def get_timetable():
		file = open("tt.txt", 'r')
		import_timetable(file)
		return tt
