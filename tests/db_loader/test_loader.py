from unittest.mock import MagicMock

import pytest

from src.db_loader import loader

HEADER = "Product_Number,Machine_Name,Machine_Number,Processing_Start_Time,Processing_Completion_Time,Sum_DateTime,Pass_judgment\n"
ROW = "185001A,A,1,2026-07-04 08:00:00,2026-07-04 08:20:00,1200,OK\n"


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "データ転送前").mkdir()
    (tmp_path / "データ転送後").mkdir()
    (tmp_path / "エラー項目").mkdir()
    return tmp_path


def test_load_csv_to_db_success_moves_file_and_commits(monkeypatch, workspace):
    csv_path = workspace / "データ転送前" / "sample.csv"
    csv_path.write_text(HEADER + ROW, encoding="utf-8")

    fake_connection = MagicMock()
    monkeypatch.setattr(loader, "get_connection", lambda: fake_connection)

    result = loader.load_csv_to_db(csv_path, workspace_root=workspace)

    assert result.success is True
    assert result.row_count == 1
    assert not csv_path.exists()
    assert (workspace / "データ転送後" / "sample.csv").exists()
    # スキーマセットアップ(ensure_schema)とMERGE(行データ)で、それぞれ1回ずつコミットされる
    assert fake_connection.commit.call_count == 2
    fake_connection.rollback.assert_not_called()
    fake_connection.close.assert_called_once()


def test_load_csv_to_db_failure_rolls_back_and_moves_to_error(monkeypatch, workspace):
    csv_path = workspace / "データ転送前" / "broken.csv"
    csv_path.write_text(HEADER + ROW, encoding="utf-8")

    fake_connection = MagicMock()
    monkeypatch.setattr(loader, "get_connection", lambda: fake_connection)
    monkeypatch.setattr(
        loader,
        "merge_records",
        MagicMock(side_effect=RuntimeError("simulated DB failure")),
    )

    result = loader.load_csv_to_db(csv_path, workspace_root=workspace)

    assert result.success is False
    assert result.error_message == "simulated DB failure"
    assert not csv_path.exists()
    assert (workspace / "エラー項目" / "broken.csv").exists()
    fake_connection.rollback.assert_called_once()
    # スキーマセットアップ(ensure_schema)は先に成功しているため1回コミット済み、
    # 行データのMERGEが失敗したため追加のコミットは発生しない
    assert fake_connection.commit.call_count == 1


def test_load_csv_to_db_failure_when_connection_unavailable(monkeypatch, workspace):
    csv_path = workspace / "データ転送前" / "no_db.csv"
    csv_path.write_text(HEADER + ROW, encoding="utf-8")

    def _raise_connection_error():
        raise ConnectionError("no driver available")

    monkeypatch.setattr(loader, "get_connection", _raise_connection_error)

    result = loader.load_csv_to_db(csv_path, workspace_root=workspace)

    assert result.success is False
    assert "no driver available" in result.error_message
    assert (workspace / "エラー項目" / "no_db.csv").exists()


def test_load_pending_csv_files_processes_all_files_in_order(monkeypatch, workspace):
    (workspace / "データ転送前" / "b.csv").write_text(HEADER + ROW, encoding="utf-8")
    (workspace / "データ転送前" / "a.csv").write_text(HEADER + ROW, encoding="utf-8")

    processed_names = []

    def _fake_load(csv_path, workspace_root=None):
        processed_names.append(csv_path.name)
        return loader.LoadResult(file_path=csv_path, success=True, row_count=1)

    monkeypatch.setattr(loader, "load_csv_to_db", _fake_load)

    results = loader.load_pending_csv_files(workspace_root=workspace)

    assert processed_names == ["a.csv", "b.csv"]  # ファイル名昇順(BR-8)
    assert len(results) == 2


def test_load_pending_csv_files_returns_empty_when_input_dir_missing(tmp_path):
    assert loader.load_pending_csv_files(workspace_root=tmp_path) == []
