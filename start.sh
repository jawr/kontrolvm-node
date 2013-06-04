#!/bin/bash
celery worker --app=tasks.installationdisk &
python main.py
