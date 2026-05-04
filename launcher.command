#!/bin/bash

cd "/Users/sst/Documents/Python Progect/Парсинг Hermes_2" || exit 1

python3 -m playwright install chromium || exit 1

python3 launcher.py
