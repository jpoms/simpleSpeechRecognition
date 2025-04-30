@echo off

SET VENV_DIR=".venv"
IF NOT EXIST "%VENV_DIR%" (
    echo virtual environment not found!
    pause
    exit /b 1
)

echo activating virtual environment...
call "%VENV_DIR%\Scripts\activate"

echo python path is...
where python

echo pip path is...
where pip

pause

pip install --upgrade pip
pip install --upgrade transformers datasets[audio] accelerate
pip install tkinterdnd2

cmd /k