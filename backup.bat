@echo off
cd /d "%~dp0"
echo Executing Core Shell Release Packaging v3.0...
powershell -Command "Compress-Archive -Path * -DestinationPath '..\AI_NETWORK_CORE_v3.0.zip' -Force"
echo ✅ Release Package Created Successfully at Desktop!
pause
