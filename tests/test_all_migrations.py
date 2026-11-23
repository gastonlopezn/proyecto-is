import sqlalchemy as sa
from alembic import command
from alembic.config import Config as AlembicConfig


def test_all_tables_migration_upgrade_and_downgrade(tmp_path, monkeypatch):
    """Test that alembic upgrade head creates all tables (domain, user, position) and downgrade removes them."""
    db_file = tmp_path / "migration_all_test.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setattr("myapp.config.Config.SQLALCHEMY_DATABASE_URI", db_url)

    alembic_cfg = AlembicConfig("migrations/alembic.ini")

    # 1. Upgrade to head on empty database
    command.upgrade(alembic_cfg, "head")

    engine = sa.create_engine(db_url)
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()

    all_tables = {"category", "tag", "question", "response", "question_tag", "user", "position"}
    assert all_tables.issubset(set(tables))

    # Verify column structure of user table
    user_cols = {col["name"] for col in inspector.get_columns("user")}
    assert {
        "id",
        "name",
        "email",
        "password_hash",
        "balance",
        "role",
    }.issubset(user_cols)

    # Verify column structure of position table
    position_cols = {col["name"] for col in inspector.get_columns("position")}
    assert {
        "id",
        "quantity",
        "purchase_price",
        "user_id",
        "response_id",
    }.issubset(position_cols)

    # 2. Downgrade -1 reverts the latest migration (remaining tables)
    command.downgrade(alembic_cfg, "-1")

    inspector = sa.inspect(engine)
    remaining_tables = inspector.get_table_names()

    remaining_remaining_tables = {"user", "position"}
    for table in remaining_remaining_tables:
        assert table not in remaining_tables

    domain_tables = {"category", "tag", "question", "response", "question_tag"}
    assert domain_tables.issubset(set(remaining_tables))

    # 3. Downgrade base reverts domain tables migration as well
    command.downgrade(alembic_cfg, "base")

    inspector = sa.inspect(engine)
    final_tables = inspector.get_table_names()

    for table in domain_tables:
        assert table not in final_tables

    # 4. Upgrade head again can run cleanly (reproducibility)
    command.upgrade(alembic_cfg, "head")

    inspector = sa.inspect(engine)
    tables_after_reupgrade = inspector.get_table_names()
    assert all_tables.issubset(set(tables_after_reupgrade))

    engine.dispose()
