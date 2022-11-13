import credentials
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from models import *
from datetime import *

conn = ibm_db.connect("DATABASE="+credentials.DB2_DATABASE_NAME+";HOSTNAME="+credentials.DB2_HOST_NAME+";PORT="+credentials.DB2_PORT+";SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID="+credentials.DB2_UID+";PWD="+credentials.DB2_PWD+"",'','')

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=credentials.COS_API_KEY_ID,
    ibm_service_instance_id=credentials.COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=credentials.COS_ENDPOINT
)

class Database:
    def __init__(self) -> None:
        pass
    def fetchUser(self,email):
        sql = "SELECT email,name,phone,country FROM user WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            user = User(account["EMAIL"],account["NAME"],account["PHONE"],account["COUNTRY"])
            return user
        return None

    def insertSignUpUserData(self,email,password,name):
        try:
            insert_sql = "INSERT INTO user(email,password,name) VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, email)
            ibm_db.bind_param(prep_stmt, 2, password)
            ibm_db.bind_param(prep_stmt, 3, name)
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True

    def fetchPassword(self,email):
        try:
            sql = "SELECT password FROM user WHERE email = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            if account:
                return account["PASSWORD"]
            else:
                return False
        except:
            return False 

    def updateUserData(self,email,name,country,phone):
        try:
            sql = "update user set name = ? , country = ?, phone = ? where email = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.bind_param(stmt,2,country)
            ibm_db.bind_param(stmt,3,phone)
            ibm_db.bind_param(stmt,4,email)
            ibm_db.execute(stmt)
        except:
            return False 
        return True

    def updatePassword(self,email,password):
        try:
            sql = "update user set password = ? where email = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,password)
            ibm_db.bind_param(stmt,2,email)
            ibm_db.execute(stmt)
        except:
            return False 
        return True

    def fetchExpensesPreview(self,email,limit=10):
        sql ="SELECT expensename,date,month,year,expenses.description,savingsname,savingstype,expenses.amount FROM expenses join savings on expenses.savingsid=savings.savingsid WHERE expenses.email=? order by expenseid desc limit ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,limit)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expenseList = []
        while expense != False:
            expenseList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expenseList
    
    def fetchExpenses(self,email):
        sql ="SELECT expenseid,expensename,date,month,year,expenses.description,savingsname,savingstype,expenses.amount FROM expenses join savings on expenses.savingsid=savings.savingsid WHERE expenses.email=? order by expenseid desc;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expenseList = []
        while expense != False:
            expenseList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expenseList
    
    def fetchSavings(self,email):
        sql ="SELECT savingsid,savingsname,savingsType from savings where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        saving = ibm_db.fetch_both(stmt)
        savingsList = []
        while saving != False:
            savingsList.append(saving)
            saving = ibm_db.fetch_both(stmt)
        return savingsList

    def getExpensesTotal(self,email):
        today = date.today()
        sql = "SELECT SUM(amount) as TOTAL from expenses where email = ? and year = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,today.year)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["TOTAL"]
    
    def getTotalExpenseCountToday(self,email,year,month,date): 
        sql = "SELECT COUNT(*) as COUNT from expenses where email = ? and year = ? and month = ? and date = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,year)
        ibm_db.bind_param(stmt,3,month)
        ibm_db.bind_param(stmt,4,date)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["COUNT"]

    def getSavingsTotal(self,email):
        sql = "SELECT SUM(amount) as TOTAL from savings where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["TOTAL"]

    def insertExpenseData(self,email,expenseid,year,month,date,expense):
        try:
            insert_sql = "INSERT INTO EXPENSES VALUES(?,?,?,?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, expenseid)
            ibm_db.bind_param(prep_stmt, 2, date)
            ibm_db.bind_param(prep_stmt, 3, month)
            ibm_db.bind_param(prep_stmt, 4, year)
            ibm_db.bind_param(prep_stmt, 5, expense["expensename"])
            ibm_db.bind_param(prep_stmt, 6, expense["expensedescription"])
            ibm_db.bind_param(prep_stmt, 7, expense["savings"])
            ibm_db.bind_param(prep_stmt, 8, email)
            ibm_db.bind_param(prep_stmt, 9, expense["expenseamount"])
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True
        
    def getExpenseData(self,expenseid):
        sql = "SELECT * from expenses where expenseid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,expenseid)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_assoc(stmt)
        return expense

    def deleteExpenseData(self,expenseid):
        try:
            sql = "delete from expenses where expenseid = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,expenseid)
            ibm_db.execute(stmt)
        except:
            return False 
        return True