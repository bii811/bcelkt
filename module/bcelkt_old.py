#!/bin/python
# author: bii811
# copyright 2016

import urllib.request, re, sys, datetime
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


if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.realpath(__file__))
    file_name = 'bcelkt_log.csv'
    log_path = os.path.join(file_dir, file_name)

    log = pull_bcel_log()
    write_csv_log(log, log_path)
    print(log_path)
