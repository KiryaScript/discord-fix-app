@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul

echo Checking admin privileges...
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Похер, нужны админские права, бери и соглашайся!
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 1
)

:: Settings
set "GITHUB_URL=https://github.com/DevikTeam/nekoray/releases/download/nekotest/nekoray.7z"
set "7ZIP_URL=https://www.7-zip.org/a/7z2500-x64.exe"
set "ARCHIVE_NAME=nekoray.7z"
set "7ZIP_EXE=7z-installer.exe"
set "TEMP_DIR=%TEMP%\nekoray_temp"
set "7ZIP_DIR=%TEMP_DIR%\7zip"
set "INSTALL_DIR=%ProgramFiles%\Nekoray"
set "NEKORAY_EXE=%INSTALL_DIR%\nekoray.exe"
set "LOG_FILE=%TEMP%\nekoray_install.log"

echo [%DATE% %TIME%] Starting Nekoray installation > "%LOG_FILE%"
echo Starting installation...

mode con: cols=80 lines=25
title NEKORAY Installer
color 0B

:: Create temp directories
echo Creating temporary directories...
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
if not exist "%7ZIP_DIR%" mkdir "%7ZIP_DIR%"
if %ERRORLEVEL% neq 0 (
    echo Пиздец, не удалось создать временные папки! >> "%LOG_FILE%"
    echo Пиздец, не удалось создать временные папки!
    pause
    exit /b 1
)
echo [✓] Temporary directories created
echo [%DATE% %TIME%] Temporary directories created >> "%LOG_FILE%"

echo Downloading 7-Zip...
powershell -Command "try { Invoke-WebRequest -Uri '%7ZIP_URL%' -OutFile '%TEMP_DIR%\%7ZIP_EXE%' -ErrorAction Stop } catch { Write-Error $_.Exception.Message; exit 1 }"
if not exist "%TEMP_DIR%\%7ZIP_EXE%" (
    echo Похер, не удалось скачать 7-Zip! >> "%LOG_FILE%"
    echo Похер, не удалось скачать 7-Zip!
    pause
    exit /b 1
)
echo [✓] 7-Zip downloaded
echo [%DATE% %TIME%] 7-Zip downloaded >> "%LOG_FILE%"

echo Installing 7-Zip...
start /wait "" "%TEMP_DIR%\%7ZIP_EXE%" /S /D="%7ZIP_DIR%"
if not exist "%7ZIP_DIR%\7z.exe" (
    echo Похер, 7-Zip не установился, проверяй, что за херня! >> "%LOG_FILE%"
    echo Похер, 7-Zip не установился!
    pause
    exit /b 1
)
echo [✓] 7-Zip installed
echo [%DATE% %TIME%] 7-Zip installed >> "%LOG_FILE%"

echo Downloading NEKORAY...
powershell -Command "try { Invoke-WebRequest -Uri '%GITHUB_URL%' -OutFile '%TEMP_DIR%\%ARCHIVE_NAME%' -ErrorAction Stop } catch { Write-Error $_.Exception.Message; exit 1 }"
if not exist "%TEMP_DIR%\%ARCHIVE_NAME%" (
    echo Пиздец, не удалось скачать NEKORAY! >> "%LOG_FILE%"
    echo Пиздец, не удалось скачать NEKORAY!
    pause
    exit /b 1
)
echo [✓] NEKORAY downloaded
echo [%DATE% %TIME%] NEKORAY downloaded >> "%LOG_FILE%"

echo Extracting archive...
"%7ZIP_DIR%\7z.exe" x "%TEMP_DIR%\%ARCHIVE_NAME%" -o"%INSTALL_DIR%" -y >nul
if %ERRORLEVEL% neq 0 (
    echo Не удалось распаковать архив, пиздец! >> "%LOG_FILE%"
    echo Не удалось распаковать архив!
    pause
    exit /b 1
)
echo [✓] Extraction complete
echo [%DATE% %TIME%] Extraction complete >> "%LOG_FILE%"

echo Cleaning up...
del "%TEMP_DIR%\%ARCHIVE_NAME%" >nul 2>&1
del "%TEMP_DIR%\%7ZIP_EXE%" >nul 2>&1
rmdir /s /q "%7ZIP_DIR%" >nul 2>&1
rmdir /s /q "%TEMP_DIR%" >nul 2>&1
if exist "%TEMP_DIR%" (
    echo Не удалось полностью очистить временные файлы, пиздец, проверяй! >> "%LOG_FILE%"
    echo Не удалось полностью очистить временные файлы!
)
echo [✓] Cleanup complete
echo [%DATE% %TIME%] Cleanup complete >> "%LOG_FILE%"

if exist "%NEKORAY_EXE%" (
    echo Launching NEKORAY...
    start "" "%NEKORAY_EXE%"
    echo [%DATE% %TIME%] NEKORAY launched >> "%LOG_FILE%"
) else (
    echo Похер, nekoray.exe не найден, что-то пошло не так! >> "%LOG_FILE%"
    echo Похер, nekoray.exe не найден!
    pause
    exit /b 1
)

mshta vbscript:Execute("msgbox ""Everything is ready to use"" & vbCrLf & ""(with love from devik)"",0,""NEKORAY"":close")
echo [%DATE% %TIME%] Installation completed >> "%LOG_FILE%"
echo Installation completed!

pause
exit