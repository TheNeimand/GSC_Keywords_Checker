@echo off
title GSC Keyword Analyzer Tool
cd /d "%~dp0"

echo Starting GUI, please wait...
echo This window will close automatically.

start pythonw gsc_gui.py

exit
