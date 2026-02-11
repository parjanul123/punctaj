' Punctaj Manager v2.5 Setup
' Creates a professional Windows installer

Dim WshShell, fso, scriptDir, installBat, result
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
installBat = scriptDir & "\INSTALL.bat"

If Not fso.FileExists(installBat) Then
    MsgBox "Error: INSTALL.bat not found in " & scriptDir, vbCritical, "Setup Error"
    WScript.Quit 1
End If

WshShell.CurrentDirectory = scriptDir
result = WshShell.Run("cmd /c INSTALL.bat", 1, True)

If result = 0 Then
    MsgBox "Installation complete", vbInformation, "Success"
Else
    MsgBox "Installation failed. Check the messages above.", vbCritical, "Error"
End If
