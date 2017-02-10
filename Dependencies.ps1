<#
    Use this to get metrics around computer resource usage for web protection
#>


#Utilitiy to print an error message with the output from a command on the next line, then exit the script
function ErrorAndExit([string]$msg, [string]$commandOutput){
    $msg = $msg + "`r`n" + ($output[0..($output.Length -1)] | Out-String)
    Write-Error $msg
    Exit
}

# -----------------------
# Script start
# -----------------------

# Pre-requisites checks 

Write-Host "Checking dependencies"
Write-Host "Checking for Chocolatey " -nonewline
# We will be using chocolatey for installing base items and then NPM for the rest. Make sure Chocolatey is installed
$chocoExists = (Get-Command choco | select-object Name |select-string 'choco').Length -eq 1 2>$null

#see if the last command succeded or not - not means needing to install chocolatey
if(!$? -or !$chocoExists){
    Write-Host "- missing"
    iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))
}
else{
    Write-Host "- confirmed"
}

Write-Host "Checking for Chrome " -nonewline
# check for java
$chromeExists = (Get-Command googlechrome | select-object Name |select-string 'googlechrome ').Length -eq 1 2>$null
if(!$? -or !$chromeExists){
    Write-Host "- missing"
    cinst googlechrome -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}
else{
    Write-Host "- confirmed"
}


Write-Host "Checking for Python " -nonewline
# make sure python is installed
$pythonInstall = (choco list -localonly python2 | select-string 'python2').Length -eq 1 2>$null
if(!$pythonInstall) {
    Write-Host "- missing"
    cinst python2 -y -o -ia "'/qn /norestart ALLUSERS=1 TARGETDIR=c:\Python27'"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}
else{
    Write-Host "- confirmed"
}


Write-Host "Checking for chrome web driver" -nonewline
# need to have chrome web driver installed
$chromeWebDriverInstalled = (choco list -localonly chromedriver | select-string 'chromedriver').Length -eq 1 2>$null
if(!$chromeWebDriverInstalled) {
    Write-Host "- missing"
    cinst chromedriver -y
}
else{
    Write-Host "- confirmed"
}

Write-Host "Checking for .Net 4.5.2" -nonewline
# need to have .Net 4.5.2 for the perf tests
$dotNetInstalled = (choco list -localonly dotnet4.5.2 | select-string 'dotnet4.5.2').Length -eq 1 2>$null
if(!$dotNetInstalled) {
    Write-Host "- missing"
    cinst dotnet4.5.2 -y
}
else{
    Write-Host "- confirmed"
}

Write-Host "Dependencies check comoplete"
Write-Host ""

Exit