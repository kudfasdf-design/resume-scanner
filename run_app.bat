@echo off
set PYTHONPATH=%~dp0;%~dp0.venv\Lib\site-packages
"%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m streamlit run app.py

