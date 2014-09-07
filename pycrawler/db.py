import sqlite3 as lite
import os
import sys


class Database:

    DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    DATABASE = '../data/data.db'

    def __init__(self):
        self._conn = None

    def db_conn(self):
        conn = None
        try:
            conn = lite.connect('{0}/{1}'.format(self.DIR_PATH, self.DATABASE))
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS url(
                            id INTEGER PRIMARY KEY,
                            url TEXT,
                            title TEXT,
                            keywords TEXT,
                            date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            data = cur.fetchone()
        except lite.Error, e:
            print 'Error %s:' % e.args[0]
            sys.exit(1)
        self._conn = conn
        return self._conn

    def execute(self, sql, params):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        self._conn.commit()
