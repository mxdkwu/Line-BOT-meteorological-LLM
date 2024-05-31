from flask import Flask, request
import os
import time

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage

import json
app = Flask(__name__)

access_token = os.environ.get('LINEBOT_ACCESS_TOKEN')
channel_secret = os.environ.get('LINEBOT_CHANNEL_SECRET')

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                 
    try:
        line_bot_api = LineBotApi(access_token)           
        handler = WebhookHandler(channel_secret)          
        signature = request.headers['X-Line-Signature']   
        handler.handle(body, signature)      
        json_data = json.loads(body)         
        reply_token = json_data['events'][0]['replyToken']    
        user_id = json_data['events'][0]['source']['userId']  
        print(json_data)                                      
        type = json_data['events'][0]['message']['type']
        if type == 'text':
            text = json_data['events'][0]['message']['text']
            if text == '雷達回波圖' or text == '雷達回波':
                line_bot_api.push_message(user_id, TextSendMessage(text='馬上找給你！抓取資料中....'))   
                img_url = f'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png?{time.time_ns()}'
                img_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
                line_bot_api.reply_message(reply_token, img_message)  
            else:          
                text_message = TextSendMessage(text=text)
                line_bot_api.reply_message(reply_token,text_message)
    except Exception as e:
        print(e)                
    return 'OK'                 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
