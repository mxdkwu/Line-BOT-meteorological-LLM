from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import os
import time

app = Flask(__name__)

access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

@app.route('/api', methods=['POST'])
def linebot():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == '雷達回波圖' or text == '雷達回波':
        user_id = event.source.user_id
        line_bot_api.push_message(user_id, TextSendMessage(text='馬上找給你！抓取資料中....'))
        img_url = f'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png?{time.time_ns()}'
        img_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
        line_bot_api.reply_message(event.reply_token, img_message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
