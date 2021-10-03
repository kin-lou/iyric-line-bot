import os
import time
import datetime

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import urllib
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

# def get_iyric(href):
#     try:
#         url = f'https://mojim.com{href}'
#         resp = requests.get(url)
#         soup = BeautifulSoup(resp.text, 'html.parser')
#         iyric = soup.select('#fsZ > dl')[-1].text
#     except:
#         iyric = ''
#     return iyric

# def get_href(song_name):
#     try:
#         url = f'https://mojim.com/{song_name}.html?t3'
#         resp = requests.get(url)
#         soup = BeautifulSoup(resp.text, 'html.parser')
#         href = soup.select('table.iB > tr > td > div > dl > dd.mxsh_dd1 a')[-1].get('href')

#         iyric = soup.select('table.iB > tr > td > div > dl > dd')[1:]

#         for i in iyric:
#             if i.select('p'):
#                 continue
#             else:
#                 print(i.select('a')[-1])

#     except:
#         href = ''
#     return href

# def crawl_by_url(url, mode):
#     try:
#         if mode == 't1':
#             print()
#         if mode == 't2':
#             print()
#         if mode == 't3':
#             print()
#         if mode == 't4':
#             print()

#         href = get_href(url)
#         iyric = get_iyric(href)
#         if iyric == '':
#             raise Exception
#         return iyric
#     except:
#         return 'some error, couldn\'t search iyric by song'

def get_crawl_mode_button(song_name):
    song_name = urllib.parse.quote(song_name.encode('utf8'))
    actions = []
    all_mode = ['歌手', '專輯', '歌名', '歌詞']
    for mode in all_mode:
        actions.append(
            PostbackTemplateAction(
                label = mode,
                text = mode,
                data = f'https://mojim.com/{song_name}.html?t{all_mode.index(mode) + 1}'
            )
        )

    template = TemplateSendMessage(
        alt_text = 'Buttons template',
        template = ButtonsTemplate(
            text = '請選擇搜尋條件',
            actions = actions
        )
    )
    return template

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
    message = event.message.text
    if message in ['歌手', '專輯', '歌名', '歌詞']:
        pass
    else:
        line_bot_api.reply_message(event.reply_token, get_crawl_mode_button(message))

@handler.add(PostbackEvent)
def handle_postback(event):
    url = event.postback.data
    mode = url.split('?')[-1]
    print(url, mode)
    # data = crawl_by_url(url, mode)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(url))

# 主程式
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
