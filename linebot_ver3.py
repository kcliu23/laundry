import os
from re import A

from flask import Flask, request, abort
import mysql.connector
from mysql.connector import Error

import datetime
import time
import copy
import numpy as np

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

line_channel_access_token = 'kBqjb5elsAWKZoWuEJAD3iVJFfZ3i4yp82VyEhyZjRtiUN0SAIN6eZvH4cSz+anFGNHcQK3Nof2pybzDgqQotRAcjz+vPO3kNoDxMKJcKn+63qMxq4/4nuCAPotfGd90FdKLy6ZyM69o6cWjbxvikgdB04t89/1O/w1cDnyilFU==' # 這邊要貼上你的 bot 的 token (在 line developers 的 Messaging API -> Channel access token 可以找到)
line_channel_secret = 'cefd331cb973c6abad4ba166c064fbb8'  # 這邊要貼上你的 bot 的 secert (在 line developers 的 Basic Settings -> Channel secret 可以找到)
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

    #  ORDER BY `time` ASC LIMIT 1 => to get the earliest data
    #  ORDER BY `time` DESC  LIMIT 1 => to get the latest data

    if user_text[0]=='功能選單':
        flex_message_menu = {
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
                        # {
                        #     "type": "button",
                        #     "action": {
                        #     "type": "message",
                        #     "label": "分台查詢",  # button 上的文字
                        #     "text": "我要查詢" # 按了button 後會傳出去的字
                        #     },
                        #     "margin": "md",
                        #     "height": "sm",
                        #     "style": "primary"
                        # },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "查詢",
                            "text": "我要查詢"
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "使用",  # button 上的文字
                            "text": "我要使用" # 按了button 後會傳出去的字
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "定時",  # button 上的文字
                            "text": "我要定時" # 按了button 後會傳出去的字
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
      
        # line_bot_api.reply_message(event.reply_token, [FlexSendMessage('功能選單', flex_message),FlexSendMessage('功能選單', flex_message2)])
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('功能選單', flex_message_menu))

    elif user_text[0]=='我要定時':
        washer_state = []
        nonempty = 0
        nonempty_washer = []
        nonempty_washer_num = 1
        for i in range(1,5):
            sql_washer_state = "SELECT `state`  FROM `washer_"+str(i)+"` ORDER BY `time` DESC LIMIT 1;"
            CURSOR.execute(sql_washer_state)
            temp = CURSOR.fetchone()
            washer_state.append(temp[0])

            if temp[0] != 'empty':
                nonempty = nonempty + 1 # 得知有幾臺可以被定時
                nonempty_washer.append(nonempty_washer_num)
                nonempty_washer_num = nonempty_washer_num + 1
            else : # 不能定時的機臺
                nonempty_washer_num = nonempty_washer_num + 1

        if nonempty == 0:
            text = "目前機臺皆為空機,因此沒有可定時的機臺"
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
                                "text": "",
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
                                "label": "第1臺洗衣機",  # button 上的文字
                                "text": "使用第1臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第2臺洗衣機",  # button 上的文字
                                "text": "使用第2臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第3臺洗衣機",  # button 上的文字
                                "text": "使用第3臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第4臺洗衣機",  # button 上的文字
                                "text": "使用第4臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "查詢",  
                                "text": "我要查詢" 
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "結束使用",  
                                "text": "結束" 
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
            
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text),FlexSendMessage('定時', flex_message)])
        
        elif nonempty == 1: #僅有一臺可被定時
            flex_message1 = {
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
                                "text": "定時",
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
                                "label": "第"+str(nonempty_washer[0])+"臺洗衣機",  # button 上的文字
                                "text": "定時第"+str(nonempty_washer[0])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "使用",  
                                "text": "我要使用" 
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
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('定時', flex_message1))

        elif nonempty == 2:
            text = "請注意若須定時多臺，按下要定時的機臺後就請按下確認後再繼續定時別臺"

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
                                "text": "定時",
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
                                "label": "第"+str(nonempty_washer[0])+"臺洗衣機",  # button 上的文字
                                "text": "定時第"+str(nonempty_washer[0])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第"+str(nonempty_washer[1])+"臺洗衣機",  # button 上的文字
                                "text": "定時第"+str(nonempty_washer[1])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "使用",  
                                "text": "我要使用" 
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
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text), FlexSendMessage('定時', flex_message2)])    

        elif nonempty == 3:
            text = "請注意若須定時多臺，按下要定時的機臺後就請按下確認後再繼續定時別臺"

            flex_message3 = {
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
                                "text": "定時",
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
                                "label": "第"+str(nonempty_washer[0])+"臺洗衣機",  # button 上的文字
                                "text": "定時第"+str(nonempty_washer[0])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第"+str(nonempty_washer[1])+"臺洗衣機",  # button 上的文字
                                "text": "定時第"+str(nonempty_washer[1])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第"+str(nonempty_washer[2])+"臺洗衣機",  # button 上的文字
                                "text": "定時第"+str(nonempty_washer[2])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "使用",  
                                "text": "我要使用" 
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
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text), FlexSendMessage('定時', flex_message3)])    

        else:
            text = "請注意若須定時多臺，按下要定時的機臺後就請按下確認後再繼續定時別臺"

            flex_message4 = {
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
                                "text": "定時",
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
                                "label": "第1臺洗衣機",  # button 上的文字
                                "text": "定時第1臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第2臺洗衣機",  # button 上的文字
                                "text": "定時第2臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第3臺洗衣機",  # button 上的文字
                                "text": "定時第3臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第4臺洗衣機",  # button 上的文字
                                "text": "定時第4臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "使用",  
                                "text": "我要使用" 
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
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=text),FlexSendMessage('定時', flex_message4)])

    elif user_text[0] == '我要使用':

        washer_state = []
        empty = 0
        empty_washer = []
        empty_washer_num = 1
        for i in range(1,5):
            sql_washer_state = "SELECT `state`  FROM `washer_"+str(i)+"` ORDER BY `time` DESC LIMIT 1;"
            CURSOR.execute(sql_washer_state)
            temp = CURSOR.fetchone()
            washer_state.append(temp[0])
            if temp[0] == 'empty':
                empty = empty + 1 # 得知有幾臺空機
                empty_washer.append(empty_washer_num)
                empty_washer_num = empty_washer_num + 1
            else : # 非空臺
                empty_washer_num = empty_washer_num + 1
        if empty == 0:
            text = "目前沒有空機可使用,但可以定時機臺,您定時的機臺完成洗衣後會通知您"

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
                                "text": "定時",
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
                                "label": "第1臺洗衣機",  # button 上的文字
                                "text": "定時第1臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第2臺洗衣機",  # button 上的文字
                                "text": "定時第2臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第3臺洗衣機",  # button 上的文字
                                "text": "定時第3臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第4臺洗衣機",  # button 上的文字
                                "text": "定時第4臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "查詢",  
                                "text": "我要查詢" 
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "結束使用",  
                                "text": "結束" 
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
            
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text),FlexSendMessage('定時', flex_message)])
        
        elif empty == 1: #僅有一臺空機
            flex_message1 = {
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
                                "text": "使用",
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
                                "label": "第"+str(empty_washer[0])+"臺洗衣機",  # button 上的文字
                                "text": "使用第"+str(empty_washer[0])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "定時",  
                                "text": "我要定時" 
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
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('使用', flex_message1))

        elif empty == 2:
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
                                "text": "使用",
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
                                "label": "第"+str(empty_washer[0])+"臺洗衣機",  # button 上的文字
                                "text": "使用第"+str(empty_washer[0])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第"+str(empty_washer[1])+"臺洗衣機",  # button 上的文字
                                "text": "使用第"+str(empty_washer[1])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "定時",  
                                "text": "我要定時" 
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
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('使用', flex_message2))    

        elif nonempty == 3:
            flex_message3 = {
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
                                "text": "使用",
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
                                "label": "第"+str(empty_washer[0])+"臺洗衣機",  # button 上的文字
                                "text": "使用第"+str(empty_washer[0])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第"+str(empty_washer[1])+"臺洗衣機",  # button 上的文字
                                "text": "使用第"+str(empty_washer[1])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第"+str(empty_washer[2])+"臺洗衣機",  # button 上的文字
                                "text": "使用第"+str(empty_washer[2])+"臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "定時",  
                                "text": "我要定時" 
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
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('使用', flex_message3))    

        else:
            flex_message4 = {
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
                                "text": "使用",
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
                                "label": "第1臺洗衣機",  # button 上的文字
                                "text": "使用第1臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第2臺洗衣機",  # button 上的文字
                                "text": "使用第2臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第3臺洗衣機",  # button 上的文字
                                "text": "使用第3臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "第4臺洗衣機",  # button 上的文字
                                "text": "使用第4臺洗衣機" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "定時",  
                                "text": "我要定時" 
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
            line_bot_api.reply_message(event.reply_token, FlexSendMessage('使用', flex_message4))

    elif user_text[0] == '我要查詢':
        user_id = event.source.user_id 

        # 查詢該臺洗衣機的狀態 & 剩餘時間
        sql_state1 = "SELECT `state` , `left_time` FROM `washer_1` ORDER BY `time` DESC LIMIT 1;" # find the latest data
        CURSOR.execute(sql_state1)
        info1=CURSOR.fetchone() 
        sql_state2 = "SELECT `state` , `left_time` FROM `washer_2` ORDER BY `time` DESC LIMIT 1;" 
        CURSOR.execute(sql_state2)
        info2=CURSOR.fetchone() 
        sql_state3 = "SELECT `state` , `left_time` FROM `washer_3` ORDER BY `time` DESC LIMIT 1;"
        CURSOR.execute(sql_state3)
        info3=CURSOR.fetchone() 
        sql_state4 = "SELECT `state` , `left_time` FROM `washer_4` ORDER BY `time` DESC LIMIT 1;" 
        CURSOR.execute(sql_state4)
        info4=CURSOR.fetchone() 
    
        # 洗衣機狀態為"使用中"
        bubble1 = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
            
                {
                    "type": "text",
                    "text": "洗衣機狀態",### bubble1["body"]["contents"][1]["text"]
                    "size": "xs",
                    "color": "#808080"
                },
                {
                    "type": "text",
                    "text": "機台1",  
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
                        "text": "text",   ### ["body"]["contents"][3]["contents"][1]["text"] 
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
                        "text": "剩餘時間:",
                        "margin": "md",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "0", ### bubble1["body"]["contents"][5]["contents"][1]["text"]
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
                    "label": "定時這臺", #button 上的字
                    "text": "button_text" #將其使用者加入排隊陣列中
                    },
                    "margin": "md",
                    "height": "sm",
                    "style": "primary"
                }
                ]
            }
        }
        
        # 洗衣機狀態為空機
        bubble2 = {
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
                    "text": "機台1",  ### bubble2["body"]["contents"][1]["text"]
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
                        "text": "text",   ### ["body"]["contents"][3]["contents"][1]["text"]
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
                    "label": "使用這臺", #button 上的字
                    "text": "使用這臺" #將其使用者加入排隊陣列中
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
            sql_state = "SELECT `state` , `left_time` FROM `washer_"+str(i)+"` ORDER BY `time` DESC LIMIT 1;" # find the latest data
            CURSOR.execute(sql_state)
            info=CURSOR.fetchone() 
            
            if (i == 1 and info1[0] =='empty') or (i == 2 and info2[0] =='empty') or (i == 3 and info3[0] =='empty') or (i == 4 and info4[0] =='empty'):
                text = "空機"
                button_text = "使用第"+str(i)+"臺洗衣機"
                bubble2["body"]["contents"][1]["text"] = "機台"+str(i)
                bubble2["body"]["contents"][3]["contents"][1]["text"] = text 
                bubble2["body"]["contents"][4]["action"]["text"] = button_text
                # bubble2["body"]["contents"][4]["contents"][1]["text"] = '2'
                # bubble2["body"]["contents"][5]["action"]["text"] = '3'
                globals()['final_dict'+str(i)]["contents"].append(copy.deepcopy(bubble2))
            else:
                text = "使用中"
                button_text = "定時第"+str(i)+"臺洗衣機"
                bubble1["body"]["contents"][1]["text"] = "機台"+str(i)
                bubble1["body"]["contents"][3]["contents"][1]["text"] = text 
                bubble1["body"]["contents"][4]["contents"][1]["text"] = "約" + info[1] + "分鐘" ## 剩餘時間
                # bubble1["body"]["contents"][5]["contents"][1]["text"] = '5'
                bubble1["body"]["contents"][5]["action"]["text"] = button_text
                globals()['final_dict'+str(i)]["contents"].append(copy.deepcopy(bubble1)) 
                
        line_bot_api.reply_message(event.reply_token, [FlexSendMessage('我要洗衣服', final_dict1),FlexSendMessage('我要洗衣服', final_dict2),FlexSendMessage('我要洗衣服', final_dict3),FlexSendMessage('我要洗衣服', final_dict4)])
      
    elif user_text[0] == '確認定時通知':
        # 先確認使用者有定時 
        sql_booked = "SELECT COUNT(*) FROM `user` WHERE `id` = '"+user_id+"';"
        CURSOR.execute(sql_booked)
        booked = CURSOR.fetchone()
        if int(booked[0]) == 0 : # 使用者沒有定時
            text = "您尚未定時任何一臺洗衣機喔!"
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
                                "text": "定時",
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
                                "label": "我要定時",  # button 上的文字
                                "text": "我要定時" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "功能選單",  # button 上的文字
                                "text": "功能選單" # 按了button 後會傳出去的字
                                },
                                "margin": "md",
                                "height": "sm",
                                "style": "primary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "message",
                                "label": "結束",  # button 上的文字
                                "text": "結束" # 按了button 後會傳出去的字
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
            
            line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text),FlexSendMessage('定時', flex_message)])
        
        elif int(booked[0]) > 0 : # 使用者有定時
            # 查詢使用者定時的洗衣機
            sql_booked_washer = "SELECT `washer`  FROM `user` WHERE `id` = '"+user_id+"'  ORDER BY `time` DESC LIMIT 1;" 
            CURSOR.execute(sql_booked_washer)
            booked_washer=CURSOR.fetchone()
            # 查詢其剩餘時間
            sql_booked_washer_lefttime = "SELECT `left_time`  FROM `washer_"+str(booked_washer[0])+"`  ORDER BY `time` DESC LIMIT 1;" 
            CURSOR.execute(sql_booked_washer_lefttime)
            booked_washer_lefttime=CURSOR.fetchone()
            # 並暫停其時長
            bwt = int(booked_washer_lefttime[0])  # *60 #以秒為單位 
            time.sleep(bwt)

            text = "第"+booked_washer[0]+"臺洗衣機已經完成洗衣了"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
    
    elif user_text[0] == '結束':
        text = "感謝您的使用"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text))
        
    elif user_text[0] == '沒有使用洗衣機':
        text = "好的,若您有需要歡迎繼續使用本服務"
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
                        # {
                        #     "type": "text",
                        #     "text": "功能選單",
                        #     "weight": "bold"
                        # },
                        # {
                        #     "type": "separator",
                        #     "margin": "md"
                        # },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "功能選單",  # button 上的文字
                            "text": "功能選單" # 按了button 後會傳出去的字
                            },
                            "margin": "md",
                            "height": "sm",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "message",
                            "label": "結束",  # button 上的文字
                            "text": "結束" # 按了button 後會傳出去的字
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
        
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=text),  FlexSendMessage('繼續使用', flex_message)])
                  
    # elif user_text[0] == '確認通知':

    # elif user_text[0] == '不用更換':
   
    elif user_text[0] == '試': # 測試資料庫是否能更新 -> 不行
        for i in range (0,30):
            sql_test = "INSERT INTO `user` (`id`, `time`, `washer`) VALUES ('"+str(i)+"','"+str(10)+"','"+str(10)+"'); "
            CURSOR.execute(sql_test)
            CONNECTION.commit()
            print(i)
            sql_test2 = "SELECT `id`  FROM `user` ORDER BY `time` DESC LIMIT 1;" # find the latest data
            CURSOR.execute(sql_test2)
            info1=CURSOR.fetchone() 
            print(info1[0])

    elif True:
        for j in range(1,5):
            if user_text[0] == '定時第'+str(j)+'臺洗衣機':
                # 先確認此臺可被定時
                sql_washer_state =  "SELECT `state` FROM `washer_"+str(j)+"`  ORDER BY `time` DESC LIMIT 1;"
                CURSOR.execute(sql_washer_state)
                washer_state = CURSOR.fetchone()
                print(washer_state[0])
            
                # 此臺正在洗衣,可以被定時
                if washer_state[0] ==  'washing' or washer_state[0] ==  '洗衣中':
                    sql_booked_washer =  "SELECT COUNT(*) FROM `user` WHERE `id` = '"+user_id+"' AND `washer` = '"+str(j)+"';"
                    CURSOR.execute(sql_booked_washer)
                    booked_washer = CURSOR.fetchone()
                    # 若使用者尚未定時過此臺
                    if booked_washer[0] == int(0):
                        sql = "INSERT INTO `user` (`id`, `time`, `washer`) VALUES ('"+user_id+"','"+get_current_time()+"','"+str(j)+"'); "
                        CURSOR.execute(sql)
                        CONNECTION.commit()

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
                                            "text": "確認定時",
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
                                            "label": "確認",  # button 上的文字
                                            "text": "確認定時通知" # 按了button 後會傳出去的字
                                            },
                                            "margin": "md",
                                            "height": "sm",
                                            "style": "primary"
                                        },
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "message",
                                            "label": "取消",  # button 上的文字
                                            "text": "取消定時第"+str(j)+"臺" # 按了button 後會傳出去的字
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
                        
                        text = "按下確認後便會在完成洗衣後會通知您"
                        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=text),FlexSendMessage('確認通知', flex_message)])
                    
                    else: #此使用者有定時過此臺 
                        text = "您已定時過此臺洗衣機，洗衣完成後會通知您"
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

                # 此臺為空機,不能被定時
                elif washer_state[0] ==  'empty' or washer_state[0] ==  '空機中':
                    text =  "此臺目前為空機,請前往洗衣並使用「使用」的服務以在洗衣完成時收到通知；或是定時其他被使用中的機臺"
                    
                    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=text),FlexSendMessage('無法定時', flex_message_menu)])

            elif user_text[0] == '取消定時第'+str(j)+'臺':
                # 先確認使用者有定時的機臺  
                sql_user_exist =  "SELECT COUNT(*) FROM `user` WHERE `id` = '"+user_id+"';"
                CURSOR.execute(sql_user_exist)
                user_exist = CURSOR.fetchone()
                print(user_exist[0])
                # 再確認使用者定時的機臺是此臺  
                sql_booked_washer =  "SELECT `washer` FROM `user` WHERE `id` = '"+user_id+"' LIMIT "+str(user_exist[0])+""
                # SELECT `washer` FROM `user` WHERE `id` = 'U7eefd979d59683685b7abc577fd66001'

                CURSOR.execute(sql_booked_washer)
                booked_washer = CURSOR.fetchall()
                print(booked_washer)
                print(booked_washer[0][0])
                print(booked_washer[1][0])
                print("here")
                cancel = 0

                for num in range(0,user_exist[0]): 
                    for k in booked_washer[num][0]:
                        print(k)
                        print(type(k))
                        print(type(j))
                        if(k == str(j)) : 
                            cancel = cancel + 1 # 取消的正確
                            break
                        else:
                            pass # 取消的錯誤

                print(cancel)
                
                

                # 使用者沒有使用定時服務
                if int(user_exist[0]) == 0 : 
                    text = "您尚未定時任何一臺洗衣機喔!"
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
                                        "text": "定時",
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
                                        "label": "我要定時",  # button 上的文字
                                        "text": "我要定時" # 按了button 後會傳出去的字
                                        },
                                        "margin": "md",
                                        "height": "sm",
                                        "style": "primary"
                                    },
                                    {
                                        "type": "button",
                                        "action": {
                                        "type": "message",
                                        "label": "功能選單",  # button 上的文字
                                        "text": "功能選單" # 按了button 後會傳出去的字
                                        },
                                        "margin": "md",
                                        "height": "sm",
                                        "style": "primary"
                                    },
                                    {
                                        "type": "button",
                                        "action": {
                                        "type": "message",
                                        "label": "結束",  # button 上的文字
                                        "text": "結束" # 按了button 後會傳出去的字
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
                    
                    line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=text),FlexSendMessage('定時', flex_message)])
                
                # 使用者有定時且是此臺
                elif int(user_exist[0] ) != 0 and cancel > 0: 
                    sql_del = "DELETE FROM `user` WHERE `id` =  '"+user_id+"' and `washer` = '"+str(j)+"'ORDER BY `time` DESC  LIMIT 1 "
                    CURSOR.execute(sql_del)
                    CONNECTION.commit()

                    text = "已將您的定時取消,歡迎再次使用本服務"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

                # 使用者有定時但不是此臺
                elif int(user_exist[0] ) != 0 and cancel == 0: 
                    text = "您沒有定時這臺喔!"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))    

            elif user_text[0] == '使用第'+str(j)+'臺洗衣機':
                # 先確認此臺可使用
                sql_washer_state =  "SELECT `state` FROM `washer_"+str(j)+"`  ORDER BY `time` DESC LIMIT 1;"
                CURSOR.execute(sql_washer_state)
                washer_state = CURSOR.fetchone()
            
                # 此臺為空,可以使用
                if washer_state[0] ==  'empty' or washer_state[0] ==  '空機中':
                    # 5分鐘後若洗衣機狀態非空則確認洗好後是通知此使用者
                    text = "請在三分鐘內開始洗衣，開始使用後請按開始，則會在洗衣完成後通知您；若沒有使用洗衣機請按否"
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
                                            "text": "開始使用洗衣機",
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
                                            "label": "是",  # button 上的文字
                                            "text": '開始使用第'+str(j)+'臺洗衣機' # 按了button 後會傳出去的字
                                            },
                                            "margin": "md",
                                            "height": "sm",
                                            "style": "primary"
                                        },
                                        {
                                            "type": "button",
                                            "action": {
                                            "type": "message",
                                            "label": "否",  # button 上的文字
                                            "text": '沒有使用洗衣機' # 按了button 後會傳出去的字
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

                    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=text),  FlexSendMessage('開始使用', flex_message)])
                # 此臺非空,不可使用
                elif washer_state[0] ==  'washing' or washer_state[0] ==  '洗衣中':
                    text =  "此臺目前在使用中,請改為定時以在其完成洗衣後收到通知；或是使用別臺空機"  
                    
                    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=text),FlexSendMessage('無法使用', flex_message_menu)])
               
            elif user_text[0] == '開始使用第'+str(j)+'臺洗衣機':   
                # 確認使用者 (無法刪除其定時紀錄)
                # 此洗衣機脫水約三分鐘
                time.sleep(180)
                sql_washer_state = "SELECT `state` FROM `washer_"+str(j)+"`  ORDER BY `time` DESC LIMIT 1;"
                CURSOR.execute(sql_washer_state)
                washer_state = CURSOR.fetchone()

                # 確認機臺有被開始使用
                # 沒有被開始使用
                if str(washer_state[0]) == "空機中" or str(washer_state[0]) == "empty":
                    text = "洗衣機目前沒有開始洗衣，請進行確認"
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text))

                # 機臺有被使用
                elif str(washer_state[0]) == "洗衣中" or str(washer_state[0]) == "washing":
                    sql_washer_lefttime = "SELECT `left_time` FROM `washer_"+str(j)+"`  ORDER BY `time` DESC LIMIT 1;"
                    CURSOR.execute(sql_washer_lefttime)
                    washer_lefttime = CURSOR.fetchone()

                    lt = int(washer_lefttime[0])# *60   #以秒為單位
                    time.sleep(lt)
    
                    text = "第"+str(j)+"臺洗衣機已完成洗衣"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))

    # else:
    #     text = "無法理解您的訊息，請確認您使用的流程正確；若有疑慮請與我們聯絡，謝謝"
    #     line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text))

               
   

# 連接資料庫
def connect_db():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1', #資料庫的host
#             port='3306', #資料庫的port (通常會是3306)
            database='laundry', #資料庫名稱# database='Laundry', #資料庫名稱
            user='laundry', #資料庫使用者
            password='12345678',# password='12345678', #資料庫密碼
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

