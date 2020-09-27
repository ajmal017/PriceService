import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt

start = 2009
end = 2010
yahoo_start = dt.datetime(2016,1,1)
yahoo_end = dt.datetime(2005,12,31)
try:
    yahoo_prices = yf.download(tickers = "4300.SR", start = "{}-01-01".format(start), end = "{}-12-31".format(end), threads=False, verify = False)
    #yahoo_prices.index = dt.datetime.combine(yahoo_prices.index.date, dt.min.time()) 
    #yahoo_prices = yahoo_prices[(yahoo_prices.index <= yahoo_end) & (yahoo_prices >= yahoo_start)]       
    #yahoo_prices['Close'] *= 100 / yahoo_prices['Close'].iat[0]
    yahoo_prices['Close'].plot()
    plt.show()
    print(yahoo_prices)
except Exception as e:
    print(str(e))
#print(yahoo_prices.loc[['AAPL', 'Close']])
