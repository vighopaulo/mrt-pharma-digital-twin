from core.resources import Resource


def test_resource_cost_totals() -> None:
    resource = Resource(
        name="Dose calibrator",
        quantity=3,
        unit_capex=25_000,
        annual_opex=2_000,
    )
    assert resource.total_capex == 75_000
    assert resource.total_annual_opex == 6_000
