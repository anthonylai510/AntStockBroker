if not "%minimized%"=="" goto :minimized
set minimized=true
start /min cmd /C "%~dpnx0"
goto :EOF
:minimized
D:\Anaconda3\Scripts\activate.bat D:\Anaconda3\envs\tensorflow && python D:\Python_RealTime_Chart\Task8\python_realtime_chart.py 0554.HK