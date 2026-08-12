import os
import secrets

# oTree 6 requires these keys. SECRET_KEY must be STABLE in production
# (set OTREE_SECRET_KEY as an env var on Replit), otherwise sessions break on restart.
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

SECRET_KEY = os.environ.get('OTREE_SECRET_KEY') or secrets.token_urlsafe(50)
ADMIN_PASSWORD = os.environ.get('OTREE_ADMIN_PASSWORD', '')
AUTH_LEVEL = os.environ.get('OTREE_AUTH_LEVEL')  # set to 'STUDY' in production

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

ADMIN_USERNAME = 'admin'

SESSION_CONFIGS = [
    dict(
        name='carbon_survey',
        display_name='碳中和宣传效果调研',
        num_demo_participants=1,
        app_sequence=['carbon'],
    ),
]

ROOMS = [
    dict(name='carbon', display_name='碳中和宣传效果调研'),
]
