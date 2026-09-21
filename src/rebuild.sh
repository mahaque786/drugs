#!/usr/bin/env bash
# Full rebuild. Everything outside src/ is generated; edit the Python modules only.
set -e
cd "$(dirname "$0")"
echo "-- build"     && python3 build.py
echo "-- validate"  && python3 validate.py
echo "-- visualize" && python3 visualize.py
echo "-- done"
