from src.db_loader.file_mover import move_to_error, move_to_success


def test_move_to_success_moves_file_and_creates_dir(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("dummy", encoding="utf-8")
    destination_dir = tmp_path / "データ転送後"

    result = move_to_success(source, destination_dir)

    assert result == destination_dir / "source.csv"
    assert result.exists()
    assert not source.exists()


def test_move_to_error_moves_file_and_creates_dir(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("dummy", encoding="utf-8")
    destination_dir = tmp_path / "エラー項目"

    result = move_to_error(source, destination_dir)

    assert result == destination_dir / "bad.csv"
    assert result.exists()
    assert not source.exists()
