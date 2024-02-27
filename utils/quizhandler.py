from utils.auth import Auth
from utils.database import DataBase 
from datetime import datetime, timedelta
from utils.type import Quiz, Result, User
from flask import Request, session, flash
import json, random, sqlite3


class QuizHandler(DataBase):
    def get(self, code:str):
        row = self.cur.execute("SELECT * FROM QUIZ WHERE CODE = ?", (code,)).fetchone()
        if row:
            return Quiz(row[0], row[1], row[2], timedelta(seconds=row[3]), row[4])
        return row

    def create_quiz(self, request: Request):
        title = request.form.get("title")
        no_of_questions = int(request.form.get("no_of_questions"))
        starts_at = request.form.get("starts_at")
        starts_at = datetime.fromisoformat(starts_at)
        d_hour, d_minute = int(request.form.get("hour", 0)), int(request.form.get("minute", 0))
        d_seconds = d_hour*3600 + d_minute * 60
        code = '-'.join(title.lower().split())

        try:
            self.cur.execute("INSERT INTO QUIZ VALUES (?, ?, ?, ?, ?)", (code, title, starts_at, d_seconds, no_of_questions))
            with open("utils/files/quiz.json") as quiz_file:
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
            return True
        

        except sqlite3.IntegrityError:
            flash("Quiz code already exists")
            return False
        
    def list_quiz(self):
        response = self.cur.execute("SELECT * FROM QUIZ ORDER BY START_TIME DESC;")
        rows =  response.fetchall()
        return [
            Quiz(
                code = row[0], 
                title=row[1], 
                starts_at=datetime.fromisoformat(row[2]), 
                duration=timedelta(seconds=row[3]), 
                no_of_questions=row[4]
            ) for row in rows]
    

    def list_questions(self, code:str):
        rows =  self.cur.execute('''
            SELECT Q.QUESTION_ID, Q.QUESTION_TEXT, A.ANSWER_ID, A.ANSWER_TEXT, A.IS_CORRECT
            FROM QUESTION Q
            JOIN ANSWER A ON Q.QUESTION_ID = A.QUESTION_ID
            WHERE Q.QUIZ_CODE = ?                                 
        ''', (code, )).fetchall()

        questions = {}

        # Process the results and populate the dictionary
        for row in rows:
            question_id, question_text, answer_id, answer_text, is_correct = row
            
            # If the question is not in the dictionary, add it with an empty list of answers
            if question_id not in questions:
                questions[question_id] = {'question_text': question_text, 'answers': []}
            
            # Add the answer to the list of answers for the corresponding question
            questions[question_id]['answers'].append({
                'answer_id': answer_id, 
                'answer_text': answer_text, 
                'is_correct': True if is_correct else False
            })
        return questions

    def delete_quiz(self, quiz_code:str)->None:
        try:
            self.cur.execute("DELETE FROM QUIZ WHERE CODE = ?", (quiz_code,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            flash("Quiz does'nt exist")

    def check_answers(self, code, request)->int:
        answers = self.cur.execute("""
                SELECT A.QUESTION_ID , A.ANSWER_ID
                FROM  ANSWER A, QUESTION QUES
                WHERE QUES.QUIZ_CODE = ? AND QUES.QUESTION_ID = A.QUESTION_ID AND A.IS_CORRECT = 1;
            """, (code,)).fetchall() 
        score = 0
        for question_id, answer_id in answers:
            if request.form.get(str(question_id)) == str(answer_id): 
                score += 1
        return score
    
    def save_result(self, code, request):
        score = self.check_answers(code, request)
        userid = self.cur.execute("SELECT ID FROM USERS WHERE EMAIL = ?", (session.get("user-token"),)).fetchone()[0]
        quiz = self.get(code)
        submitted_at = datetime.now()
        time_taken =   submitted_at - datetime.fromisoformat(quiz.starts_at)
        time_taken = time_taken.total_seconds()
        self.cur.execute("""INSERT INTO RESULT (SCORE, USER_ID, QUIZ_CODE, TIME_TAKEN, SUBMITTED_AT) VALUES (?, ?, ?, ?, ?) """, (score, userid, code, time_taken, submitted_at))
        self.conn.commit()

    def get_result(self, code):
        user = Auth().get_user(session.get("user-token"))
        result = self.cur.execute("SELECT * FROM RESULT WHERE QUIZ_CODE = ? AND USER_ID = ?", (code, user.id)).fetchone()
        return Result(
            user=user, 
            quiz = QuizHandler().get(code),
            score = result[1],
            time_taken=timedelta(seconds=result[4]),
            submitted_at=result[5]
        )
        

    def is_done(self, code)->bool:
        user = Auth().get_user(session.get("user-token"))
        res_count = self.cur.execute("SELECT COUNT(*) FROM RESULT WHERE  USER_ID = ? AND QUIZ_CODE = ?", (user.id, code)).fetchone()[0]
        if res_count > 0:
            return True
        else:
            return False


    def stats(self, code):
        stats = self.cur.execute("""SELECT U.FNAME || ' ' || U.LNAME, R.SCORE, R.TIME_TAKEN , U.EMAIL
                         FROM USERS U JOIN RESULT R ON U.ID = R.USER_ID
                         WHERE R.QUIZ_CODE = ?
                         ORDER BY R.SUBMITTED_AT;
                         """, (code, )).fetchall()    
        return stats