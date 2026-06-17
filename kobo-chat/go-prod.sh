#!/bin/bash

# Set these params locally on your deploy
export GLYPH_PASS_UNSAFE=
export GLYPH_SECRET_KEY=
export GLYPH_NTFY_TOPIC=

source .venv/bin/activate
screen -d -m -S glyphchat sh -c "flask --app main.py run --debug -p 4646 --host=0.0.0.0 $@"
screen -r
