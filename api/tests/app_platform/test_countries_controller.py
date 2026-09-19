BASE = "/api/v1/countries"


class TestGetCountries:
    async def test_get_countries_valid(self, client):
        resp = await client.get(BASE)
        assert resp.status_code == 200
        body = resp.json()
        assert any(item["code"] == "CO" for item in body)


class TestGetDocumentTypes:
    async def test_get_document_types_valid(self, client):
        resp = await client.get(f"{BASE}/document-types")
        assert resp.status_code == 200
        body = resp.json()
        assert "CC" in body["labels"]
        assert isinstance(body["groups"], list)
