# please zip the directory that contains your Flask app and upload it to NYU Classes.
from flask import Flask,render_template
import requests
from datetime import *

app = Flask(__name__)

@app.route('/')
def hello_visitor():

    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date= datetime.now().strftime('%Y-%m-%d')
    time=datetime.now().strftime('%H:%M:%S')

    message="The date is {d} and time is {t}".format(d=date,t=time)

    return render_template("index.html",message=message)


app.run(host='0.0.0.0',port=5000,debug=True)

# More on flask: http://exploreflask.com/en/latest/