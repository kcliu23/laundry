import os
from re import A

from flask import Flask, request, abort
import mysql.connector
from mysql.connector import Error

import datetime
import time
import copy

### LineBot所需要的模組
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError
)
from linebot.models import *

app = Flask(__name__)

line_channel_access_token = 'mOqJN9En2HBRJRpJBUPVs2oAKwyw+U0tZ5PxFzOdIWJs4w9IHY4FcM69vvQX+LEGucmiBtJQ5ukW+p7mDAEJWgX6lrZCNIdDQl0xF+HVFwfjXSssOUbOvfDt1lpHWwBf9bfdKYOvBvZRMJeCxKsIfQdB04t89/1O/w1cDnyilFU=' # # 這邊要貼上你的 bot 的 token (在 line developers 的 Messaging API -> Channel access token 可以找到)
line_channel_secret = '9812f454160055ccef697442174379e5'  # 這邊要貼上你的 bot 的 secert (在 line developers 的 Basic Settings -> Channel secret 可以找到)
line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret)

### 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value?
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


### 訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)  # 判斷訊息類別
def handle_message(event):
    user_text = event.message.text  # 使用者傳給 bot 的東東
    user_text = user_text.split('@')
    user_id = event.source.user_id  # 使用者的line user id
    CONNECTION, CURSOR = connect_db()

    if user_text[0]=='功能選單':
        # final_dict2 = {
        #     "type": "carousel",
            
        #     "contents": []
        # }
        flex_message = {
            "type": "bubble",
            "alignItems":"flex-start",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "功能選單",
                            "weight": "bold"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "我要洗衣服",  # button 上的文字
                            "text": "我要洗衣服" # 按了button 後會傳出去的字
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "我的服務",
                            "text": "我的服務"
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        }
                        ],
                        "margin":"md"
                    }
                ]
            }
            
        }

        flex_message2 = {
            "type": "bubble",
            "alignItems":"flex-start",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "功能選單",
                            "weight": "bold"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "我要洗衣服",  # button 上的文字
                            "text": "我要洗衣服" # 按了button 後會傳出去的字
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "我的服務",
                            "text": "我的服務"
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        }
                        ],
                        "margin":"md"
                    }
                ]
            }
            
        }
                
        line_bot_api.reply_message(event.reply_token, [FlexSendMessage('功能選單', flex_message),FlexSendMessage('功能選單', flex_message2)])

    
    elif user_text[0] == '傳文字':
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text='Hello World!'),TextSendMessage(text='Hello World!')])


    elif user_text[0] == '我要洗衣服': 
    
    ####要取得四個whaher table 的 state 
    ###if state=='1'(使用中) -> 取得lining_num
    ### bulbble內無法使用 if
        user_id = get_userid(event)
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
            
                {
                    "type": "text",
                    "text": "洗衣機狀態",
                    "size": "xs",
                    "color": "#808080"
                },
                {
                    "type": "text",
                    "text": "機台1",  ### 洗衣機編號
                    "weight": "bold",
                    "size": "lg",
                    "margin": "sm"
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "狀態:",
                        "margin": "md",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "text",   ### 洗衣機狀態 #state == '1'
                        "margin": "md",
                        "flex": 9
                    }
                    
                    ],
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "排隊人數:",
                        "margin": "md",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "0",
                        "margin": "md",
                        "flex": 9
                    }
                    ],
                    "margin": "md"
                },
                {
                    # 洗衣機狀態為"使用中/有人前往中"
                    "type": "button",
                    "action": {
                    "type": "message",
                    "label": "我要排隊",
                    "text": "我要排第一台" #將其使用者加入排隊陣列中
                    },
                    "margin": "md",
                    "height": "sm",
                    "style": "primary"
                }
                ]
            }
        }
        for i in range(1,5):
            globals()['final_dict'+str(i)] = {
            "type": "carousel", #旋轉
            "contents": []
            }
            sql = "SELECT `state` FROM `washer_"+str(i)+"` ORDER BY `time` DESC;" # ORDER BY `?????嚙踝蕭嚙?????????????` DESC; 
            sql_lining_num = "SELECT `lining_num` FROM `washer_"+str(i)+"`"
            CURSOR.execute(sql)
            state=CURSOR.fetchall() #拿資料
            CURSOR.execute(sql_lining_num)
            linenum = CURSOR.fetchall()
            if state[0][0] =='1':
                text = "使用中"
            else:
                text = "空機"
            bubble["body"]["contents"][1]["text"] = "機台"+str(i)
            bubble["body"]["contents"][3]["contents"][1]["text"] = text
            bubble["body"]["contents"][4]["contents"][1]["text"] = str(linenum[0][0])
            bubble["body"]["contents"][5]["action"]["text"] = "我要排第"+str(i)+"臺"
            globals()['final_dict'+str(i)]["contents"].append(copy.deepcopy(bubble))
        line_bot_api.reply_message(event.reply_token, [FlexSendMessage('我要洗衣服', final_dict1),FlexSendMessage('我要洗衣服', final_dict2),FlexSendMessage('我要洗衣服', final_dict3),FlexSendMessage('我要洗衣服', final_dict4)])
            

    elif user_text[0] == '我的服務':
        washer_num = 'A'# 洗衣機代號
        left_time = 23  # 剩餘洗滌時間
        lining_people = 3 # 排隊隊伍中在使用者前面的人數
        estimated_time = '17:25 ~ 17:45' # 預估最短時間 ~ 預估最長時間 

        try:
        # 注意引號
        ####要取得user中的state (使用中 == '1' ; 排隊中 == '2';)
        ###if state=='1'(使用中) -> 取得lining_num
        ### bulbble內無法使用 if    
            sql = "SELECT `state` FROM `user`  ORDER BY `time` DESC"; 
            CURSOR.execute(sql)
            state = CURSOR.fetchall()
            if state == '1':
                message = TextSendMessage(text="您正在使用"+washer_num+"洗衣機,距離洗衣完成剩約"+str(left_time)+"分鐘")
            elif state == '2':
                message = TextSendMessage(text="您正在"+washer_num+"洗衣機的排隊隊伍,您前面還有"+left_people+"人,約"+ str(estimated_time)+"時換您")
            else:
                message = TextSendMessage(text="您沒有正在使用的服務喔")
        
        except:
            text = "發生錯誤。"
            message = TextSendMessage(text=text)
        line_bot_api.reply_message(event.reply_token, message)  



    elif user_text[0] == '我要排第1臺':
        user_id = event.source.user_id    
        state = str(2)
        try:
            sql = "INSERT INTO `user` (`user`, `time`, `state`, `washer`) VALUES ('"+user_id+"', '"+get_current_time()+"', '"+state+"', '"+str(1)+"'); "
            CURSOR.execute(sql)
            CONNECTION.commit()
            text = "您已開始排第1臺洗衣機"
            message = TextSendMessage(text=text)
        except:
            text = "發生錯誤。"
            message = TextSendMessage(text=text)
        line_bot_api.reply_message(event.reply_token, message)    
    
# ????????嚙踝蕭嚙?????????????嚙踝蕭嚙???
def connect_db():
    try:
        connection = mysql.connector.connect(
            host='35.77.173.217', #資料庫的host
            # port='3306',  #資料庫的port (通常會是3306)
            database='Laundry', #資料庫名稱
            user='laundry',  #資料庫使用者
            password='12345678', #資料庫密碼
        )
        if connection.is_connected():
            cursor = connection.cursor()

    except Error as e:
        print('資料庫連接失敗,'+'\n'+'錯誤代碼為 '+e)

    return connection, cursor

def get_current_time():
    current_time = str(datetime.datetime.now()).split('.')[0]
    return current_time
def get_userid(event):# 取得使用者ID
    UserId = event.source.user_id
    profile = line_bot_api.get_profile(UserId)
    return profile   
def estimated_time(event,lining_num):
    seconds = time.time()
    result = time.localtime(seconds)
    now_time = result.tm_year + result.tm_mon + result.tm_mday+result.tm_hour+result.tm_min+result.tm_sec

    estimated1 = lining_num * 40 # longest
    estimated2 = lining_num * 34 # shortest
    s = estimated1 % 60  
    t = estimated2 % 60
    i = estimated1 /60
    j =  estimated2 /60

    if result.tm_hour + i > 24 | result.tm_min + s > 60:
        min_estimated_time =( result.tm_hour + i - 24 + 1 ) +":"+( result.tm_min + s - 60)
    elif result.tm_hour + i > 24 | result.tm_min + s < 60:
        min_estimated_time =( result.tm_hour + i-24) +":"+ result.tm_min + s    
    elif result.tm_hour + i < 24 | result.tm_min + s > 60:
        min_estimated_time =( result.tm_hour + i +1 ) +":"+( result.tm_min + s - 60)   
    else:
         min_estimated_time =( result.tm_hour + i ) +":"+( result.tm_min + s )      


    if result.tm_hour + j > 24 | result.tm_min + t > 60:
        max_estimated_time =( result.tm_hour + j - 24 + 1 ) +":"+( result.tm_min + t - 60)
    elif result.tm_hour + j > 24 | result.tm_min + t < 60:
        max_estimated_time =( result.tm_hour + i-24) +":"+ result.tm_min + s    
    elif result.tm_hour + j < 24 | result.tm_min + t > 60:
        max_estimated_time =( result.tm_hour + j +1 ) +":"+( result.tm_min + t - 60)   
    else:
        max_estimated_time =( result.tm_hour + j ) +":"+( result.tm_min + t )     

    estimated_time = min_estimated_time + " ~ " + max_estimated_time

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))  # 這邊的 port 要跟跑 ngrok 的 port 相同
    app.run(host='0.0.0.0', port=port)