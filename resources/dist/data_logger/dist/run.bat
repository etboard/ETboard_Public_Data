@echo off
@cls
@chcp 65001 > nul

@echo ##################################################################################
@echo # ETboard Data Logger V0.92
@echo # ================================================================================
@echo # HTTP://ET.KETRi.RE.KR Copyright 2022. KETRi. All rights reserved.
@echo ##################################################################################

if [%1]==[] goto :blank

@echo "Mac address of ETboard " %1

set EXEC_NAME=etboard_data_logger_iot.exe
set PARAMS=-b broker.hivemq.com -p 1883 -t %1/et/smpl/tele/sensor -n data-logger

if exist %EXEC_NAME% (
    set EXEC_PATH=%EXEC_NAME%
) else if exist dist\%EXEC_NAME% (
    set EXEC_PATH=dist\%EXEC_NAME%
) else (
    @echo Error: %EXEC_NAME% not found in current directory or dist folder.
    goto :error
)

%EXEC_PATH% %PARAMS%

@pause

:blank
@echo:
@echo Please run with the mac address of ETboard like as below
@echo run 96:EA:E8
@echo:
@pause
goto :eof

:error
@echo:
@echo Unable to find %EXEC_NAME%. Please make sure it exists in the current directory or in the dist folder.
@echo:
@pause
