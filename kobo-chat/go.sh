#!/bin/bash

# Password or PIN necessary to use the /unsafe command
export GLYPH_PASS_UNSAFE=forGithub

flask --app main.py run --debug -p 4646 --host=0.0.0.0 $@
