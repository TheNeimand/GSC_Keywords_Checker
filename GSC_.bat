@echo off
title GSC Keyword Analyzer Tool
cd /d "%~dp0"

echo Arayuz aciliyor, lutfen bekleyin... / Starting GUI, please wait...
echo Siyah ekran kendiliginden kapanacak. / This window will close automatically.

start pythonw GSC_Arayuz.py

exit
