import os
import datetime
import copy

import mysql.connector
from mysql.connector import Error

from flask import Flask, request, abort

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

line_channel_access_token = 'mOqJN9En2HBRJRpJBUPVs2oAKwyw+U0tZ5PxFzOdIWJs4w9IHY4FcM69vvQX+LEGucmiBtJQ5ukW+p7mDAEJWgX6lrZCNIdDQl0xF+HVFwfjXSssOUbOvfDt1lpHWwBf9bfdKYOvBvZRMJeCxKsIfQdB04t89/1O/w1cDnyilFU=' # 這邊要貼上你的 bot 的 token (在 line developers 的 Messaging API -> Channel access token 可以找到)
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
    # if user_text[0]=='功能選單':
    if user_text[0]=='我要洗衣服':
        flex_message = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "洗衣機狀態",
                        "weight": "bold"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "機台1:空機",
                        
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
                        # "text": "我要洗衣服" # 按了button 後會傳出去的字
                        "text": "我要洗衣" 
                        },
                        "margin": "md",
                        "height": "sm",
                        "style": "primary"
                    },

                    {
                        "type": "text",
                        "text": "機台2:使用中",
                        # "text": "test",
                        # "weight": "bold"

                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "我的服務",
                        # "text": "我的服務"
                        "text": "我要排隊"
                        },
                        "margin": "md",
                        "height": "sm",
                        "style": "primary"
                    },
                    {
                        "type": "text",
                        "text": "機台3:使用中",
                        # "text": "test",
                        # "weight": "bold"

                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "我的服務",
                        # "text": "我的服務"
                        "text": "我要排隊"
                        },
                        "margin": "md",
                        "height": "sm",
                        "style": "primary"
                    },
                    {
                        "type": "text",
                        "text": "機台4:有人正要使用",
                        # "text": "test",
                        # "weight": "bold"

                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "我的服務",
                        # "text": "我的服務"
                        "text": "我要排隊"
                        },
                        "margin": "md",
                        "height": "sm",
                        "style": "primary"
                    }

                ]
            }
        }
        line_bot_api.reply_message(
        event.reply_token, FlexSendMessage("功能選單", flex_message))
            
    elif user_text[0] == '我要洗衣服':
        final_dict = {
            "type": "carousel", #旋轉
            "contents": []
        }

        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "會員基本資料總覽",
                    "size": "xs",
                    "color": "#808080"
                },
                {
                    "type": "text",
                    # "text": "王小明",  ### 會員姓名
                    "text": "A",  ### 洗衣機編號
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
                        # "text": "性別:",
                        "text": "狀態:",
                        "margin": "md",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "使用中",  ### 洗衣機狀態
                        "margin": "md",
                        "flex": 9
                    }
                    ],
                    "margin": "md"
                },
                #{
                #    "type": "box",
                #    "layout": "horizontal",
                #    "contents": [
                #    {
                #         "type": "text",
                #         "text": "手機號碼:",
                #         "margin": "md",
                #         "flex": 4
                #     },
                #     {
                #         "type": "text",
                #         "text": "0983911599",   ### 會員手機號碼
                #         "margin": "md",
                #         "flex": 9
                #     }
                #     ],
                #     "margin": "md"
                # },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        # "text": "入會時間:",
                        "text": "排隊人數:",
                        "margin": "md",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        # "text": "2022-07-13 14:00:22",   ### 會員入會時間
                        "text": "2",
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
                    "text": "您已開始排隊" #將其使用者加入排隊陣列中
                    },
                    "margin": "md",
                    "height": "sm",
                    "style": "primary"
                },
                {
                    # 洗衣機狀態為"空機"
                    "type": "button",
                    "action": {
                    "type": "message",
                    "label": "我要去洗",
                    "text": "洗衣機狀態已改為'有人前往中'請在五分鐘內開始洗衣,謝謝" #更改洗衣機狀態
                    #五分鐘後發送確認訊息
                    },
                    "margin": "md",
                    "height": "sm",
                    "style": "primary"
                    }
                ]
            }
        }

        sql = "SELECT `手機號碼`, `姓名`, `性別`, `入會時間` FROM `會員基本資料` ORDER BY `入會時間` DESC; "
        CURSOR.execute(sql)
        infos=CURSOR.fetchall()

        for info in infos:
            phone = info[0]
            name = info[1]
            gender = info[2]
            time = info[3]
            bubble["body"]["contents"][1]["text"] = name
            bubble["body"]["contents"][3]["contents"][1]["text"] = gender
            bubble["body"]["contents"][4]["contents"][1]["text"] = phone
            # bubble["body"]["contents"][5]["contents"][1]["text"] = str(time)
            final_dict["contents"].append(copy.deepcopy(bubble))
        
        message = FlexSendMessage('會員資料總覽', final_dict)
        line_bot_api.reply_message(event.reply_token, message)

        

    elif user_text[0] == '我的服務':
        state = '正在洗'
        washer_num = 'A'# 洗衣機代號
        left_time = 23 # 剩餘洗滌時間
        left_people = 3 # 排隊隊伍中在使用者前面的人數
        estimated_time = '17:25 ~ 17:45' #預估最短時間 ~ 預估最長時間


        if state == '正在洗':
            message = TextSendMessage(text="您正在使用"+str(washer_num)+"洗衣機,距離洗衣完成剩約"+str(left_time)+"分鐘")
        elif state == '排隊中':
            message = TextSendMessage(text="您正在"+washer_num+"洗衣機的排隊隊伍,您前面還有"+str(left_people)+"人,約"+ estimated_time+"時換您")
        else:
            message = TextSendMessage(text="您沒有正在使用的服務喔")
        line_bot_api.reply_message(event.reply_token, message)

    elif user_text[0] == '我要洗衣服':
        final_dict = {
            "type": "carousel", #旋轉
            "contents": []
        }

        bubble ={
        "type": "template",
        "altText": "Example confirm template",
        "template": {
            "type": "confirm",
            "text": "Are you sure?",
            "actions": [
                {
                    "type": "message",
                    "label": "Yes",
                    "text": "Yes"
                },
                {
                    "type": "message",
                    "label": "No",
                    "text": "No"
                }
            ]
        }
    }

        
        message = FlexSendMessage('會員資料總覽', final_dict)
        line_bot_api.reply_message(event.reply_token, message)
    
    
        

# 連接資料庫
def connect_db():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1', #資料庫的host
            port='3306', #資料庫的port (通常會是3306)
            database='Laundry', #資料庫名稱
            user='root', #資料庫使用者
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # 這邊的 port 要跟跑 ngrok 的 port 相同    
    app.run(host='0.0.0.0', port=port)