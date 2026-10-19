@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist bin mkdir bin
javac -Xlint:all -encoding UTF-8 -d bin src\ec\edu\ups\parqueadero\*.java test\ec\edu\ups\parqueadero\*.java
if errorlevel 1 exit /b 1
java -Dfile.encoding=UTF-8 -cp bin ec.edu.ups.parqueadero.PruebasParqueadero
