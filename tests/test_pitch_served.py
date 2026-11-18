"""The 2-minute pitch page is served by the backend at /pitch/, so the demo opens from any computer."""


def test_pitch_page_and_its_data_are_served():
    from fastapi.testclient import TestClient
    from finagent import server

    client = TestClient(server.app)
    page = client.get("/pitch/")
    assert page.status_code == 200 and "text/html" in page.headers["content-type"]
    assert 'src="data.js"' in page.text
    data = client.get("/pitch/data.js")
    assert data.status_code == 200 and "javascript" in data.headers["content-type"]
