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
line_bot_api.push_message(os.environ['UID'], TextSendMessage(text='start cmd'))


def crawl_by_url(url):
    print(url)


@app.route('/test', methods=['GET'])
def test():
    msg = request.args.get('msg', None)
    url = request.args.get('u', None)
    if msg == 'crawl' and url:
        line_bot_api.push_message(
            os.environ['UID'], TextSendMessage(text=f'start {msg} {url}'))
        crawl_by_url(url)
        line_bot_api.push_message(
            os.environ['UID'], TextSendMessage(text=f'finish {msg} {url}'))
    elif msg != 'crawl':
        line_bot_api.push_message(
            os.environ['UID'], TextSendMessage(text='you use error cmd'))
    elif url is None:
        line_bot_api.push_message(os.environ['UID'], TextSendMessage(
            text='you didn\'t post any url'))
    else:
        line_bot_api.push_message(os.environ['UID'], TextSendMessage(
            text='you didn\'t push any message'))
    return ''

# 監聽所有來自 /callback 的 Post Request


@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    data = {}
    # data['body'] = str(body)
    # data['signature'] = str(signature)
    data['crawl_time'] = 'test_time'

    # handle webhook body
    try:
        handler.handle(str(data), signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)


# 主程式
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
