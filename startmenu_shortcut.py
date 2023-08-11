import os, winshell
from win32com.client import Dispatch
import os

# pyinstaller --onefile --noconsole main.py

directory = os.path.dirname(os.path.abspath(__file__))

start_menu = os.path.join(winshell.start_menu(), "Programs")
shortcut_path = os.path.join(start_menu, "Photo Renamer.lnk")
executable_path = os.path.join(directory, "dist", "main.exe")
working_path = os.path.dirname(executable_path)
icon_path = os.path.join(directory, "icon.ico")

shell = Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = executable_path
shortcut.WorkingDirectory = working_path
shortcut.IconLocation = icon_path
print(shortcut)
shortcut.save()
