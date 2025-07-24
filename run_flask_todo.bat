@echo off

:: 切换到项目文件夹
cd /d "C:\Users\Administrator\Work\flask_todo_app"

:: 激活虚拟环境
call todo_venv\Scripts\activate.bat

start /B pythonw app.pyw

@REM # 临时调试，端口是 5990
@REM # 开机运行，端口是 5995

@REM 把这个 bat 文件, 复制一份，放到启动目录
@REM C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup 


