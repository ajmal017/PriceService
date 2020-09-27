from pymongo import MongoClient
import os

MONGO_HOST = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'B2Cdev_db'

MONGO_DB_NAME = {'db': os.environ.get('MONGO_DB_NAME',MONGO_DB_NAME), 
                 'host': os.environ.get('MONGO_HOST', MONGO_HOST)}

client = MongoClient(MONGO_DB_NAME['host'])
db = client[MONGO_DB_NAME['db']]
table = db.prices

mapping = db.assets

class Security():
    def __init__(self, ticker):
        specs = mapping.find_one({'ticker':ticker})
        if specs is None:
            raise Exception('{} not found in database !'.format(ticker))
        self.ticker = ticker
        self.country = specs['country']
        self.investing_ticker = str(specs['investing_ticker'])
        self.yahoo_ticker = str(specs['yahoo_ticker'])
        self.instrument_type = specs['asset_class']

    def get_security_info(self):
        return {'Ticker':self.ticker, 'Country':self.country,'Instrument type':self.instrument_type,'investing_ticker':self.investing_ticker,'yahoo_ticker':self.yahoo_ticker}