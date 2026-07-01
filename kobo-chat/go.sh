#!/bin/bash

# Password or PIN necessary to use the /html command
export GLYPH_PASS_UNSAFE=forGithub
export GLYPH_SECRET_KEY=forGithub

# Integration with the https://ntfy.sh/ service for sending to phone(s) via the /alert command
export GLYPH_NTFY_TOPIC=

# Whether we debug Flask internally or not
export ENABLE_FLASH_DEBUG=true

# Integrate with https://aqicn.org/api/ for air quality monitoring via the /air command
# You need a free auth token from their website
# Then you'll need the Station ID which can be manually retrieved at:
# https://api.waqi.info/search/?keyword=SOMECITY&token=YOURTOKEN
# You're looking for the "uid", such as 1451
export GLYPH_AQICN_AUTH_TOKEN=
export GLYPH_AQICN_STATION_ID=

source .venv/bin/activate
flask --app main.py run --debug -p 4646 --host=0.0.0.0 $@
