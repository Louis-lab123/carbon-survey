import os
import time
import itertools

from otree.api import models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, ExtraModel
from otree.database import db, Link

# ---------------------------------------------------------------------------
# Choice sets
# ---------------------------------------------------------------------------
LIKERT7 = [
    [1, '完全不同意'],
    [2, '比较不同意'],
    [3, '轻微不同意'],
    [4, '一般'],
    [5, '轻微同意'],
    [6, '比较同意'],
    [7, '完全同意'],
]
CERT5 = [
    [1, '非常不确定'],
    [2, '比较不确定'],
    [3, '一般'],
    [4, '比较确定'],
    [5, '非常确定'],
]
GENDER = [[1, '男'], [2, '女'], [3, '其他 / 不愿透露']]
AGE = [
    [1, '18岁及以下'],
    [2, '19-22岁'],
    [3, '23-25岁'],
    [4, '26-35岁'],
    [5, '36-45岁'],
    [6, '46岁及以上'],
]
EDU = [[1, '高中及以下'], [2, '专科'], [3, '本科'], [4, '硕士及以上']]
FREQ5 = [
    [1, '从不关注'],
    [2, '偶尔关注'],
    [3, '一般关注'],
    [4, '经常关注'],
    [5, '每天关注'],
]
YESNO = [[1, '是'], [0, '否']]

# ---------------------------------------------------------------------------
# Reading materials (4 balanced random treatments)
# ---------------------------------------------------------------------------
TREATMENTS = {
    1: '【组1：抽象数据宣传】\n践行碳中和，需要每个人每年减少约1 吨二氧化碳排放。1 吨二氧化碳在标准大气压下占据约509 立方米的空间，是全球人均年碳排放量的约1/4。全民主动减碳，是助力国家碳中和目标实现、缓解温室效应的重要基础。',
    2: '【组2：具象场景宣传】\n践行碳中和，需要每个人每年减少约1 吨二氧化碳排放。这相当于为你所在的城市种下30 棵生长10 年的冷杉，或让一辆私家车少行驶整整5000 公里。想象一下，一片小树林的生机，或是一整年清新无车的街道，就握在你的每次低碳选择里。全民参与微小的减碳行动，就能汇聚成守护生态环境的巨大力量。',
    3: '【组3：碳中和基础信息】\n碳中和是指国家、企业、产品、活动或个人在一定时间内直接或间接产生的二氧化碳或温室气体排放总量，通过植树造林、节能减排等形式，以抵消自身产生的二氧化碳或温室气体排放量，实现正负抵消，达到相对“零排放”。中国提出力争2030 年前二氧化碳排放达到峰值，努力争取2060 年前实现碳中和。',
    4: '【组4：中性阅读材料】\n高效阅读是提升自我的重要方式，掌握科学的阅读技巧能够大幅提升知识吸收效率。日常阅读时，我们可以提前梳理书籍框架、抓取核心段落、做好读书笔记，同时定期复盘阅读内容，长期坚持能够有效拓宽认知视野、提升逻辑思维能力。',
}


class Constants(BaseConstants):
    name_in_url = 'carbon'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    total_downloads = models.IntegerField(initial=0)
    total_downloaders = models.IntegerField(initial=0)

    def creating_session(self):
        cyc = itertools.cycle([1, 2, 3, 4])
        for player in self.get_players():
            player.treatment = next(cyc)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.IntegerField(initial=1)

    # ---- Part 1: 环保身份与价值观 ----
    q1 = models.IntegerField(label='1. 我认为自己是一名注重环保、环境友好的人。', choices=LIKERT7)
    q2 = models.IntegerField(label='2. 践行低碳环保行为是我个人身份的重要组成部分。', choices=LIKERT7)
    q3 = models.IntegerField(label='3. 我为自己的环保行为感到自豪。', choices=LIKERT7)
    q4 = models.IntegerField(label='4. 环保是我价值观的重要组成部分。', choices=LIKERT7)
    est1 = models.FloatField(label='5. 请您估算：要实现碳中和目标，平均每人每年需要减少约多少吨二氧化碳排放？')

    def est1_error_message(self, value):
        if value is None or value < 0:
            return '请输入一个不小于 0 的数字'

    # ---- Part 3: 阅读后评价 ----
    q6 = models.IntegerField(label='6. 您对以上答案的确信程度是？', choices=CERT5)
    q7 = models.IntegerField(label='7. 总体而言，您认为个人减碳行为对缓解气候变化的效果有多大？', choices=LIKERT7)
    q8 = models.IntegerField(label='8. 闲暇时，我愿意主动学习新的知识与生活技能。', choices=LIKERT7)
    q9 = models.IntegerField(label='9. 我认为刚才阅读的内容是抽象的。', choices=LIKERT7)
    q10 = models.IntegerField(label='10. 我认为刚才阅读的内容是具体的。', choices=LIKERT7)
    q11 = models.IntegerField(label='11. 阅读内容让我能够在脑海中形成生动的画面感。', choices=LIKERT7)
    q12 = models.IntegerField(label='12. 您认为刚才阅读的内容的可信度如何？', choices=LIKERT7)
    q13 = models.IntegerField(label='13. 为保证问卷有效性，本题请直接选择“比较同意”。', choices=LIKERT7)

    q14 = models.IntegerField(label='14. 上述内容让我相信，个人减碳行为是有意义的。', choices=LIKERT7)
    q15 = models.IntegerField(label='15. 上述内容让我认为，个人参与减碳能够产生实际环保效果。', choices=LIKERT7)
    q16 = models.IntegerField(label='16. 上述内容让我觉得，普通人践行低碳行为简单、可落实。', choices=LIKERT7)
    q17 = models.IntegerField(label='17. 上述内容增强了我对减碳行动效果的信心。', choices=LIKERT7)
    q18 = models.IntegerField(label='18. 阅读内容后，我产生了对环境保护的责任感。', choices=LIKERT7)
    q19 = models.IntegerField(label='19. 阅读内容后，我产生了行动的紧迫感。', choices=LIKERT7)
    q20 = models.IntegerField(label='20. 阅读内容后，我对地球生态产生了共情。', choices=LIKERT7)
    q21 = models.IntegerField(label='21. 阅读内容后，我内心受到了鼓舞。', choices=LIKERT7)

    # ---- Part 4: 信念更新与行为意愿 ----
    est2 = models.FloatField(label='22. 根据您刚刚阅读的内容，请再次估算：平均每人每年需要减少约多少吨二氧化碳排放？')

    def est2_error_message(self, value):
        if value is None or value < 0:
            return '请输入一个不小于 0 的数字'

    q23 = models.IntegerField(label='23. 未来一个月，我愿意在日常生活中践行更多低碳行为。', choices=LIKERT7)
    q24 = models.IntegerField(label='24. 未来一个月，我愿意主动节约水电、减少一次性用品使用。', choices=LIKERT7)
    q25 = models.IntegerField(label='25. 未来一个月，我愿意优先选择低碳出行方式。', choices=LIKERT7)
    q26 = models.IntegerField(label='26. 我愿意向亲友推荐低碳环保的生活方式。', choices=LIKERT7)
    q27 = models.IntegerField(label='27. 我愿意将本调研问卷分享给1 位亲友，让更多人了解低碳环保。', choices=YESNO)
    q28_light = models.BooleanField(label='随手关灯、关电器')
    q28_cup = models.BooleanField(label='自带水杯，减少一次性杯子使用')
    q28_transit = models.BooleanField(label='优先选择公共交通出行')
    q28_takeout = models.BooleanField(label='减少外卖点餐次数')
    q28_garbage = models.BooleanField(label='垃圾分类投放')
    q28_none = models.BooleanField(label='暂时没有计划')

    # ---- Part 5: 基本信息 ----
    q29 = models.IntegerField(label='29. 您的性别：', choices=GENDER)
    q30 = models.IntegerField(label='30. 您的年龄段：', choices=AGE)
    q31 = models.IntegerField(label='31. 您的最高学历：', choices=EDU)
    q32 = models.IntegerField(label='32. 您日常关注低碳、环保、碳中和相关资讯的频率：', choices=FREQ5)

    # ---- Download tracking ----
    download_count = models.IntegerField(initial=0)
    downloaded = models.BooleanField(initial=False)
    first_download_time = models.StringField(initial='')
    last_download_time = models.StringField(initial='')
    download_clicks_client = models.IntegerField(initial=0)


class DownloadEvent(ExtraModel):
    player = Link(Player)
    participant_code = models.StringField()
    source = models.StringField()
    timestamp = models.StringField()
    unix_ts = models.FloatField()
    seq_for_player = models.IntegerField()


# ---------------------------------------------------------------------------
# Guide file. Served over HTTP as an attachment (Content-Disposition: attachment)
# so the browser SAVES it instead of previewing it inline. Raw bytes are never
# placed in any HTML template.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE_PATH = os.path.join(_HERE, 'guide.pdf')
GUIDE_FILENAME = '日常低碳行动极简指南.pdf'


def _now_str():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def record_download(player):
    """Increment counts only AFTER the client confirms a complete save."""
    player.download_count = (player.download_count or 0) + 1
    if not player.downloaded:
        player.downloaded = True
        player.first_download_time = _now_str()
    player.last_download_time = _now_str()

    sub = player.subsession
    sub.total_downloads = (sub.total_downloads or 0) + 1
    if player.download_count == 1:
        sub.total_downloaders = (sub.total_downloaders or 0) + 1

    DownloadEvent.create(
        player=player,
        participant_code=player.participant.code,
        source='guide',
        timestamp=_now_str(),
        unix_ts=time.time(),
        seq_for_player=player.download_count,
    )
    db.commit()


# ---------------------------------------------------------------------------
# Admin export: 4 tables -> (1) per-participant answers + download counts,
# (2) subsession totals, (3) per-treatment download stats, (4) audit log.
# ---------------------------------------------------------------------------
def custom_export(players):
    fields = [
        'treatment',
        'q1', 'q2', 'q3', 'q4', 'est1',
        'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13',
        'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21',
        'est2', 'q23', 'q24', 'q25', 'q26', 'q27',
        'q28_light', 'q28_cup', 'q28_transit', 'q28_takeout', 'q28_garbage', 'q28_none',
        'q29', 'q30', 'q31', 'q32',
        'download_count', 'downloaded', 'first_download_time', 'last_download_time',
    ]

    # Table 1: per participant
    yield ['participant_code', 'id_in_session', 'id_in_group'] + fields
    for p in players:
        row = [p.participant.code, p.id_in_session, p.id_in_group]
        for f in fields:
            row.append(p.field_maybe_none(f))
        yield row

    yield []

    # Table 2: subsession totals
    yield ['subsession_id', 'num_players', 'total_downloads', 'total_downloaders']
    subs = {}
    for p in players:
        subs.setdefault(p.subsession_id, p.subsession)
    for sid, sub in subs.items():
        n = sum(1 for p in players if p.subsession_id == sid)
        yield [sid, n, sub.total_downloads, sub.total_downloaders]

    yield []

    # Table 3: per-treatment download stats
    yield ['treatment', 'num_players', 'downloaders', 'total_downloads', 'avg_downloads']
    from collections import defaultdict
    stats = defaultdict(lambda: [0, 0, 0])
    for p in players:
        s = stats[p.treatment]
        s[0] += 1
        if p.download_count and p.download_count > 0:
            s[1] += 1
        s[2] += (p.download_count or 0)
    for t in sorted(stats):
        n, dl, tot = stats[t]
        avg = round(tot / n, 3) if n else 0
        yield [t, n, dl, tot, avg]

    yield []

    # Table 4: DownloadEvent audit log
    yield ['event_id', 'participant_code', 'source', 'seq_for_player', 'timestamp', 'unix_ts']
    for ev in DownloadEvent.filter():
        yield [ev.id, ev.participant_code, ev.source, ev.seq_for_player, ev.timestamp, ev.unix_ts]
