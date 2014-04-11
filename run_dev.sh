#!/bin/bash
fig run --rm web python manage.py syncdb --all --settings=dev_settings
fig run --rm web python manage.py migrate --fake --settings=dev_settings
fig up web
