from flask import Flask, flash, redirect, url_for, render_template, request, session, abort,make_response
import os,json,sqlite3 as sql
import sendgrid
import pdfkit
import stripe
import base64
from datetime import datetime,timedelta
from sendgrid.helpers.mail import *
from collections import defaultdict 
app = Flask(__name__)
alog = False
global mida
admin = 'NULL'
@app.route("/")
def home():
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        return render_template('rb/rb.html',user = session['username'])
@app.route("/admin")
def ahome():
    if not alog:
        return redirect(url_for('do_a_login'))
    else:
        return render_template('admindash/dashboard.html',user = admin)
@app.route("/alogin",methods=['GET','POST'])
def do_a_login():
        if request.method == 'POST':
            global admin
            admin = request.form['username']
            passw = request.form['password']
            conn = sql.connect("db/bus.db")
            conn.row_factory = sql.Row
            cur = conn.cursor()
            cur.execute("select password from administrator_login where username = ?",(admin,))
            rows = cur.fetchall()
            if (len(rows) == 0):
                flash('no such user')
            else:
                for row in rows:
                    if(passw == row['password']):
                        global alog
                        alog = True
                        conn = sql.connect("db/bus.db")
                        conn.row_factory = sql.Row
                        cur = conn.cursor()
                        cur.execute("select admin_id from admin_login_info where username = ?",(admin,))
                        rows = cur.fetchall()
                        global mida
                        mida = rows[0]['admin_id']
                        return redirect(url_for('ahome'))
                    else:
                        flash('wrong password')  
        return render_template('login1.html')    
@app.route('/login', methods=['GET','POST'])
def do_admin_login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        passw = request.form['password']
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select password from member_login where username = ?",(session['username'],))
        rows = cur.fetchall()
        if (len(rows) == 0):
            flash('no such user')
        else:
            for row in rows:
                if(passw == row['password']):
                    session['logged_in'] = True
                    conn = sql.connect("db/bus.db")
                    conn.row_factory = sql.Row
                    cur = conn.cursor()
                    cur.execute("select member_id from member_login_info where username = ?",(session['username'],))
                    rows = cur.fetchall()
                    session['mid'] = rows[0]['member_id']
                    return redirect(url_for('home'))
                else:
                    flash('wrong password')  
    return render_template('login.html')
@app.route('/adminrec',methods=['GET','POST'])
def adminrec():
    if request.method == 'POST':
        un = request.form['username']
        ps = request.form['password']
        mail = request.form['email']
        ph = request.form['phone']
        nm = request.form['name']
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  administrator_login (username,password) values (?,?)",(un,ps))
            conn.commit()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select admin_id from administrator")
        rows = cur.fetchall()
        x = -1
        for row in rows :
            k = row['admin_id']
            x = max(x,int(k[1:len(k)]))
        mida = "a"+str(x+1)
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  administrator (admin_id,name,email_id,phone_number) values (?,?,?,?)",(mida,nm,mail,ph))
            conn.commit()
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  admin_login_info (admin_id,username) values (?,?)",(mida,un))
            conn.commit()
    return redirect(url_for('do_a_login'))
@app.route('/addrec',methods=['GET','POST'])
def addrec():
    if request.method == 'POST':
        un = request.form['username']
        ps = request.form['password']
        mail = request.form['email']
        ph = request.form['phone']
        nm = request.form['name']
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  member_login (username,password) values (?,?)",(un,ps))
            conn.commit()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select member_id from member")
        rows = cur.fetchall()
        x = -1
        for row in rows :
            k = row['member_id']
            x = max(x,int(k[1:len(k)]))
        session['mid'] = "m"+str(x+1)
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  member (member_id,name,email_id,phone_number) values (?,?,?,?)",(session['mid'],nm,mail,ph))
            conn.commit()
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  member_login_info (member_id,username) values (?,?)",(session['mid'],un))
            conn.commit()
    return redirect(url_for('do_admin_login'))
global adjlist
global visited
global pathlist
def create_graph(rows):
    global adjlist
    adjlist = defaultdict(set)
    global visited
    visited = {}
    for i in range(len(rows)):
        adjlist[rows[i]['source']].add(rows[i]['destination'])
        adjlist[rows[i]['destination']].add(rows[i]['source'])
        visited[rows[i]['source']] = False
        visited[rows[i]['destination']] = False
def func(source,destination,path):
    global visited
    global adjlist
    global pathlist
    visited[source] = True
    path.append(source)
    if source == destination:
        pathlist.append(list(path))
    else:
        if adjlist.get(source):
            for i in adjlist.get(source):
                if visited[i] == False:
                    func(i,destination,path)
    path.pop()
    visited[source] = False
def search_node(source,destination):
    global adjlist
    global visited
    path = []
    func(source,destination,path)
global blist
global bnamelist
global busidlist
global busnamelist
global tmpl
global tmp1l
global tmp2l
global mlist
global modelist
def recf(i,j,lst,lst1,lst2):
    global tmpl
    global tmp1l
    global busidlist
    global busnamelist
    global tmp2l
    global modelist
    if j == len(busnamelist[i]):
        tmpl.append(list(lst))
        tmp1l.append(list(lst1))
        tmp2l.append(list(lst2))
    else:
        for id in range(len(busnamelist[i][j])):
            list1 = lst
            list1.append(busidlist[i][j][id])
            list2 = lst1
            list2.append(busnamelist[i][j][id])
            list3 = lst2
            list3.append(modelist[i][j][id])
            recf(i,j+1,list1,list2,list3)
            list1.pop()
            list2.pop()
            list3.pop()

@app.route('/reqbu',methods = ['GET','POST'])
def reqbu():
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        if request.method == 'POST':
            conn = sql.connect("db/bus.db")
            conn.row_factory = sql.Row
            cur = conn.cursor()
            cur.execute("select source,destination from bus")
            rows1 = cur.fetchall();
            src = request.form['source']
            des = request.form['dest']
            global pathlist
            global busidlist
            global busnamelist
            global blist
            global bnamelist
            global tmpl
            global tmp1l
            global tmp2l
            global mlist
            global modelist
            pathlist = []
            create_graph(rows1)
            search_node(src,des)
            busidlist = []
            busnamelist = []
            blist = []
            bnamelist = []
            mlist = []
            modelist = []
            ref = []*(len(pathlist))
            for i in range(len(pathlist)):
                l = []
                bl = []
                ml = []
                for j in range(len(pathlist[i])-1):
                    # print(str(i)+" "+str(j))
                    conn = sql.connect("db/bus.db")
                    conn.row_factory = sql.Row
                    cur = conn.cursor()
                    cur.execute("select * from bus where source = ? and destination = ?",(pathlist[i][j],pathlist[i][j+1]))
                    rows = cur.fetchall()
                    l1 = []
                    l2 = []
                    l3 = []
                    for k in range(len(rows)):
                        # print(str(i)+" "+str(j)+" "+str(k))
                        l1.append(rows[k]['bus_id'])
                        l2.append(rows[k]['bus_name'])
                        l3.append(rows[k]['mode'])
                    l.append(l1)
                    bl.append(l2)
                    ml.append(l3)
                busidlist.append(l)
                busnamelist.append(bl)
                modelist.append(ml)
                tmpl = []
                tmp1l = []
                tmp2l = []
                recf(i,0,[],[],[])
                # print(tmpl)
                blist.append(list(tmpl))
                bnamelist.append(list(tmp1l))
                mlist.append(list(tmp2l))
            return render_template('rb2/rb2.html',src=src,dest=des,data = bnamelist,data2 = pathlist,data3 = mlist,user = session['username'])
total = 0
selseat = []
busid = 'b0'

@app.route('/viewseats1/<id>/<id1>',methods = ['GET','POST'])
def viewseats1(id,id1):
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        if request.method == 'GET':
            global blist
            bidlist = blist[int(id)][int(id1)]
            data = []
            for i in bidlist:
                conn = sql.connect("db/bus.db")
                conn.row_factory = sql.Row
                cur = conn.cursor()
                for row in cur.execute("select * from bus where bus_id = ?",(i,)):
                    data.append(row)
                # rows = cur.fetchall();
                # print(rows["bus_name"])
                # data.append(rows)
            print(data[0][0])
            return render_template('rb2/rb3.html',rows = data,user = session['username'])
    return make_response("hello")
@app.route('/viewseats/<id>',methods = ['GET','POST'])
def viewseats(id):
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        if request.method == 'POST':
            seatsel = str(request.form['seatlist'])
            global total
            total = int(request.form['tot'])
            lit=[]
            global selseat
            selseat = []
            start = 0
            cnt=0
            l=len(seatsel)
            for i in range(0,l) :
                if(seatsel[i]==';'):
                    lit.append(seatsel[start:i]);
                    start = i+1;
                    cnt=cnt+1;
            for i in range(0,cnt) :
                with sql.connect("db/bus.db") as conn:
                    cur = conn.cursor()
                    sr = "s"+str(lit[i])
                    selseat.append(sr)
                    cur.execute("update seats set seat_status='0',time = ? where seat_id = ? and bus_id = ?",(datetime.now()+timedelta(minutes = 1),sr,id))
                    conn.commit()
            return render_template('p.html',amt = total,user = session['username'])
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        bid = id
        cur.execute("select * from seats where bus_id = ?",(bid,))
        rows = cur.fetchall()
        lists=[];
        x=0;
        print(datetime.strptime(rows[0]['time'],"%Y-%m-%d %H:%M:%S.%f"))
        print(datetime.now())
        for row in rows:
            if((row['seat_status'] =='1')or(row['seat_status']=='0'and datetime.strptime(row['time'],"%Y-%m-%d %H:%M:%S.%f")>datetime.now())):
                if(x%4<2):
                    k=x%4+1
                else:
                    k=x%4+2
                strs=str(int(x/4)+1)+"_"+str(k)
                lists.append(strs)
            elif(row['seat_status']=='0'and datetime.strptime(row['time'],"%Y-%m-%d %H:%M:%S.%f")<=datetime.now()):
                 with sql.connect("db/bus.db") as conn:
                    cur = conn.cursor()
                    cur.execute("update seats set seat_status='-1' where seat_id = ? and bus_id = ?",(row['seat_id'],id))
                    conn.commit()
            x=x+1;
        return render_template('viewseat.html',id=id,lent = len(rows),list=json.dumps(lists),user = session['username']);
@app.route('/pay',methods = ["GET","POST"])
def pay():
    global selseat
    cnt = len(selseat)
    global busid
    for i in range(0,cnt) :
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        print(selseat[i])
        cur.execute("select seat_status from seats where seat_id = ? and bus_id = ?",(selseat[i],busid))
        rows = cur.fetchall()
        for row in rows:
            if(row['seat_status']=='1'):
                return redirect(url_for('viewseats',id = busid))
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            # print(selseat[i])
            # x = str(selseat[i])
            # query = "update seats set seat_status='1' where seat_id = " + x + " and bus_id = " + busid;
            cur.execute("update seats set seat_status='1' where seat_id = ? and bus_id = ?",(selseat[i],busid))
            conn.commit()
    conn = sql.connect("db/bus.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select * from payment")
    rows = cur.fetchall()
    x = len(rows)
    p = "p"+str(x+1)
    conn = sql.connect("db/bus.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select * from pays")
    rows = cur.fetchall()
    x = len(rows)
    u = "up"+str(x+1)
    conn = sql.connect("db/bus.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select uid from booked")
    rows = cur.fetchall()
    x = -1
    for row in rows :
        k = row['uid']
        x = max(x,int(k[2:len(k)]))
    bo = "bp"+str(x+1)
    with sql.connect("db/bus.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO payment values (?,?,?)",(p,total,datetime.now()))
        conn.commit()
    with sql.connect("db/bus.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO pays values (?,?,?)",(u,session['mid'],p))
        conn.commit()
    with sql.connect("db/bus.db") as conn:
        cnt = len(selseat)
        for i in range (0,cnt):
            cur = conn.cursor()
            cur.execute("INSERT INTO booked values (?,?,?,?)",(bo,p,selseat[i],busid))
            bo = "bp"+str(int(bo[2:len(bo)])+1)
            conn.commit()
    global resp
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    rendered = render_template('invoice1.html',x = p,bus = busid,selseat = selseat,l = cnt,total = int(total/cnt)*cnt,unit=int(total/cnt),user = session['username'])
    pdf = pdfkit.from_string(rendered,False,configuration=config)
    resp = make_response(pdf)
    resp.headers['Content-Type'] = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attatchment; filename=op.pdf'
    encoded = base64.b64encode(pdf).decode()
    attachment = Attachment()
    attachment.content = encoded
    attachment.type = "application/pdf"
    attachment.filename = "my_pdf_attachment.pdf"
    attachment.disposition = "attachment"
    attachment.content_id = "PDF Document file"
    sg = sendgrid.SendGridAPIClient(apikey="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")
    from_email = Email("hj.harshit007@gmail.com")
    to_email = Email(request.form['stripeEmail'])
    content = Content("text/html", 'Hello')
    mail = Mail(from_email, 'Attachment mail PDF', to_email, content)
    mail.add_attachment(attachment)
    response = sg.client.mail.send.post(request_body=mail.get())
    stripe.api_key = 'sk_test_vtOKl0ZcIcd1cXpqWl9t30h3'
    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=total*100,
        currency='usd',
        description='seats'
    )       
    return render_template('invoice.html',x = p,bus = busid,selseat = selseat,l = cnt,total = int(total/cnt)*cnt,unit=int(total/cnt),user = session['username'])      
@app.route('/aboard')
def aboard():
    return render_template('admindash/dashboard.html',user = admin)
@app.route('/getpdf')
def getpdf():
    global resp
    return resp
@app.route('/addbus',methods = ["GET","POST"])
def addbus():
    if not alog:
        return redirect(url_for('do_a_login'))
    else:
        bus_id = request.form['busid']
        bus_name = request.form['busname']
        source = request.form['source']
        dest = request.form['destination']
        startt = request.form['starttime']
        startd = request.form['startdate']
        sno = request.form['sno']
        mode = request.form['mode']
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO bus values (?,?,?,?,?,?,?,?)",(bus_id,bus_name,source,dest,startd,startt,sno,mode))
            conn.commit()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select * from seats")
        rows = cur.fetchall()
        n = len(rows)
        for i in range(1,int(sno)+1):
            sid = "s"+str(i)
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO seats values (?,?,?,?,?)",(sid,bus_id,'a','-1',datetime.now()))
                conn.commit()
        return render_template('admindash/dashboard.html',user = admin)
@app.route('/rembus',methods = ["GET","POST"])
def rembus():
    if not alog:
        return redirect(url_for('do_a_login'))
    else:
        bus_id = request.form['remid']
        with sql.connect("db/bus.db") as conn:
            cur = conn.cursor()
            cur.execute("Delete from bus where bus_id = ?",(bus_id,))
            conn.commit()
        return render_template('admindash/dashboard.html',user = admin)
@app.route('/dashboard/<id>',methods = ["GET","POST"])
def dash(id):
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        if request.method == 'POST':
            x = request.form['st']
            y = request.form['bs']
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("delete from booked where bus_id = ? AND seat_id = ?",(y,x))
                conn.commit()
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("update seats set seat_status='-1' where seat_id = ? and bus_id = ?",(x,y))
                conn.commit()
            return redirect(url_for('dash',id = id))
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select payment_id from pays where member_id = ?",(id,))
        rows = cur.fetchall()
        datab=[]
        datas=[]
        for row in rows:
            conn = sql.connect("db/bus.db")
            conn.row_factory = sql.Row
            cur = conn.cursor()
            cur.execute("select bus_id,seat_id from booked where payment_id = ?",(row['payment_id'],))
            rowss = cur.fetchall()
            for ro in rowss:
                datab.append(ro['bus_id'])
                datas.append(ro['seat_id'])
        l = len(datas)
        return render_template('userdash/dashboard.html',datab = datab,datas = datas,id = id,l = l,user = session['username']);
@app.route('/apro',methods = ["GET","POST"])
def apro():
    if not alog:
        return redirect(url_for('do_a_login'))
    else:
        if request.method == 'POST':
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("update administrator set name = ? , email_id = ? , phone_number = ? where admin_id = ?",(request.form['name'],request.form['phone'],request.form['email'],mida))
                conn.commit()
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("update administrator_login set password = ? where username = ?",(request.form['pass'],request.form['username']))
                conn.commit()
            return redirect(url_for('apro'))   
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select * from administrator where admin_id = ?",(mida,))
        rows = cur.fetchall()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select username from admin_login_info where admin_id = ?",(mida,))
        rows1 = cur.fetchall()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select password from administrator_login where username = ?",(rows1[0]['username'],))
        rows2 = cur.fetchall()
        return render_template('admindash/user.html',rows = rows,rows1 = rows1,rows2 = rows2)
@app.route('/mpro',methods = ["GET","POST"])
def mpro():
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        if request.method == 'POST':
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("update member set name = ? , email_id = ? , phone_number = ? where member_id = ?",(request.form['name'],request.form['phone'],request.form['email'],session['mid']))
                conn.commit()
            with sql.connect("db/bus.db") as conn:
                cur = conn.cursor()
                cur.execute("update member_login set password = ? where username = ?",(request.form['pass'],request.form['username']))
                conn.commit()
            return redirect(url_for('mpro'))   
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select * from member where member_id = ?",(session['mid'],))
        rows = cur.fetchall()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select username from member_login_info where member_id = ?",(session['mid'],))
        rows1 = cur.fetchall()
        conn = sql.connect("db/bus.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("select password from member_login where username = ?",(rows1[0]['username'],))
        rows2 = cur.fetchall()
        return render_template('userdash/user.html',rows = rows,rows1 = rows1,rows2 = rows2)
@app.route('/dboard',methods = ["GET","POST"])
def dboard():
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        return redirect(url_for('dash',id = session['mid']))
@app.route('/memout',methods = ["GET","POST"])
def memout():
    if not session.get('logged_in'):
        return redirect(url_for('do_admin_login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('do_admin_login'))
@app.route('/aout',methods = ["GET","POST"])
def aout():
    global alog
    if not alog:
        return redirect(url_for('do_a_login'))
    else:
        alog = False
        return redirect(url_for('do_a_login'))
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)