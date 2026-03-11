$headers = @{ "Content-Type" = "application/json" }
$url = "http://127.0.0.1:5000/chat"

# 1. Start Chat
$body1 = @{ message = "" } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body1 -Headers $headers

# 2. Select 'PayIn'
$body2 = @{ message = "PayIn" } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body2 -Headers $headers

# 3. Select 'Submit Details'
$body3 = @{ message = "Submit Details" } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body3 -Headers $headers

# 4. Enter Name
$body4 = @{ message = "John Doe" } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body4 -Headers $headers

# 5. Enter Phone
$body5 = @{ message = "9876543210" } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body5 -Headers $headers

# 6. Enter Email
$body6 = @{ message = "john@example.com" } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body6 -Headers $headers

# 7. Enter Question
$body7 = @{ message = "Need help with PayIn integration." } | ConvertTo-Json
Invoke-RestMethod -Uri $url -Method Post -Body $body7 -Headers $headers
