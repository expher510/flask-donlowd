from os import name
from sqlite3.dbapi2 import Cursor
from flask import Flask, app ,template_rendered ,request ,redirect
from flask.templating import render_template
import sqlite3
import requests
import json
from requests.api import post

conect=sqlite3.connect('data.db',check_same_thread=False)
db=conect.cursor()
db.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name,password,email)')

app=Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/sign',methods=['post','get'])
def sign():
    name=request.form.get('username')
    password=request.form.get('password')
    email=request.form.get('email') 
    dataname=db.execute(f'SELECT * FROM users where name="{name}"')
    c=dataname.fetchone()
    if not name:
        massge='write password mother facker'
        return render_template('/main.html',massge=massge)
    if  c !=None :
        massge=f'name alrade exist '
        return render_template('/main.html',massge=massge)
    if not password:
        massge='write password mother facker'
        return render_template('/main.html',massge=massge)
    response = requests.get(f"https://emailvalidation.abstractapi.com/v1/?api_key=4d6dd9fcdfa84e68bbe9cce77ad59520&email={email}")
    x=response.content
    q=json.loads(x)
    format=q['is_valid_format']['value']
    if format == False:
        massge='un valid emali'
        return render_template('/main.html',massge=massge)
    else:
        db.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name,password,email)')
        db.execute(f'INSERT INTO users(name,password,email) VALUES("{name}","{password}","{email}")')
        conect.commit()
        return render_template('/main.html')
@app.route('/main', methods=['post','get'])
def main():
    name=request.form.get('name')
    password=request.form.get('password')
    dataname=db.execute(f'SELECT * FROM users where name="{name.strip()}" and password="{password}"')
    c=dataname.fetchone()
    if not c:
        massge='sign up'
    else:
        massge='u are in'
    return render_template('/main.html',name=massge)
if __name__=="__main":
    app.run(debug=True)