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