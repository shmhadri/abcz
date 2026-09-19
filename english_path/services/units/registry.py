from functools import lru_cache

from english_path.services.a1_phase3 import enrich_a1_unit
from english_path.services.unit_schema import validate_unit
from english_path.services.units.a1_01 import UNIT as A1_01
from english_path.services.units.a1_02 import UNIT as A1_02
from english_path.services.units.a1_03 import UNIT as A1_03
from english_path.services.units.a1_04 import UNIT as A1_04
from english_path.services.units.a1_05 import UNIT as A1_05
from english_path.services.units.a1_06 import UNIT as A1_06
from english_path.services.units.a1_07 import UNIT as A1_07
from english_path.services.units.a1_08 import UNIT as A1_08
from english_path.services.units.a1_09 import UNIT as A1_09
from english_path.services.units.a1_10 import UNIT as A1_10
from english_path.services.units.a1_expansion import EXPANDED_A1_UNITS
from english_path.services.units.a2_01 import UNIT as A2_01
from english_path.services.units.a2_02 import UNIT as A2_02
from english_path.services.units.a2_03 import UNIT as A2_03
from english_path.services.units.a2_04 import UNIT as A2_04
from english_path.services.units.a2_05 import UNIT as A2_05
from english_path.services.units.a2_06 import UNIT as A2_06
from english_path.services.units.a2_07 import UNIT as A2_07
from english_path.services.units.a2_08 import UNIT as A2_08
from english_path.services.units.a2_09 import UNIT as A2_09
from english_path.services.units.a2_10 import UNIT as A2_10

A1_UNITS = tuple(validate_unit(enrich_a1_unit(unit)) for unit in (A1_01, A1_02, A1_03, A1_04, A1_05, A1_06, A1_07, A1_08, A1_09, A1_10, *EXPANDED_A1_UNITS))
A2_UNITS = (A2_01, A2_02, A2_03, A2_04, A2_05, A2_06, A2_07, A2_08, A2_09, A2_10)
UNIT_BY_SLUG = {unit["code"].lower().replace(".", "-"): unit for unit in (*A1_UNITS, *A2_UNITS)}


@lru_cache(maxsize=32)
def get_unit_content(unit_slug):
    return UNIT_BY_SLUG.get(unit_slug.lower())


def all_a1_units():
    return A1_UNITS


def all_a2_units():
    return A2_UNITS
