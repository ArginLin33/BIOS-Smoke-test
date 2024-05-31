@echo off
setlocal enabledelayedexpansion

:: Define variables
set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=WB_Stress.lnk
set CB_SHORTCUT_NAME=CB_Stress.lnk
set STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
set RESTART_FLAG=%temp%\restart.flag
set TEST_PHASE_FLAG=%temp%\test_phase.flag
set COUNT_FILE=%temp%\count.txt
set NUM_ITERATIONS=5
set shutdowndelay=30

:: Check restart status
if exist "%RESTART_FLAG%" (
    echo Resuming batch file after reboot...
    set /p TEST_PHASE=<%TEST_PHASE_FLAG%
    if "%TEST_PHASE%"=="WBTest" goto :WBTestResume
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
) else (
    echo No restart flag found.
)

:: Initialize the count file
if not exist "%COUNT_FILE%" (
    echo Initializing count file...
    echo 0 > "%COUNT_FILE%"
) else (
    echo Count file already exists.
)

:: Run WB test
:WBTest
echo Running WB test...
timeout /t 10

:: Read the count value
if exist "%COUNT_FILE%" (
    set /p COUNTER=<%COUNT_FILE%
    echo Read counter value: %COUNTER%
) else (
    echo Error: Count file not found. Exiting...
    exit /B 1
)

:WBLoop
set /a COUNTER+=1
echo WB test iteration !COUNTER! of %NUM_ITERATIONS%

:: Update the count value
echo %COUNTER% > "%COUNT_FILE%"
echo Updated counter value to %COUNTER%

if !COUNTER! LEQ %NUM_ITERATIONS% (
    echo Setting restart flag...
    echo WBTest > "%TEST_PHASE_FLAG%"
    echo 1 > "%RESTART_FLAG%"
    echo Restarting in %shutdowndelay% seconds...
    shutdown /r /t %shutdowndelay%
    exit /B 0
)
echo WB test completed.
goto :CleanupWB

:WBTestResume
echo Resuming WB test...
del "%RESTART_FLAG%"
del "%TEST_PHASE_FLAG%"
if exist "%COUNT_FILE%" (
    set /p COUNTER=<%COUNT_FILE%
    echo Resumed counter value: %COUNTER%
) else (
    echo Error: Count file not found. Exiting...
    exit /B 1
)
goto :WBLoop

:CleanupWB
echo Cleaning up WB shortcut...
del "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
if exist "%STARTUP_FOLDER%\%SHORTCUT_NAME%" (
    echo Error: Failed to delete WB shortcut.
) else (
    echo WB shortcut deleted.
)
echo Setting up CB_Stress shortcut...
powershell -command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SCRIPT_DIR%%CB_SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%CB_Stress.bat'; $Shortcut.Save()"
if errorlevel 1 (
    echo Error: Failed to create CB_Stress shortcut.
) else (
    echo CB_Stress shortcut created successfully.
)
move "%SCRIPT_DIR%%CB_SHORTCUT_NAME%" "%STARTUP_FOLDER%"
if errorlevel 1 (
    echo Error: Failed to move CB_Stress shortcut to startup folder.
) else (
    echo CB_Stress shortcut moved to startup folder.
)
start "" "%SCRIPT_DIR%CB_Stress.bat"
if errorlevel 1 (
    echo Error: Failed to start CB_Stress.bat.
) else (
    echo CB_Stress.bat started successfully.
)
del "%COUNT_FILE%"
if exist "%COUNT_FILE%" (
    echo Error: Failed to delete count file.
) else (
    echo Count file deleted.
)
exit /B 0
