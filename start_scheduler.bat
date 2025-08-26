@echo off
echo Starting AI Podcast Agent Scheduler...
echo Time: %date% %time%

cd /d "C:\Users\jkran\Podcastai"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting scheduler...
python run_scheduler.py

echo Scheduler stopped at %time%
pause 