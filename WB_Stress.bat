@echo off
setlocal enabledelayedexpansion

:: 定义变量
set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=WB_Stress.lnk
set CB_SHORTCUT_NAME=CB_Stress.lnk
set STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
set RESTART_FLAG=%temp%\restart.flag
set TEST_PHASE_FLAG=%temp%\test_phase.flag
set COUNT_FILE=%temp%\count.txt
set NUM_ITERATIONS=1
set shutdowndelay=30

:: 检查重启状态
if exist "%RESTART_FLAG%" (
    echo Resuming batch file after reboot...
    set /p TEST_PHASE=<%TEST_PHASE_FLAG%
    if "%TEST_PHASE%"=="WBTest" goto :WBTestResume
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
)

:: 初始化计数文件
if not exist "%COUNT_FILE%" (
    echo 0 > "%COUNT_FILE%"
)

:: 运行 WB 测试
:WBTest
echo Running WB test...
timeout /t 40

:: 读取计数值
set /p COUNTER=<%COUNT_FILE%

:WBLoop
set /a COUNTER+=1
echo WB test iteration !COUNTER! of %NUM_ITERATIONS%

:: 更新计数值
echo %COUNTER% > "%COUNT_FILE%"

if !COUNTER! LEQ %NUM_ITERATIONS% (
    echo Setting restart flag...
    echo WBTest > "%TEST_PHASE_FLAG%"
    echo 1 > "%RESTART_FLAG%"
    shutdown /r /t %shutdowndelay%
    exit /B 0
)
echo WB test completed.
goto :CleanupWB

:WBTestResume
del "%RESTART_FLAG%"
del "%TEST_PHASE_FLAG%"
set /p COUNTER=<%COUNT_FILE%
goto :WBLoop

:CleanupWB
echo Cleaning up WB shortcut...
del "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
echo Setting up CB_Stress shortcut...
powershell -command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SCRIPT_DIR%%CB_SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%CB_Stress.bat'; $Shortcut.Save()"
move "%SCRIPT_DIR%%CB_SHORTCUT_NAME%" "%STARTUP_FOLDER%"
start "" "%SCRIPT_DIR%CB_Stress.bat"
del "%COUNT_FILE%"
exit /B 0
