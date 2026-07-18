from math import isclose
from core.radionuclides import Radionuclide

def test_half_life_retains_half_activity() -> None:
    isotope = Radionuclide("Fluorine-18", "F-18", 109.77)
    assert isclose(isotope.retained_fraction(109.77), 0.5, rel_tol=1e-9)
    assert isclose(isotope.remaining_activity(10.0, 109.77), 5.0, rel_tol=1e-9)
