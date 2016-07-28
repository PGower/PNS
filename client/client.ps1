Param(
    [string]$action="update",
    [string]$uri="http://pns.stmonicas.qld.edu.au:5000"
)

function get-loggedonuser ($computername){
    #http://stackoverflow.com/questions/23219718/powershell-script-to-see-currently-logged-in-users-domain-and-machine-status

    $regexa = '.+Domain="(.+)",Name="(.+)"$'
    $regexd = '.+LogonId="(\d+)"$'

    $logontype = @{
    "0"="Local System"
    "2"="Interactive" #(Local logon)
    "3"="Network" # (Remote logon)
    "4"="Batch" # (Scheduled task)
    "5"="Service" # (Service account logon)
    "7"="Unlock" #(Screen saver)
    "8"="NetworkCleartext" # (Cleartext network logon)
    "9"="NewCredentials" #(RunAs using alternate credentials)
    "10"="RemoteInteractive" #(RDP\TS\RemoteAssistance)
    "11"="CachedInteractive" #(Local w\cached credentials)
    }

    $logon_sessions = @(gwmi win32_logonsession -ComputerName $computername)
    $logon_users = @(gwmi win32_loggedonuser -ComputerName $computername)

    $session_user = @{}

    $logon_users |% {
        $user_info = New-Object -TypeName psobject
        
        $_.antecedent -match $regexa > $nul
        $user_info | Add-Member -MemberType NoteProperty -Name "Username" -Value $matches[2]
        $user_info | Add-Member -MemberType NoteProperty -Name "Domain" -Value $matches[1]
        $_.dependent -match $regexd > $nul
        $session = $matches[1]
        $session_user[$session] += $user_info
    }

    $logon_sessions |%{
        $domainname = $session_user[$_.logonid].Domain
        $username = $session_user[$_.logonid].Username

        # I dont care about users that arent domain users.
        if ($domainname -ne "STMONICAS") { return }

        $fullname = ([adsi]"WinNT://$domainname/$username,user").fullname.tostring()

        $starttime = [management.managementdatetimeconverter]::todatetime($_.starttime)

        $loggedonuser = New-Object -TypeName psobject
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "Session" -Value $_.logonid
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "User" -Value $username
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "Domain" -Value $domainame
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "Fullname" -Value $fullname
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "Type" -Value $logontype[$_.logontype.tostring()]
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "Auth" -Value $_.authenticationpackage
        $loggedonuser | Add-Member -MemberType NoteProperty -Name "StartTime" -Value $starttime

        $loggedonuser
    }

}

# action is one of login, update, logout
if (-not($action -iin @("login", "logout", "update"))) {
    exit
}

# get the machine IP, if its not in 10.192.80.0/255.255.240.0 then exit
$smc_ip_addresses = Get-NetIPAddress | Where-Object -FilterScript { $_.IPAddress -match "^10\.192\.[8-9][0-9]\.[0-9]{1,3}$" } | Select-Object IPAddress
if ($smc_ip_addresses.count -eq 0) {
    # Either we have no IP or we are not on the SMC network. Exit.
    exit
}

# get the computername
$computer_name = $env:computername
# get information about currently logged on users
$userinfo = $(get-loggedonuser($computer_name))

# Send the information to the PNS REST API
$userinfo |% {
    $body = @{
        username = $_.User
        fullname = $_.Fullname
        computer_name = $computer_name
        ip_address = $smc_ip_addresses[0].IPAddress
        action = $action
    }
    Invoke-RestMethod -Method Post -Uri ($uri + '/api/v1/mapping/action') -Body $body
}
