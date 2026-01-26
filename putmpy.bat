@echo off
d:
cd /esp/microp/

for %%F in (*.mpy) do (
    REM echo Processing %%F
	python webrepl_cli.py -p p %%F 192.168.178.%1:/%%F
	IF ERRORLEVEL 1 (
		echo Fehler!!!
		exit /b 1
	) ELSE (
		time /T
	)
)
