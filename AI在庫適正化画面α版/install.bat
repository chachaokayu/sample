chcp 65001

@echo off
if exist ".venv" (
    GOTO :CHECK
)else (
    GOTO :INSTALL
)

:CHECK
SET /P INSTALL_CONF="この環境にはライブラリがインストールされています。本当にインストールしますか？（yes）"

IF "%INSTALL_CONF%"=="yes" (ECHO インストールを実施します・・・
)ELSE (GOTO :CHECK)


:INSTALL
if exist ".venv" (rmdir /s /q ".venv")

for /f "usebackq delims=" %%i in (`python --version`) do set python_version=%%i

if not "%python_version%"=="Python 3.7.9" (
    call pyenv local 3.7.9
)

call python -m venv .venv

call .\.venv\Scripts\activate


REM ライブラリのインストール
pip install -r requirements.txt
echo ライブラリのインストールに成功しました


if %errorlevel% neq 0 (


    echo ***************************
    echo Error!!
    echo ***************************
    
    pause
    exit /b
)

echo ***************************
echo Success!!
echo ***************************

pause

