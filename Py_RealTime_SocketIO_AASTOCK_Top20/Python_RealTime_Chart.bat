if not "%minimized%"=="" goto :minimized
set minimized=true
start /min cmd /C "%~dpnx0"
goto :EOF
:minimized
D:\Anaconda35\Scripts\activate.bat D:\Anaconda35 && python D:\Python_RealTime_SocketIO_AASTOCK_Top20\python_realtime_chart.py 0162.HK