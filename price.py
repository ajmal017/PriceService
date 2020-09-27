from security import *
import datetime as dt
import investpy as invest
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

current_year = dt.datetime.today().year

class Price():
    def __init__(self, security : Security, start_year , end_year = current_year):
        self.security = security
        self.start_year = start_year
        self.end_year = end_year
        self.investing_prices = pd.DataFrame()
        self.yahoo_prices = pd.DataFrame()
        self.prices = self.get_prices()
        #self.prices[['Close']].plot()
        #plt.show()
    
    def get_prices(self):
        """fetchs prices from database if existing or investing/yahoo api"""
        prices = []
        query_years = [year for year in range(self.start_year, self.end_year+1)]
        self.missing_years = []
        for year in query_years:
            price_query = table.find_one({'ticker':self.security.ticker, 'year':year})
            if price_query is not None:
                print('{} ok'.format(year))
                prices.append(pd.read_json(price_query['historical_prices'], orient = 'table').reset_index(drop=False))
            else:
                print('{} NONE'.format(year))
                self.missing_years.append(year)
        if len(prices)!=0:
            prices = pd.concat(prices)
        else:
            prices = pd.DataFrame()
        if len(self.missing_years) == 0:
            return prices
        else:
            self.missing_years.sort()
            self.get_investing_price()
            self.get_yahoo_price()
            self.investing_prices['year'] = self.investing_prices['Date'].map(lambda date: date.year)
            self.yahoo_prices['year'] = self.yahoo_prices['Date'].map(lambda date: date.year)
            self.investing_prices = self.investing_prices[self.investing_prices['year'].isin(self.missing_years)]
            self.yahoo_prices = self.yahoo_prices[self.yahoo_prices['year'].isin(self.missing_years)]
            #self.investing_prices.drop('year', axis = 1, inplace = True)
            #self.yahoo_prices.drop('year', axis = 1, inplace = True)
            new_prices = self.choose_prices()
            self.insert_into_db(new_prices)
            new_prices.drop('year', axis = 1, inplace = True)
            if len(new_prices) != 0:
                output = pd.concat([prices,new_prices])
                #print(output)
                output.set_index('Date', inplace = True)
                output.sort_index(axis = 0, inplace = True)
                return output

    def get_investing_price(self):
        try:
            instrument_nature = self.security.instrument_type
            asset_country = self.security.country
            investing_ticker = self.security.investing_ticker
            start_date = '01/01/{}'.format(self.start_year)
            end_date = '31/12/{}'.format(self.end_year)
            if instrument_nature=="STOCK":
                hist_prices = invest.get_stock_historical_data(stock=investing_ticker,country=asset_country,from_date=start_date,to_date=end_date).reset_index(drop = False)
            elif instrument_nature=="ETF":
                hist_prices=invest.get_etf_historical_data(etf=investing_ticker, country=asset_country, from_date=start_date, to_date=end_date).reset_index(drop = False)
            elif instrument_nature=="index":
                hist_prices=invest.get_index_historical_data(index=investing_ticker, country=asset_country, from_date=start_date, to_date=end_date).reset_index(drop = False)
            elif instrument_nature=="Curr":
                hist_prices=invest.currency_crosses.get_currency_cross_historical_data(currency_cross=investing_ticker, from_date=start_date, to_date=end_date).reset_index(drop = False)
            elif instrument_nature=='BOND':
                hist_prices=invest.bonds.get_bond_historical_data(bond=investing_ticker, from_date=start_date, to_date=end_date).reset_index(drop = False)
            elif instrument_nature=='commodity':
                hist_prices=invest.commodity.get_bond_historical_data(commodity=investing_ticker, from_date=start_date, to_date=end_date).reset_index(drop = False)
            self.investing_prices = hist_prices
        except Exception as e:
            #print(str(e))
            #logger.error("Error in get_investing_price: {}".format(str(e)))
            hist_prices = pd.DataFrame()
            self.investing_prices = hist_prices

    def get_yahoo_price(self):
        try:
            yahoo_prices = yf.download(tickers = self.security.yahoo_ticker, start = "{}-01-01".format(self.start_year), end = "{}-12-31".format(self.end_year), threads=False, verify = False)
            yahoo_prices.reset_index(drop = False, inplace = True)
            self.yahoo_prices = yahoo_prices
        except Exception as e:
            #logger.error("Error in get_yahoo_price: {}".format(str(e)))
            #print(str(e))
            yahoo_prices = pd.DataFrame()
            self.yahoo_prices = yahoo_prices

    def choose_prices(self):
        """compares yahoo prices with investing prices and returns the best"""
        if len(self.investing_prices) >= len(self.yahoo_prices):
            prices = self.investing_prices
        else:
            prices = self.yahoo_prices
        if len(prices) != 0:
            #prices.set_index('Date', inplace=True)
            return prices
        else:
            return prices

    def insert_into_db(self, prices):
        """inserts prices to database if non existing, updates existing prices"""
        entry_prices = prices.copy()
        entry_prices.set_index('year', inplace = True)
        idxs = entry_prices.index.drop_duplicates(keep = 'first')
        for idx in idxs: 
            query = table.find_one({'ticker':self.security.ticker, 'year':idx})
            if query is None :
                entry = {'ticker': self.security.ticker, 'year': idx, 'historical_prices': entry_prices.loc[idx].set_index('Date').to_json(orient = 'table')}
                table.insert_one(entry)
                #logger.info("The {} prices for {} were inserted into the database".format(idx, ticker))
            else:
                updated = { "$set": { "historical_prices":  entry_prices.set_index('Date').to_json(orient = 'table') } }
                table.update_one(query, updated)
                #logger.info("The {} prices for {} were updated in the database".format(idx, ticker))
        entry_prices.reset_index(drop = True, inplace = True)

"""
sec = Security('IVV')
print(sec.get_security_info())
"""
start = 2005
end = 2020

#dp = Price(sec,start,end)

#dp.choose_prices()

#print(dp.prices)
#print(dp.security.get_security_info())


query = mapping.find()
errors = []
missing = []
for item in query:
    ticker = item['ticker']
    try:
        sec = Security(ticker)
        print(sec.get_security_info())
        dp = Price(sec,start,end)
        #dp.choose_prices()
        if len(dp.prices) != 0 :
            dp.prices[['Close']].plot()
            plt.savefig('Plots/{}.png'.format(ticker))
            print('{} OK'.format(ticker))
        else:
            print('No prices for {}'.foramt(ticker))
            missing.append(ticker)
    except :
        errors.append(ticker)
        continue

print('Errors : ',errors)
print('Missing : ',missing)
