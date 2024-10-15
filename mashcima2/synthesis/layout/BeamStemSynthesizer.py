from mashcima2.scene.visual.Stafflines import Stafflines
from mashcima2.scene.semantic.Staff import Staff
from mashcima2.scene.semantic.Note import Note
from mashcima2.scene.semantic.Rest import Rest
from mashcima2.scene.semantic.BeamedGroup import BeamedGroup
from mashcima2.scene.semantic.ScoreMeasure import ScoreMeasure
from mashcima2.scene.semantic.Part import Part
from mashcima2.scene.semantic.Chord import Chord
from mashcima2.scene.semantic.Measure import Measure
from mashcima2.scene.semantic.StemValue import StemValue
from mashcima2.scene.AffineSpace import AffineSpace
from mashcima2.scene.Sprite import Sprite
from mashcima2.scene.visual.Notehead import Notehead
from mashcima2.scene.visual.Stem import Stem
from mashcima2.scene.visual.LineGlyph import LineGlyph
from mashcima2.geometry.Transform import Transform
from mashcima2.geometry.Rectangle import Rectangle
from mashcima2.geometry.Vector2 import Vector2
from mashcima2.geometry.Point import Point
from mashcima2.synthesis.glyph.LineSynthesizer import LineSynthesizer
from mashcima2.synthesis.glyph.SmuflGlyphClass import SmuflGlyphClass
from mashcima2.synthesis.glyph.SmashcimaGlyphClass import SmashcimaGlyphClass
from typing import List, Optional
from collections import Counter
import cv2
import numpy as np
import random
import math


MAX_BEAM_SLOPE = 0.35
BEAM_SLOPE_JITTER = 0.1


def softclamp(x: float, limit: float) -> float:
    """Acts as a symmetric clamp to keep (-limit <= x <= limit), but softly."""
    return math.tanh(x / limit) * limit


class BeamStemSynthesizer:
    def __init__(self, line_synthesizer: LineSynthesizer, rng: random.Random):
        self.line_synthesizer = line_synthesizer
        self.rng = rng

    def synthesize_beams_and_stems_for_measure(
        self,
        paper_space: AffineSpace,
        score_measure: ScoreMeasure
    ):
        # get all chords and beamed groups
        chords: List[Chord] = []
        groups: List[BeamedGroup] = []

        for score_event in score_measure.events:
            for event in score_event.events:
                for durable in event.durables:

                    if not isinstance(durable, Note):
                        continue

                    chord = Chord.of_note(durable)
                    if chord is not None and chord not in chords:
                        chords.append(chord)
                    
                    group = BeamedGroup.of_chord(chord)
                    if group is not None and group not in groups:
                        groups.append(group)
        
        # synthesize stems for all chords
        for chord in chords:
            self.synthesize_stem(paper_space, chord)

        # synthesize beam for each beamed group
        for group in groups:
            self.synthesize_beams(paper_space, group)

        # adjust stems for beamed groups
        for group in groups:
            self.adjust_stems_for_beam_group(group)

    def synthesize_stem(self, paper_space: AffineSpace, chord: Chord):
        # notehead in the middle of the stem (the "top" notehead)
        center_notehead = Notehead.of_note(
            chord.notes[-1 if chord.stem_value == StemValue.up else 0],
            fail_if_none=True
        )

        # notehead at the base of the stem (the "bottom" notehead)
        base_notehead = Notehead.of_note(
            chord.notes[0 if chord.stem_value == StemValue.up else -1],
            fail_if_none=True
        )

        # get stem orientation
        stem_value = chord.stem_value or self.infer_stem_orientation(chord)
        assert stem_value in [StemValue.none, StemValue.up, StemValue.down], \
            f"Invalid stem value {stem_value}, must be only up or down."
        
        # if no stem, do not render one
        if stem_value == StemValue.none:
            return

        # get both stem points
        stem_base = paper_space.transform_from(base_notehead.space).apply_to(
            self.get_stem_base_point(base_notehead, stem_value)
        )
        stem_center = paper_space.transform_from(center_notehead.space).apply_to(
            self.get_stem_base_point(center_notehead, stem_value)
        )
        stem_tip = self.get_stem_tip_point(stem_center, stem_value)

        # synthesize the stem glyph
        stem = Stem(
            glyph_class=SmuflGlyphClass.stem.value,
            space=AffineSpace(parent_space=paper_space),
            chord=chord
        )
        self.line_synthesizer.synthesize_line(
            glyph=stem,
            start_point=stem_base,
            end_point=stem_tip
        )
    
    def infer_stem_orientation(self, chord: Chord) -> StemValue:
        # NOTE: could be implemented in the future,
        # or can be subclassed and overriden by the user
        event = chord.get_event()
        onset = event.fractional_measure_onset
        measure = Measure.of_event(event, fail_if_none=True)
        part = Part.of_measure(measure, fail_if_none=True)
        measure_index = part.measures.index(measure)
        raise NotImplementedError(
            "Stem orientation inference is not supported. " + \
            "Provide explicit stem orientation in the scene semantic data. " + \
            f"Measure index: {measure_index}, onset: {onset}"
        )

    def get_stem_base_point(
        self,
        notehead: Notehead,
        orientation: StemValue
    ) -> Point:
        """Returns the point where the stem begins, in the notehead's space"""
        # TODO: account for notehead size or learn a distribution or something
        point = Point(1.0, 0)
        
        if orientation == StemValue.down:
            point = -point
        
        return point
    
    def get_stem_tip_point(
        self,
        base_point: Point,
        orientation: StemValue
    ) -> Point:
        """Returns the stem tip point in paper space, given the base point
        also in paper space"""
        # TODO: sample from a learned distribution
        delta_vector = Vector2(0.0, -5.0)

        if orientation == StemValue.down:
            delta_vector = -delta_vector
        
        return Point.from_origin_vector(base_point.vector + delta_vector)

    def synthesize_beams(self, paper_space: AffineSpace, group: BeamedGroup):
        assert len(group.chords) >= 2, \
            "There must be at least 2 chords in a beamed group"

        stems = [Stem.of_chord(ch, fail_if_none=True) for ch in group.chords]
        tips = [s.tip.transform_to(paper_space) for s in stems]
        up_stem_count = len(
            [s for s in stems if s.chord.stem_value == StemValue.up]
        )
        down_stem_count = len(
            [s for s in stems if s.chord.stem_value == StemValue.down]
        )
        assert up_stem_count + down_stem_count == len(stems), \
            "Beamed group must contain only up/down stems"
        
        # === 1) compute the slope of the beam ===

        # get the slope of the beam by fitting a line through the points
        slope = 0
        line = cv2.fitLine(
            np.array([list(tip) for tip in tips]),
            cv2.DIST_L2, 0, 0, 0
        ).flatten()
        slope = line[1] / line[0]
        
        # randomize slope if too straight
        if abs(slope) < 0.01:
            slope = self.rng.uniform(-BEAM_SLOPE_JITTER, BEAM_SLOPE_JITTER)
        
        # soft-clamp the slope to a reasonable value
        slope = softclamp(slope, MAX_BEAM_SLOPE)

        # === 2) compute beam vertical placement ===

        # If all stems pointed up, we place the beam from above so high,
        # that it does not squish a single stem. It only lengthens them.
        # Same if they all point down. If they have mixed directions,
        # we do both of these and then take the weighted average of the
        # two possible beam placements.

        def get_q(sub_tips: List[Point], stem_up: bool) -> Optional[float]:
            """Returns the "q" term of "kx+q" line for a list of tip points"""
            if len(sub_tips) == 0:
                return None
            
            # define the reference line
            origin = tips[0]
            offset = 0
            def _f(x: float) -> float:
                "The function of the beam line"
                return origin.y + (x - origin.x) * slope + offset
            
            if stem_up:
                offset -= max(
                    _f(sub_tip.x) - sub_tip.y
                    for sub_tip in sub_tips
                )
            else:
                offset += max(
                    sub_tip.y - _f(sub_tip.x)
                    for sub_tip in sub_tips
                )
            
            return _f(0)
        
        # get the two "q" constnat offsets of the line at x=0
        # based on stems pointing up or down
        q_for_up = get_q([
            tips[i] for i in range(len(stems))
            if stems[i].chord.stem_value == StemValue.up
        ], stem_up=True)
        q_for_down = get_q([
            tips[i] for i in range(len(stems))
            if stems[i].chord.stem_value == StemValue.down
        ], stem_up=False)

        # if there are both movements, do a weighted average,
        # else take the computed movement
        if q_for_up is not None and q_for_down is not None:
            q = (
                (q_for_up * up_stem_count + q_for_down * down_stem_count)
                / len(stems)
            )
        elif q_for_up is not None:
            q = q_for_up
        elif q_for_down is not None:
            q = q_for_down
        else:
            raise Exception("This should never be raised.")
        
        # TODO: guess or synth somehow
        BEAM_SPACING = 1.5

        def f(x: float, beam_number: int, stem_value: StemValue) -> float:
            """Defines the beam line (beam number is 1-based)"""
            beam_index = (beam_number - 1)
            if stem_value == StemValue.down:
                beam_index *= -1
            return slope * x + q + (beam_index * BEAM_SPACING)

        # === 3) synthesize beam glyphs ===

        def _determine_beam_orientation(chords: List[Chord]) -> StemValue:
            key, count = Counter(
                [ch.stem_value for ch in chords]
            ).most_common(1)[0]
            return key

        # beams
        for beam_number, chords in group.iterate_beams():
            beam = LineGlyph(
                glyph_class=SmashcimaGlyphClass.beam.value,
                space=AffineSpace(parent_space=paper_space)
            )
            start_tip = tips[group.chords.index(chords[0])]
            end_tip = tips[group.chords.index(chords[-1])]
            stem_value = _determine_beam_orientation(chords)
            self.line_synthesizer.synthesize_line(
                glyph=beam,
                start_point=Point(
                    start_tip.x,
                    f(start_tip.x, beam_number, stem_value)
                ),
                end_point=Point(
                    end_tip.x,
                    f(end_tip.x, beam_number, stem_value)
                )
            )
        
        # hooks
        # TODO...

    def adjust_stems_for_beam_group(self, group: BeamedGroup):
        # TODO ...
        pass
