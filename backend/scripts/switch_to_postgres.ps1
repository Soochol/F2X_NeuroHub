# PostgreSQL 설정으로 변경하는 스크립트

# .env 파일 업데이트
$envFile = "c:\myCode\F2X_NeuroHub\backend\.env"
$content = Get-Content $envFile
$newContent = $content -replace 'DATABASE_URL=sqlite:///dev.db', 'DATABASE_URL=postgresql://postgres:postgres@localhost:5432/f2x_neurohub'
$newContent | Set-Content $envFile

Write-Host "✅ DATABASE_URL updated to PostgreSQL"
Write-Host "Please restart the backend server for changes to take effect."
