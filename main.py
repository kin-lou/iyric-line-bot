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

def get_bool_convert(value):
    if value:
        return '是'
    else:
        return '否'

def get_condition(stock):
    actions = []
    all_condition = ['三/六日乖離率', '量多/量縮', '三日均價/六日均價', '綜合分析']
    for condition in all_condition:
        postback = PostbackTemplateAction(label=condition, text=condition, data=f'{stock},{all_condition.index(condition)}')
        actions.append(postback)

    data = TemplateSendMessage(
        alt_text = 'Buttons template',
        template = ButtonsTemplate(
            text = f'股票代號: {stock}\n請選擇分析指標',
            actions = actions
        )
    )
    return data

def get_analysis(stock, condition):
    analysis = twstock.BestFourPoint(twstock.Stock(stock))
    if condition == 0:
        data = get_analysis_bias_ratio(analysis)
    elif condition == 1:
        data = get_analysis_trading_volume(analysis)
    elif condition == 2:
        data = get_analysis_price(analysis)
    elif condition == 3:
        data = get_analysis_comprehensive(analysis)
    return data

def get_analysis_bias_ratio(analysis):
    print(analysis.bias_ratio())
    print(analysis.plus_bias_ratio())
    print(analysis.mins_bias_ratio())

def get_analysis_trading_volume(analysis):
    print(analysis.best_buy_1())
    print(analysis.best_sell_1())
    print(analysis.best_buy_2())
    print(analysis.best_sell_2())

def get_analysis_price(analysis):
    print(analysis.best_buy_3())
    print(analysis.best_sell_3())
    print(analysis.best_buy_4())
    print(analysis.best_sell_4())

def get_analysis_comprehensive(analysis):
    result = analysis.best_four_point()
    if result:
        return f'是否為買點 : {get_bool_convert(result[0])}\n是否為賣點 : {get_bool_convert(not result[0])}'
    else:
        return '是否為買點 : 否\n是否為賣點 : 否'

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
    postback = event.postback.data.split(',')
    data = get_analysis(postback[0], postback[1])
    line_bot_api.reply_message(event.reply_token, TextSendMessage(data))

# 主程式
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
