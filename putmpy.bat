@echo off
for %%f in (*.mpy) do (
    echo Uploading %%f ...
    python webrepl_cli.py  -p p %%f 192.168.178.%1:/%%f
)
echo Done!


