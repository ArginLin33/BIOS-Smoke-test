@echo off
setlocal
set Version=%1
set BASEDIR=%BASEDIR%
set RESOURCEDIR=%RESOURCEDIR%
set EXEDIR=%EXEDIR%

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

:: Check if the version directory exists
if not exist "%BASEDIR%" (
    echo Version directory does not exist.
    echo BASEDIR is %BASEDIR%
    pause
    exit /b
)

:: Ensure the GPIO directory exists
if not exist "%BASEDIR%\GPIO" mkdir "%BASEDIR%\GPIO"

:: Step 1: FPTW64.exe and move ROM file
cd /d "%EXEDIR%\MEinfo\MTL"
echo Running FPTW64.exe...
FPTW64.exe -d %Version%.rom
timeout /t 5
move %Version%.rom "%BASEDIR%"
if errorlevel 1 (
    echo File not found after FPTW64 operation.
    pause
    goto end
)

cd /d "%EXEDIR%\BRAT"
echo Running BRAT.exe...
BRAT.exe "%BASEDIR%\%Version%.rom" > "%BASEDIR%\BRAT.txt"
timeout /t 5
if errorlevel 1 (
    echo BRAT operation failed.
    pause
    goto end
)

:: Step 2: Save MEinfo log
cd /d "%EXEDIR%\MEinfo\MTL"
echo Running MEInfoWin64.exe...
MEInfoWin64.exe > "%BASEDIR%\Meinfo.txt"
timeout /t 5
if errorlevel 1 (
    echo MEInfoWin64 operation failed.
    pause
    goto end
)

:: Step 3: Save Setup log
cd /d "%RESOURCEDIR%\PlatCfg2W64.exe"
echo Running PlatCfg2W64.exe...
PlatCfg2W64.exe -dump > Setup.txt
move Setup.txt "%BASEDIR%"
timeout /t 5
if errorlevel 1 (
    echo PlatCfg2W64 operation failed.
    pause
    goto end
)

:: Step 4: Save SMBIOS log
cd /d "%RESOURCEDIR%\SmbiosDump64\SmbiosDump64.exe"
echo Running SmbiosDump64.exe...
SmbiosDump64.exe > "%BASEDIR%\SMBIOS.txt"
timeout /t 5
if errorlevel 1 (
    echo SmbiosDump64 operation failed.
    pause
    goto end
)

:: Step 5: Save Sensor log
cd /d "%EXEDIR%\MEinfo\MTL"
echo Running ISSU.exe...
ISSU.exe -BIST > Sensor.txt
move Sensor.txt "%BASEDIR%"
timeout /t 5
if errorlevel 1 (
    echo ISH Sensor operation failed.
    pause
    goto end
)

:: Step 6: GPIO Config operations - using the installation directory
cd "C:\Program Files\Intel Corporation\Intel(R)GPIO3.x"
for %%i in (0 1 3 4 5) do (
    echo Running GPIOConfig.exe for Community%%i...
    .\GPIOConfig.exe -d -c Community%%i -s MTL_P > "%BASEDIR%\GPIO\Community%%i.txt"
    if %errorlevel% neq 0 (
        echo GPIO operation for Community%%i failed.
        pause
        goto end
    )
)

echo All operations completed successfully.
:end
cd /d "%BASEDIR%"
endlocal
