#!/bin/bash
pip install --upgrade pip

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port $PORT