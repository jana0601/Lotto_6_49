@echo off
setlocal
cd /d "%~dp0"

py -3.14 -m pip install -r requirements-build.txt
py -3.14 -m PyInstaller --noconfirm --clean Lotto_6_49.spec

echo.
echo Output: %~dp0dist\Lotto_6_49.exe
endlocal
