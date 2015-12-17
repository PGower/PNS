;;https://social.technet.microsoft.com/Forums/scriptcenter/en-US/01fcff8d-3c81-4e53-bee8-f4fb1ec9848c/how-to-execute-a-powershell-script-with-no-window?forum=ITCG
Dim shell,command
Dim action, uri
if WScript.Arguments.Count = 0 then
	action = "update"
	uri = "http://pns.stmonicas.qld.edu.au:5000"
else
	action = WScript.Arguments(0)
	uri = WScript.Arguments(1)
end if
command = "powershell.exe -nologo -file .\client.ps1 -action " & action & " -uri " & uri
Set shell = CreateObject("WScript.Shell")
shell.Run command,0