$headers = @{ "Content-Type" = "application/json" }
$url = "http://127.0.0.1:5000/chat"

function Test-Step($msg) {
    Write-Host "Sending: '$msg'"
    $body = @{ message = $msg } | ConvertTo-Json
    $resp = Invoke-RestMethod -Uri $url -Method Post -Body $body -Headers $headers
    Write-Host "Bot: $($resp.bot)"
    if ($resp.second_line) { Write-Host "Bot (2nd line): $($resp.second_line)" }
    Write-Host "Options: $($resp.options -join ', ')"
    Write-Host "----------------"
    return $resp
}

Test-Step ""
Test-Step "PayIn"
Test-Step "Submit Details"
Test-Step "John Doe"
Test-Step "9876543210"
Test-Step "john@example.com"
Test-Step "How to pay?"
