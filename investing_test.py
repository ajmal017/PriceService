import investpy as invest
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import os
try:
    hist_prices = invest.get_stock_historical_data(stock = "4300", country = 'Saudi Arabia',from_date="1/01/2005", to_date="31/12/2020").reset_index(drop = False)
    hist_prices = hist_prices[['Date','Close']]
    hist_prices.set_index('Date',inplace = True)
    print(hist_prices)
    hist_prices.plot()
    plt.show()
except IndexError as e:
    print(str(e))

#{"id_": 8880, "name": "US 10 Year T-Note Futures", 
# "symbol": "TY", 
# "country": "united states",
#  "tag": "us-10-yr-t-note", 
# "pair_type": "bond", 
# "exchange": ""}