import os

from cs50 import SQL
import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
import secrets
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from flask_login import current_user
from functools import wraps
from helpers import  login_required
app = Flask(__name__)
secret = secrets.token_urlsafe(32)
app.secret_key = secret
app.config["TEMPLATES_AUTO_RELOAD"] = True
bandera= False

# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response

# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# def hello():
#     return "Hello world"
db = SQL("sqlite:///C:\wamp64\www\phpLiteAdmin\weight.db")
# path = "C:\wamp64\www\phpLiteAdmin\weight.db"
# db = sqlite3.connect(path, check_same_thread=False)
@app.route("/")
def index():
    
    return render_template("calculate.html")
@app.route('/login',methods=["GET","POST"])
def login():
    formusername = request.form.get("username")
    if request.method == "POST":
       rows = db.execute("SELECT * FROM Users WHERE username = :username",
       username = formusername)
       if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("Invalid user")
       session["user_id"] = rows[0]["id"]
       session['logged_in']=True
       return render_template("calculate.html")
    else:    
        imc = 0
        bandera=False
        return render_template("login.html",imc=imc,bandera=bandera)
@app.route('/logout')
def logout():
    session['logged_in']=False
    session.clear()
    imc = 0
    bandera=False
    return render_template("calculate.html",imc=imc,bandera=bandera)
if __name__ == '__main__':
    app.run()
@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "POST":
        if not request.form.get('username'):
            return apology("hola")
        rows = db.execute("INSERT INTO Users(username,password,gender,name) VALUES (:username,:password,:gender,:name)",
        username = request.form.get('username'),
        password = generate_password_hash(request.form.get('password')),
        gender = request.form.get('gender'),
        name = request.form.get('name')
        )
        return render_template("calculate.html")
    else: 
        return render_template("register.html")

@app.route('/calculate',methods=["GET","POST"])
def calculate():
  
    if request.method == "POST":
        weight = int(request.form.get("weight"))
        preHeight = int(request.form.get("height"))
        finalHeight = preHeight/100
        height = finalHeight * finalHeight
        imc = weight/height
        bandera = True
        if 'logged_in' in session:
            rows = db.execute("INSERT INTO weightRecord(weight_Weight,weight_Height,weight_Imc,user_Id) VALUES(:weight1,:height,:imc1,:userId)",
            weight1 = weight,
            height = preHeight,
            imc1 = imc,
            userId = session["user_id"],
            
            )
            return render_template('calculate.html',imc=imc,bandera=bandera)
        else :
            return render_template('calculate.html',imc=imc,bandera=bandera)
       
        
    else:
        bandera = False
        return render_template('calculate.html',bandera=bandera)

@app.route('/progress',methods=["GET","POST"])
@login_required
def progress():
    history = db.execute("""
    SELECT weight_Id,weight_Weight,weight_Height,weight_Imc,weight_Date 
    FROM weightRecord
    WHERE 
    User_Id = :user_id
    ORDER BY weight_Date DESC
    """, user_id = session["user_id"])
    return render_template("progress.html",history = history)

@app.route('/change',methods=["GET","POST"])
@login_required
def change():
    if request.method == 'POST':
        password = request.form.get("passwordChange")
        passworddHash = generate_password_hash(password)
        if request.form.get("passwordChange") != request.form.get("passwordChangeConfirmation"):
            return apology("Passwords do not match")
        else:

            db.execute("""
            UPDATE Users SET password=:password WHERE id = :user_Id

            """,
            user_Id = session["user_id"],
            password = passworddHash)
        return render_template("calculate.html")
    else:
        return render_template('change.html')
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
