from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import json, time, requests
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage
import uvicorn

app = FastAPI()

def earth_quake():
    result = []
    code = os.getenv('CWA_TOKEN')  # 從環境變數獲取中央氣象局 API 授權碼
    try:
        url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={code}'
        req1 = requests.get(url)
        data1 = req1.json()
        eq1 = data1['records']['Earthquake'][0]
        t1 = data1['records']['Earthquake'][0]['EarthquakeInfo']['OriginTime']

        url2 = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={code}'
        req2 = requests.get(url2)
        data2 = req2.json()
        eq2 = data2['records']['Earthquake'][0]
        t2 = data2['records']['Earthquake'][0]['EarthquakeInfo']['OriginTime']
        
        result = [eq1['ReportContent'], eq1['ReportImageURI']]
        if t2 > t1:
            result = [eq2['ReportContent'], eq2['ReportImageURI']]
    except Exception as e:
        print(e)
        result = ['抓取失敗...', '']
    return result

access_token = os.getenv('LINE_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

@app.post("/")
async def linebot(request: Request):
    body = await request.body()
    signature = request.headers['x-line-signature']

    try:
        handler.handle(body.decode('utf-8'), signature)
        json_data = json.loads(body.decode('utf-8'))
        reply_token = json_data['events'][0]['replyToken']
        user_id = json_data['events'][0]['source']['userId']
        print(json_data)
        message_type = json_data['events'][0]['message']['type']

        if message_type == 'text':
            text = json_data['events'][0]['message']['text']
            if text == '雷達回波圖' or text == '雷達回波':
                await line_bot_api.push_message(user_id, TextSendMessage(text='馬上找給你！抓取資料中....'))
                img_url = f'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0058-001.png?{time.time_ns()}'
                img_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
                await line_bot_api.reply_message(reply_token, img_message)
            elif text == '地震':
                await line_bot_api.push_message(user_id, TextSendMessage(text='馬上找給你！抓取資料中....'))
                reply = earth_quake()
                text_message = TextSendMessage(text=reply[0])
                await line_bot_api.reply_message(reply_token, text_message)
                await line_bot_api.push_message(user_id, ImageSendMessage(original_content_url=reply[1], preview_image_url=reply[1]))
            else:
                text_message = TextSendMessage(text=text)
                await line_bot_api.reply_message(reply_token, text_message)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="無效的簽名")
    except Exception as e:
        print(e)

    return PlainTextResponse('OK')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
