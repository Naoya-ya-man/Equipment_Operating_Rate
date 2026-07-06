from src.csv_generator.capacity import compute_window_capacity


def test_compute_window_capacity_normal_case():
    # 12000秒 / 2400秒(加工機C) = 5 * 5号機 = 25
    assert compute_window_capacity(12000) == 25


def test_compute_window_capacity_zero_when_no_available_seconds():
    assert compute_window_capacity(0) == 0


def test_compute_window_capacity_floors_partial_units():
    # 2500秒 / 2400秒 = 1.04 -> floor 1 * 5号機 = 5
    assert compute_window_capacity(2500) == 5
