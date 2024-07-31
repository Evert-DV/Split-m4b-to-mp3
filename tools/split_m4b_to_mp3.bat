@echo off
setlocal

echo Creating Python virtual environment and running pip, this may take a second...

REM Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"

REM Set the Python virtual environment directory
set "VENV_DIR=%SCRIPT_DIR%my_venv"

REM Create the Python virtual environment
python -m venv "%VENV_DIR%"

REM Activate the virtual environment
call "%VENV_DIR%\Scripts\activate"

REM Install natsort package
pip install natsort -q

REM Run your Python script
REM Make sure to replace 'your_script.py' with the actual script name
python "%SCRIPT_DIR%/split_m4b_to_mp3.py"

REM Deactivate the virtual environment
call "%VENV_DIR%\Scripts\deactivate"

echo Removing the virtual environment directory...

echo Finished.

pause

REM Remove the virtual environment directory
rmdir /s /q "%VENV_DIR%"

endlocal
