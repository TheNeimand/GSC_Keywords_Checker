@echo off
title GSC Keyword Analyzer Tool
cd /d "%~dp0"

echo Arayuz aciliyor, lutfen bekleyin... / Starting GUI, please wait...
echo Siyah ekran arayuz açildiğinda kendiğinden kapanacak. / This window will close automatically.

start /b pythonw gsc_gui.py || start /b python gsc_gui.py || start /b pyw gsc_gui.py

exit
