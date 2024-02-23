import sqlite3
from config import DATABASE



with sqlite3.connect(DATABASE) as conn:
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    # cur.execute("INSERT INTO QUESTION (QUESTION_TEXT, DIFFICULTY, QUIZ_CODE) VALUES (?, ?, ?)", ("HELLO", 0, "secretejyjh-santa"))
    cur.execute("DELETE FROM QUIZ WHERE CODE = 'secret-santa'")
   
    # conn.commit()