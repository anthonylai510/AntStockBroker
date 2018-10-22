from datetime import datetime, date, timedelta
from matplotlib.ticker import Formatter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import dask.dataframe as dd
import pandas as pd
import numpy as np
import sys
from mpl_finance import volume_overlay3, candlestick_ochl
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes


import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'


idx = 1

print(pd.__version__)

#df = dd.read_csv('./{0}_*.csv'.format('2967.HK'), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
#df['Close'] = df['Close'].astype('float').round(4)
#df['Volume'] = (df['Volume'].replace(r'[KM]+$', '', regex=True).astype(float) * df['Volume'].str.extract(r'[\d\.]+([KM]+)', expand=False).fillna(1).replace(['K','M'], [10**3, 10**6]).astype(int))
#df['Volume'] = df['Volume'].apply(value_to_float)
#df = df.compute()

EndDate = date.today() + timedelta(1)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx()
# generate inset axes
#axins = zoomed_inset_axes(ax1, zoom=1.0, loc=10)  # zoom = 1.5





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


def data_gen(symbol):
    try:
        cnt = 0
        df = dd.read_csv('./{0}_*.csv'.format(symbol), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Close'] = df['Close'].astype('float').round(4)
        df['Volume'] = df['Volume'].apply(value_to_float)
        df = df.compute()
        while cnt < len(df):
            print('cnt: {0}, len(df): {1}'.format(cnt, len(df)))
            cnt += 1
            yield df.head(cnt)
    except Exception as e:
        print('Error generating data for {0}: {1}'.format(symbol, str(e)))



#def animate(i, symbol, idx):
def animate(df, symbol, idx):
    try:
        print(symbol)

        #df = pd.read_csv('.\\{0}_{1}-{2}-{3}.csv'.format(symbol, EndDate.year, EndDate.month, EndDate.day), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
        #df = dd.read_csv('./{0}_*.csv'.format(symbol), header=None, names=['DateTime','Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'])
        #df = df.compute()
        #df = df.head(idx)
        #idx= idx + 1

        #dfFB = dd.read_csv('./FB_Max_Min.csv', header=None, names=['FB_Max', 'FB_Min'])
        dfFB = pd.read_csv('./FB_Max_Min.csv', header=0)
        price_max = dfFB['FB_Max'].tail(1).values[0]
        price_min = dfFB['FB_Min'].tail(1).values[0]
        #print('idx= {0}, price_max = {1}, price_min={2}'.format(idx, price_max, price_min))
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

        #find OVB
        #df['OVB'] = (df['Volume'] * (~df['Close'].diff().le(0) * 2 - 1)).cumsum()

        df['Volume_New'] = df['Volume'] - df['Volume'].shift(1)
        df['Volume_New'] = df['Volume_New'].fillna(0)
        df['Volume_New'] = np.where(df['Volume_New'] < 0, 0, df['Volume_New'])
        #df['Volume'] = df['Volume']/1e6  # dollar volume in millions

        #df['SMA(10)'] = df['Close'].rolling(window=10).mean()
        #df['SMA(20)'] = df['Close'].rolling(window=20).mean()
        #df['SMA(50)'] = df['Close'].rolling(window=50).mean()
        df['SMA(200)'] = df['Close'].rolling(window=200).mean()
        df['SMA(150)'] = df['Close'].rolling(window=150).mean()



        #y = df['Close'].tail(60).values
        #x = df.tail(60).index.values

        #fit = np.polyfit(x, y, deg=1)
        titleColor = 'red'
        pctChange = 100*(df['Close'].tail(1).values[0] - df['Open'].tail(1).values[0]) / df['Open'].tail(1).values[0]
        if pctChange > 0.0:
            titleColor = 'green'
        elif pctChange == 0.0:
            titleColor = 'black'

        df2 = df[['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']]
        print(df2.tail(5))

        ax1.clear()
        ax2.clear()
        #axins.clear()

        ax1.set_title('{0} ({1:.2f}%)'.format(symbol, pctChange), color=titleColor, fontsize= 15, fontweight='bold')
        #ax1.plot(x, fit[0] * x + fit[1], color='red', linewidth=5.0)

        ax1.axhspan(level1, price_min, alpha=0.4, color='lightsalmon')
        #ax1.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
        ax1.axhspan(level2, level1, alpha=0.5, color='gold')
        ax1.axhspan(level3, level2, alpha=0.5, color='palegreen')
        ax1.axhspan(price_max, level3, alpha=0.5, color='powderblue')

        df.plot(y= ['Close', 'High'], color=['Blue','Green'], ax=ax1)
        #quotes = list(zip(df.index.tolist(), df['Open'].tolist(), df['High'].tolist(), df['Low'].tolist(), df['Close'].tolist(), df['Volume'].tolist()))
        #candlestick_ochl(ax1, quotes, colorup='b', colordown='g', width=0.2, alpha=1.0)
        #df.plot(y= ['SMA(10)', 'SMA(20)', 'SMA(50)', 'SMA(200)'], color=['Red', 'Yellow', 'Purple', 'Orange'], ax=ax1)
        #df.plot(y= ['SMA(10)', 'SMA(50)', 'SMA(150)'], color=['Red', 'Purple', 'Yellow'], ax=ax1)
        df.plot(y= ['SMA(150)', 'SMA(200)'], color=['Yellow', 'Purple'], ax=ax1)


        yLast = df['Close'].tail(1).values[0]
        #print(yLast)
        #plt.annotate('%0.3f' % yLast, xy=(1, yLast), xytext=(8, 0), xycoords=('axes fraction', 'data'), textcoords='offset points')
        #plt.axhline(y=yLast, color='y', linestyle='-.')
        ax1.annotate('%0.3f' % yLast, xy=(0.95, yLast), xytext=(8, 0), xycoords=('axes fraction', 'data'), textcoords='offset points')
        ax1.axhline(y=yLast, color='y', linestyle='-.')
        ax1.legend(loc='upper left')
        #ax1.margins(x=0, y=0.25)   # Values in (-0.5, 0.0) zooms in to center
        # Plot Volume Chart
        #df['Price * Volume'] = (df['Close'] * df['Volume'])/1e6  # dollar volume in millions
        #vmax = df['Price * Volume'].max()
        #df.plot(y= ['Price * Volume'], kind='bar', legend=False, color=['Orange'], ax=ax2)
        #df['Volume'] = df['Volume']/1e6  # dollar volume in millions

        #vmin = df['Volume'].min()
        #vmax = df['Volume'].max()
        #df['Volume']=df['Volume'].loc[::5]
        #df.plot(y= ['Volume'], legend=False, color=['Orange'], ax=ax2)
        #df.plot(y= ['Volume'], kind='bar', color=['Orange'], ax=ax2)
        #ax2.set_ylim(vmin, 5*vmax)
        #ax.set_yticks([])
        #ax2.xaxis.label.set_visible(False)

        # Plot Volume Chart
        quotes = list(zip(df.index.tolist(), df['Open'].tolist(), df['High'].tolist(), df['Low'].tolist(), df['Close'].tolist(), df['Volume_New'].tolist()))
        bc = volume_overlay3(ax2, quotes, colorup='g', colordown='r', width=2.5, alpha=1.0)
        ax2.set_ylim(df['Volume_New'].min(), 5*df['Volume_New'].max())
        #ax2.margins(x=0, y=0.25)   # Values in (-0.5, 0.0) zooms in to center
        ax2.add_collection(bc)


        # plot in the inset axes
        #df.plot(y= ['Close', 'High'], color=['Blue','Green'], ax=axins)
        # fix the x, y limit of the inset axes
        #axins.set_xlim(-1, 1)
        #axins.set_ylim(-1, 1)

        #vmin = df['Volume'].min()
        #vmax = df['Volume'].max()
        #df.plot(y= ['Volume'], legend=False, color=['Orange'], ax=ax2)
        #df.plot(y= ['Volume'], kind='bar', color=['Orange'], ax=ax2)
        #ax2.set_ylim(vmin, 3*vmax)
        #ax.set_yticks([])
        #ax2.xaxis.label.set_visible(False)



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
        #ax2.set_xticklabels(df["DateTime"].tolist(), rotation=15, ha='right')
        ax1.xaxis.set_major_formatter(formatter) 
        #ax2.xaxis.set_major_formatter(formatter)    

        #Don't set the xlim; commented by Anthony Lai on 2018-08-19 because price on chart will look better for the beginning and end
        #ax1.set_xlim(0, len(df)-5)

        ax1.minorticks_on()
        #ax2.minorticks_on()
        # Customize the major grid
        ax1.grid(which='major', linestyle='-', linewidth='0.5', color='red')
        #ax2.grid(which='major', linestyle='-', linewidth='0.5', color='red')
        # Customize the minor grid
        ax1.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
        #ax2.grid(which='minor', linestyle=':', linewidth='0.5', color='black')


    except Exception as e:
        print('Error plotting data for {0}: {1}'.format(symbol, str(e)))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide valid stock quotoe. e.g. python python_realtime_chart.py 0005.HK')
        sys.exit(2)
    print(sys.argv)
    symbol = sys.argv[1]
    ani = animation.FuncAnimation(fig, animate, data_gen(symbol), fargs=(symbol, idx), interval=500)
    plt.show()