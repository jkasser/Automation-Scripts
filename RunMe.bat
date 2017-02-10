@ECHO OFF
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges ) 

:getPrivileges 
if '%1'=='ELEV' (shift & goto gotPrivileges)  
setlocal DisableDelayedExpansion
set "batchPath=%~0"
setlocal EnableDelayedExpansion
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%temp%\OEgetPrivileges.vbs" 
ECHO UAC.ShellExecute "!batchPath!", "ELEV", "", "runas", 1 >> "%temp%\OEgetPrivileges.vbs" 
"%temp%\OEgetPrivileges.vbs" 
exit /B 

:gotPrivileges
CD C:\EchoPerf
powershell.exe Set-ExecutionPolicy RemoteSigned
powershell.exe -noprofile -file "C:\EchoPerf\Dependencies.ps1"

CD C:\Python27\Scripts
pip install --upgrade pip
pip install -U selenium
pip install -U requests
pip install -U matplotlib

CD C:\EchoPerf
Automation_Main.py