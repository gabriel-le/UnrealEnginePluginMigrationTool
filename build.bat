@echo off
echo Building Unreal Plugin Migration Tool...
echo.

REM Check if pyinstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    echo.
)

REM Ensure flet_desktop is installed (needed for native window builds)
python -m pip show flet-desktop >nul 2>&1
if errorlevel 1 (
    echo flet-desktop not found. Installing...
    python -m pip install flet-desktop
    echo.
)

REM Build the executable as a single file
echo Creating single-file executable...
pyinstaller --name="UnrealPluginMigrationTool" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --collect-data flet ^
    --collect-data flet_core ^
    --hidden-import=flet_desktop ^
    --collect-all flet_desktop ^
    UnrealPluginMigrationTool.py

echo.
if exist "dist\UnrealPluginMigrationTool.exe" (
    echo Build successful!
    echo Executable location: dist\UnrealPluginMigrationTool.exe
    echo.
    echo This is a single-file executable that can be distributed standalone.
    echo You can now upload this .exe file to GitHub Releases.
) else (
    echo Build failed! Check the output above for errors.
)

REM Skip pause in CI environments
if not defined CI pause
