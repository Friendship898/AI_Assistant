def test_app_factory_symbol_is_available() -> None:
    from app.main import create_app

    assert callable(create_app)

