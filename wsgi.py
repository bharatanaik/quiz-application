from flask import Flask, flash, render_template, request, redirect, session
from utils.quizhandler import QuizHandler
from utils.auth import Auth
from utils.decorators import login_required, admin_required

app = Flask(__name__)
app.secret_key = "c$7cdap2cs84d+3&p=c*#z)@g(7&ds5e47d9&1%kdx@dsiwnca"


@app.template_filter('duration_format')
def duration_format(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"


QuizHandler().init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def index():
    quizzes = QuizHandler().list_quiz()
    user = None
    if session.get("user-token"):
        user = Auth().get_user(session.get("user-token"))
    return render_template("index.html", quizzes=quizzes, user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if Auth().create(request):
            return redirect("/login")
    return render_template("register.html")


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = Auth().get_user(session.get("user-token"))
    if request.method == "POST":
        if Auth().update(request):
            return redirect("/")
    return render_template("edit-profile.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Auth().authenticate(request)
        if user:
            session["user-token"] = user.email
            if request.args.get("next"):
                return redirect(request.args.get("next"))
            else:
                return redirect("/dashboard")
    return render_template("login.html")


@app.route("/quiz/attend/<code>", methods=["GET", "POST"])
@login_required
def attend_quiz(code):
    if QuizHandler().is_done(code):
        return redirect(f"/quiz/result/{code}")
    questions = QuizHandler().list_questions(code)
    if request.method == "POST":
        QuizHandler().save_result(code, request)
        return redirect(f"/quiz/result/{code}")
    quiz = QuizHandler().get(code)
    return render_template("quiz/attend.html", questions=questions, user=Auth().get_user(session.get("user-token")),
                           quiz=quiz,
                           json_data={
                               "starts_at": quiz.starts_at,
                               "time_seconds": quiz.duration.seconds,
                           })


@app.route("/quiz/result/<code>", methods=["GET", "POST"])
@login_required
def result(code):
    result = QuizHandler().get_result(code)
    return render_template("quiz/result.html", result=result)


@app.route("/logout")
def logout():
    if 'user-token' in session:
        session.pop('user-token')
    return redirect("/")


# ADMIN HANDLING PAGES
@app.route("/quiz/create", methods=["GET", "POST"])
@admin_required
def quiz_create():
    if request.method == "POST":
        quiz = QuizHandler().create_quiz(request)
        if quiz:
            return redirect("/")
    return render_template("quiz/create.html")


@app.route("/quiz/stats/<code>")
@admin_required
def statistics(code):
    return render_template("quiz/statistics.html", stats=QuizHandler().stats(code))


@app.route("/quiz/delete/<code>")
@admin_required
def quiz_delete(code):
    QuizHandler().delete_quiz(code)
    return redirect("/")
