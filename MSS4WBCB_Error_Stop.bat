@echo off
setlocal enabledelayedexpansion

:: Define variables
set NUM_ITERATIONS=5
set shutdowndelay=30
set SCRIPT_DIR=%~dp0
set WB_SUB_BATCH_NAME=WB_Stress.bat
set WB_SHORTCUT_NAME=WB_Stress.lnk
set STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
set RESTART_FLAG=%temp%\restart.flag
set TEST_PHASE_FLAG=%temp%\test_phase.flag

:: Check Startup folder exist
if not exist "%STARTUP_FOLDER%" (
    echo Startup folder does not exist: %STARTUP_FOLDER%
    goto EndTest
)

:: Check restart status
if exist "%RESTART_FLAG%" (
    echo Resuming batch file after reboot...
    set /p TEST_PHASE=<%TEST_PHASE_FLAG%
    if "%TEST_PHASE%"=="WBTest" goto :StartWBTest
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
)

:Main
call :CheckAndRunDeviceCompare
if errorlevel 1 goto EndTest

call :MsTest
if errorlevel 1 goto EndTest

call :S4Test
if errorlevel 1 goto EndTest

call :SetupWBStress
if errorlevel 1 goto EndTest

start "" "%SCRIPT_DIR%%WB_SUB_BATCH_NAME%"
goto EndTest

:: Run Device Compare
:CheckAndRunDeviceCompare
echo Checking if DeviceCompare.exe is running...
tasklist /FI "IMAGENAME eq DeviceCompare.exe" | find /I "DeviceCompare.exe" >nul 2>&1
if errorlevel 1 (
    echo DeviceCompare.exe is not running. Starting it now...
    start "" "%SCRIPT_DIR%DeviceCompare\DeviceCompare.exe" 30
    timeout /t 10
) else (
    echo DeviceCompare.exe is already running.
)
exit /B 0

:: Run Ms test
:MsTest
echo Running Ms test...
set /a COUNTER=0
:MsLoop
set /a COUNTER+=1
echo Ms test iteration !COUNTER! of %NUM_ITERATIONS%
if !COUNTER! LEQ %NUM_ITERATIONS% (
    call :RunMs
    if errorlevel 1 (
        echo Error: Ms test failed on iteration !COUNTER!.
        exit /B 1
    )
    goto MsLoop
)
:MsTestEnd
echo Ms test completed.
exit /B 0

:RunMs
cd /d "%SCRIPT_DIR%DeviceCompare"
if not exist DEV_loopCount.txt goto MsRun

:MsCheckLoop
set num="2:"
for /f "tokens=1*delims=:" %%i in ('findstr/n . DEV_loopCount.txt ^| findstr/b %num%') do (
    set /a FailCOUNTER=%%j
)
if !FailCOUNTER! GEQ 1 exit /B 1
goto MsRun

:MsRun
set /a COUNTERSS=COUNTER
cd "%SCRIPT_DIR%"
pwrtest.exe /CS /c:1 /d:90 /p:90
timeout /t 30
exit /B 0

:: Run S4 test
:S4Test
echo Running S4 test...
set /a COUNTER=0
:S4Loop
set /a COUNTER+=1
echo S4 test iteration !COUNTER! of %NUM_ITERATIONS%
if !COUNTER! LEQ %NUM_ITERATIONS% (
    call :RunS4
    if errorlevel 1 (
        echo Error: S4 test failed on iteration !COUNTER!.
        exit /B 1
    )
    goto S4Loop
)
:S4TestEnd
echo S4 test completed.
exit /B 0

:RunS4
cd /d "%SCRIPT_DIR%DeviceCompare"
if not exist DEV_loopCount.txt goto S4Run

:S4CheckLoop
set num="2:"
for /f "tokens=1*delims=:" %%i in ('findstr/n . DEV_loopCount.txt ^| findstr/b %num%') do (
    set /a FailCOUNTER=%%j
)
if !FailCOUNTER! GEQ 1 exit /B 1
goto S4Run

:S4Run
set /a COUNTERSS=COUNTER
cd "%SCRIPT_DIR%"
pwrtest.exe /sleep /s:4 /c:1 /d:90 /p:180
timeout /t 30
exit /B 0

:: Setup and run WB_Stress
:SetupWBStress
echo Setting up WB_Stress...
powershell -command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SCRIPT_DIR%%WB_SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%%WB_SUB_BATCH_NAME%'; $Shortcut.Save()"
if errorlevel 1 (
    echo Error: Failed to create WB_Stress shortcut.
) else (
    echo WB_Stress shortcut created successfully.
)
move "%SCRIPT_DIR%%WB_SHORTCUT_NAME%" "%STARTUP_FOLDER%"
if errorlevel 1 (
    echo Error: Failed to move WB_Stress shortcut to startup folder.
) else (
    echo WB_Stress shortcut moved to startup folder.
)
exit /B 0

:EndTest
echo Test cycle complete
pause
exit /B 0
