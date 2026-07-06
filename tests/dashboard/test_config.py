from src.dashboard.config import BASE_COLORS, color_for_series


def test_color_for_series_returns_base_color_for_machine_type_only():
    assert color_for_series("A", "A") == BASE_COLORS["A"]


def test_color_for_series_shades_by_unit_number():
    color_unit_1 = color_for_series("A", "A-1")
    color_unit_5 = color_for_series("A", "A-5")

    assert color_unit_1 == BASE_COLORS["A"]  # 号機1は基準色そのまま
    assert color_unit_5 != color_unit_1  # 号機5は異なる濃淡


def test_color_for_series_is_deterministic():
    assert color_for_series("B", "B-3") == color_for_series("B", "B-3")


def test_color_for_series_differs_across_machine_types():
    assert color_for_series("A", "A-1") != color_for_series("B", "B-1")
