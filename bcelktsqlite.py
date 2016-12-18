#!/bin/python
# author: bii811
# copyright 2016

import urllib.request
import re
import sys
import datetime
import sqlite3
import csv
import os


def write_csv_log(data, path):
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def read_csv_log(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)


def pull_bcel_log():
    data = []
    read_data = ''

    try:
        timestamp = str(datetime.datetime.now())
        data.append(timestamp)

        with urllib.request.urlopen('http://www.lsx.com.la/jsp/scrollingIndex.jsp') as f:
                read_data = f.read().decode("utf-8")

    except urllib.request.URLError as err:
            data.append("Can't connect to site.'")
    else:
        header_list = ['DateLog', 'TimeLog', 'Date', 'LSX Composite Index', 'BCEL', 'EDL-Gen', 'LWPC', 'PTL', 'SVN']
        for header in header_list[2:]:
            if header == 'Date':
                pattern = "(?<=Date: )\d+/\d+/\d+"
            else:
                pattern = "(?<=" + header + ": )\d+(?:,\d+)?"

            m = re.search(pattern, read_data)
            if m:
                if header =='Date':
                    data.append(datetime.datetime.strptime(m.group(0), '%d/%m/%Y').strftime('%Y-%m-%d'))
                else:
                    data.append(m.group(0).replace(',', ''))
    finally:
        return data


conn = sqlite3.connect('bcelkt_daily_log.db')
