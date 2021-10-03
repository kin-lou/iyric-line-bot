import os
import time
import datetime

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import requests
from bs4 import BeautifulSoup

import setting

app = Flask(__name__)

# Access Token
line_bot_api = LineBotApi(os.environ['LINE_BOT_TOKEN'])
# Channel Secret
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
# Developer ID
line_bot_api.push_message(os.environ['DEV_UID'], TextSendMessage(text='start cmd'))

def get_iyric(href):
    try:
        url = f'https://mojim.com{href}'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        iyric = soup.select('#fsZ > dl')[-1].text
    except:
        iyric = ''
    return iyric

def get_href(song_name):
    try:
        url = f'https://mojim.com/{song_name}.html?t3'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        href = soup.select('table.iB > tr > td > div > dl > dd.mxsh_dd1 a')[-1].get('href')
    except:
        href = ''
    return href

def crawl_by_song_name(song_name):
    try:
        href = get_href(song_name)
        iyric = get_iyric(href)
        if iyric == '':
            raise Exception
        return iyric
    except:
        return 'some error, couldn\'t search iyric by song'

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
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

# 訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    a = {
        "type": "template",
        "altText": "This is a buttons template",
        "template": {
            "type": "buttons",
            "thumbnailImageUrl": "https://example.com/bot/images/image.jpg",
            "imageAspectRatio": "rectangle",
            "imageSize": "cover",
            "imageBackgroundColor": "#FFFFFF",
            "title": "Menu",
            "text": "Please select",
            "defaultAction": {
                "type": "uri",
                "label": "View detail",
                "uri": "http://example.com/page/123"
            },
            "actions": [
                {
                    "type": "postback",
                    "label": "Buy",
                    "data": "action=buy&itemid=123"
                },
                {
                    "type": "postback",
                    "label": "Add to cart",
                    "data": "action=add&itemid=123"
                },
                {
                    "type": "uri",
                    "label": "View detail",
                    "uri": "http://example.com/page/123"
                }
            ]
        }
    }
    message = TextSendMessage(text=event.message.text)
    # data = crawl_by_song_name(event.message.text)

    print(event.message.text)
    try:
        print(event.postback.data)
    except:
        pass

    test_button = TemplateSendMessage(
        alt_text = 'Buttons template',
        template = ButtonsTemplate(
            text = '請選擇地區',
            actions = [
                MessageTemplateAction(
                    label = '台北市',
                    text = '台北市'
                ),
                PostbackTemplateAction(
                    label = '台中市',
                    text = '台中市',
                    data = 'test postback 台中市'
                ),
                MessageTemplateAction(
                    label = '高雄市',
                    text = '高雄市'
                )
            ]
        )
    )

    # line_bot_api.reply_message(event.reply_token, TextSendMessage(data))
    line_bot_api.reply_message(event.reply_token, test_button)

# 主程式
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
