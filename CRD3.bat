REM Anaconda3 Environment
REM set root=%USERPROFILE%\anaconda3
set root=%LOCALAPPDATA%\miniconda3
call %root%\Scripts\activate.bat %root%
REM call conda env list
call conda activate base

REM Start App
call cd /d D:\git\CRD3\
call python CRD3.py

REM pause
exit