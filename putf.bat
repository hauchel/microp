@echo off
d:
cd /esp/microp/
python webrepl_cli.py -p p %1 192.168.178.%2:/%1
IF ERRORLEVEL 1 (
    echo Fehler!!!
) ELSE (
	time /T
	echo %2
)

