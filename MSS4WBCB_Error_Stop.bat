@echo off
setlocal enabledelayedexpansion

:: Define variables
set NUM_ITERATIONS=5
set shutdowndelay=30
set RESOURCEDIR=%RESOURCEDIR%
set BASEDIR=%BASEDIR%
set WB_SUB_BATCH_NAME=WB_Stress.bat
set STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
set RESTART_FLAG=%temp%\restart.flag
set TEST_PHASE_FLAG=%temp%\test_phase.flag
set LOG_FILE=%temp%\MSS4_Stress.log

:: Clear the log file at the start
echo Starting MSS4WBCB_Error_Stop.bat > %LOG_FILE%

:: Log RESOURCEDIR value
echo RESOURCEDIR=%RESOURCEDIR% >> %LOG_FILE%
echo BASEDIR=%BASEDIR% >> %LOG_FILE%
echo WB_SUB_BATCH_NAME=%WB_SUB_BATCH_NAME% >> %LOG_FILE%

:: Check Startup folder exist
if not exist "%STARTUP_FOLDER%" (
    echo Startup folder does not exist: %STARTUP_FOLDER% >> %LOG_FILE%
    goto EndTest
)

:: Check restart status
if exist "%RESTART_FLAG%" (
    echo Resuming batch file after reboot... >> %LOG_FILE%
    set /p TEST_PHASE=<%TEST_PHASE_FLAG%
    if "%TEST_PHASE%"=="WBTest" goto :StartWBTest
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
)

:Main
call :CheckAndRunDeviceCompare
if %errorlevel% neq 0 goto EndTest

call :MsTest
if %errorlevel% neq 0 goto EndTest

call :S4Test
if %errorlevel% neq 0 goto EndTest

call :SetupWBStress
if %errorlevel% neq 0 goto EndTest

start "" "%RESOURCEDIR%\%WB_SUB_BATCH_NAME%"
goto EndTest

:: Run Device Compare
:CheckAndRunDeviceCompare
echo Checking if DeviceCompare.exe is running... >> %LOG_FILE%
tasklist /FI "IMAGENAME eq DeviceCompare.exe" | find /I "DeviceCompare.exe" >nul 2>&1
if %errorlevel% neq 0 (
    echo DeviceCompare.exe is not running. Starting it now... >> %LOG_FILE%
    start "" "%BASEDIR%\DeviceCompare\DeviceCompare.exe" 30
    timeout /t 10
) else (
    echo DeviceCompare.exe is already running. >> %LOG_FILE%
)
exit /B 0

:: Run Ms test
:MsTest
echo Running Ms test... >> %LOG_FILE%
set /a COUNTER=0
:MsLoop
set /a COUNTER+=1
echo Ms test iteration !COUNTER! of %NUM_ITERATIONS% >> %LOG_FILE%
if !COUNTER! LEQ %NUM_ITERATIONS% (
    call :RunMs
    if %errorlevel% neq 0 (
        echo Error: Ms test failed on iteration !COUNTER!. >> %LOG_FILE%
        pause
        exit /B 1
    )
    goto MsLoop
)
:MsTestEnd
echo Ms test completed. >> %LOG_FILE%
exit /B 0

:RunMs
cd /d "%BASEDIR%\DeviceCompare\"
if not exist DEV_loopCount.txt goto MsRun

:MsCheckLoop
set num="2:"
for /f "tokens=1*delims=:" %%i in ('findstr/n . DEV_loopCount.txt ^| findstr/b %num%') do (
    set /a FailCOUNTER=%%j
)
if !FailCOUNTER! GEQ 1 (
    echo Error: FailCOUNTER in MsCheckLoop is greater than or equal to 1. >> %LOG_FILE%
    pause
    exit /B 1
)
goto MsRun

:MsRun
set /a COUNTERSS=COUNTER
cd "%RESOURCEDIR%\pwrtest.exe\"
echo Running pwrtest.exe /CS /c:1 /d:90 /p:90... >> %LOG_FILE%
pwrtest.exe /CS /c:1 /d:90 /p:90
timeout /t 30
exit /B 0

:: Run S4 test
:S4Test
echo Running S4 test... >> %LOG_FILE%
set /a COUNTER=0
:S4Loop
set /a COUNTER+=1
echo S4 test iteration !COUNTER! of %NUM_ITERATIONS% >> %LOG_FILE%
if !COUNTER! LEQ %NUM_ITERATIONS% (
    call :RunS4
    if %errorlevel% neq 0 (
        echo Error: S4 test failed on iteration !COUNTER!. >> %LOG_FILE%
        pause
        exit /B 1
    )
    goto S4Loop
)
:S4TestEnd
echo S4 test completed. >> %LOG_FILE%
exit /B 0

:RunS4
cd /d "%BASEDIR%\DeviceCompare\"
if not exist DEV_loopCount.txt goto S4Run

:S4CheckLoop
set num="2:"
for /f "tokens=1*delims=:" %%i in ('findstr/n . DEV_loopCount.txt ^| findstr/b %num%') do (
    set /a FailCOUNTER=%%j
)
if !FailCOUNTER! GEQ 1 (
    echo Error: FailCOUNTER in S4CheckLoop is greater than or equal to 1. >> %LOG_FILE%
    pause
    exit /B 1
)
goto S4Run

:S4Run
set /a COUNTERSS=COUNTER
cd "%RESOURCEDIR%\pwrtest.exe\"
echo Running pwrtest.exe /sleep /s:4 /c:1 /d:90 /p:180... >> %LOG_FILE%
pwrtest.exe /sleep /s:4 /c:1 /d:90 /p:90
timeout /t 30
exit /B 0

:: Setup and run WB_Stress
:SetupWBStress
echo Setting up WB_Stress... >> %LOG_FILE%

:: Copy WB_Stress.bat directly to the Startup folder
echo Copying WB_Stress.bat to startup folder... >> %LOG_FILE%
copy "%RESOURCEDIR%\%WB_SUB_BATCH_NAME%" "%STARTUP_FOLDER%\%WB_SUB_BATCH_NAME%"
if %errorlevel% neq 0 (
    echo Error: Failed to copy WB_Stress.bat to startup folder. >> %LOG_FILE%
    pause
    exit /B 1
) else (
    echo WB_Stress.bat copied to startup folder successfully. >> %LOG_FILE%
)

:: Execute WB_Stress.bat
echo Executing WB_Stress.bat... >> %LOG_FILE%
start "" "%STARTUP_FOLDER%\WB_Stress.bat"
if %errorlevel% neq 0 (
    echo Error: Failed to start WB_Stress.bat. >> %LOG_FILE%
    pause
    exit /B 1
) else (
    echo WB_Stress.bat started successfully. >> %LOG_FILE%
)
exit /B 0

:EndTest
echo Test cycle complete >> %LOG_FILE%
pause
exit /B 0
