param(
  [string]$BaseUrl = "https://www.runrategroup.com"
)

$ErrorActionPreference = "Stop"

Write-Output "Normal homepage should not be blocked:"
curl.exe -I "$BaseUrl/"

Write-Output "Static asset should not be blocked:"
curl.exe -I "$BaseUrl/favicon.ico"

Write-Output "SQLi signal should be logged or blocked depending rollout mode:"
curl.exe -s -o NUL -w "SQLi status %{http_code}`n" "$BaseUrl/?q=UNION%20SELECT%201,2,3"

Write-Output "XSS signal should be logged or blocked depending rollout mode:"
curl.exe -s -o NUL -w "XSS status %{http_code}`n" "$BaseUrl/?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E"

Write-Output "Path traversal signal should be logged or blocked depending rollout mode:"
curl.exe --path-as-is -s -o NUL -w "Path traversal status %{http_code}`n" "$BaseUrl/..%2f..%2fetc%2fpasswd"

Write-Output "Rate limit test against /api/contact: expect 429 after threshold if repeated quickly."
for ($i = 1; $i -le 7; $i++) {
  curl.exe -s -o NUL -w "attempt $i status %{http_code}`n" `
    -X POST "$BaseUrl/api/contact" `
    -H "content-type: application/json" `
    --data "{""name"":""Rate Test"",""email"":""rate-test@example.com"",""company"":""RunRate Test"",""message"":""Synthetic rate limit verification""}"
}
