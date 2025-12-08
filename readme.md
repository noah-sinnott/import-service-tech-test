# Import Service

Full-stack data import service with FastAPI backend and React frontend.

## Setup

```bash
# Run all in one (reccomended)
./run.ps1

# Or run manually
cd backend && pip install -r requirements.txt && uvicorn app.main:app
cd frontend && npm install && npm start
```

Backend: http://localhost:8000  
Frontend: http://localhost:3000

## Possible Improvements

- Add retry mechanism for failed API calls
- Implement OAuth flow
- Add job scheduling/queueing for better scalability
- Real-time updates via WebSockets instead of polling
- Implement monitoring for error handling
