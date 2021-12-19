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

def get_bool_convert(value):
    if value:
        return '是'
    else:
        return '否'

def get_condition(stock):
    actions = []
    all_condition = ['三/六日乖離率', '量多/量縮', '三日均價/六日均價', '綜合分析']
    for condition in all_condition:
        postback = PostbackTemplateAction(label=condition, text=condition, data=f'{stock}')
        actions.append(postback)

    data = TemplateSendMessage(
        alt_text = 'Buttons template',
        template = ButtonsTemplate(
            text = f'股票代號: {stock}\n請選擇分析指標',
            actions = actions
        )
    )
    return data

def get_analysis(condition):
    if condition == 0:
        data = get_analysis_bias_ratio()
    elif condition == 1:
        data = get_analysis_trading_volume()
    elif condition == 2:
        data = get_analysis_price()
    elif condition == 3:
        data = get_analysis_comprehensive()
    return 

def get_analysis_bias_ratio():
    print()

def get_analysis_trading_volume():
    print()

def get_analysis_price():
    print()

def get_analysis_comprehensive():
    print()

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

    condition = ['三/六日乖離率', '量多/量縮', '三日均價/六日均價', '綜合分析']
    if message in condition:
        pass
    else:
        try:
            m = re.search(r'-?(\d+)\.?\d*', message)
            stock_code = m.group(1)
            line_bot_api.reply_message(event.reply_token, get_condition(stock_code))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage('請重新輸入正確股票代碼'))

@handler.add(PostbackEvent)
def handle_postback(event):
    stock = event.postback.data
    print(f'stock code : {stock}')
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
