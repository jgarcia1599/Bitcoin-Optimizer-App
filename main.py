# please zip the directory that contains your Flask app and upload it to NYU Classes.
from flask import Flask,render_template,request
import requests
from datetime import *
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import pandas
import json
from pathlib import Path
import matplotlib.pyplot as plt
import math
from datetime import date, datetime, timedelta
from pandas.plotting import register_matplotlib_converters
import statistics
import finviz

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/',methods=['POST'])
def calculate():

    # USER INPUT
    user_risk_input=int(request.form['risk'])
    user_amount=int(request.form['amount'])

    register_matplotlib_converters()

    myapikey = 'd259c24ace80ac05a14202761b532b6c3f6154399d23480213b20fce538dbc95'
    headers = {'authorization':f'Apikey {myapikey}'}
    params = {'fsym':'BTC','tsym':'USD','allData':'false','limit':'365'}
    resp = requests.get("https://min-api.cryptocompare.com/data/histoday",params = params,headers = headers)
    resp = resp.json()

    o = []
    c = []
    h = []
    l = []
    dates = []
    for day in resp['Data']:
        o.append(day['open'])
        c.append(day['close'])
        h.append(day['high'])
        l.append(day['low'])
        dates.append(pd.Timestamp.fromtimestamp(day['time']))

    BTCprices = pd.DataFrame(index = dates, columns = ['open','high','low','close'])
    BTCprices['open'] = o
    BTCprices['high'] = h
    BTCprices['low'] = l
    BTCprices['close'] = c 

    close = BTCprices['close'].values
    ret = (close[1:]-close[:-1])/close[:-1]
    r = []

    for d in range(len(c)):
        if d==0:
            continue
        start = (c[d]/c[d-1])-1
        r.append(start)

    # This is for Robin
    BTCretstr = pd.DataFrame(np.append([np.NaN],ret), index = BTCprices.index, columns = ['ret'])
    BTCstdevdaily = statistics.stdev(r)

    BTCreturn = (close[-1]-close[0])/close[0]
    BTCstdev = BTCstdevdaily*math.sqrt(len(r))

    ER_1, SD_1 = BTCreturn, BTCstdev

    #S&P 500 Data
    SPY_return = finviz.get_stock('SPY')['Perf Year']
    SPY_vol = finviz.get_stock('SPY')['Volatility']
    risk_free = 0.01747

    SPY_return = (float(SPY_return.strip('%')))/100
    SPY_vol = (float(SPY_vol[0:4].strip('%'))/100)
    SPY_vol = ((1+SPY_vol)**24)-1

    ER_2, SD_2 = SPY_return, SPY_vol
    ER_f, SD_f = 0.016, 0     # risk free asset -> SD = 0
    c=0.03

    # calcualte the optimal weight
    # cov = c**SD_2*SD_3 (c = correltion of the 2 risky assets)
    w_1 = ((ER_1-ER_f)*SD_2**2 - (ER_2-ER_f)*c*SD_1*SD_2) / ((ER_1-ER_f)*SD_2**2 + (ER_2-ER_f)*SD_1**2 - (ER_1-ER_f+ER_2-ER_f)*c*SD_1*SD_2)
    w_2 = 1-w_1

    # from weight calculate mean variance effecient (MVE)
    mve_x = np.sqrt(w_1**2 * SD_1**2 + w_2**2 * SD_2**2 + 2*w_1*w_2*c*SD_1*SD_2)
    mve_y = w_1*ER_1 + w_2*ER_2

    # calculate the capital allocation line (CAL) (line that combines the risk-free asset and the MVE portfolio)
    # slope = SRp = Sharpe Ratio, we need to get the max SRp
    SR = (mve_y - ER_f)/mve_x

    CAL_x = np.linspace(0, 0.5, num = 10) #create list of 2 numbers in the given interval
    CAL_y = ER_f + (SR)*CAL_x     # calculate the ER for a given SD

    user_risk = user_risk_input
    user_funds = user_amount
    print('\nInitial Investment for Moderately Risk-Averse Investor')
    risk_perc=str(round(CAL_x[user_risk-1]*100,2))
    risk_amount=str(round(CAL_x[user_risk-1]*100,2)*user_amount)
    print('Risk:    ', risk_perc+'%','\t' + str(round((CAL_x[user_risk-1]-SPY_return)*100,2)*-1)+'% less risky the S&P 500')
    e_return=str(round(CAL_y[user_risk-1]*100,2))
    print('Return:  ', e_return+'%','\t' + str(round((CAL_y[user_risk-1]-SPY_return)*100,2))+'% higher return than the S&P 500')
    bonds=str(round((1 - CAL_x[user_risk-1]/mve_x)*user_funds,2)) 
    print('Bonds:  ', '$'+bonds)    # gives % of portfolio that should be invested in bonds, multiply with user input
    btc=str(round((CAL_x[user_risk-1]/mve_x)*w_1*user_funds,2))
    print('BTC:    ', '$'+btc)
    snp500=str(round((CAL_x[user_risk-1]/mve_x)*w_2*user_funds,2))
    print('S&P:    ', '$'+snp500)
    total_received=str(round((1 - CAL_x[user_risk-1]/mve_x)*user_funds + (CAL_x[user_risk-1]/mve_x)*w_1*user_funds + (CAL_x[user_risk-1]/mve_x)*w_2*user_funds,2))
    print('Total:  ', '$'+total_received)
    printresults = True
    
    return render_template("result.html",risk_perc=risk_perc,risk_amount=risk_amount,e_return=e_return,bonds=bonds,btc=btc,snp500=snp500,total_received=total_received,printresults=printresults)
app.run(host='0.0.0.0',port=8000,debug=True)

# More on flask: http://exploreflask.com/en/latest/