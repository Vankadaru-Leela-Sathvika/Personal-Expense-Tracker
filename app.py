from flask import *

from database import *
from models import *

user = User("sample","sample","sample","sample")
database = Database()

app = Flask(__name__)
app.secret_key = "FlaskNotFoundError"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signout')  
def signOut():  
    if 'email' in session:  
        session.pop('email',None)  
        session.pop('name',None)
        return redirect('/')
    return redirect('/')  
    

@app.route('/home')
def presentHome():
    email = session['email']
    user = database.fetchUser(email)
    totalExpenses = database.getExpensesTotal(email)
    totalSavings = database.getSavingsTotal(email)
    expenseFilter = "year"
    savingsFilter = "year"
    expenses = database.fetchExpensesPreview(email,5)
    return render_template('home.html',user = user,expenseFilter = expenseFilter,totalExpenses = totalExpenses, savingsFilter = savingsFilter, totalSavings = totalSavings, expenses = expenses)

@app.route('/profile')
def presentProfile():
    user = database.fetchUser(session['email'])
    return render_template('profile.html', user = user,pageType="profile-overview")

@app.route('/expenses')
def presentExpenses():
    user = database.fetchUser(session['email'])
    expenses = database.fetchExpensesPreview(session['email'])
    savings = database.fetchSavings(session['email'])
    return render_template('expenses.html',user = user, expenses = expenses,savings=savings)

@app.route('/sample')
def presentSample():
    user = database.fetchUser(session['email'])
    return render_template('sample.html',user=user)


@app.route('/postSignUpData',methods =['POST','GET'])
def postSignUpData():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        account = database.fetchUser(email)
        if account:
            return render_template('signin.html', msg="You are already a member, please login using your details")
        else:
            if database.insertSignUpUserData(email,password,name):
                return render_template('signin.html', msg="Registration successfull...")
        return render_template('signup.html', msg="Unable to Register!! Try again")

@app.route('/postSignInData',methods =['POST','GET'])
def postSignInData():
    global user
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if database.fetchUser(email):
            fetchedPassword = database.fetchPassword(email)
            if fetchedPassword==password:
                session['email']=email 
                return redirect('home')
            else:
                return render_template('signin.html', invalidLogin="Your Password is wrong!!")                
        else:
            return render_template('signin.html', invalidLogin="You have not Registered yet!!")

@app.route('/editProfile',methods=['POST','GET'])
def editProfile():
    global user
    if request.method=="POST":
        print(request.form)
        name=request.form["name"]
        country=request.form["country"]
        phone=request.form["phone"]
        email=session["email"]
    
        database.updateUserData(email,name,country,phone)
        user=database.fetchUser(email)
        if user:
            return render_template('profile.html',user=user,pageType="profile-edit",profileEditSuccessful="Saved Changes!!")

@app.route('/changePassword',methods = ['GET','POST'])
def changePassword():
    if request.method == 'POST':
        password = request.form["password"]
        newpassword = request.form["newpassword"]
        renewpassword = request.form["renewpassword"]
        fetchedPassword = database.fetchPassword(session['email'])
        print(fetchedPassword)
        user = database.fetchUser(session['email'])
        if fetchedPassword != password:
            return render_template('profile.html',user=user, wrongPassword = "Wrong Password !!",pageType="profile-change-password")
        if newpassword != renewpassword:
            return render_template('profile.html',user=user, noMatch = "Your new Password and Re-type Password don't match!! Enter Password Again...",pageType="profile-change-password")
        if database.updatePassword(session['email'],newpassword):
            return render_template('profile.html',user=user, passwordChangeSuccessful = "Password Changed Successfully !!",pageType="profile-change-password")
        return render_template('profile.html',user=user, wrongPassword = "Couldn't Change Password !!",pageType="profile-change-password")

@app.route('/addExpense',methods = ['GET','POST'])
def addExpense():
    email = session['email']
    date = request.form["expensedate"].split("-")
    expenseid=email+"".join(date)+str(database.getTotalExpenseCountToday(email,date[0],date[1],date[2])+1)
    print(request.form)
    if database.insertExpenseData(email,expenseid,date[0],date[1],date[2],request.form):
        return redirect('/expenses')
    return redirect('/expenses')