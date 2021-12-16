import os
import re
import time
import datetime

from flask import Flask, request, abort, jsonify

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import twstock

import setting

app = Flask(__name__)

# Access Token
line_bot_api = LineBotApi(os.environ['LINE_BOT_TOKEN'])
# Channel Secret
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
# Developer ID
line_bot_api.push_message(os.environ['DEV_UID'], TextSendMessage(text='start cmd'))

def crawl_by_cd(url):
    all_item = []
    try:
        _ = '待規劃'

    except:
        pass
    return all_item

# def crawl_by_song(url):
#     all_item = []
#     try:
#         resp = requests.get(url)
#         soup = BeautifulSoup(resp.text, 'html.parser')
#         items = soup.select('table.iB > tr > td > div > dl > dd')[1:100]

#         for i in items:
#             if i.select('p'):
#                 continue

#             text = ''
#             for k in i.select('a'):
#                 text += k.text + '\n'

#             all_item.append({
#                 'text': text,
#                 'sub_url': i.select('a')[-1].get('href')
#             })
#     except:
#         pass
#     return all_item

# def crawl_by_url(url):
#     search_list = []
#     try:
#         mode = url.split('?')[-1]
#         if mode == 't2':
#             search_list = crawl_by_cd(url)
#         elif mode == 't3':
#             search_list = crawl_by_song(url)

#         if len(search_list) == 0:
#             raise Exception

#         cnt_columns = 0
#         flag = False
#         columns = []
#         actions = []
#         for item in search_list:
#             flag = False
#             actions.append(
#                 URIAction(
#                     label=item['text'][:20],
#                     uri=f'https://mojim.com{item["sub_url"]}'
#                 )
#             )

#             if len(columns) == cnt_columns:
#                 columns.append('')
#             columns[cnt_columns] = CarouselColumn(
#                 text=f'分頁_{cnt_columns + 1}',
#                 actions=actions
#             )

#             if len(actions) % 3 == 0:
#                 cnt_columns += 1
#                 flag = True
#                 actions = []

#         if flag is False:
#             columns.pop()

#         template = CarouselTemplate(columns=columns[:10])
#         return True, template
#     except Exception as e:
#         return False, 'Sorry, you get some error'

# def get_crawl_mode_button(song_name):
#     song_name = urllib.parse.quote(song_name.encode('utf8'))
#     actions = []
#     all_mode = ['專輯', '歌名']
#     for mode in all_mode:
#         actions.append(
#             PostbackTemplateAction(
#                 label=mode,
#                 text=mode,
#                 data=f'https://mojim.com/{song_name}.html?t{all_mode.index(mode) + 2}'
#             )
#         )

#     actions.append(
#         URIAction(
#             label='test',
#             uri=f'https://iyric-line-bot.herokuapp.com/test'
#         )
#     )

#     template = TemplateSendMessage(
#         alt_text='Buttons template',
#         template=ButtonsTemplate(
#             text='請選擇搜尋條件',
#             actions=actions
#         )
#     )
#     return template

@app.route('/test', methods=['GET'])
def test():
    print(type(request.headers))
    print(request.headers)
    data = {
        'route': 'test',
        'content-type': 'json'
    }
    return jsonify(data)

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    m = re.search(r'-?(\d+)\.?\d*', message)
    stock_code = m.group(1)

    if message in ['專輯', '歌名']:
        pass
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(stock_code))

@handler.add(PostbackEvent)
def handle_postback(event):
    url = event.postback.data
    # status, data = crawl_by_url(url)
    status, data = False, 'test'

    if status:
        line_bot_api.reply_message(
            event.reply_token, TemplateSendMessage(alt_text='結果', template=data))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(data))

# 主程式
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
