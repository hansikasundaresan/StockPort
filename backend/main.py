from flask import Flask, request, json, Response # include the flask library
from stock_api import *
from trial import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/user-stock-info", methods=['GET', 'POST'])
def user_stock_info():
    email_id=str(request.get_json())
    #if email_id is None:
    #email_id = "ashwin.silveroaks@gmail.com"
    db = intiliaze_firebase()
    stocks = db.collection('user-stocks').document(email_id).get().to_dict()
    total_price = 0
    price_dictionary = {}
    print(stocks)
    for stock in stocks:
        current_stock_price = get_stock_price(stock)['c'] *stocks[stock]
        price_dictionary[stock] = current_stock_price
        total_price += current_stock_price
    price_dictionary["total_price"] =total_price
    return json.dumps(price_dictionary)
    
@app.route("/general-news", methods = ['GET'])
def general_news_to_frontend():
    return json.dumps(general_news())

@app.route("/stock-recs", methods = ['GET', 'POST'])
def stock_recommendation():
    output = {}
    symbol=str(request.get_json())
    output['name'] = get_stock_symbol(symbol)
    output['price'] = get_stock_price(symbol)
    db = intiliaze_firebase()
    stocks = db.collection('stock-info').document('$'+output['name']).get().to_dict()
    if stocks is None:
        output['sentiment'] = get_stock_sentiment(symbol)
    else:
        output['sentiment']= stocks['sentiment']
    if output['sentiment'] > 0.95:
        output['recommendation'] = 'HOLD'
    elif output['sentiment'] > 0.90:
        output['recommendation'] = 'BUY'
    else:
        output['recommendation'] = 'Nothing'
    if output['price']["h"] - output['price']["l"] > 10.0:
        output['sell_recommendation'] = 'SELL'
    else:
        output['sell_recommendation'] = 'Not Enough net increase'
    output['price'] = output['price']['c']
    return json.dumps(output)

@app.route("/subtract-stock", methods = ['POST', 'GET'])
def sell_stock():
    email_id,stock_to_sell =request.get_json().split(" ")
    stock_to_sell =get_stock_symbol(stock_to_sell)
    db = intiliaze_firebase()
    #email_id=str(request.get_json())
    stocks = db.collection('user-stocks').document(email_id).get().to_dict()
    if stock_to_sell not in stocks:
        return json.dumps({stock_to_sell: "You have no stock to sell"})
    if stocks[stock_to_sell] == 0:
        return json.dumps({stock_to_sell: "You have no stock to sell"})
    stocks[stock_to_sell] = stocks[stock_to_sell]-1
    db.collection("user-stocks").document(email_id).set(stocks)
    return json.dumps({stock_to_sell: stocks[stock_to_sell]})

    


@app.route("/buy-stock", methods = ['POST', 'GET'])
def buy_stock():
    email_id,stock_to_buy =request.get_json().split(" ")
    stock_to_buy =get_stock_symbol(stock_to_buy)
    db = intiliaze_firebase()
    stocks = db.collection('user-stocks').document(email_id).get().to_dict()
    if stock_to_buy in stocks:
        stocks[stock_to_buy] = stocks[stock_to_buy]+1
    else:
        stocks[stock_to_buy] = 1
    db.collection("user-stocks").document(email_id).set(stocks)
    return json.dumps({stock_to_buy: stocks[stock_to_buy]})
    
    


if __name__ == '__main__':
   app.run(port=5000, debug=True)
