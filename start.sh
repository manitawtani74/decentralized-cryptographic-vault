#!/bin/bash

if [ "$DEBUG" == "True" ]; then
    sleep 15
fi

# As we are using S3, takes 30-60 to load static. Not needed.
# python3 manage.py collectstatic --no-input
python3 manage.py migrate

if [ "$DEBUG" == "True" ]; then
    python3 manage.py runserver 0.0.0.0:8080
fi