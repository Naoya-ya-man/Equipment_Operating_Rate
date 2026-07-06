from unittest.mock import MagicMock

from src.db_loader.schema_setup import ensure_schema


def test_ensure_schema_executes_three_statements_and_commits():
    connection = MagicMock()

    ensure_schema(connection)

    cursor = connection.cursor.return_value
    assert cursor.execute.call_count == 3

    executed_sql = [call.args[0] for call in cursor.execute.call_args_list]
    assert any("CREATE TABLE" in sql for sql in executed_sql)
    assert any("CREATE UNIQUE INDEX" in sql for sql in executed_sql)
    assert any("CREATE INDEX" in sql and "UNIQUE" not in sql for sql in executed_sql)

    connection.commit.assert_called_once()
