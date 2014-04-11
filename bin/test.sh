#!/bin/bash
TESTS=${1:-}
fig run --rm web python manage.py test $TESTS --settings=dev_settings_test
