#!/bin/bash

# Password or PIN necessary to use the /html command
export GLYPH_PASS_UNSAFE=forGithub
export GLYPH_SECRET_KEY=forGithub

# Integration with ntfy for sending to phone(s)
export GLYPH_NTFY_TOPIC=

flask --app main.py run --debug -p 4646 --host=0.0.0.0 $@
