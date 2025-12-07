# Backend setup
Set-Location backend
py -m pip install -r requirements.txt > $null
if (-not (Test-Path "import_service.db")) {
    py scripts/init_db.py > $null
}
Set-Location ..

# Frontend setup
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    npm install > $null
}
Set-Location ..

# Start servers
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; py -m uvicorn app.main:app --reload --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start"
