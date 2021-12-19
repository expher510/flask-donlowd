from os import name
from sqlite3.dbapi2 import Cursor
from flask import Flask, app ,render_template ,request ,redirect
import sqlite3
import requests
import json


conect=sqlite3.connect('data.db',check_same_thread=False)
db=conect.cursor()
db.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name,password,email)')

def deeptranslat(texts):
    url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"


    payload = "{\r\n    \"q\": \"%s\",\r\n    \"source\": \"en\",\r\n    \"target\": \"ar\"\r\n}"%(texts)
    headers = {
    'content-type': "application/json",
    'x-rapidapi-host': "deep-translate1.p.rapidapi.com",
    'x-rapidapi-key': "57db9070cdmsh06b567ff745d247p186af7jsnaac444f63237"
    }

    headers = {
    'content-type': "application/json",
    'x-rapidapi-host': "deep-translate1.p.rapidapi.com",
    'x-rapidapi-key': "57db9070cdmsh06b567ff745d247p186af7jsnaac444f63237"
                }
    response = requests.request("POST", url, data=payload, headers=headers)
    r=json.loads(response.text)
    result=r['data']['translations']['translatedText']
    return result

def googletranslat(texts):
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
    target='ar'
    payload = f"q={texts}&target={target}&source=en"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'accept-encoding': "application/gzip",
        'x-rapidapi-host': "google-translate1.p.rapidapi.com",
        'x-rapidapi-key': "57db9070cdmsh06b567ff745d247p186af7jsnaac444f63237"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    
    return response
   
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
        massge='write name pless'
        return render_template('/index.html',massge=massge)
    if  c !=None :
        massge=f'name already exist'
        return render_template('/index.html',massge=massge)
    if not password:
        massge='write password pless'
        return render_template('/index.html',massge=massge)
    response = requests.get(f"https://emailvalidation.abstractapi.com/v1/?api_key=4d6dd9fcdfa84e68bbe9cce77ad59520&email={email}")
    x=response.content
    q=json.loads(x)
    format=q['is_valid_format']['value']
    if format == False:
        massge='invalid email'
        return render_template('/index.html',massge=massge)
    else:
        db.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name,password,email)')
        db.execute(f'INSERT INTO users(name,password,email) VALUES("{name}","{password}","{email}")')
        conect.commit()
        return render_template('/translate.html')
@app.route('/main', methods=['post'])
def main():
    if request.method =='POST':
        name=request.form.get('name')
        password=request.form.get('password')
        dataname=db.execute(f'SELECT * FROM users where name="{name.strip()}" and password="{password}"')
        c=dataname.fetchone() 
        if not c:
            massge=' invaled password or email'
            return render_template('/index.html',massge=massge)
    texts=request.args.get('text')
    laan=request.accept_languages
    lang=laan
    translat_api=request.args.get('translator')
    if translat_api=='google':
        result=googletranslat(texts)
        return render_template('/main.html',result=result ,laan=laan)
    if translat_api== "deep":
        result=deeptranslat(texts)
        return render_template('/main.html',result=result)
    else:
        return render_template('/main.html',result='result')

    
    
    
