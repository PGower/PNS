Param(
    [string]$action="update",
    [string]$uri="http://pns.stmonicas.qld.edu.au:5000"
)

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
# get the currently logged on username
$username = $env:username
# get the currently logged on domain name
$domainname = $env:userdomain
# get the fullname of logged in user 
$fullname = ([adsi]"WinNT://$domainname/$username,user").fullname
# Send the information to the PNS REST API
$body = @{
    username = $username
    fullname = $fullname
    computer_name = $computer_name
    ip_address = $smc_ip_addresses[0].IPAddress
    action = $action
}

Invoke-RestMethod -Method Post -Uri ($uri + '/api/v1/mapping/action') -Body $body


