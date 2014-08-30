import sqlite3 as lite

class Database:

    def __init__(self):
        self._conn = None


    def db_conn(self):
        conn = None
        try:
            conn = lite.connect('data.db')
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


    def insert(self, sql, params):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        self._conn.commit()
