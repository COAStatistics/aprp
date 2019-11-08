#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

python manage.py init_user admin admin@test.com 123456 --is-staff --is-superuser
python manage.py loaddata logs accounts configs sources
python manage.py loaddata cog01 cog02 cog03 cog04 cog05 cog06 cog07 cog08 cog09 cog10 cog11 cog12 cog13 cog14
python manage.py loaddata eventtype
python manage.py loaddata fixtures/watchlists/*.yaml