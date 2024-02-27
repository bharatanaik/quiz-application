import  sqlite3

class DataBase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect("db.sqlite3")
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON;")

    def init_db(self):
        with open('utils/files/schema.sql', mode='r') as f:
            self.cur.executescript(f.read())
        self.conn.commit()

    def __del__(self):
        self.conn.close()

