@echo off
REM Activate the virtual environment
call venv\Scripts\activate

REM Export the dependencies to requirements.txt
pip freeze > requirements.txt

REM Deactivate the virtual environment
deactivate

echo Requirements updated successfully.