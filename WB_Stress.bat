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
set DESKTOP_DIR=%USERPROFILE%\Desktop
set COUNT_FILE=%DESKTOP_DIR%\count.txt
set STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
set RESTART_FLAG=%temp%\restart.flag
set TEST_PHASE_FLAG=%temp%\test_phase.flag
set NUM_ITERATIONS=5
set shutdowndelay=30
set LOG_FILE=%DESKTOP_DIR%\WB_Stress.log

:: Clear the log file at the start
echo Starting WB_Stress.bat > %LOG_FILE%

:: Read BASEDIR from the file on the desktop
set BASEDIR_FILE=%DESKTOP_DIR%\basedir.txt
if exist "%BASEDIR_FILE%" (
    echo Reading BASEDIR from %BASEDIR_FILE% >> %LOG_FILE%
    for /f "tokens=*" %%i in (%BASEDIR_FILE%) do (
        set SCRIPT_DIR=%%i
        echo Read line: %%i >> %LOG_FILE%
    )
    echo BASEDIR read from file: !SCRIPT_DIR! >> %LOG_FILE%
    if "!SCRIPT_DIR!"=="" (
        echo Error: BASEDIR read as empty >> %LOG_FILE%
    )
) else (
    echo Error: BASEDIR file not found at %BASEDIR_FILE%. >> %LOG_FILE%
    exit /b 1
)

:: Check restart status
if exist "%RESTART_FLAG%" (
    echo Resuming batch file after reboot... >> %LOG_FILE%
    set /p TEST_PHASE=<%TEST_PHASE_FLAG%
    if "%TEST_PHASE%"=="WBTest" goto :WBTestResume
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
) else (
    echo No restart flag found. >> %LOG_FILE%
)

:: Initialize the count file
if not exist "%COUNT_FILE%" (
    echo Initializing count file... >> %LOG_FILE%
    echo 0 > "%COUNT_FILE%"
) else (
    echo Count file already exists. >> %LOG_FILE%
)

:: Run WB test
:WBTest
echo Running WB test... >> %LOG_FILE%
timeout /t 10

:: Read the count value
if exist "%COUNT_FILE%" (
    set /p COUNTER=<%COUNT_FILE%
    echo Read counter value: %COUNTER% >> %LOG_FILE%
) else (
    echo Error: Count file not found. Exiting... >> %LOG_FILE%
    exit /B 1
)

:WBLoop
set /a COUNTER+=1
echo WB test iteration !COUNTER! of %NUM_ITERATIONS% >> %LOG_FILE%

:: Update the count value
echo %COUNTER% > "%COUNT_FILE%"
echo Updated counter value to %COUNTER% >> %LOG_FILE%

if !COUNTER! LEQ %NUM_ITERATIONS% (
    echo Setting restart flag... >> %LOG_FILE%
    echo WBTest > "%TEST_PHASE_FLAG%"
    echo 1 > "%RESTART_FLAG%"
    echo Restarting in %shutdowndelay% seconds... >> %LOG_FILE%
    shutdown /r /t %shutdowndelay%
    exit /B 0
)
echo WB test completed. >> %LOG_FILE%
goto :CleanupWB

:WBTestResume
echo Resuming WB test... >> %LOG_FILE%
del "%RESTART_FLAG%"
del "%TEST_PHASE_FLAG%"
if exist "%COUNT_FILE%" (
    set /p COUNTER=<%COUNT_FILE%
    echo Resumed counter value: %COUNTER% >> %LOG_FILE%
) else (
    echo Error: Count file not found. Exiting... >> %LOG_FILE%
    exit /B 1
)
goto :WBLoop

:CleanupWB
echo Entering CleanupWB... >> %LOG_FILE%
echo Cleaning up WB batch file... >> %LOG_FILE%
if exist "%COUNT_FILE%" (
    del "%COUNT_FILE%"
    if %errorlevel% neq 0 (
        echo Error: Failed to delete count file. >> %LOG_FILE%
        echo Delete command failed with error level: %errorlevel% >> %LOG_FILE%
        exit /B 1
    ) else (
        echo Count file deleted. >> %LOG_FILE%
    )
) else (
    echo Count file does not exist. >> %LOG_FILE%
)

:: Check if CB_Stress.bat exists
if exist "%SCRIPT_DIR%\CB_Stress.bat" (
    echo CB_Stress batch file found. >> %LOG_FILE%

    echo Creating CB_Stress shortcut... >> %LOG_FILE%
    powershell -command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\CB_Stress.lnk'); $Shortcut.TargetPath = '%SCRIPT_DIR%\CB_Stress.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Save()"
    if %errorlevel% neq 0 (
        echo Error: Failed to create CB_Stress shortcut. >> %LOG_FILE%
        exit /B 1
    ) else (
        echo CB_Stress shortcut created successfully. >> %LOG_FILE%
    )

    :: Check if CB_Stress shortcut exists in startup folder
    if exist "%STARTUP_FOLDER%\CB_Stress.lnk" (
        echo CB_Stress shortcut found in startup folder. >> %LOG_FILE%

        echo Starting CB_Stress.bat... >> %LOG_FILE%
        start "" "%STARTUP_FOLDER%\CB_Stress.lnk"
        del "%STARTUP_FOLDER%\WB_Stress.bat"
        if %errorlevel% neq 0 (
            echo Error: Failed to start CB_Stress.bat. >> %LOG_FILE%
            echo Start command failed with error level: %errorlevel% >> %LOG_FILE%
            exit /B 1
        ) else (
            echo CB_Stress.bat started successfully. >> %LOG_FILE%
        )
    ) else (
        echo Error: CB_Stress shortcut not found in startup folder. >> %LOG_FILE%
        exit /B 1
    )
) else (
    echo Error: CB_Stress batch file not found. >> %LOG_FILE%
    exit /B 1
)

echo Exiting script... >> %LOG_FILE%
exit /B 0

:EOF
echo Script reached EOF. >> %LOG_FILE%
