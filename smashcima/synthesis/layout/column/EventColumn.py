from smashcima.scene.semantic.Score import Score
from smashcima.scene.semantic.ScoreEvent import ScoreEvent
from smashcima.scene.visual.Stafflines import Stafflines
from smashcima.synthesis.glyph.GlyphSynthesizer import GlyphSynthesizer
from .NoteheadsColumn import NoteheadsColumn, synthesize_noteheads_column
from .RestsColumn import RestsColumn, synthesize_rests_column
from .ColumnBase import ColumnBase
from typing import List
import random


class EventColumn(NoteheadsColumn, RestsColumn):
    def __init__(self, *args, **kwargs):
        # ignore constructors of parents, initialize only the super-parent
        ColumnBase.__init__(self, *args, **kwargs)
    
    def __post_init__(self):
        NoteheadsColumn.__post_init__(self)
        RestsColumn.__post_init__(self)

    def _position_glyphs(self):
        NoteheadsColumn._position_glyphs(self)
        RestsColumn._position_glyphs(self)


def synthesize_event_column(
    staves: List[Stafflines],
    rng: random.Random,
    glyph_synthesizer: GlyphSynthesizer,
    score: Score,
    score_event: ScoreEvent
) -> EventColumn:
    column = EventColumn(staves, rng.random())

    synthesize_noteheads_column(
        column=column,
        staves=staves,
        glyph_synthesizer=glyph_synthesizer,
        score=score,
        score_event=score_event
    )

    synthesize_rests_column(
        column=column,
        staves=staves,
        glyph_synthesizer=glyph_synthesizer,
        score=score,
        score_event=score_event
    )
    
    return column
