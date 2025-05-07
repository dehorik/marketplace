#!/usr/bin/env bash

set -e

python app/core/database/init_database.py

exec "$@"