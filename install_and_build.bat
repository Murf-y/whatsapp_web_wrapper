@echo off

rem Check if Python is installed and install it if not
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    curl https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe -o python-3.9.6-amd64.exe
    python-3.9.6-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python-3.9.6-amd64.exe
    echo Python installed.
)

rem Check if pip is installed and install it if not
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not installed. Installing Pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

rem Install requirements.txt
pip install -r requirements.txt

echo Building APPLICATION 1 executable
pyinstaller --onefile application1.py --name application1

@REM remove spec file and build folder
rmdir /s /q build
del application1.spec

@REM Move the executable from dist to the root folder
move dist\application1.exe .
rmdir /s /q dist

echo Build application1 complete.

echo Building APPLICATION 2 executable
pyinstaller --onefile --noconsole application2.py --name application2

@REM remove spec file and build folder
rmdir /s /q build
del application2.spec

@REM Move the executable from dist to the root folder
move dist\application2.exe .
rmdir /s /q dist

echo Build application2 complete.