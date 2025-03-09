from flask import Flask, render_template,request,send_file,url_for,redirect, render_template_string
import base64,sqlite3,os 
import threading
import cv2,random,string
import nicepay
import requests
import mysql.connector
def get_static_rates():
    # Статические курсы валют относительно RUB
    return {
        "USD": 0.014,  # 1 RUB = 0.014 USD
        "EUR": 0.012,  # 1 RUB = 0.012 EUR
        "KZT": 6.5,    # 1 RUB = 6.5 KZT
        "UAH": 0.4,    # 1 RUB = 0.4 UAH
    }

def convert_currency(amount, from_currency, to_currency):
    rates = get_static_rates()
    
    if to_currency in rates:
        return amount * rates[to_currency]
    else:
        raise Exception(f"Валюта {to_currency} не найдена")

app = Flask(__name__)
conn = mysql.connector.connect(
    host="d8.aurorix.net",
    port=3306,
    user="u83995_YdB7znKWMQ",
    password="1c+DtC^gcTyo.vUtUKCy+gL6",
    database="s83995_ghjfghj")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS payments (
    token TEXT,
    price INT,
    cmd TEXT
)""")
conn.commit()
def gh(v):
    random.seed(v)
    return "".join(random.choices(string.ascii_letters+string.digits,k=len(v+random.randint(0,50))))
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/rules')
def rules():
    return render_template('rules.html')
@app.route('/news')
def news():
    return render_template('news.html')
@app.route('/favicon.ico')
def favicon():
    return send_file("favicon.ico")
@app.route('/favicon.png')
def faviconn():
    return send_file("favicon.png")
@app.route('/pay',methods=['POST'])
def pay():
    ar = request.json
    price = ar['price']*100
    if ar['method'] == "crypto_bot":
        if ar['currency'] != "RUB":
            price = convert_currency(price, "RUB", ar['currency'])
        token = "".join(random.choices(string.ascii_lowercase,k=16))
        try:
            api = nicepay.create_payment("66d0dad66efaafd67116f6bb","uedIE-TIYAG-ZSrbs-bnQ1q-V3fLB",price,f"https://127.0.0.1:5000/success_payment?token={token}",ar['nickname'],ar['currency'])
        except ValueError as exx:
            print({"ok":False,"message":exx.args[0]})
            return {"ok":False,"message":exx.args[0]}
        cursor.execute("INSERT INTO payments (token, price, cmd) VALUES (%s, %s, %s)", (token, ar['price'],ar['cmd'].replace("%player%",ar['nickname'])))
        conn.commit()
        return {"ok":True, "url":api}
from mcrcon import MCRcon
@app.route("/success_payment")
def success():
    token = request.args['token']
    cursor.execute("SELECT cmd FROM payments WHERE token=%s", (token,))
    cmd = cursor.fetchone()
    if cmd == None:
        return redirect(url_for("index"))
    cmd = cmd[0]
    with MCRcon("89.35.130.8", "GbaHXzKlASInBsKlaJbXaUwD",port=25644) as mcr:
        print(cmd)
        resp = mcr.command("lifedonate "+str(cmd))
        print(resp)
    cursor.execute("DELETE FROM payments WHERE token=?", (token,))
    conn.commit()
    return render_template('success.html')
    
    


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
