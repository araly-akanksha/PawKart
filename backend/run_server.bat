@echo off
set PYTHONPATH=%cd%
uvicorn app.main:app --reload
