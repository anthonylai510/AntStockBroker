from datetime import datetime, date, timedelta
from matplotlib.ticker import Formatter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import dask.dataframe as dd
import pandas as pd
import numpy as np
import sys


EndDate = date.today() + timedelta(1)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


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

    #df = pd.read_csv('.\\{0}_{1}-{2}-{3}.csv'.format(symbol, EndDate.year, EndDate.month, EndDate.day), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df = dd.read_csv('./data/{0}_*.csv'.format(symbol), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df = df.compute()

    price_min = df['Close'].min()
    price_max = df['Close'].max()

    # Fibonacci Levels considering original trend as upward move
    diff = price_max - price_min
    level1 = price_max - 0.236 * diff
    level2 = price_max - 0.382 * diff
    level3 = price_max - 0.618 * diff


    #df['SMA(10)'] = df['Close'].rolling(window=10).mean()
    #df['SMA(20)'] = df['Close'].rolling(window=20).mean()
    #df['SMA(50)'] = df['Close'].rolling(window=50).mean()
    df['SMA(200)'] = df['Close'].rolling(window=200).mean()
    df['SMA(150)'] = df['Close'].rolling(window=150).mean()


    #list = df['Close'].tolist()

    #y = df['Close'].tail(60).values
    #x = df.tail(60).index.values

    #fit = np.polyfit(x, y, deg=1)


    print(df.tail(5))

    ax1.clear()
    ax1.set_title(symbol)
    #ax1.plot(x, fit[0] * x + fit[1], color='red', linewidth=5.0)

    ax1.axhspan(level1, price_min, alpha=0.4, color='lightsalmon')
    #ax1.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
    ax1.axhspan(level2, level1, alpha=0.5, color='gold')
    ax1.axhspan(level3, level2, alpha=0.5, color='palegreen')
    ax1.axhspan(price_max, level3, alpha=0.5, color='powderblue')

    df.plot(y= ['Close', 'High'], color=['Blue','Green'], ax=ax1)
    #df.plot(y= ['SMA(10)', 'SMA(20)', 'SMA(50)'], color=['Red', 'Yellow', 'Purple'], ax=ax1)
    df.plot(y= ['SMA(150)', 'SMA(200)'], color=['Yellow', 'Purple'], ax=ax1)
    yLast = df.tail(1)['Close'].values[0]
    #print(yLast)
    plt.annotate('%0.3f' % yLast, xy=(1, yLast), xytext=(8, 0), xycoords=('axes fraction', 'data'), textcoords='offset points')
    plt.axhline(y=yLast, color='y', linestyle='-.')


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
    if len(sys.argv) < 2:
        print('Please provide valid stock quotoe. e.g. python python_realtime_chart.py 0005.HK')
        sys.exit(2)
    print(sys.argv)
    symbol = sys.argv[1]
    ani = animation.FuncAnimation(fig, animate, fargs=(symbol,), interval=1000)
    plt.show()