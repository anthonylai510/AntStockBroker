# Ant Stock Broker

## 1.AASTOCK Top 20 Stock List Data Real-Time Streaming 
AASTOCK Top 20 Stock List Data Real-Time Streaming (demo: https://www.youtube.com/watch?v=jsrTexhlBu4)  
Requirements:  
	mpl_finance==0.10.0  
	selenium==3.12.0  
	numpy==1.14.3    
	eventlet==0.23.0  
	Flask==1.0.2  
	dask==0.19.4  
	Flask_SocketIO==2.9.3  
	pandas==0.23.4  
	matplotlib==2.0.2  
	beautifulsoup4==4.6.3  

To get real-time AASTOCK Top 20 Stock List Data,  
change to the directory of `[Py_RealTime_SocketIO_AASTOCK_Top20]` and run the following script:  
	`python get_realtime_aastock_top20_stock_data.py`  

![Getting AASTOCK top 20 Stock List Data](docs/Getting_AASTOCK_Top20_Stock_List_Data.png)

To display real-time AASTOCK Top 20 Stock List Data on web page,  
in the same directory, run the following script and navigate to http://localhost:5001  
	`python app.py`  

![AASTOCK top 20 Stock List Data real-time Streaming results](docs/Top20.png)

## 2.Real-Time Stock List Data with [MACD > EMA and MACD > 0]  
Real-Time Stock List Data where its previous day [MACD > EMA and MACD > 0]  
Requirements:  
	matplotlib==2.0.2  
	Flask==1.0.2  
	eventlet==0.23.0  
	mpl_finance==0.10.0  
	pandas==0.23.4  
	Flask_SocketIO==2.9.3  
	selenium==3.12.0  
	numpy==1.14.3  
	dask==0.19.4  
	beautifulsoup4==4.6.3  

To get Real-Time Stock List data with its previous day [MACD > EMA and MACD > 0],  
change to the directory of `[Python_RealTime_SocketIO_MACD_Over_EMA_Task]` and run the following script:  
	`python py_thread_get_realtime_money18_stock_data.py`  

To display the above real-time Stock List Data on web page,  
in the same directory, run the following script and navigate to http://localhost:6003  
	`python app.py`  

![real-time MACD > EMA and MACD > 0 results](docs/MACD_EMA1.png)

## 3.Real-Time Stock List Data with [MACD > EMA and MACD < 0]
Real-Time Stock List Data where its previous day [MACD > EMA and MACD < 0]  
Requirements:  
	matplotlib==2.0.2
	dask==0.19.4
	Flask_SocketIO==2.9.3
	Flask==1.0.2
	eventlet==0.23.0
	mpl_finance==0.10.0
	selenium==3.12.0
	numpy==1.14.3
	pandas==0.23.4
	beautifulsoup4==4.6.3  

To get Real-Time Stock List data with its previous day [MACD > EMA and MACD < 0],  
change to the directory of `[Python_RealTime_SocketIO_MACD_Over_EMA_Task2]` and run the following script:  
	`python py_thread_get_realtime_money18_stock_data.py`  

To display the above real-time Stock List Data on web page,  
in the same directory, run the following script and navigate to http://localhost:6004  
	`python app.py`  

![real-time MACD > EMA and MACD < 0 results](docs/MACD_EMA2.png)

## 4.Real-Time Stock Chart
Real-Time Stock Chart using mpl_finance.candlestick_ochl and mpl_finance.volume_overlay3
Requirements:  
	dask==0.19.4
	selenium==3.12.0
	matplotlib==2.0.2
	numpy==1.14.3
	pandas==0.23.4
	mpl_finance==0.10.0
	beautifulsoup4==4.6.3  

To run real-time stock chart, first we have to get Real-Time Stock Data. Do the following steps:

i.change to the directory of `[Python_RealTime_Chart]`, open the file `[Task_Ticker.csv]` and
edit the stock list as wanted. `(The list is limited to 10 stocks only)`

ii.change to the directory of `[Python_RealTime_Chart\Taskn]` where n = 0,1,2,..10
and run the following script:  
	`python py_thread_get_realtime_money18_stock_data.py`  

iii.in the same directory above, run the following script to display real-time stock chart:
	`python python_realtime_chart.py`  

Real-Time Stock Chart Demo (https://www.youtube.com/watch?v=2asnITNytdQ)

