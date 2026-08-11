from otree.api import Page
from .models import (
    record_download,
    GUIDE_CHUNKS,
    GUIDE_TOTAL,
    GUIDE_FILENAME,
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

    def live_method(player, data):
        action = data.get('action')
        if action == 'download_start':
            return {
                player.id_in_group: {
                    'type': 'meta',
                    'total_chunks': GUIDE_TOTAL,
                    'filename': GUIDE_FILENAME,
                }
            }
        elif action == 'chunk':
            i = data.get('index', 0)
            return {
                player.id_in_group: {
                    'type': 'chunk',
                    'index': i,
                    'data': GUIDE_CHUNKS[i],
                    'last': i == GUIDE_TOTAL - 1,
                }
            }
        elif action == 'download_done':
            record_download(player)
            return {player.id_in_group: {'type': 'ok', 'count': player.download_count}}
        return {player.id_in_group: {'type': 'error'}}


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
