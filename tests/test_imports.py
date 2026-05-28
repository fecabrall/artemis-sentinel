def test_import_src_package():
    import src  # noqa: F401


def test_import_collectors():
    from src.collectors import nasa_donki, nasa_power  # noqa: F401


def test_import_risk_engine():
    from src.intelligence import risk_engine  # noqa: F401

