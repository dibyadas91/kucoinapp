from flask import Flask, request, jsonify
import json, config
from kucoin_futures.client import Trade

app = Flask(__name__)

RSI_COUNT = 0

def order(price,side, size, symbol,leverage,stopprice):


    print("Trying to connect to KuCoin...")
    client = Trade(key=config.API_KEY, secret=config.SECRET_KEY, passphrase=config.WEBHOOK_PASSPHRASE,
                   is_sandbox=False, url='')
    print("Connected to Kucoin...")

    positions = client.get_all_position()

    if len(positions) == 0:
        order = client.create_market_order(symbol, side, leverage, 'LOl2', size=size)
        position_detail = client.get_position_details(symbol)
    else:
        return "fail"
    return "success"



@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/webhook', methods=['POST'])
def webhook():
    print(request)

    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
            return {
                "code": "error",
                "message": "There is an error."
            }

    side = data['order_action'].upper()
    quantity = data['quantity']
    symbol = data['symbol']
    price = data['price']
    leverage = data['leverage']
    stopprice = data['stopprice']

    print("Data... sie:{}, quantity:{}, symbol:{}".format(side, quantity, symbol))

    order_response = order(price, side, quantity, symbol, leverage,stopprice)

    if order_response=="Success":
        return "200 OK"
    else:
        print("order failed")
        return "200 FAILED"
        

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=4040)