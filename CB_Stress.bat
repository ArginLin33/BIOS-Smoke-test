@echo off
setlocal enabledelayedexpansion

:: 定义变量
set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=CB_Stress.lnk
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
    if "%TEST_PHASE%"=="CBTest" goto :CBTestResume
    del "%RESTART_FLAG%"
    del "%TEST_PHASE_FLAG%"
)

:: 初始化计数文件
if not exist "%COUNT_FILE%" (
    echo 0 > "%COUNT_FILE%"
)

:: 运行 CB 测试
:CBTest
echo Running CB test...

:: 读取计数值
set /p COUNTER=<%COUNT_FILE%

:CBLoop
set /a COUNTER+=1
echo CB test iteration !COUNTER! of %NUM_ITERATIONS%

:: 更新计数值
echo %COUNTER% > "%COUNT_FILE%"

if !COUNTER! LEQ %NUM_ITERATIONS% (
    echo Setting shutdown flag...
    echo CBTest > "%TEST_PHASE_FLAG%"
    echo 1 > "%RESTART_FLAG%"
    shutdown /s /t %shutdowndelay%
    exit /B 0
)
echo CB test completed.
goto :CleanupCB

:CBTestResume
del "%RESTART_FLAG%"
del "%TEST_PHASE_FLAG%"
set /p COUNTER=<%COUNT_FILE%
goto :CBLoop

:CleanupCB
echo Cleaning up CB shortcut...
del "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
del "%COUNT_FILE%"
python "%SCRIPT_DIR%compare_all.py"
exit /B 0
