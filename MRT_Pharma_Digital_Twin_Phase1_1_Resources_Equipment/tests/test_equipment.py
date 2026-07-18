from core.equipment import Cyclotron, Scanner


def test_zero_capacity_cyclotron_is_valid_for_greenfield_project() -> None:
    cyclotron = Cyclotron(
        name="Future Cyclotron",
        maximum_beam_current_ua=0,
        production_hours_per_day=0,
    )
    assert cyclotron.is_brand_new_uncommissioned


def test_scanner_nominal_daily_capacity() -> None:
    scanner = Scanner(
        name="PET/CT",
        quantity=2,
        scans_per_hour=2,
        operating_hours_per_day=10,
        utilization_target=0.75,
    )
    assert scanner.nominal_daily_capacity == 30
