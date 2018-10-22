if not "%minimized%"=="" goto :minimized
set minimized=true
start /min cmd /C "%~dpnx0"
goto :EOF
:minimized
D:\Anaconda3\Scripts\activate.bat D:\Anaconda3\envs\tensorflow && python D:\Python_RealTime_Chart\Task10\python_realtime_chart.py 2312.HK