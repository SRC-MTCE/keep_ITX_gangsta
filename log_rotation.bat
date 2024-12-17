@echo off
setlocal

:: Set the target folder
set "target_folder=C:\ITX_Gang_Tag_Multi_PIP\log"

:: Find and delete .log files older than 30 days
forfiles /p "%target_folder%" /s /m *.log /d -30 /c "cmd /c del /q @path"

endlocal
