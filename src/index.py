from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = FastAPI()

# LINE Bot 相關設定
access_token = os.getenv('LINE_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

# LINE Bot webhook 處理
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameters")
    return "OK"

# 處理收到的訊息
@handler.add(MessageEvent, message=TextMessage)
def handling_message(event):
    if isinstance(event.message, TextMessage):
        user_message = event.message.text
        # 這裡可以根據用戶訊息做出回應
        reply_msg = f"你說了：{user_message}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

# 預設路由
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
