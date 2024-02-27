import sqlite3
from utils.database import DataBase
from flask import Request,  flash, session
from utils.type import User


class Auth(DataBase):
    def create(self, request:Request) -> User:
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        age = int(request.form.get("age"))
        try:
            self.cur.execute("INSERT INTO USERS (FNAME, LNAME, AGE, EMAIL) VALUES (?, ?, ?, ?)", (fname, lname, age, email))
            self.conn.commit()
        except sqlite3.IntegrityError:
            flash("User already exists...")
            return False
        return User(fname, lname, age, email)
    
    def get_user(self, email:str):
        row =  self.cur.execute("SELECT ID,  FNAME, LNAME, AGE, EMAIL FROM USERS WHERE EMAIL = ?", (email, )).fetchone()
        if row:
            return User(*row)
        return None
    
    def authenticate(self, request:Request):
        email = request.form.get("email")
        age = int(request.form.get("age"))
        user = self.get_user(email)
        if user:
            if user.age == (age):
                return user
            else:
                flash("Your Answer is Wrong...")
        else:
            flash("User Email Does Not Exist...")
        return None
    
    def update(self,  request):
   
        self.cur.execute("UPDATE USERS SET FNAME = ?, LNAME = ?, EMAIL = ?, AGE = ? WHERE ID = ?", 
                            (
                                request.form.get("fname"),
                                request.form.get('lname'),
                                request.form.get("email"),
                                int((request.form.get("age"))),
                                Auth().get_user(session.get("user-token")).id
                            ))
        self.conn.commit()
        session["user-token"] = request.form.get("email")
        return True
   

    def delete(self, email:str):
        try:
            self.cur.execute("DELETE FROM USERS WHERE EMAIL = ?", (email,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            return False
        return True
