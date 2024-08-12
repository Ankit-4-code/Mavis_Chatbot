@echo off
echo Starting the web application...

REM Starting the backend
start cmd /k "cd /d D:\ML\Mavis Chatbot && call Mavis\Scripts\activate.bat && cd backend && set FLASK_ENV=development && set FLASK_APP=app.py && python app.py"

REM Starting the frontend
start cmd /k "cd /d "D:\ML\Mavis Chatbot" && call "Mavis\Scripts\activate.bat" && cd frontend && npm start"

echo Backend and frontend processes have been started.
echo You can close this window now.