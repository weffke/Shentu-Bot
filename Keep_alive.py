from flask import Flask
from threading import Thread


app = Flask('')
stop_keep_alive=0

@app.route('/')
def home():
    return "Hello. I am alive!"

def run():
    app.run(host='0.0.0.0',port=8080)
    
  

def Keep_alive():
    t = Thread(target=run)
    t.start()