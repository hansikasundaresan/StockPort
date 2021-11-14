import flair
sentiment_model = flair.models.TextClassifier.load('en-sentiment')
import csv
import firebase_admin
from firebase_admin import credentials, firestore
import finnhub
import re
from re import search
import demoji


db= None
def intiliaze_firebase():
    global db
    if db is not None:
        return db
    cred = credentials.Certificate("cred.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def company_sentiment_adder(sentence):
        pass

def remove(sent):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', sent)

def read_file_populate(database, filename = "./sentiment_files/tweets_labelled_09042020_16072020.csv"):
    stock_dict = {}
    finnhub_client = finnhub.Client(api_key="c682tl2ad3iagio36nhg")
    stock_dict["$AAPL"] =["Apple", 0,0]
    stock_dict["$MSFT"] =["Microsoft", 0,0]
    stock_dict["$AMZN"] =["Amazon", 0,0]
    stock_dict["$FB"] =["Facebook", 0,0]
    stock_dict["$GOOG"] =["Google", 0,0]
    stock_dict["$COF"] =["Capital One", 0,0]
    stock_dict["$JPM"] =["JP Morgan Chase", 0,0]
    stock_dict["$GS"] =["Goldman Sachs", 0,0]
    stock_dict["$TSLA"] =["Tesla", 0,0]
    stock_dict["$AAL"] =["American Airlines", 0,0]
    

    
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        #print(fields)
        temp_sentence = ""
        sent = next(csvreader)
        count = 0
        while sent != None:
            if count==12000:
                break
            count+=1
            next_sent = next(csvreader)
            if next_sent == []:
                continue
            if search(re.compile("[0-9]+;2020"), next_sent[0]):
                new_row = sent[0].split(';', 2)[2]
                new_row =demoji.replace(new_row, "")
                for stock_symbol in stock_dict:
                    if stock_symbol in new_row.upper() or stock_dict[stock_symbol][0].lower() in new_row.lower():
                        sentence = flair.data.Sentence(new_row)
                        sentiment_model.predict(sentence)
                        stock_dict[stock_symbol][1] = stock_dict[stock_symbol][1] + sentence.labels[0].score
                        stock_dict[stock_symbol][2] = stock_dict[stock_symbol][2]+1
                sent = next_sent
            else:
                sent[0]+= next_sent[0]
    
    for stock_symbol in stock_dict:
        tempD = {}
        if stock_dict[stock_symbol][2] != 0:
            tempD["sentiment"] =stock_dict[stock_symbol][1]/stock_dict[stock_symbol][2]
            db.collection("stock_info").document(stock_symbol).set(tempD)
    
    return

def set_up_datebase():
    database = intiliaze_firebase()
    coll = database.collection('stock_info')
    read_file_populate(database = database)

def main():
    #sentence = flair.data.Sentence("")
    #sentiment_model.predict(sentence)
    #print(sentence)
    set_up_datebase()
    return "done"
    
    
if __name__ == '__main__':
    main()
