"""The opening screen: who is here, how much detail, how to explain it. Asked once, changeable from any chapter."""
from pathlib import Path

from finagent import run, stage

ROOT = Path(__file__).resolve().parents[1]
WEAH = ROOT / "cases" / "timothy-melanie-weah" / "financial-health.json"
WEB = stage.TEMPLATE.with_name("web")


def test_every_page_offers_the_opening_screen(tmp_path, monkeypatch):
    monkeypatch.setenv("VOICE_ENGINE", "mock")
    for mode in ("complete", "simple"):
        page = run.main(WEAH, tmp_path / mode, mode).read_text(encoding="utf-8")
        assert 'import(SITE + "web/welcome.js")' in page and "welcome.offer()" in page, mode
        assert "apply: takeChoices" in page, mode


def test_changing_the_detail_keeps_the_chapter(tmp_path, monkeypatch):
    """The other mode is another page: the chapter being read travels in the address and is opened again."""
    monkeypatch.setenv("VOICE_ENGINE", "mock")
    page = run.main(WEAH, tmp_path).read_text(encoding="utf-8")
    assert '"#ch-" + reading' in page and 'location.hash.startsWith("#ch-")' in page
    assert "function resumeChapter()" in page and "tryHouse3d().then(resumeChapter)" in page


def test_nothing_is_locked():
    """The same screen comes back with "Change", and a link can force it or leave it out (recordings, tests)."""
    module = (WEB / "welcome.js").read_text(encoding="utf-8")
    assert "change-btn" in module and "open(false)" in module
    assert 'asked === "0"' in module and 'asked !== "1"' in module
    assert '"Who is here?"' in module and '"How much detail?"' in module and '"How should we explain it?"' in module
    assert module.index('"Who is here?"') < module.index('"How much detail?"') < module.index('"How should we explain it?"')


def test_the_opening_screen_is_served_from_the_repo():
    from fastapi.testclient import TestClient
    from finagent import server

    module = TestClient(server.app).get("/web/welcome.js")
    assert module.status_code == 200 and "javascript" in module.headers["content-type"]
    assert 'from "./styles.js"' in module.text
    assert "http://" not in module.text and "https://" not in module.text
