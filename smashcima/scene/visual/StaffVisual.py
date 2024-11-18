from dataclasses import dataclass

from ..AffineSpace import AffineSpace
from ..Glyph import Glyph
from ..SceneObject import SceneObject
from .StaffCoordinateSystem import StaffCoordinateSystem


@dataclass
class StaffVisual(SceneObject):
    """Represents the visual stafflines for a staff on the page"""

    width: float
    "Width (in millimeters) of these stafflines"

    staff_coordinate_system: StaffCoordinateSystem
    "Coordinate system that maps from pitch-time space to 2D position"

    space: AffineSpace
    """The affine space that contains all glyphs (noteheads, rests, accidentals)
    on these stafflines"""

    glyph: Glyph
    """Glyph of the stafflines themselves (all lines together, usually composite
    where each line is a sub-glyph). Child of the staff space."""
