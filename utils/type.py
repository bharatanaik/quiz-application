from dataclasses import dataclass
from datetime import datetime, timedelta
from config import ADMIN_MAILS

@dataclass
class User:
    id:int
    fname:str
    lname:str
    age:int
    email:str

    def full_name(self):
        return self.fname + " " + self.lname
    
    
    def is_admin(self):
        return self.email in ADMIN_MAILS

@dataclass
class Quiz:
    code:str
    title:str
    starts_at:datetime
    duration:timedelta
    no_of_questions:int

    def is_expired(self)->bool:
        return (self.starts_at + self.duration ) < datetime.now()


@dataclass
class Result:
    user:User
    quiz:Quiz
    score:int
    time_taken:timedelta
    submitted_at:datetime