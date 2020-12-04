from flask import Flask,render_template,request,session,url_for,json
import pandas as pd
import csv
from datetime import datetime
import pygal
import random
import mysql.connector
from pandas import DataFrame
from random import randint
import string
import onetimepad
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

app= Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dataowner')
def dataowner():
    return render_template("dataowner.html")


@app.route('/dataowner1',methods=['POST','GET'])
def dataowner1():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        if name == 'owner' and password == 'owner':
            return render_template("ownerhome.html")
    return render_template('dataowner.html',msg="Invalid Credentials...")


@app.route('/fileupload')
def fileupload():
    return render_template("fileupload.html")


@app.route('/upload',methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        dname = request.form['dname']
        demail = request.form['demail']
        pname = request.form['pname']
        pemail = request.form['pemail']
        disease = request.form['disease']
        age = request.form['age']
        fname = request.form['fname']
        pfile = request.form['pfile']

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()
        sql = "select count(*) from doctor where fname=%s"
        val = (pname,)
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        count = result[0]
        #print(count)
        if count == 0:
            sql = "insert into doctor(dname,demail,pname,disease,age,fname,file,email) values(%s,%s,%s,%s,%s,%s,%s,%s)"
            key1 = random.randint(1, 10000)
            key1 = str(key1)
            file_name = "f:\\dataleakage\\" + fname + ".txt"
            f = open(file_name, 'r')
            fdata=''
            fdata = f.read()
            #nltk.download('stopwords')
            #nltk.download('punkt')
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(fdata)
            fdata1=[]
            [fdata1.append(w) for w in word_tokens if not w in stop_words]
            hdata=''
            for word in fdata1:
                hdata+=word+' '
            hdata = hdata[:-1]
            print(fdata)
            print(hdata)
            f.close()
            hdata = onetimepad.encrypt(hdata,'random')
            cipher_text = onetimepad.encrypt(fdata, 'random')
            print(cipher_text)
            val = (dname,demail,pname,disease,age,fname,cipher_text,pemail)
            mycursor.execute(sql, val)
            mydb.commit()

            sql = "insert into files(fname,content) values(%s,%s)"
            val = (fname,fdata)
            mycursor.execute(sql, val)
            mydb.commit()


            sql = "insert into datasharer(pname,age,disease) values(%s,%s,%s)"
            val = (pname,age,disease)
            mycursor.execute(sql, val)
            mydb.commit()
        else:
            return render_template("fileupload.html", msg='File already Exists!!!')
        mydb.close()
    return render_template("fileupload.html",msg='File Uploaded Successfully!!!')

@app.route('/viewusers')
def viewusers():

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select * from doctor"
    mycursor.execute(sql)
    users = pd.DataFrame(mycursor.fetchall())
    users.iloc[:,8] = users.iloc[:,8].str[:20]
    rows = mycursor.rowcount
    if rows!=0:
        users.columns = ['Did','Doctor Name', 'Doctor Email','Patient Name', 'Disease', 'Age','Fname','Content','Patient Email']
    if rows==0:
        return render_template("viewusers.html", msg='null')
    mydb.close()
    return render_template("viewusers.html",data=users.to_html(index=False))

@app.route('/login',methods=['POST','GET'])
def login():
   return render_template("userlogin.html")

@app.route('/datauser',methods=['POST','GET'])
def datauser():
   return render_template("userlogin.html")

@app.route('/userlogin',methods=['POST','GET'])
def userlogin():
    global email1
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()

        sql = "select count(*) from patient where email= %s and  password=%s"
        val = ( email, password )
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        res = result[0]
        print(res)
        if int(res) == 0:
            return render_template("userlogin.html",msg ='Failure!!!')
        email1 = email
        mydb.close()
    return render_template("userhome.html")

@app.route('/register')
def register():
    return render_template("registration.html")

@app.route('/userhome')
def userhome():
    return render_template("userhome.html")


@app.route('/registration',methods=['POST','GET'])
def registration():
    global email
    if request.method=='POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        number = request.form['number']
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()

        sql = "INSERT INTO patient (pname, password, email, mobile) VALUES (%s, %s, %s, %s)"
        val = (name,password,email,number)
        mycursor.execute(sql, val)
        mydb.commit()
    return render_template("registration.html",msg='success')

@app.route('/profile')
def profile():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select pname,password,email,mobile from patient where email=%s"
    vals=(email1,)
    mycursor.execute(sql,vals)
    users1 = pd.DataFrame(mycursor.fetchall())
    users1.columns = ['Patient Name ','Password','Email','Number']
    mydb.close()
    return render_template("profile.html", users=users1)

@app.route('/update')
def update():
    return render_template("update.html")

@app.route('/update1',methods=["POST","GET"])
def update1():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        number = request.form['number']
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()
        sql = "update patient set pname=%s, password=%s, mobile=%s where email=%s"
        vals=(name,password,number,email1)
        mycursor.execute(sql, vals)
        mydb.commit()
        mydb.close()
    return render_template("update.html", msg='success')

@app.route('/viewfiles2')
def viewfiles2():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select pname,email,mobile from patient where email=%s"
    vals=(email1,)
    mycursor.execute(sql,vals)
    users = pd.DataFrame(mycursor.fetchall())
    rows = mycursor.rowcount
    if rows!=0:
        users.columns=['Patient Name','Email','Mobile']
    if rows ==0:
        return render_template("viewfiles2.html", msg='null')
    mydb.close()
    return render_template("viewfiles2.html", data=users.to_html(index=False))

@app.route('/viewfiles3')
def viewfiles3():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select pname,age,disease from datasharer"
    mycursor.execute(sql)
    users = pd.DataFrame(mycursor.fetchall())
    rows = mycursor.rowcount
    if rows!=0:
        users.columns=['Patient Name','Age','Disease']
    if rows ==0:
        return render_template("viewfiles3.html", msg='null')
    mydb.close()
    return render_template("viewfiles3.html", data=users.to_html(index=False))

@app.route('/viewfiles4')
def viewfiles4():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select * from files"
    mycursor.execute(sql)
    users = pd.DataFrame(mycursor.fetchall())
    rows = mycursor.rowcount
    if rows!=0:
        users.columns=['File Name','Content']
    if rows ==0:
        return render_template("viewfiles4.html", msg='null')
    mydb.close()
    return render_template("viewfiles4.html", data=users.to_html(index=False))


@app.route('/requestfiles',methods=['POST','GET'])
def requestfiles():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr")


    mycursor = mydb.cursor(buffered=True)

    sql = "select pname from patient where email = %s"
    vals = (email1,)
    mycursor.execute(sql,vals)
    ptname = mycursor.fetchall()[0]

    sql = "select pname,age,disease from datasharer where pname=%s"
    vals=(ptname,)
    mycursor.execute(sql,ptname)
    rows = mycursor.rowcount
    print('request file rows',rows)
    if rows>0:
        users1 = pd.DataFrame(mycursor.fetchall())
        users1.columns = ['Patient Name','Age','Disease']
    else:
        return render_template('requestfiles.html',msg='null')
    return render_template("requestfiles.html",users=users1)


@app.route('/request1/<pname>',methods=['POST','GET'])
def request1(pname):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr")

    mycursor = mydb.cursor()
    sql = "select * from datasharer where pname=%s"
    vals=(pname,)
    mycursor.execute(sql,vals)
    users1 = pd.DataFrame(mycursor.fetchall())
    sql = "insert into request(pname,age,disease,status) values(%s,%s,%s,%s)"
    vals=(str(users1.loc[0][0]),str(users1.loc[0][1]),str(users1.loc[0][2]),'pending')
    mycursor.execute(sql, vals)
    mydb.commit()
    return render_template("userhome1.html",user='success')

@app.route('/ca')
def ca():
    return render_template("ca.html")

@app.route('/ca1',methods=['POST','GET'])
def ca1():
    username = request.form['username']
    password = request.form['password']
    if username == 'ca' and password =='ca':
        return render_template('cahome.html')
    return render_template("ca.html",msg='Incorrect Credentials!!!')


@app.route('/viewrequest')
def viewrequest():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select * from request where status='pending'"
    mycursor.execute(sql)
    users1 = pd.DataFrame(mycursor.fetchall())
    rows = mycursor.rowcount
    if rows != 0:
        users1.columns = ['Patient Name', 'Age', 'Disease', 'Status']
    if rows == 0:
        return render_template('viewrequest.html', msg='null')
    mydb.close()
    return render_template("viewrequest.html", users=users1)


@app.route('/accept1/<fname>')
def accept1(fname):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()
    sql = "update request set status='accepted' where pname=%s"
    val = (fname,)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()
    sql = "select * from request"
    mycursor.execute(sql)
    users1 = pd.DataFrame(mycursor.fetchall())
    users1.columns = ['Patient Name', 'Age', 'Disease', 'Status']
    mydb.close()
    return render_template("viewrequest.html", users=users1)

@app.route('/accepted1')
def accepted1():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select * from request where status='accepted'"
    mycursor.execute(sql)
    users = pd.DataFrame(mycursor.fetchall())
    if mycursor.rowcount > 0:
        users.columns = ['Patient Name', 'Age', 'Disease', 'Status']
        return render_template("accepted1.html", data=users.to_html(index=False))
    mydb.close()
    return render_template("accepted1.html", msg='failure')

@app.route('/users')
def users():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()

    sql = "select pname,email,mobile from patient"
    mycursor.execute(sql)
    users = pd.DataFrame(mycursor.fetchall())
    users.columns = ['Patient Name', 'Email', 'Number']
    mydb.close()
    return render_template("users.html", data=users.to_html(index=False))

@app.route('/download')
def download():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()
    sql = "select fname from doctor where email=%s"
    vals=(email1,)
    mycursor.execute(sql,vals)
    df = pd.DataFrame(mycursor.fetchall())
    if mycursor.rowcount > 0:

        return render_template("download.html",data=df)
    return render_template("download.html",msg='failure')

@app.route('/searchfiles',methods=["POST","GET"])
def searchfiles():
    global encfile,fname,query
    if request.method == 'POST':
        #query = request.form['search']
        #words = query.split(" ")
        #encquery = onetimepad.encrypt(query,'random')
        #print('encrypted query is :',encquery)

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()

        sql = "select file, fname from doctor where email = %s"
        vals=(email1,)
        mycursor.execute(sql,vals)
        found = False
        users = pd.DataFrame(mycursor.fetchall())
        if mycursor.rowcount != 0:
                found = True
                encfile = users.iloc[0][0]
                fname = users.iloc[0][1]
        if found == True:
            return render_template('downloadfile.html')
    return render_template("download.html",msg='No Records')

@app.route('/download2',methods=['POST','GET'])
def download2():
            searchfiles()
            key = request.form['k1']
            print('key',key)

            print('key1',key1)
            if key == str(key1):
                file = onetimepad.decrypt(encfile.decode(),'random')
                print("File Content",file)
                file1 = open('f:\\dataleakage\\target\\'+fname+".txt",'w')
                file1.write(str(file))
                file1.close()
                return render_template("success.html",msg='success')
            return render_template("Failure.html", msg='Failure')


@app.route('/downloadfile',methods=['POST','GET'])
def downloadfile():
    return render_template("keydownload.html", msg='Failure')


@app.route('/cloudserver')
def cloudserver():
    return render_template("cloudserver.html")

@app.route('/cloudfiles')
def cloudfiles():
    return render_template("cloudfiles.html")

@app.route('/cloudhome')
def cloudhome():
    return render_template("cloudhome.html")

@app.route('/cloudserver1',methods=['POST','GET'])
def cloudserver1():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        if name == 'cs' and password == 'cs':
            return render_template("cloudhome.html")
    return render_template('cloudserver.html', msg="Invalid Credentials...")

@app.route('/keydownload/<fname1>')
def keydownload(fname1):
    global key1
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()
    sql = "insert into userkey(pname,key1) values (%s,%s)"
    key1 = randint(1, 10000)
    print('Key of the file:', key1)
    vals = (fname1, key1)
    mycursor.execute(sql, vals)
    mydb.commit()

    mycursor = mydb.cursor()
    sql = "select * from userkey where pname=%s"
    vals=(fname1,)
    mycursor.execute(sql,vals)
    users = pd.DataFrame(mycursor.fetchall())
    users.columns = ['Name', 'Key']
    mydb.close()
    return render_template("keydownload.html",data=users.to_html(index=False))

@app.route('/downloadfile1')
def downloadfile1():
    return render_template('downloadfile.html')

@app.route('/ownerhome')
def ownerhome():
    return render_template("ownerhome.html")

@app.route('/cahome')
def cahome():
    return render_template("cahome.html")

@app.route('/dataagent')
def dataagent():
    return render_template("dataagentlogin.html")

@app.route('/dataagentlogin',methods=["POST","GET"])
def dataagentlogin():
    global agentuser
    if request.method == 'POST':
        uname = request.form['user']
        password = request.form['password']

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()
        sql ="select count(*) from dataagent where name=%s and password=%s and password!='blocked'"
        vals=(uname,password)
        mycursor.execute(sql,vals)
        if mycursor.fetchone()[0] > 0:
            agentuser = uname
            return render_template('dataagenthome.html')
    return render_template("dataagentlogin.html",msg='ACCOUNT BLOCKED')

@app.route('/registeragent')
def registeragent():
    return render_template("dataagentregistration.html")

@app.route('/dataagentregistration',methods=["POST","GET"])
def dataagentregistration():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        number = request.form['number']

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="ehr"
    )
    mycursor = mydb.cursor()
    sql = "insert into dataagent values(%s,%s,%s,%s)"
    vals=(name,password,email,number)
    mycursor.execute(sql,vals)
    mydb.commit()
    return render_template("dataagentregistration.html",msg='success')

@app.route('/filedownload',methods=["POST","GET"])
def filedownload():
    return render_template("filedownload.html")

@app.route('/searchforfile',methods=["POST","GET"])
def searchforfile():
    global data1,srch
    if request.method=='POST':
        srch = request.form['file']
        print('file needs to be searched',srch)
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ehr"
        )
        mycursor = mydb.cursor()
        sql = "select content from files where fname = %s"
        vals = (srch,)
        mycursor.execute(sql,vals)
        data2 = mycursor.fetchall()
        if mycursor.rowcount > 0:
            data1 = data2[0][0]
            print('file content',data1)
            return render_template('filedownload.html',data=data1)
    return render_template("filedownload.html",data='null')


@app.route('/tryfordownload',methods=["POST","GET"])
def tryfordownload():
    if request.method == 'POST':
        data = request.form['content']
        if data != data1:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="",
                database="ehr"
            )
            mycursor = mydb.cursor()
            sql = "update dataagent set password='blocked' where name=%s"
            vals=(agentuser,)
            mycursor.execute(sql,vals)
            mydb.commit()

            sql = "insert into attackedfiles values(%s,%s,%s)"
            vals=(agentuser,srch,datetime.now())
            mycursor.execute(sql, vals)
            mydb.commit()

    return render_template("filedownload.html")



if __name__ == ("__main__"):
    app.secret_key = ".."
    app.run(debug=True)