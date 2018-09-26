import sqlite3
import time
import os
from bs4 import BeautifulSoup
import logging
import re
import requests


class BCELKtStock:
    def __init__(self):
        logging.basicConfig(filename='log_bcelkt.log', level=logging.INFO)

        self.__stock_url = r'http://lsx.com.la/jsp/scrollingIndex.jsp'
        self.__database = os.path.dirname(__file__) + "/../db/bcelkt.db"
        self.stock_name_list = [
                'BCEL',
                'EDL Gen',
                'LWPC',
                'PTL',
                'SVN',
                'PCD',
                'LCC'
                ]

        self.stock = {}

    def db_setup(self):
        with sqlite3.connect(self.__database) as conn:
            c = conn.cursor()
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

    def get_page_response(self):
        retry = 3
        regex_str = r'([a-zA-Z-_]+|Date|LSX Composite Index): (\d+,\d+|\d+\.\d+|\d{2}/\d{2}/\d{2})'
        
        while retry:
            try:
                page_response = requests.get(self.__stock_url, timeout=5)
                c = re.compile(regex_str)
                data = c.findall(page_response.text)
                self.stock = {re.sub('[ \-]', '_', x).lower(): y.replace(',', '') for x, y in data}
                
                if page_response.status_code == 200:
                    print("OK!")
                    logging.info('{}: Successful response: {}'.format(time.time(), self.stock))
                    break

            except:
                print("error")
                retry -= 1


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

    def execute(self):
        self.db_setup()
        self.get_page_response()
        self.db_save()


if __name__ == '__main__':
    b = BCELKtStock()
    b.execute()
