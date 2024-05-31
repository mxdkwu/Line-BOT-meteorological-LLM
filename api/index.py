from flask import Flask, request
import os
import time

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

import json
app = Flask(__name__)

# 從環境變數中取得 LINE Bot 的設定
access_token = os.getenv("LINE_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)  # 取得收到的訊息內容
    try:
        signature = request.headers['X-Line-Signature']  # 確認 LINE 的簽名
        handler.handle(body, signature)  # 綁定訊息回傳的相關資訊
        json_data = json.loads(body)  # 轉換內容為 json 格式
        reply_token = json_data['events'][0]['replyToken']  # 取得回傳訊息的 Token ( reply message 使用 )
        user_id = json_data['events'][0]['source']['userId']  # 取得使用者 ID ( push message 使用 )
        print(json_data)  # 印出內容
        message_type = json_data['events'][0]['message']['type']
        
        if message_type == 'text':
            text = json_data['events'][0]['message']['text']
            if text in ['雷達回波圖', '雷達回波']:
                line_bot_api.push_message(user_id, TextSendMessage(text='馬上找給你！抓取資料中....'))  # 先發送訊息
                img_url = f'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png?{time.time_ns()}'
                img_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
                line_bot_api.reply_message(reply_token, img_message)  # 回傳訊息
            else:
                text_message = TextSendMessage(text=text)
                line_bot_api.reply_message(reply_token, text_message)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        return 'Invalid signature', 400
    except Exception as e:
        print(f"Error: {e}")  # 發生錯誤就印出完整錯誤內容
        return str(e), 500
    return 'OK'  # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()
