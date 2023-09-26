if exist venv\ (call venv\scripts\activate)
if exist .venv\ (call .venv\scripts\activate)

python osd-tool.py

deactivate
pause
