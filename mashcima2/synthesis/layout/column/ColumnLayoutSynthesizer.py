from mashcima2.scene.visual.Stafflines import Stafflines
from mashcima2.scene.semantic.Score import Score
from mashcima2.scene.visual.System import System
from mashcima2.scene.visual.Page import Page
from mashcima2.synthesis.glyph.GlyphSynthesizer import GlyphSynthesizer
from ..BeamStemSynthesizer import BeamStemSynthesizer
from ...glyph.LineSynthesizer import LineSynthesizer
from .Column import Column
from .ColumnBase import ColumnBase
from .BarlinesColumn import synthesize_barlines_column
from .ClefsColumn import synthesize_header_clefs
from .NotesColumn import NotesColumn, synthesize_notes_column
from typing import List, Optional, Dict
import random


class SystemState:
    """Holds state while synthesizing a single system of music"""

    def __init__(self, minimal_column_spacing: float):
        self.minimal_column_spacing = minimal_column_spacing
        "Minimum spacing inserted in between columns"
        
        self.columns: List[Column] = []
        "List of columns in this system"

        self.total_width = 0
        "Total width of all the columns, if stacked most tightly"

        self.current_measure_index: Optional[int] = None
        "What measure are we currently in? None means no measure (header/footer)"

        self.measure_indices: List[int] = []
        "List of measures in the system, indicated by their score index"

        self.columns_per_measure: Dict[int, List[Column]] = {}
        "Columns attached to their measure by score measure index"
    
    def enter_measure(self, measure_index: int):
        assert measure_index not in self.measure_indices, \
            "You cannot enter a measure twice"
        self.current_measure_index = measure_index
        self.measure_indices.append(measure_index)
    
    def exit_measure(self):
        self.current_measure_index = None
    
    @property
    def measure_count(self) -> int:
        """How many measures are present in the system"""
        return len(self.measure_indices)
    
    def append_column(self, column: Column):
        column.position_glyphs()
        
        if len(self.columns) > 0:
            self.total_width += self.minimal_column_spacing

        self.total_width += column.width
        self.columns.append(column)

        if self.current_measure_index is not None:
            self.columns_per_measure.setdefault(self.current_measure_index, [])
            self.columns_per_measure[self.current_measure_index].append(column)
    
    def delete_measure(self, measure_index: int):
        assert measure_index in self.measure_indices
        assert measure_index in self.columns_per_measure

        columns = self.columns_per_measure[measure_index]
        del self.columns_per_measure[measure_index]
        self.measure_indices.remove(measure_index)

        for column in columns:
            self.total_width -= column.width + self.minimal_column_spacing
            self.columns.remove(column)
            column.detach()


def place_columns_tightly(state: SystemState, minimal_column_spacing: float):
    """Places columns from left to right with minimal spacing between them"""
    time_position = 0
    for column in state.columns:
        column.time_position = time_position + column.left_width
        column.position_glyphs()
        time_position += column.width + minimal_column_spacing


def place_columns_flexbox(
    state: SystemState,
    minimal_column_spacing: float,
    available_width: float
):
    """Places columns stretched out to fill the staff width, like CSS flexbox"""
    width_to_distribute = max(available_width - state.total_width, 0)
    total_flex_grow = sum(c.flex_grow for c in state.columns)
    width_unit = width_to_distribute / total_flex_grow

    time_position = 0
    for column in state.columns:
        width_portion = width_unit * column.flex_grow
        time_position += width_portion / 2
        
        column.time_position = time_position + column.left_width
        column.position_glyphs()
        time_position += column.width + minimal_column_spacing
        
        time_position += width_portion / 2


# TODO: define a layout synthesizer interface and inherit
# IN -> semantic scene object graph
# OUT -> visual scene object graph
class ColumnLayoutSynthesizer:
    def __init__(self, glyph_synthesizer: GlyphSynthesizer, rng: random.Random):
        self.glyph_synthesizer = glyph_synthesizer
        self.rng = rng

        self.minimal_column_spacing = 1.2
        "Minimal spacing inserted between columns"

        self.stretch_out_columns = True
        "Whether to place columns tightly or to stretch them out to fill staff"

        self.place_debug_rectangles = False
        "Places column rectangles for debugging (to see the columns)"

    def fill_page(
        self,
        page: Page,
        score: Score,
        start_on_measure: int
    ) -> List[System]:
        """Fills the page with music and returns the list of synthesized systems"""
        systems: List[System] = []
        
        # state
        remaining_staves = len(page.staves)
        completed_staves = 0
        current_measure = start_on_measure

        # synthesize systems until we have the space available
        while remaining_staves >= score.staff_count:

            # or until there are measures left to synthesize
            if current_measure >= score.measure_count:
                break

            # or until we hit a page break
            # TODO if ?: break

            # synthesize a single system
            system = self.synthesize_system(
                staves=page.staves[
                    completed_staves:
                    completed_staves+score.staff_count
                ],
                score=score,
                start_on_measure=current_measure
            )
            systems.append(system)

            # update state
            remaining_staves -= score.staff_count
            completed_staves += score.staff_count
            current_measure += system.measure_count
        
        return systems
    
    def synthesize_system(
        self,
        staves: List[Stafflines],
        score: Score,
        start_on_measure: int
    ) -> System:
        """Synthesizes a single system of music onto the provided staves"""
        assert start_on_measure < score.measure_count, \
            "There must be at least one measure left to be placed on the system"

        assert len(staves) == score.staff_count, \
            "Given staves do not match the required number of staves per system"

        # === phase 1: synthesizing columns ===

        state = SystemState(
            minimal_column_spacing=self.minimal_column_spacing
        )
        available_width = min(sf.width for sf in staves)

        # synthesize header = start of the system signatures
        # TODO: extract this into a method
        state.append_column(
            synthesize_header_clefs(
                staves, self.rng, self.glyph_synthesizer,
                score, start_on_measure
            )
        )

        # synthesize measures until there is space left
        next_measure_index = start_on_measure
        while state.total_width < available_width:

            # or until there are measures to synthesize
            if next_measure_index >= score.measure_count:
                break

            # or until we hit a line break
            # TODO if ?: break

            state.enter_measure(next_measure_index)
            score_measure = score.get_score_measure(next_measure_index)
            next_measure_index += 1

            # TODO: extract this into a method, there's going to be a lot
            # of code here eventually (synthesize_measure)

            # construct a column for each event
            for score_event in score_measure.events:
                state.append_column(
                    synthesize_notes_column(
                        staves, self.rng, self.glyph_synthesizer,
                        score, score_event
                    )
                )
            
            # column for the barlines
            state.append_column(
                synthesize_barlines_column(
                    staves, self.rng, self.glyph_synthesizer
                )
            )

            state.exit_measure()

        # TODO: synthesize system footer (key and time changes)

        # remove measures from the end until we stop overflowing
        # (and we want at least one measure to reman no matter what)
        while state.total_width >= available_width and state.measure_count > 1:
            state.delete_measure(state.measure_indices[-1])

        # === phase 2: placing columns ===

        # tight or flexbox stretch
        if self.stretch_out_columns:
            place_columns_flexbox(
                state,
                self.minimal_column_spacing,
                available_width
            )
        else:
            place_columns_tightly(state, self.minimal_column_spacing)

        # optionally place debugging boxes around columns
        if self.place_debug_rectangles:
            for column in state.columns:
                if isinstance(column, ColumnBase):
                    column.place_debug_boxes()

        # === phase 3: synthesizing beams and stems ===

        # TODO: get paper_space as an argument
        paper_space = staves[0].space.parent_space

        line_synthesizer = LineSynthesizer()
        beam_stem_synthesizer = BeamStemSynthesizer(line_synthesizer)

        # TODO: DEBUG: just testing out the line synth
        for column in state.columns:
            if isinstance(column, NotesColumn):
                for notehead_context in column.notehead_contexts:
                    beam_stem_synthesizer.synthesize_stem(
                        paper_space,
                        notehead_context.notehead
                    )

        return System(
            first_measure_index=start_on_measure,
            measure_count=state.measure_count
        )
