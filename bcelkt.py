#!/bin/python

import urllib.request, re, sys, datetime

log = ""
timestamp = str(datetime.datetime.now()) + ": "

try:
        with urllib.request.urlopen('http://www.lsx.com.la/jsp/scrollingIndex.jsp') as f:
                read_data = f.read().decode("utf-8")

except urllib.request.URLError as err:
        log = "Have problem with connection"

sList = ['Date', 'LSX Composite Index', 'BCEL', 'EDL-Gen', 'LWPC', 'PTL', 'SVN']

for s in sList:
	if s == 'Date':
		pattern = "(?<=Date: )\d+/\d+/\d+"
	else:
		pattern = "(?<=" + s + ": )\d+(?:,\d+)?"

	m = re.search(pattern, read_data)


	if log != "":
		log += ", "
	
	if m:
		line = s + "(" + m.group(0).replace(',', '') + ")"
		log += line


log = timestamp + log + '\n'
with open('bcelkt.log', 'a') as f:
	f.write(log)


#r = input("Press enter to exit...")
