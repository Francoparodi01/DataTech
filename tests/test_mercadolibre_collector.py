from datatech.collectors.mercadolibre import MercadoLibreCollector


class _Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "results": [
                {
                    "id": "MLA1",
                    "title": "GPU",
                    "price": 123.45,
                    "currency_id": "ARS",
                    "permalink": "https://example.test/MLA1",
                    "thumbnail": "https://img.test/1.jpg",
                    "seller": {"id": 99},
                }
            ]
        }


class _Session:
    def __init__(self):
        self.headers = {}

    def get(self, *args, **kwargs):
        return _Response()


def test_meli_collector_maps_api_payload_to_snapshot():
    collector = MercadoLibreCollector(session=_Session())
    rows = collector.search("gpu")
    assert len(rows) == 1
    assert rows[0].source == "mercadolibre"
    assert rows[0].source_product_id == "MLA1"
    assert rows[0].seller_id == "99"
