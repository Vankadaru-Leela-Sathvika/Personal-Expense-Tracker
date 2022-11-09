from flask import Flask,  render_template,request,redirect
import sqlite3 as sql
import ibm_db

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/home')
def presentHome():
    return render_template('home.html')

@app.route('/profile')
def presentProfile():
    return render_template('profile.html')

@app.route('/expenses')
def presentExpenses():
    return render_template('expenses.html')

@app.route('/sample')
def presentSample():
    return render_template('sample.html')