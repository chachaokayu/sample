@echo off


if not exist ".venv" ( call python -m venv .venv )

call ..venv\Scripts\activate

call pip install python==3.10.8

call pip install -r .\requirements.txt

pause @echo on