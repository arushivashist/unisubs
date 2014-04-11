#!/bin/sh
fig run --rm web python manage.py syncdb --all --noinput --settings=dev_settings
fig run --rm web python manage.py migrate --fake --settings=dev_settings
