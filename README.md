stock-ship-checker
===

## 動機
相信許多人平時課業或工作繁重，因此不想多花時間去看自己的股票APP，怕影響心情，做出不必要的買賣，所以做出了能查詢股價的line-bot，例如可能半個月看一次這個月的股價變化就好，並且最近進入大航海時代，因此也提供了FBX的航運報價，以提供使用者了解航運景氣的變動。
## 作品介紹
在Line-bot上以圖文選單的方式供使用者選擇功能，第一個是輸入上市股價代號，並回傳此月的股價，以及繪製近兩個月的K棒給使用者(上櫃股目前還不行)，而第二個是能查詢美洲航線很重要的FBX航運報價，並繪製當月的價格折線圖給用戶。

## 環境
### env
- Ubuntu 20.04.2 LTS
- Python 3.8.5
### python package

- 套件都放在requirement.txt，可用以下指令下載
```
pip install -r requirements.txt
```
## 如何架設

由於此程式需要使用line-bot，關於line-bot的架設請參考我寫的這篇: https://hackmd.io/s_WRq6dJTsmak8wrI9WvvA

Line-bot與Flask做連接請參考這篇:
https://hackmd.io/LR1MrUUgTR2y44Ys9yTAWw#

看完以上兩個連結變可完成架設

## line-bot介面

<p>
<img src="https://i.imgur.com/EO0UiEP.jpg" alt="first" height="500" width="300" >
<img src="https://i.imgur.com/4IdWGCL.jpg" alt="first" height="500" width="300" >
</p>


## 使用方法
- 使用者點擊左方圖文選單，會跑出查詢股價，系統回傳請輸入股票代號
- 使用者輸入上市股價代號，系統回傳該股票這個月的目前的日期與股價，並回傳進兩個月的K棒圖
<div style="float:left">
<img src="https://user-images.githubusercontent.com/46188299/122892122-b4092800-d377-11eb-9279-1873e4216a61.gif"  alt="123" height="500" width="300">
<img src="https://user-images.githubusercontent.com/46188299/122892744-3d205f00-d378-11eb-8048-f172e3591738.gif"  alt="123" height="500" width="300">
</div>
- 使用者點擊右方圖文選單，會跑出最新FBX航運價格與近十天價格折線圖
<p>
<img src="https://i.imgur.com/6wqIBob.gif"  alt="123" height="500" width="300">
</p>

## 使用的API介紹

* 台灣證券交易所:
    https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&stockNo= ，stockNo=>上市股票代號

* 台灣證券交易所:https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=&stockNo= ，date=日期(ex:20210501)，stockNo=>上市股票代號

* FBX:https://fbx.freightos.com/api/lane/FBX?isDaily=true
，isDaily=true=>回傳每日航運價格，isDaily=false=>一周航運價格
* Flask架設API:[https://ar3s.dev/stock/getpic?file=](https://ar3s.dev/stock/getpic?file=) ，file=candle.png or fbx.png
* Line message API



## stock.py功能講解
1. flask架設
2. line-bot連接
3. 利用Line-bot API回傳股價，以及航運報價
4. 如何傳照片講解
---
### 1.Flask架設
建立Flask物件，並且設定靜態資料夾，用來存放line-bot要回傳的圖片，而所選擇的資料是linux環境內建的tmp，如果用heroku也是同樣概念，結構如下

```python
app = Flask(__name__, static_folder='/tmp/')
```

![](https://i.imgur.com/LsxYvHw.png)



建立測試路由，以供測試
```python
@app.route("/")
def test():
    return "Hello"
```
開啟flask路由，port開在7777
```python
if __name__=="__main__":
    app.run(port=7777)
```

### 2.line-bot連接


關於如何建立line-bot及圖文選單請參考我寫的這篇文章:
[Google](https://www.google.com.tw)

設定Channel secret及
Channel access token

```python
#請填入自己的line-bot Chennel access token以及Channel secret 
line_bot_api = LineBotApi('聊天機器人的 Chennel access token')

handler = WebhookHandler('聊天機器人的 Channel secret')  
```   


建立callback路由，
檢查 LINE Bot的資料是否正確，藉由此路由與將line-bot與flask server做連接
```python
@app.route("/callback",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body=request.get_data(as_text=True)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
```


<img src="https://i.imgur.com/T59Ttdg.png" alt="error" height="300" width="600">

當使用者傳送訊息給LINE Bot時，會觸發MessageEvent事件，此處僅處理收到的文字訊息，「message = TextMessage」表示收到的是文字訊息，也就是說收到的是文字訊息才會由此路由處理，參數event包含傳回的各項訊息，例如建立的函式名稱為handle_message
```
@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    ...
```

### 3.利用Message API回傳股價和航運報價
#### 3.1 取得使用者傳送的文字於mtext變數中
```python
mtext = event.message.text
```

#### 3.2 使用者點擊左方圖文選單
系統藉由 reply_message 將"請輸入股價代號"回傳給使用者
```python
if mtext == "查詢股價":
    try:
        message = TextSendMessage(
            text = "請輸入股價代號"
        )
        line_bot_api.reply_message(event.reply_token,message)

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
```
#### 3.3 使用者點擊右方圖文選單
會先對該api進行get請求，請把結果轉為json格式，由於我們需要的資料在indexPoints裡，所以取["indexPoints"]放入fbx變數裡

第6行``save_img``能取得近十天航運價格的摺線圖網址，後面會有詳細說明

10-14行處理完之後可以得到當天最新航運價格與前一天差多少，ex:2021/06/21 6218點 相較昨日上升:34.1點

16-19行把此資訊傳送給使用者

20-26行是使用push_message這個function，因為line-bot要回傳兩個訊息以上的話不能再選擇``reply_message``，這邊我選擇``push_message``，並且使用`ImageSendMessage`，傳送圖檔

```python
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
```
#### 3.4 輸入上市股票代號
使用者輸入文字之後，先使用Regular Expression判斷只有數字才能進行操作

接著在3-10行對台灣證券交易所API取得該股票的股價，所以如果這時候使用者輸入錯誤的股票代號，就會進到38-39行的except輸出查無此股票

12-15行回傳股價資訊

17-25行進行近兩個月份的K棒，month_k_plot這個function後面會介紹

27行取得剛剛繪製的K棒網址

29-37行傳送給使用者K棒圖片
 
```python
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
```
- 3.4.1 繪製K棒講解

    - ``get_stock_data(start_year, start_month, end_year, end_month,No):start_year=起始年，start_month=起始月，end_year=結束年,end_month=結束月,No=股票代號``

        2-4行傳入的開始年月與結束年月算出其範圍並取該日的第一天，ex:get_stock_data(2021,04,2021,06) => month_list = [2021/04/01,2021/05/01,2021/06/01]
這是為了符合API回傳的資訊

        5-17行是對API進行request並剃除我們不需要的資料，並繪製成dataframe的形式，以利後面plotly繪圖套件的格式
        
    - ``month_k_plot(start_year, start_month, end_year, end_month,No):start_year=起始年，start_month=起始月，end_year=結束年,end_month=結束月,No=股票代號``
    
        23行先取得近兩個月資料的dataframe形式放入stock
        
        25行將stock使用plotly進行K棒的繪製，由於參數則填入dataframe的欄位，以及K棒顏色調成台灣人習慣的模式
        
        34行將圖片存入tmp資料夾內，以供存取
```python
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

    fig = go.Figure(data=[go.Candlestick(x=stock['Date'],
                    open=stock['Open'],
                    high=stock['High'],
                    low=stock['Low'],
                    close=stock['Close'],
                    increasing_line_color= 'red', 
                    decreasing_line_color= 'green')])
    fig.update_layout(xaxis_rangeslider_visible=False)
   
    plotly.io.write_image(fig,'/tmp/candle.png',format="png")

    return fig
```
### 4.如何傳照片講解
``save_img(url,select,Pass): url=照片儲存位置，select看要存取K棒圖片或是航運價格圖片，Pass=航運價格資料``
    
12,20行先判斷為航運價格或是股價K棒，如果是航運價格的話就取近10天的資訊繪製成圖片放入tmp資料夾，而在19行要回傳的是呼叫自己的API `https://ar3s.dev/stock/getpic?file=`取得照片，因為在line-bot的ImageSendMessage(
                original_content_url=im_url,
                preview_image_url=im_url
            )，im_url限定是https開頭的網址，所以在這裡使用了這個方法完成此目的，而股價K棒也是同概念，不另作說明

1-7行是判斷是否傳來的資訊為fbx.png or candle.png，是的話就使用flask內建的``send_from_directory``function回傳整張png圖檔，若不是的話則回傳錯誤訊息
```python
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
```



## Reference
