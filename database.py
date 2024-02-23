from datetime import datetime
import json, random, sqlite3
from config import DATABASE
from flask import flash, g


class Quiz:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(DATABASE)
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON;")
        self.init_db()

    def init_db(self):
        with open('schema.sql', mode='r') as f:
            self.cur.executescript(f.read())
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def create_quiz(self, request):
        title = request.form.get("title")
        no_of_questions = int(request.form.get("no_of_questions"))
        starts_at = request.form.get("starts_at")
        starts_at = datetime.fromisoformat(starts_at)
        d_hour, d_minute = int(request.form.get("hour", 0)), int(request.form.get("minute", 0))
        d_seconds = d_hour*3600 + d_minute * 60
        code = '-'.join(title.lower().split())

        try:
            self.cur.execute("INSERT INTO QUIZ VALUES (?, ?, ?, ?, ?)", (code, title, starts_at, d_seconds, no_of_questions))
            with open("quiz.json") as quiz_file:
                all_questions = json.load(quiz_file)
                questions = random.sample(all_questions, no_of_questions)
                for question in questions:
                    self.cur.execute("INSERT INTO QUESTION (QUESTION_TEXT, DIFFICULTY, QUIZ_CODE) VALUES (?, ?, ?)", (question["question"], 0, code ))
                    question_id = self.cur.execute("""select last_insert_rowid();""").fetchone()[0]
                    self.cur.execute("INSERT INTO ANSWER (ANSWER_TEXT, IS_CORRECT, QUESTION_ID) VALUES (?, ?, ?)", (question["A"], question["answer"] == "A", question_id))
                    self.cur.execute("INSERT INTO ANSWER (ANSWER_TEXT, IS_CORRECT, QUESTION_ID) VALUES (?, ?, ?)", (question["B"], question["answer"] == "B", question_id))
                    self.cur.execute("INSERT INTO ANSWER (ANSWER_TEXT, IS_CORRECT, QUESTION_ID) VALUES (?, ?, ?)", (question["C"], question["answer"] == "C", question_id))
                    self.cur.execute("INSERT INTO ANSWER (ANSWER_TEXT, IS_CORRECT, QUESTION_ID) VALUES (?, ?, ?)", (question["D"], question["answer"] == "D", question_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            flash("Quiz code already exists")

    def list_quiz(self):
        response = self.cur.execute("SELECT * FROM QUIZ;")
        return response.fetchall()