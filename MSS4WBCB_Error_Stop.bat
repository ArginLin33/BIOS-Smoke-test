@echo off
setlocal enabledelayedexpansion

:: 定义变量
set NUM_ITERATIONS=1
set shutdowndelay=30
set SCRIPT_DIR=%~dp0
set WB_SUB_BATCH_NAME=WB_Stress.bat
set WB_SHORTCUT_NAME=WB_Stress.lnk
set STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
set RESTART_FLAG=%temp%\restart.flag
set TEST_PHASE_FLAG=%temp%\test_phase.flag

:: 确保启动文件夹存在
if not exist "%STARTUP_FOLDER%" (
    echo Startup folder does not exist: %STARTUP_FOLDER%
    goto EndTest
)

:: 检查是否有重启标志
if exist "%RESTART_FLAG%" (
    echo Resuming batch file after reboot...
    set /p TEST_PHASE=<%TEST_PHASE_FLAG%
    if "%TEST_PHASE%"=="WBTest" goto :StartWBTest
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
)

:: 主控制流程
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

:: 检查并运行 DeviceCompare.exe
:CheckAndRunDeviceCompare
echo Checking if DeviceCompare.exe is running...
tasklist /FI "IMAGENAME eq DeviceCompare.exe" | find /I "DeviceCompare.exe" >nul 2>&1
if errorlevel 1 (
    echo DeviceCompare.exe is not running. Starting it now...
    start "" "%SCRIPT_DIR%DeviceCompare\DeviceCompare.exe" 60
    timeout /t 60
) else (
    echo DeviceCompare.exe is already running.
)
exit /B 0

:: 运行 Ms 测试
:MsTest
echo Running Ms test...
set /a COUNTER=0
:MsLoop
set /a COUNTER+=1
echo Ms test iteration !COUNTER! of %NUM_ITERATIONS%
if !COUNTER! LEQ %NUM_ITERATIONS% (
    call :RunMs
    if errorlevel 1 exit /B 1
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
timeout /t 90
exit /B 0

:: 运行 S4 测试
:S4Test
echo Running S4 test...
set /a COUNTER=0
:S4Loop
set /a COUNTER+=1
echo S4 test iteration !COUNTER! of %NUM_ITERATIONS%
if !COUNTER! LEQ %NUM_ITERATIONS% (
    call :RunS4
    if errorlevel 1 exit /B 1
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
timeout /t 180
exit /B 0

:: 设置并运行 WB_Stress
:SetupWBStress
echo Setting up WB_Stress...
powershell -command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SCRIPT_DIR%%WB_SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%%WB_SUB_BATCH_NAME%'; $Shortcut.Save()"
move "%SCRIPT_DIR%%WB_SHORTCUT_NAME%" "%STARTUP_FOLDER%"
exit /B 0

:EndTest
echo Test cycle complete
pause
exit /B 0
