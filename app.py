# importing necessary packages
from flask import Flask, render_template

app = Flask(__name__)

# HOME PAGE 
@app.route("/")
def index():
    return render_template("index.html")


# Create Quiz Page
@app.route("/quiz/create")
def quiz_create():
    return render_template("quiz/create.html")
