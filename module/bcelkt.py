import sqlite3
import urllib.request
from urllib.error import URLError
import time
import os
from bs4 import BeautifulSoup
import logging
import re


class BCELKtStock:
    def __init__(self):
        logging.basicConfig(filename='bcelkt.log', level=logging.INFO)

        self.__stock_url = 'http://www.bcel-kt.com/index.php'
        self.__database = os.path.dirname(__file__) + "/../db/bcelkt.db"
        self.stock_name_list = ['BCEL', 'EDL Gen', 'LWPC', 'PTL', 'SVN', 'PCD']

        self.stock = []

    def db_setup(self):
        with sqlite3.connect(self.__database) as conn:
            c = conn.cursor()
            # c.execute('''
            # CREATE TABLE IF NOT EXISTS stock_daily(
            #     id INTEGER PRIMARY KEY,
            #     bcel INTEGER,
            #     edlgen INTEGER,
            #     lwpc INTEGER,
            #     ptl INTEGER,
            #     svn INTEGER,
            #     pcd INTEGER,
            #     timestamp INTEGER NOT NULL)
            # ''')

            c.execute('''
                        CREATE TABLE IF NOT EXISTS lsx(
                            id INTEGER PRIMARY KEY,
                            date TEXT,
                            lsx_composite_index REAL,
                            bcel INTEGER,
                            edl_gen INTEGER,
                            lwpc INTEGER,
                            ptl INTEGER,
                            svn INTEGER,
                            pcd INTEGER,
                            lcc INTEGER,
                            timestamp INTEGER NOT NULL)
                        ''')

    def get_data(self):
        # use db_save() to save
        retry = 3
        while retry:
            try:
                with urllib.request.urlopen('http://lsx.com.la/jsp/scrollingIndex.jsp', timeout=5) as f:
                    request_data = f.read().decode('utf-8')
                    c = re.compile(r'([a-zA-Z-_]+|Date|LSX Composite Index): (\d+,\d+|\d+\.\d+|\d{2}/\d{2}/\d{2})')
                    data = c.findall(request_data)

                    self.stock = {re.sub('[ \-]', '_', x).lower(): y.replace(',', '') for x, y in data}

            except URLError as e:
                logging.warning('{}: {}'.format(time.time(), e))
                retry -= 1
                time.sleep(1)

    def db_save(self):
        if self.stock:
            query = 'INSERT INTO lsx VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            param = (self.stock['date'],
                     self.stock['lsx_composite_index'],
                     self.stock['bcel'],
                     self.stock['edl_gen'],
                     self.stock['lwpc'],
                     self.stock['ptl'],
                     self.stock['svn'],
                     self.stock['pcd'],
                     self.stock['lcc'],
                     time.time())

            try:
                with sqlite3.connect(self.__database) as conn:
                    c = conn.cursor()
                    c.execute(query, param)
                    conn.commit()

                logging.info('{}: Data has been saved to db: {}'.format(time.time(), param))

            except sqlite3.Error as err:
                print(err.args[0])
                logging.info("{}: Sqlite3 error: {}".format(time.time(), err.args[0]))

        else:
            logging.info('No data in stock.')

    # def get_exchange_today(self):
    #     try:
    #         with urllib.request.urlopen(self.__stock_url) as rq:
    #             data = rq.read().decode('utf-8')
    #
    #         soup = BeautifulSoup(data, 'html.parser')
    #
    #         result = soup.find_all(
    #             "table",
    #             attrs={'width': 300, 'align': 'right', 'style': 'border-collapse:collapse', 'border': 1}
    #         )
    #
    #         tb_stock = result[1].find_all('tr')
    #         tb_stock_header = [h.text.lower() for h in tb_stock[1]]
    #         tb_stock_value = [
    #             [i.text.replace('\n', '').replace('\t', '') for i in v.find_all('td')] for v in tb_stock[2:]
    #         ]
    #         tb_stock_value = {i[0].replace(' ', '').lower(): i[1] for i in tb_stock_value}
    #         stock = [tb_stock_header, tb_stock_value]
    #
    #         self.stock = stock
    #         logging.info('Request stock: {}'.format(self.stock))
    #
    #     except urllib.request.URLError as err:
    #         logging.info("Can't connect to site. Request error: {}".format(err.args[0]))
    #
    # def save_data_to_db(self):
    #     if self.stock:
    #         query = 'INSERT INTO stock_daily VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)'
    #         d = self.stock[1]
    #         param = (d['bcel'], d['edlgen'], d['lwpc'], d['ptl'], d['svn'], d['pcd'], time.time())
    #
    #         try:
    #             with sqlite3.connect(self.__database) as conn:
    #                 c = conn.cursor()
    #                 c.execute(query, param)
    #                 conn.commit()
    #
    #             logging.info('Data has been saved to db: {}'.format(d))
    #
    #         except sqlite3.Error as err:
    #             print(err.args[0])
    #             logging.info("Sqlite3 error: {}".format(err.args[0]))
    #
    #     else:
    #         logging.info('No data in stock.')
    #
    # def run(self):
    #     if not os.path.exists(self.__database):
    #         self.db_setup()
    #
    #     self.get_exchange_today()
    #     self.save_data_to_db()

    def execute(self):
        self.db_setup()

        self.get_data()
        self.db_save()


if __name__ == '__main__':
    b = BCELKtStock()
    b.execute()
