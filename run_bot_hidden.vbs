Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd C:\Users\USER\TG-forwarder && python main.py", 0, False
