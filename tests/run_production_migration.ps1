# Production Database Migration Script
# Run this script after copying your DATABASE_URL from Vercel dashboard

param(
    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Production Database Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable
$env:DATABASE_URL = $DatabaseUrl

# Navigate to backend
Set-Location backend

# Show current migration status
Write-Host "Current migration status:" -ForegroundColor Yellow
alembic current

Write-Host ""
Write-Host "Running migration..." -ForegroundColor Yellow

# Run migration
alembic upgrade head

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Testing chat API..." -ForegroundColor Yellow

# Test the chat API
python -c @"
import requests
BACKEND = 'https://backend-kvm8wghw0-hamdanprofessionals-projects.vercel.app'
r = requests.post(f'{BACKEND}/api/auth/login', json={'email': 'test1@test.com', 'password': 'Test1234'})
if r.status_code == 200:
    token = r.json()['access_token']
    chat = requests.post(f'{BACKEND}/api/chat', json={'message': 'test migration fix'}, headers={'Authorization': f'Bearer {token}'})
    if chat.status_code == 200:
        print('✅ SUCCESS! Chat is now working on production!')
    else:
        print(f'❌ Chat still failing: {chat.status_code}')
        print(chat.json())
else:
    print(f'❌ Login failed: {r.status_code}')
"@

Write-Host ""
Write-Host "Next: Test at https://frontend-hamdanprofessionals-projects.vercel.app/chat" -ForegroundColor Cyan
