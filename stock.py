#!/usr/bin/env python
#coding=utf-8
from bs4 import BeautifulSoup
import requests
from flask import Flask,request,abort,send_from_directory
import json
import re

from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage,ImageSendMessage,StickerSendMessage,LocationSendMessage,QuickReply,QuickReplyButton,MessageAction
import matplotlib.pyplot as plt

import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go,plotly

import every_No as G

everyNo = G.get()

headers = {
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

app = Flask(__name__, static_folder='/tmp/')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

line_bot_api = LineBotApi('')

handler = WebhookHandler('')  

def get_stock_data(start_year, start_month, end_year, end_month,No):
    start_date = str(date(start_year, start_month, 1))
    end_date = str(date(end_year, end_month, 1))
    month_list = pd.date_range(start_date, end_date, freq='MS').strftime("%Y%m%d").tolist()
    df = pd.DataFrame()
    for month in month_list:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date="+month+"&stockNo={}".format(No)
        res = requests.get(url)
        stock_json = res.json()['data']
        for i in range(0,len(stock_json)):
            del stock_json[i][1:3]
            del stock_json[i][5:7]
        #print(stock_json)
        stock_df = pd.DataFrame.from_dict(stock_json)
        df = df.append(stock_df, ignore_index = True)
        
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    #print(df)
    return df

def month_k_plot(start_year, start_month, end_year, end_month,No):

    stock = get_stock_data(start_year = start_year, start_month = start_month, end_year = end_year, end_month = end_month,No = No)
    #print(stock)
    # for col in range(1, 5):
    #     for row in range(stock.shape[0]):
    #         stock.iloc[row, col] = float(stock.iloc[row,col].replace(',', ''))

    fig = go.Figure(data=[go.Candlestick(x=stock['Date'],
                    open=stock['Open'],
                    high=stock['High'],
                    low=stock['Low'],
                    close=stock['Close'],
                    increasing_line_color= 'red', 
                    decreasing_line_color= 'green')])
    fig.update_layout(xaxis_rangeslider_visible=False)
    #print(fig)
    plotly.io.write_image(fig,'/tmp/candle.png',format="png")
    #fig.write_image("")
    #fig.write_html("test.html",auto_open=True)
    
    return fig

@app.route("/")
def test():
    return "Hello"

@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body=request.get_data(as_text=True)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/getpic",methods=['GET'])
def getpic():
    filee = request.args.get('file')
    if(filee == "fbx.png" or filee == "candle.png"):
        return send_from_directory(app.static_folder,f'{filee}')
    else:
        return {'error:':'please enter file = fbx.png or candle.png. ex: https://ar3s.dev/stock/getpic?file=candle.png'}

def save_img(url,select,Pass):
    x = []
    y = []
    if select == "fbx":
        for i in range(-10,0):
            x.append(Pass[i]['indexDate'])
            y.append(Pass[i]['value'])
        plt.xticks(rotation=15) 
        plt.plot(x, y, color='blue', linewidth=2, marker='o') # Step 3&4
        plt.savefig(url)
        return f'https://ar3s.dev/stock/getpic?file=fbx.png'
    elif select == "stock":
        return f'https://ar3s.dev/stock/getpic?file=candle.png'
    
@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    #print(mtext)
    if mtext == "查詢股價":
        try:
            message = TextSendMessage(
                text = "請輸入股價代號"
            )
            line_bot_api.reply_message(event.reply_token,message)
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
    elif mtext == "FBX航運價格":
        try:
            response = requests.get('https://fbx.freightos.com/api/lane/FBX?isDaily=true')
            fbx = response.json()['indexPoints']
            
            im_url = save_img("/tmp/fbx.png","fbx",fbx)
            
            test = ""
        
            if float(fbx[-1]['value']) > float(fbx[-2]['value']): 
                test = "相較昨日上升:" 
            else: 
                test = "相較昨日下降:"
            text = str(fbx[-1]['indexDate'])+'\n'+ str(fbx[-1]['value'])+'\n' + test + str(round(abs((float(fbx[-1]['value']) - float(fbx[-2]['value'])) ),2)) + "點"
            
            message = TextSendMessage(
                text = text
            )
            line_bot_api.reply_message(event.reply_token,message)
            user_id = event.source.user_id
            line_bot_api.push_message(
                user_id,
                ImageSendMessage(
                    original_content_url=im_url,
                    preview_image_url=im_url
                )
            )
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
            
    elif re.match(r'^[0-9]+$',mtext):
        try:
            response = requests.get('https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&stockNo={}'.format(str(mtext)))
            stock = response.json()['data']
            text = everyNo[mtext] + '\n'
            for i in range(0,len(stock)):
                if(i != len(stock) - 1):
                    text += "日期:" + stock[i][0] + '\n' + "股價:" + stock[i][1] + '\n'
                else:
                    text += stock[i][0] + '\n' + "股價:" + stock[i][1]
            
            #im_url = save_img("/tmp/stock.png","stock",stock)
            
            message = TextSendMessage(
                text = text
            )
            line_bot_api.reply_message(event.reply_token,message)

            today = datetime.today()
            month = today.month
            year = today.year
            pre_month = month - 1
            pre_year = year
            if month == 1:
                pre_month = 12
                pre_year = year - 1
            month_k_plot(pre_year, pre_month, year,month,mtext)

            im_url = save_img("/tmp/candle.png","stock","")

            user_id = event.source.user_id

            line_bot_api.push_message(
                user_id,
                ImageSendMessage(
                    original_content_url=im_url,
                    preview_image_url=im_url
                )
            )
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='查無此股票!!!'))
    
if __name__=="__main__":
    app.run(port=7777)