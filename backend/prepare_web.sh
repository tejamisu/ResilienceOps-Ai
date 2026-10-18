#!/bin/sh
# Build the app and put it where the container serves it (/ on Cloud Run).
set -e
cd "$(dirname "$0")"
python3 ../test-run/build-app.py
mkdir -p web && cp ../test-run/resilienceops.html web/index.html && cp ../test-run/field.html web/field.html
echo "web/index.html ready"
