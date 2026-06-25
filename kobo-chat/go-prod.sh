#!/bin/bash

# Set unique secret values for actual Production deployment
export GLYPH_PASS_UNSAFE=
export GLYPH_SECRET_KEY=
export GLYPH_NTFY_TOPIC=

source .venv/bin/activate
#screen -d -m -S glyphchat sh -c "flask --app main.py run -p 4646 --host=0.0.0.0 $@"
screen -d -m -S glyphchat sh -c "bash go-gunicorn.sh"
screen -r
