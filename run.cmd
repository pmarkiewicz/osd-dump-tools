if exist venv\ (call venv\scripts\activate)
if exist .venv\ (call .venv\scripts\activate)

python run.py

deactivate
pause
