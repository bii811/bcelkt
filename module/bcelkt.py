import sqlite3
import urllib.request
import time
import re


class BcelktStock:
    def __init__(self):
        self.__stock_url = 'http://www.lsx.com.la/jsp/scrollingIndex.jsp'
        self.__database = 'db/bcelkt_log.db'
        self.web_read_data = ''
        self.error_message = []
        self.data = {}

    def setup(self):
        with sqlite3.connect(self.__database) as conn:
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS stock_daily_log(
                id INTEGER PRIMARY KEY,
                date TEXT,
                lsx INTEGER,
                bcel INTEGER,
                edlgen INTEGER,
                lwpc INTEGER,
                ptl INTEGER,
                svn INTEGER,
                timestamp INTEGER NOT NULL)
            ''')

    def filter_data(self):
        temp = self.web_read_data
        m = re.findall(r"(Date|LSX Composite Index|BCEL|EDL-Gen|LWPC|PTL|SVN):\s(.*)\";", temp)
        if m:
            for i, j in m:
                if i == "Date":
                    j = j.strip()
                self.data[i] = j

    def pull_data_from_web(self):
        try:
            with urllib.request.urlopen(self.__stock_url) as f:
                self.web_read_data = f.read().decode("utf-8")

        except urllib.request.URLError as err:
            self.error_message.append("Can't connect to site. Request error: {}".format(err.args[0]))

    def save_data_to_db(self):
        query = 'INSERT INTO stock_daily_log VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)'
        d = self.data
        param = (d['Date'], d['LSX Composite Index'], d['BCEL'], d['EDL-Gen'], d['LWPC'], d['PTL'], d['SVN'], time.time())

        try:
            with sqlite3.connect(self.__database) as conn:
                c = conn.cursor()
                c.execute(query, param)
                conn.commit()

            print(self.data)

        except sqlite3.Error as err:
            self.error_message.append("Sqlite3 error: {}".format(err.args[0]))

    def run(self):
        self.setup()
        self.pull_data_from_web()
        self.filter_data()
        self.save_data_to_db()
