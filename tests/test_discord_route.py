import web


def test_discord_redirects():
    client = web.app.test_client()
    response = client.get("/discord")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://discord.gg/z9vfpxy5KS"
