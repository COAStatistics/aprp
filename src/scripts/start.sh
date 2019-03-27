#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

python manage.py migrate
python manage.py compilemessages
python manage.py collectstatic --noinput --verbosity 0

python manage.py loaddata logs accounts configs sources
python manage.py loaddata cog01 cog02 cog03 cog04 cog05 cog06 cog07 cog08 cog09 cog10 cog11 cog12 cog13 cog14
python manage.py loaddata eventtype
python manage.py loaddata 2018h1 2018h2 2019h1 mp-2018h1 mp-2018h2 mp-2019h1

python manage.py runserver 0.0.0.0:8000
