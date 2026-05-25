#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Move into the Django project directory
cd home/webapp/attendance_monitor

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py setup_project
