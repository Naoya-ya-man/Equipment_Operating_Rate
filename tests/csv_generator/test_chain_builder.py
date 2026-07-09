from datetime import datetime, timedelta

from src.csv_generator.chain_builder import UnitAssignmentTracker, generate_product_chains
from src.csv_generator.config import MACHINE_TYPES
from src.csv_generator.models import ExecutionWindow


def _make_window(hour_length: int = 12, is_holiday: bool = False, available_seconds: int = 38400) -> ExecutionWindow:
    start = datetime(2026, 7, 7, 0, 0)  # 火曜日
    end = datetime(2026, 7, 7, hour_length, 0)
    return ExecutionWindow(
        window_start=start,
        window_end=end,
        is_holiday=is_holiday,
        available_seconds=available_seconds,
        earliest_start=start,
    )


def test_generate_product_chains_returns_empty_when_target_is_zero():
    window = _make_window()
    chains = generate_product_chains(window, target_chain_count=0)
    assert chains == []


def test_generate_product_chains_returns_empty_when_holiday():
    window = _make_window(is_holiday=True, available_seconds=0)
    chains = generate_product_chains(window, target_chain_count=10)
    assert chains == []


def test_generate_product_chains_each_chain_has_five_sequential_stages():
    window = _make_window()
    chains = generate_product_chains(window, target_chain_count=3)

    assert len(chains) <= 3
    assert len(chains) > 0

    for chain in chains:
        assert chain.is_completed
        assert [s.machine_name for s in chain.stages] == MACHINE_TYPES

        for stage in chain.stages:
            assert stage.processing_start_time >= window.window_start
            assert stage.processing_completion_time <= window.window_end
            assert stage.processing_completion_time > stage.processing_start_time
            assert stage.product_number == f"{chain.base_product_id}{stage.machine_name}"
            assert stage.pass_judgment in ("OK", "NG")

        # 後工程の開始時刻は前工程の終了時刻以降であること(BR-5)
        for earlier, later in zip(chain.stages, chain.stages[1:]):
            assert later.processing_start_time >= earlier.processing_completion_time


def test_generate_product_chains_stops_when_not_enough_time_remains():
    # 窓が極端に短い場合、1チェーンも作らずに打ち切る(BR-6)
    window = _make_window(hour_length=0)
    window.window_end = window.window_start  # 窓の長さを実質0にする
    chains = generate_product_chains(window, target_chain_count=5)
    assert chains == []


def test_unit_assignment_tracker_balances_across_units():
    tracker = UnitAssignmentTracker(datetime(2026, 7, 7, 0, 0))
    for _ in range(50):
        tracker.assign_unit("A")

    counts = tracker._counts["A"].values()
    assert max(counts) - min(counts) <= 1


def test_generate_product_chains_uses_five_units_in_parallel():
    # 直列(1本のライン相当)では130分/チェーンとして最大4〜5件しか作れないが、
    # 5号機が並行稼働すれば、12時間の窓でその5倍近くまで生成できるはずである。
    window = _make_window()
    chains = generate_product_chains(window, target_chain_count=20)

    assert len(chains) >= 15  # 直列実装(4〜5件)を大幅に上回ることを確認


def test_generate_product_chains_allows_overlapping_chains_on_different_units():
    window = _make_window()
    chains = generate_product_chains(window, target_chain_count=5)

    a_stage_starts = sorted(chain.stages[0].processing_start_time for chain in chains)
    # 直列実装なら次のチェーンのA開始は前のチェーンの完了(約130分後)まで来ないはずだが、
    # 並行実装ではA号機が5台あるため、もっと早い間隔で複数チェーンが開始できる
    assert a_stage_starts[-1] - a_stage_starts[0] < timedelta(minutes=130)
