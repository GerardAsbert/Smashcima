from typing import Set, Type
from .GlyphSynthesizer import GlyphSynthesizer, T
from mashcima2.scene.visual.Glyph import Glyph
from mashcima2.assets.AssetRepository import AssetRepository
from mashcima2.assets.glyphs.muscima_pp.MuscimaPPGlyphs import MuscimaPPGlyphs
from mashcima2.assets.glyphs.muscima_pp.MppGlyphClass import MppGlyphClass
from .SmuflGlyphClass import SmuflGlyphClass
import random
import copy


class MuscimaPPGlyphSynthesizer(GlyphSynthesizer):
    """
    Synthesizes glyphs by sampling from the MUSCIMA++ dataset
    """
    def __init__(self, assets: AssetRepository, rng: random.Random):
        self.rng = rng
        bundle = assets.resolve_bundle(MuscimaPPGlyphs)
        self.symbol_repository = bundle.load_symbol_repository()
    
    @property
    def supported_glyphs(self) -> Set[str]:
        return {
            # noteheads
            SmuflGlyphClass.noteheadWhole.value,
            SmuflGlyphClass.noteheadHalf.value,
            SmuflGlyphClass.noteheadBlack.value,
            MppGlyphClass.noteheadEmpty.value,
            MppGlyphClass.noteheadFull.value,
            
            # barlines
            SmuflGlyphClass.barlineSingle.value,
        }
    
    def synthesize_glyph(
        self,
        glyph_class: str,
        expected_glyph_type: Type[T] = Glyph
    ) -> T:
        assert type(glyph_class) is str, "Requested glyph class must be str type"

        # pick a glyph from the symbol repository
        glyph = self._synthesize_glyph(glyph_class)

        # make a copy of that glyph before returning
        glyph_copy = copy.deepcopy(glyph)

        # adjust its glyph class to match what the user wants
        # (e.g. SMUFL instead of MUSCIMA++)
        glyph_copy.glyph_class = glyph_class

        # verify before returning
        self.verify_glyph_type_and_class(
            glyph_class,
            expected_glyph_type,
            glyph_copy
        )

        return glyph_copy
    
    def _synthesize_glyph(self, glyph_class: str) -> Glyph:
        # noteheads
        if glyph_class == SmuflGlyphClass.noteheadWhole \
        or glyph_class == SmuflGlyphClass.noteheadHalf \
        or glyph_class == MppGlyphClass.noteheadEmpty:
            return self.pick(MppGlyphClass.noteheadEmpty.value)
        
        if glyph_class == SmuflGlyphClass.noteheadBlack \
        or glyph_class == MppGlyphClass.noteheadFull:
            return self.pick(MppGlyphClass.noteheadFull.value)
        
        # barlines
        if glyph_class == SmuflGlyphClass.barlineSingle \
        or glyph_class == MppGlyphClass.thinBarline:
            return self.pick(MppGlyphClass.thinBarline.value)
        
        raise Exception("Unsupported glyph class: " + glyph_class)
    
    def pick(self, glyph_class: str) -> Glyph:
        # TODO: randomize writer selection only once per page!
        writer = self.rng.choice(list(self.symbol_repository.all_writers))
        
        # get the list of glyphs to choose from
        # (if writer is missing this class, fall back on all writers)
        glyphs = self.symbol_repository.glyphs_by_class_and_writer.get(
            (glyph_class, writer)
        ) or self.symbol_repository.glyphs_by_class.get(glyph_class)

        if glyphs is None or len(glyphs) == 0:
            raise Exception(
                f"The glyph class {glyph_class} is not present in " + \
                "the symbol repository"
            )
        
        # pick a random glyph from the list
        return self.rng.choice(glyphs)
