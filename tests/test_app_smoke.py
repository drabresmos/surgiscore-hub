from streamlit.testing.v1 import AppTest


def test_app_starts_without_exception(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app_smoke.db'}")
    app = AppTest.from_file("app.py", default_timeout=45).run()
    assert not app.exception
