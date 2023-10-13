#!/bin/sh

make migrate
# make load-fixtures
make collect

exec "$@"
