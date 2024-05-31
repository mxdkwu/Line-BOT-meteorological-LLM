from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage
import json
import os

app = Flask(__name__)

access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
channel_secret = os.environ.get('LINE_CHANNEL_SECRET', '')

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        return 'Invalid signature', 400
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    reply_token = event.reply_token
    user_id = event.source.user_id

    if text == '雷達回波圖' or text == '雷達回波':
        line_bot_api.reply_message(reply_token, TextSendMessage(text='馬上找給你！抓取資料中....'))
        img_url = 'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png'
        img_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
        line_bot_api.push_message(user_id, img_message)
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

if __name__ == "__main__":
    app.run()
