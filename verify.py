import os
import base64

os.environ['OTREE_SETTINGS_MODULE'] = 'settings'
from otree.main import setup

setup()

from otree.database import db
from otree.session import create_session
from carbon.models import DownloadEvent, GUIDE_TOTAL, GUIDE_FILENAME
from carbon.pages import Thanks

sess = create_session('carbon_survey', num_participants=2)
db.commit()

players = [p.get_players()[0] for p in sess.get_participants()]
player = players[0]

# 1) meta
meta = Thanks.live_method(player, {'action': 'download_start'})[player.id_in_group]
assert meta['type'] == 'meta', meta
assert meta['total_chunks'] == GUIDE_TOTAL
assert meta['filename'] == GUIDE_FILENAME

# 2) reconstruct all chunks -> must equal the original PDF bytes exactly
full = b''
for i in range(GUIDE_TOTAL):
    c = Thanks.live_method(player, {'action': 'chunk', 'index': i})[player.id_in_group]
    assert c['type'] == 'chunk'
    full += base64.b64decode(c['data'])

with open('carbon/guide.pdf', 'rb') as f:
    orig = f.read()
assert full == orig, 'chunk reconstruction mismatch'
assert full[:5] == b'%PDF-', 'not a PDF header'

# 3) download_done -> server-side counting
before = player.download_count
res = Thanks.live_method(player, {'action': 'download_done'})[player.id_in_group]
db.commit()
assert res['type'] == 'ok'
assert player.download_count == before + 1, player.download_count
sub = player.subsession
assert sub.total_downloads == 1, sub.total_downloads
assert sub.total_downloaders == 1, sub.total_downloaders
events = DownloadEvent.filter()
assert len(events) == 1, len(events)
assert events[0].participant_code == player.participant.code

# 4) second download increments per-person count but not downloaders
Thanks.live_method(player, {'action': 'download_done'})[player.id_in_group]
db.commit()
assert player.download_count == 2, player.download_count
assert player.subsession.total_downloaders == 1
assert player.subsession.total_downloads == 2

# 5) a second participant downloading
Thanks.live_method(players[1], {'action': 'download_done'})[players[1].id_in_group]
db.commit()
assert players[1].subsession.total_downloaders == 2
assert players[1].subsession.total_downloads == 3

print('ALL CHECKS PASSED: chunks=%d pdf_bytes=%d' % (GUIDE_TOTAL, len(full)))
