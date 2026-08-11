#!/bin/bash
set -e

# Idempotent DB init: only resetdb when the oTree tables do not yet exist.
# NEVER unconditionally resetdb -> that would wipe participant data on every redeploy.
python bootstrap_db.py || otree resetdb --noinput

exec otree prodserver "${PORT:-8000}"
