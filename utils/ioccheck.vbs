' +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
' ioccheck.vbs
' Downloads IOC Client and checks for IOCs on the system with pyiocClient
'
' This will check the processor architecture of the target system and
' download the apropriate client (32 or 64 bit) in Windows systems.
'
' This .vbs script could be used to deploy pyiocClient to several 
' target systems via Active Directory group policy (GPO) or 
' using scripting:
'
' Transfer the file to target systems:
' wmiFileTransfer.exe -f ioccheck.vbs -P targets.txt -d c:
'
' Execute ioccheck.vbs in target systems:
' psexec -d @targets.txt cscript /b /nologo c:\ioccheck.vbs
'
' SETUP:
' For this to work you should provide an webserver to act as a
' distribuition server. This could be the same system where you
' have pyiocServer running, and should provide the following
' files:
'
' /IOC/pyioc32.exe - the 32 bit binary of pyiocClient
' /IOC/pyioc64.exe - the 64 bit binary of pyiocClient
' /IOC/log.php - an optional dummy php log script. 
'                This is called to log the start and stop of the 
'                checking against the IOC Server.
'                Client hostname and active IP addresses are sent in
'                the query string. 
'
' This file is licensed with the same license of pyioc itself.
' Any questions or requests, ping me at vrsantos_at_sectoid_dot_com
'
' +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

' Settings

' hostname or ip of your pyIOCServer
strIOCServer = "ioc.example.com"
strIOCPort = "8443"

' hostname or ip of your distribution server
strDistServer = "dist.example.com"
strDistPort = "80"

strIOCClientPath = "c:\pyioc.exe"

On Error Resume Next

' Check processor arch and download apropriated binary
strHostnameAttr = getHostnameStr()

Set WshShell = WScript.CreateObject("WScript.Shell")
Arch = WshShell.RegRead("HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment\PROCESSOR_ARCHITECTURE")

If Arch = "x86" Then
  ' URL to the 32bit binary
    strFileURL = "http://" & strDistServer & ":" & strDistPort & "/IOC/pyioc32.exe"

ElseIf InStr(Arch, "64") Then
  ' URL to the 64bit binary
    strFileURL = "http://" & strDistServer & ":" & strDistPort & "/IOC/pyioc64.exe"

End If

' log start activity with IOC Server
fetchURL "http://" & strDistServer & ":" & strDistPort & "/IOC/log.php?a=start&h=" & strHostnameAttr, ""

' fetch client binary
fetchURL strFileURL, strIOCClientPath

' Run pyioc
strCmd = strIOCClientPath & " -s " & strIOCServer & " -p " & strIOCPort 
return = WshShell.Run(strCmd, 0, true)

' Clean up and kill myself
Set objFSO = Createobject("Scripting.FileSystemObject")

objFSO.DeleteFile strIOCClientPath
strSelf = Wscript.ScriptFullName
objFSO.DeleteFile strSelf

Set objFSO = Nothing

' log stop activity with IOC Server
fetchURL "http://" & strDistServer & ":" & strDistPort & "/IOC/log.php?a=stop&h=" & strHostnameAttr, ""



' getHostnameStr() - returns hostname and all active IP addresses in one string
Function getHostnameStr()

	Set objNTInfo = CreateObject("WinNTSystemInfo")
	GetComputerName = ucase(objNTInfo.ComputerName)

	strComputer = "."
	Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
	Set IPConfigSet = objWMIService.ExecQuery("Select IPAddress from Win32_NetworkAdapterConfiguration WHERE IPEnabled = 'True' and ServiceName != 'VMNetAdapter'")
	For Each IPConfig in IPConfigSet
		If Not IsNull(IPConfig.IPAddress) Then
			For i = LBound(IPConfig.IPAddress) to UBound(IPConfig.IPAddress)
				If Not Instr(IPConfig.IPAddress(i), ":") > 0 Then
					if Not strMsg="" Then
						strMsg = strMsg & ","
					End If
					strMsg = strMsg & IPConfig.IPAddress(i)
				End if
			Next
		End If
	Next

	getHostnameStr = GetComputerName & ";" & strMsg
	
End Function


Sub fetchURL(sFileURL, sLocation)
 
	'create xmlhttp object
	Set objXMLHTTP = CreateObject("MSXML2.XMLHTTP")
 
	'get the remote file
	objXMLHTTP.open "GET", sFileURL, false
 
	'send the request
	objXMLHTTP.send()
 
	'wait until the data has downloaded successfully
	do until objXMLHTTP.Status = 200 :  wscript.sleep(1000) :  loop
 
	'if the data has downloaded sucessfully
	If ((objXMLHTTP.Status = 200) And (sLocation <> "")) Then
 
    	'create binary stream object
		Set objADOStream = CreateObject("ADODB.Stream")
		objADOStream.Open
 
	    'adTypeBinary
		objADOStream.Type = 1
		objADOStream.Write objXMLHTTP.ResponseBody
 
	    'Set the stream position to the start
		objADOStream.Position = 0    
 
        'create file system object to allow the script to check for an existing file
        Set objFSO = Createobject("Scripting.FileSystemObject")

        'check if the file exists, if it exists then delete it
		If objFSO.Fileexists(sLocation) Then objFSO.DeleteFile sLocation
 
	    'destroy file system object	
		Set objFSO = Nothing
 
	    'save the ado stream to a file
		objADOStream.SaveToFile sLocation
 
	    'close the ado stream
		objADOStream.Close
 
		'destroy the ado stream object
		Set objADOStream = Nothing
 
	End if
 
	'destroy xml http object
	Set objXMLHTTP = Nothing
 
End Sub
