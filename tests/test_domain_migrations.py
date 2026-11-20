import sqlalchemy as sa
from alembic import command
from alembic.config import Config as AlembicConfig


def test_domain_tables_migration_upgrade_and_downgrade(tmp_path, monkeypatch):
    """Test that alembic upgrade head creates domain tables and downgrade -1 removes them."""
    db_file = tmp_path / "migration_test.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setattr("myapp.config.Config.SQLALCHEMY_DATABASE_URI", db_url)

    alembic_cfg = AlembicConfig("migrations/alembic.ini")

    # 1. Upgrade to head on empty database
    command.upgrade(alembic_cfg, "head")

    engine = sa.create_engine(db_url)
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()

    domain_tables = {"category", "tag", "question", "response", "question_tag"}
    assert domain_tables.issubset(set(tables))

    # Verify column structure of question table
    question_cols = {col["name"] for col in inspector.get_columns("question")}
    assert {
        "id",
        "title",
        "body",
        "date",
        "source",
        "state",
        "category_title",
    }.issubset(question_cols)

    # Verify column structure of response table
    response_cols = {col["name"] for col in inspector.get_columns("response")}
    assert {
        "id",
        "title",
        "body",
        "price",
        "probability",
        "is_winner",
        "question_id",
    }.issubset(response_cols)

    # Verify question_tag association table
    qt_cols = {col["name"] for col in inspector.get_columns("question_tag")}
    assert {"question_id", "tag_title"}.issubset(qt_cols)

    # 2. Downgrade -1 reverts domain tables migration
    command.downgrade(alembic_cfg, "-1")

    inspector = sa.inspect(engine)
    remaining_tables = inspector.get_table_names()

    for table in domain_tables:
        assert table not in remaining_tables

    # 3. Upgrade head again can run cleanly (reproducibility)
    command.upgrade(alembic_cfg, "head")

    inspector = sa.inspect(engine)
    tables_after_reupgrade = inspector.get_table_names()
    assert domain_tables.issubset(set(tables_after_reupgrade))

    engine.dispose()
