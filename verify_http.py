"""End-to-end test of the HTTP guide download (no WebSocket).
Walks a participant through every page, then POSTs the download on Thanks
and asserts the response is a real PDF file with Content-Disposition: attachment
and that the per-player download count incremented server-side.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('OTREE_SECRET_KEY', 'verify-secret-key-1234567890')
from otree.main import setup
setup()
from otree.database import init_orm
init_orm()

from otree.session import create_session
from otree.database import db
from otree.models import Participant
from otree.urls import routes
from starlette.applications import Starlette
from starlette.testclient import TestClient

FORM = {
    'Intro': {},
    'Part1': {'q1': '4', 'q2': '4', 'q3': '4', 'q4': '4', 'est1': '1.0'},
    'Reading': {},
    'PostReadingA': {'q6': '3', 'q7': '3', 'q8': '3', 'q9': '3', 'q10': '3',
                     'q11': '3', 'q12': '3', 'q13': '6'},
    'PostReadingB': {'q14': '3', 'q15': '3', 'q16': '3', 'q17': '3', 'q18': '3',
                     'q19': '3', 'q20': '3', 'q21': '3'},
    'Part4': {'est2': '1.0', 'q23': '3', 'q24': '3', 'q25': '3', 'q26': '3', 'q27': '1',
              'q28_light': 'True', 'q28_cup': 'True', 'q28_transit': 'True',
              'q28_takeout': 'False', 'q28_garbage': 'True', 'q28_none': 'False'},
    'Part5': {'q29': '1', 'q30': '2', 'q31': '3', 'q32': '3'},
    'Thanks': {'download_guide': '1'},
}

app = Starlette(routes=routes)
client = TestClient(app)

session = create_session(session_config_name='carbon_survey', num_participants=1)
pcode = session.get_participants()[0].code
print('participant code:', pcode)

ok = False
for step in range(30):
    participant = Participant.objects_get(code=pcode)
    url = participant._url_i_should_be_on()
    page = url.rstrip('/').split('/')[-2]
    print(f'step {step}: {page}  ({url})')

    r = client.get(url)
    assert r.status_code == 200, f'GET {url} -> {r.status_code}'
    m = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    csrf = m.group(1) if m else ''

    if page == 'Thanks':
        r2 = client.post(url, data={'csrf_token': csrf, 'download_guide': '1'},
                         allow_redirects=True)
        disp = r2.headers.get('content-disposition', '')
        ctype = r2.headers.get('content-type', '')
        print('download POST status:', r2.status_code)
        print('content-disposition:', disp)
        print('content-type:', ctype)
        print('bytes:', len(r2.content), 'head:', r2.content[:5])
        assert 'attachment' in disp, 'NOT forced download!'
        assert ctype == 'application/octet-stream', 'wrong content-type'
        assert r2.content[:4] == b'%PDF', 'not a PDF'
        participant = Participant.objects_get(code=pcode)
        from carbon.models import Player
        player = db.query(Player).filter_by(participant_id=participant.id).first()
        print('download_count after 1 download:', player.download_count)
        assert player.download_count == 1, 'count not incremented'
        # a second download should bump to 2
        r3 = client.post(url, data={'csrf_token': csrf, 'download_guide': '1'})
        assert r3.content[:4] == b'%PDF'
        # re-query the player (oTree 6 DBWrapper has no .refresh)
        player = db.query(Player).filter_by(participant_id=participant.id).first()
        print('download_count after 2 downloads:', player.download_count)
        assert player.download_count == 2, 'second count failed'
        ok = True
        break

    data = dict(FORM.get(page, {}))
    data['csrf_token'] = csrf
    r2 = client.post(url, data=data, allow_redirects=True)
    new_url = Participant.objects_get(code=pcode)._url_i_should_be_on()
    if new_url == url:
        print('STUCK on', page, 'POST status', r2.status_code)
        import re
        for kw in ['此字段', '必填', '无效', 'error', 'invalid', 'required', '不能为空']:
            for m in re.finditer(kw, r2.text, re.I):
                s = max(0, m.start() - 80)
                e = min(len(r2.text), m.end() + 80)
                print('ERR:', r2.text[s:e].replace('\n', ' '))
        # also dump input names present
        names = re.findall(r'name="([^"]+)"', r2.text)
        print('INPUTS:', names)
        break

print('\nRESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
