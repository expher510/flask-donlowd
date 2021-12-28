from os import link, name
from flask import Flask, render_template, request, redirect, session, url_for
from flask import app
import sqlite3
import json
import datetime
import requests


def clean(char):
    # for sql injector
    string = "" if char is None else char
    x = string.replace("'", '"')
    return x


conect = sqlite3.connect('data.db', check_same_thread=False)
db = conect.cursor()
db.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name,password,email)')
db.execute('CREATE TABLE IF NOT EXISTS body(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,date,name,quat,summary,writer,book_linke)')


app = Flask(__name__)


app.secret_key = "hello"


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign', methods=['post', 'get'])
def sign():
    name = clean(request.form.get('username'))
    password = clean(request.form.get('password'))
    email = clean(request.form.get('email'))
    dataname = db.execute(f"SELECT * FROM users where name='{name}'")
    c = dataname.fetchone()
# validation
    if not name:
        massge = 'write name pless'
        return render_template('/login.html', massge=massge)
    if c != None:
        massge = f'name already exist'
        return render_template('/login.html', massge=massge)
    if not password:
        massge = 'write password pless'
        return render_template('/login.html', massge=massge)
    response = requests.get(
        f"https://emailvalidation.abstractapi.com/v1/?api_key=4d6dd9fcdfa84e68bbe9cce77ad59520&email={email}")
    x = response.content
    q = json.loads(x)
    format = q['is_valid_format']['value']

    if format == False:
        massge = 'invalid email'
        return render_template('/login.html', massge=massge)
# end of validation
    else:
        # save user and email in database
        db.execute(
            'CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name,password,email)')
        db.execute(
            f"INSERT INTO users(name,password,email) VALUES('{name}','{password}','{email}')")
        conect.commit()
        session['user'] = name

        return redirect('/')


@app.route('/main', methods=['post'])
def main():
    if request.method == 'POST':
        name = clean(request.form.get('username'))
        password = clean(request.form.get('password'))
# validation
        dataname = db.execute(
            f"SELECT * FROM users where name='{name}' and password='{password}'")
        c = dataname.fetchone()
        if not c:
            massge = ' invaled password or email'
            return render_template('/login.html', massge=f"{name}__{password}")
        session['user'] = name

        return render_template('/control.html')


@app.route('/control', methods=['post', 'get'])
def control():
    if request.method == "POST":
        name = clean(request.form.get('name'))
        quat = clean(request.form.get('quat'))
        summary = clean(request.form.get('summary'))
        book_linke = clean(request.form.get('book_linke'))
        writer = session['user']
        x = datetime.datetime.now()
        time = x.strftime("%Y %b %d ")
        # save the booke data in database
        db.execute(
            f"INSERT INTO body(date,name,quat,summary,writer,book_linke) VALUES('{time}','{name}','{quat}','{summary}' ,'{writer}','{book_linke}')")
        conect.commit()
        return render_template('/control.html', massge='ok')
    if 'user' in session and session['user'] != None:
        return render_template('/control.html')

    return redirect("/login")


@app.route('/logout')
def loguot():
    session['user'] = None
    return redirect(url_for('index'))


@app.route('/')
def index():
    search = clean(request.args.get('search'))
    linke = clean(request.args.get('linke'))
    if linke:
        dataname = db.execute(f"SELECT * FROM body where writer='{linke}'")
        c = dataname.fetchall()
        return render_template('/index.html', c=c)
    if search:
        dataname = db.execute(
            f"SELECT * FROM body where name  like '%{search}%'")
        c = dataname.fetchall()
        if c:
            return render_template('/index.html', c=c)
        else:
            return render_template(f'/index.html', massge=search)

    else:
        dataname = db.execute(f'SELECT * FROM body')
        c = dataname.fetchall()
        return render_template('/index.html', c=c)


@app.route('/edit', methods=["post", "get"])
def edit():
    if request.method == "POST":
        id_delet = request.form.get("delet")
        edit_summary = request.form.get("edit_sumrray")
        id_edit = request.form.get('id_edit')
        if id_edit:
            db.execute(
                f"UPDATE  body SET summary ='{edit_summary}' WHERE ID={id_edit} and writer='{session['user']}'")

        if id_delet:
            db.execute(
                f"DELETE FROM body WHERE ID={id_delet} and writer='{session['user']}'")

        conect.commit()
        redirect('/edit')
    dataname = db.execute(
        f"SELECT * FROM body Where writer='{session['user']}'")
    c = dataname.fetchall()
    if c:
        return render_template('/edit.html', c=c)
    else:
        return render_template('/edit.html', massge="summary")

