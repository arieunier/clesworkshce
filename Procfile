web:  export PYTHONPATH=.:./libs:./appsrc; env;  gunicorn --workers=4 run:app
worker: export PYTHONPATH=.:./appsrc; python appsrc/cometd.py

