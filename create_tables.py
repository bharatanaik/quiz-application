import sqlite3


conn = sqlite3.connect("temp.db")


cur = conn.cursor()

TABLE = {
    "users" : """
        CREATE TABLE IF NOT EXISTS USERS (
            ID INTEGER PRIMARY KEY,
            FNAME TEXT,
            LNAME TEXT,
            EMAIL TEXT,
            AGE INTEGER
        );
    """,
    "quiz":"""
        CREATE TABLE IF NOT EXISTS QUIZ (
            CODE TEXT PRIMARY KEY,
            TITLE TEXT,
            START_TIME DATETIME,
            DURATION FLOAT,
            NO_QUESTIONS INTEGER
        );
    """,
    "result":"""
        CREATE TABLE IF NOT EXISTS RESULT (
            RESULT_ID INTEGER PRIMARY KEY,
            SCORE INTEGER,
            USER_ID INTEGER,
            QUIZ_CODE TEXT,
            TIME_TAKEN FLOAT,
            SUBMITTED_AT DATETIME,
            FOREIGN KEY(USER_ID) REFERENCES USERS(ID),
            FOREIGN KEY(QUIZ_CODE) REFERENCES QUIZ(CODE)
        );
    """,
    "question":"""
        CREATE TABLE IF NOT EXISTS QUESTION (
            QUESTION_ID INTEGER PRIMARY KEY,
            QUESTION_TEXT TEXT,
            DIFFICULTY INTEGER,
            QUIZ_CODE TEXT,
            FOREIGN KEY(QUIZ_CODE) REFERENCES QUIZ(CODE)
        );
    """,
    "answer":"""
        CREATE TABLE IF NOT EXISTS ANSWER (
            ANSWER_ID INTEGER PRIMARY KEY,
            ANSWER_TEXT TEXT,
            IS_CORRECT BOOLEAN,
            QUESTION_ID INTEGER,
            FOREIGN KEY(QUESTION_ID) REFERENCES QUESTION(QUESTION_ID)
        );

    """
}




cur.execute(TABLE["answer"])

# cur.execute("DROP TABLE QUIZ;")

cur.close()