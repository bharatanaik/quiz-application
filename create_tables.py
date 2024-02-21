import sqlite3


conn = sqlite3.connect("temp.db")


cur = conn.cursor()

query = """
CREATE TABLE USERS (
    ID INTEGER PRIMARY KEY,
    FNAME TEXT,
    LNAME TEXT,
    EMAIL TEXT,
    AGE INTEGER
);

"""

cur.execute(query)

cur.close()