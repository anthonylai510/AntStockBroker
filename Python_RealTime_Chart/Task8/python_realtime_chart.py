from mpl_finance import volume_overlay3, candlestick_ochl
from datetime import datetime, date, timedelta
from matplotlib.ticker import Formatter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import dask.dataframe as dd
import pandas as pd
import numpy as np
import sys

import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'

EndDate = date.today() + timedelta(1)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx()

def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0


def SimpleMovingAverage(values, window):
    weigths = np.repeat(1.0, window)/window
    sma = np.convolve(values, weigths, 'valid')
    return sma # as a numpy array


def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a


def animate(i, symbol):
    print(symbol)

    df = dd.read_csv('./{0}_*.csv'.format(symbol), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Volume'] = df['Volume'].apply(value_to_float)
    df = df.compute()

    #Read the FB_Max and FB_Min from file
    dfFB = pd.read_csv('./FB_Max_Min.csv', header=0)
    price_max = dfFB['FB_Max'].tail(1).values[0]
    price_min = dfFB['FB_Min'].tail(1).values[0]
    if(price_max == 0.0 and price_min == 0.0):
        #price_max = df['Close'].max()
        #price_min = df['Close'].min()
        price_max = 2*(df['Close'].max() + df['Close'].min() + df['Close'].tail(1).values[0])/3 - df['Close'].min()
        price_min = 2*(df['Close'].max() + df['Close'].min() + df['Close'].tail(1).values[0])/3 - df['Close'].max()


    # Fibonacci Levels considering original trend as upward move
    diff = price_max - price_min
    level1 = price_max - 0.236 * diff
    level2 = price_max - 0.382 * diff
    level3 = price_max - 0.618 * diff


    df['Volume_New'] = df['Volume'] - df['Volume'].shift(1)
    df['Volume_New'] = df['Volume_New'].fillna(0)
    df['Volume_New'] = np.where(df['Volume_New'] < 0, 0, df['Volume_New'])
    #df['Volume_New'] = df['Volume_New']/1e6  # dollar volume in millions


    #df['SMA(10)'] = df['Close'].rolling(window=10).mean()
    #df['SMA(20)'] = df['Close'].rolling(window=20).mean()
    #df['SMA(50)'] = df['Close'].rolling(window=50).mean()
    df['SMA(150)'] = df['Close'].rolling(window=150).mean()
    df['SMA(200)'] = df['Close'].rolling(window=200).mean()


    #y = df['Close'].tail(60).values
    #x = df.tail(60).index.values

    #fit = np.polyfit(x, y, deg=1)
    titleColor = 'red'
    pctChange = 100*(df['Close'].tail(1).values[0] - df['Open'].tail(1).values[0]) / df['Open'].tail(1).values[0]
    if pctChange > 0:
        titleColor = 'green'
    elif pctChange == 0.0:
        titleColor = 'black'


    df2 = df[['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    print(df2.head(5))

    #clear ax1, ax2
    ax1.clear()
    ax2.clear()
    ax1.set_title('{0} ({1:.2f}%)'.format(symbol, pctChange), color=titleColor, fontsize= 15)
    #ax1.plot(x, fit[0] * x + fit[1], color='red', linewidth=5.0)

    ax1.axhspan(level1, price_min, alpha=0.4, color='lightsalmon')
    #ax1.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
    ax1.axhspan(level2, level1, alpha=0.5, color='gold')
    ax1.axhspan(level3, level2, alpha=0.5, color='palegreen')
    ax1.axhspan(price_max, level3, alpha=0.5, color='powderblue')

    #Plot Close, High as line
    df.plot(y= ['Close', 'High'], color=['Blue','Green'], ax=ax1)
    #df.plot(y= ['SMA(10)', 'SMA(20)', 'SMA(50)', 'SMA(200)'], color=['Red', 'Yellow', 'Purple', 'Orange'], ax=ax1)
    #df.plot(y= ['SMA(10)', 'SMA(50)', 'SMA(200)'], color=['Red', 'Purple', 'Orange'], ax=ax1)
    df.plot(y= ['SMA(150)', 'SMA(200)'], color=['Yellow', 'Purple'], ax=ax1)


    yLast = df.tail(1)['Close'].values[0]
    #print(yLast)
    ax1.annotate('%0.3f' % yLast, xy=(0.95, yLast), xytext=(8, 0), xycoords=('axes fraction', 'data'), textcoords='offset points')
    ax1.axhline(y=yLast, color='y', linestyle='-.')
    ax1.legend(loc='upper left')

    #Plot Volume as positive and negative bar
    #df['Volume']=df['Volume'].loc[::10]
    quotes = list(zip(df.index.tolist(), df['Open'].tolist(), df['High'].tolist(), df['Low'].tolist(), df['Close'].tolist(), df['Volume_New'].tolist()))
    bc = volume_overlay3(ax2, quotes, colorup='g', colordown='r', width=2.5, alpha=1.0)
    ax2.set_ylim(df['Volume_New'].min(), 5*df['Volume_New'].max())
    ax2.add_collection(bc)



    # Formatter Class to eliminate weekend data gaps on chart
    class MyFormatter(Formatter):
        def __init__(self, datetimes, fmt='%Y-%m-%d %H:%M:%S'):
            self.datetimes = datetimes
            self.fmt = fmt
        def __call__(self, x, pos=0):
            'Return the label for time x at position pos'
            ind = int(round(x))
            #print(ind)
            
            
            if ind>=len(self.datetimes) or ind<0: 
                return ''          

            #print(self.datetimes[ind])
            return self.datetimes[ind].strftime(self.fmt)
            #return self.dates[ind]

    dff = pd.to_datetime(df['DateTime'])
    #print(type(dff))
    formatter = MyFormatter(dff)

    ax1.set_xticklabels(df["DateTime"].tolist(), rotation=15, ha='right')
    ax1.xaxis.set_major_formatter(formatter)    
    #ax1.set_xlim(0, len(df)-1)
    
    ax1.minorticks_on()
    # Customize the major grid
    ax1.grid(which='major', linestyle='-', linewidth='0.5', color='red')
    # Customize the minor grid
    ax1.grid(which='minor', linestyle=':', linewidth='0.5', color='black')


if __name__ == '__main__':
    #if len(sys.argv) < 2:
    #    print('Please provide valid stock quotoe. e.g. python python_realtime_chart.py 0005.HK')
    #    sys.exit(2)
    #print(sys.argv)
    #symbol = sys.argv[1]

    #Read ticker to DataFrame
    filePath = '../Task_Ticker.csv'
    dfA = pd.read_csv(filePath)
    df = dfA[dfA['Task_Id'] == 8]
    #print(df['Ticker'].values)
    symbol = df['Ticker'].values[0]

    ani = animation.FuncAnimation(fig, animate, fargs=(symbol,), interval=1000)
    plt.show()