from otree.api import Page
from starlette.responses import Response
from urllib.parse import quote
import os
from .models import (
    record_download,
    GUIDE_FILENAME,
    GUIDE_PATH,
    TREATMENTS,
)


class Intro(Page):
    pass


class Part1(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'est1']
    template_name = 'carbon/Survey.html'

    def vars_for_template(self):
        return dict(title='第一部分：环保身份与价值观')


class Reading(Page):
    def vars_for_template(self):
        treatment = self.player.treatment
        return dict(treatment_text=TREATMENTS.get(treatment, ''), treatment=treatment)


class PostReadingA(Page):
    form_model = 'player'
    form_fields = ['q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13']
    template_name = 'carbon/Survey.html'

    def vars_for_template(self):
        return dict(title='第三部分（上）：阅读后评价')


class PostReadingB(Page):
    form_model = 'player'
    form_fields = ['q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21']
    template_name = 'carbon/Survey.html'

    def vars_for_template(self):
        return dict(title='第三部分（下）：感知有效性与情感唤起')


class Part4(Page):
    form_model = 'player'
    form_fields = ['est2', 'q23', 'q24', 'q25', 'q26', 'q27',
                   'q28_light', 'q28_cup', 'q28_transit', 'q28_takeout', 'q28_garbage', 'q28_none']
    template_name = 'carbon/Survey.html'

    def vars_for_template(self):
        return dict(title='第四部分：信念更新与行为意愿')


class Part5(Page):
    form_model = 'player'
    form_fields = ['q29', 'q30', 'q31', 'q32']
    template_name = 'carbon/Survey.html'

    def vars_for_template(self):
        return dict(title='第五部分：基本信息')


class Thanks(Page):
    def vars_for_template(self):
        return dict(
            download_count=self.player.download_count,
            filename=GUIDE_FILENAME,
        )

    def post(self, request=None, **kwargs):
        fd = getattr(self, '_form_data', None)
        if fd is not None and fd.get('download_guide'):
            player = self.player
            with open(GUIDE_PATH, 'rb') as _f:
                data = _f.read()
            # Force a real download (never inline preview), with a safe ASCII
            # fallback name plus a UTF-8 encoded original name for modern browsers.
            disp = (
                'attachment; filename="carbon-guide.pdf"; '
                "filename*=UTF-8''" + quote(GUIDE_FILENAME)
            )
            resp = Response(content=data, media_type='application/octet-stream')
            resp.headers['Content-Disposition'] = disp
            resp.headers['Content-Length'] = str(len(data))
            resp.headers['Cache-Control'] = 'no-store'
            record_download(player)
            return resp
        return super().post()


page_sequence = [
    Intro,
    Part1,
    Reading,
    PostReadingA,
    PostReadingB,
    Part4,
    Part5,
    Thanks,
]
