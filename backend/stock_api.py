import finnhub
import flair
from trial import sentiment_model

def get_stock_symbol(stock_name):
  result  = finnhub_client.symbol_lookup(stock_name)
  if result['count']>=1:
    return result['result'][0]['displaySymbol']
  else:
    return "ERROR"
def get_stock_price(stock_name):
  stock_symbol = get_stock_symbol(stock_name)
  result = finnhub_client.quote(stock_symbol)
  return result

def get_stock_news(stock_name):
  stock_symbol = get_stock_symbol(stock_name)
  result = finnhub_client.company_news(stock_symbol, _from="2021-11-07", to="2021-11-13")
  return result

def get_stock_sentiment(stock_name):
  result = get_stock_news(stock_name)
  sentiment = 0.0
  count = 0
  for dictionary in result:
    if dictionary['headline'] != "":
      count = count + 1
      sentence = flair.data.Sentence(dictionary['headline'])
      sentiment_model.predict(sentence)
      sentiment+=sentence.labels[0].score
  if count>=1:
    return sentiment/count
  else:
    return "ERROR"

def general_news():
  return finnhub_client.general_news('general', min_id=0)[:5]

