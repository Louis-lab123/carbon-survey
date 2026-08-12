"""PythonAnywhere WSGI entry point.

PythonAnywhere serves apps over WSGI, but oTree 6 is an ASGI (Starlette) app.
We bridge the two with `a2wsgi.ASGIMiddleware` so the same code runs on PA's
WSGI server. The repo root is added to sys.path so `settings.py` and the
`carbon` app package are importable, and oTree reads its config from env vars
(set in the PA Web tab's "Environment variables" box).

This file lives at the repo root (e.g. /home/<user>/carbon-survey/wsgi.py).
In the PA Web tab set:
  - Source code directory: /home/<user>/carbon-survey
  - WSGI configuration file: /home/<user>/carbon-survey/wsgi.py
  - Virtualenv: /home/<user>/.virtualenvs/carbon-survey  (or your venv path)
"""
import os
import sys

# This file is at the repo root; make it importable so `settings` (the oTree
# settings module) and the `carbon` app package resolve.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# oTree discovers its settings module via OTREE_SETTINGS_MODULE (default 'settings').
os.environ.setdefault('OTREE_SETTINGS_MODULE', 'settings')
# Production defaults (can also be set in the PA Web tab env vars).
os.environ.setdefault('OTREE_PRODUCTION', '1')
os.environ.setdefault('OTREE_AUTH_LEVEL', 'STUDY')

from a2wsgi import ASGIMiddleware
from otree.asgi import app as asgi_app

# Wrap the ASGI app so it is callable as a WSGI app.
application = ASGIMiddleware(asgi_app)
