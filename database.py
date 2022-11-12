import credentials
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from models import *

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
    def fetchExpenses(self,email):
        sql = "SELECT * FROM expenses WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expenseList = []
        while expense != False:
            expenseList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        print(expenseList)
        return expenseList


