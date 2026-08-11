import os
import sys

from sqlalchemy import create_engine, inspect

url = os.environ.get('DATABASE_URL', '')

if not url:
    # No external DB configured -> let oTree use its default local SQLite.
    # (On Render this branch should never happen; DATABASE_URL is always set.)
    sys.exit(1)

if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)

try:
    eng = create_engine(url, connect_args={'connect_timeout': 10})
    tables = inspect(eng).get_table_names()
except Exception as e:
    print('DB inspect failed:', e)
    sys.exit(1)

# Exit 0 if oTree tables already exist (keep data), 1 otherwise (need resetdb).
sys.exit(0 if 'otree_participant' in tables else 1)
