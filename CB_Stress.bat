@echo off
setlocal enabledelayedexpansion

:: Check for admin rights
:: BatchGotAdmin
:: ------------------------------------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"

:: Define variables
set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=CB_Stress.lnk
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
    if "%TEST_PHASE%"=="CBTest" goto :CBTestResume
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
) else (
    echo No restart flag found.
)

:: Initialize the count file
if not exist "%COUNT_FILE%" (
    echo Initializing count file...
    echo 0 > "%COUNT_FILE%"
    echo Setting Auto On...
    start "" "%SCRIPT_DIR%PlatCfg64W.exe" -w Auto_On:daily
    if errorlevel 1 (
        echo Error: Failed to execute PlatCfg64W.exe -w Auto_On:daily
        pause
    ) else (
        echo Auto_On:daily set successfully.
    )
    start "" "%SCRIPT_DIR%PlatCfg64W.exe" -w Auto_On_Time:11:03
    if errorlevel 1 (
        echo Error: Failed to execute PlatCfg64W.exe -w Auto_On_Time:11:03
        pause
    ) else (
        echo Auto_On_Time set to 11:03 successfully.
    )
) else (
    echo Count file already exists.
)

:: Run CB test
:CBTest
echo Running CB test...

:: Read the count value
if exist "%COUNT_FILE%" (
    set /p COUNTER=<%COUNT_FILE%
    echo Read counter value: %COUNTER%
) else (
    echo Error: Count file not found. Exiting...
    exit /B 1
)

:: Set system time
:SetLocalTime
echo Setting system time to 10:57 AM...
time 10:57 AM
if errorlevel 1 (
    echo Error: Failed to set system time.
    pause
) else (
    echo System time set to 10:57 AM successfully.
)

:CBLoop
set /a COUNTER+=1
echo CB test iteration !COUNTER! of %NUM_ITERATIONS%

:: Update the count value
echo %COUNTER% > "%COUNT_FILE%"
echo Updated counter value to %COUNTER%

if !COUNTER! LEQ %NUM_ITERATIONS% (
    echo Setting shutdown flag...
    echo CBTest > "%TEST_PHASE_FLAG%"
    echo 1 > "%RESTART_FLAG%"
    echo Shutting down in %shutdowndelay% seconds...
    shutdown /s /t %shutdowndelay%
    exit /B 0
)
echo CB test completed.
goto :CleanupCB

:CBTestResume
echo Resuming CB test...
del "%RESTART_FLAG%"
del "%TEST_PHASE_FLAG%"
if exist "%COUNT_FILE%" (
    set /p COUNTER=<%COUNT_FILE%
    echo Resumed counter value: %COUNTER%
) else (
    echo Error: Count file not found. Exiting...
    exit /B 1
)
goto :CBLoop

:CleanupCB
echo Cleaning up CB shortcut...
del "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
if exist "%STARTUP_FOLDER%\%SHORTCUT_NAME%" (
    echo Error: Failed to delete CB shortcut.
    pause
) else (
    echo CB shortcut deleted.
)
del "%COUNT_FILE%"
if exist "%COUNT_FILE%" (
    echo Error: Failed to delete count file.
    pause
) else (
    echo Count file deleted.
)
echo Running Pass.bat script...
start "" "%SCRIPT_DIR%PASS.bat"
if errorlevel 1 (
    echo Error: PASS.bat script failed.
    pause
) else (
    echo PASS.bat script completed successfully.
)
pause
exit /B 0
