@echo off
echo ========================================================
echo               BUILDING JORA APPLICATION
echo ========================================================
echo.

:: 1. Hapus folder build & dist lama biar bersih
echo [1/3] Cleaning up old build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /f /q "*.spec"

:: 2. Jalankan PyInstaller
echo [2/3] Compiling JORA to standalone .exe...
pyinstaller --noconsole ^
            --onefile ^
            --name "JORA" ^
            --icon=JORA_logo.ico ^
            --add-data "JORA_logo.ico;." ^
            --add-data "C:\Users\ASUS\AppData\Roaming\Python\Python314\site-packages\pykakasi;pykakasi" ^
            jora_gui.py

:: 3. Status Selesai
echo.
if exist "dist\JORA.exe" (
    echo ========================================================
    echo [SUCCESS] JORA.exe successfully created in 'dist' folder!
    echo ========================================================
) else (
    echo ========================================================
    echo [ERROR] Build failed. Please check the error log above.
    echo ========================================================
)

echo.
pause