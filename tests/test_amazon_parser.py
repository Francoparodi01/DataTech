from datatech.collectors.amazon import AmazonHtmlCollector


def test_amazon_parser_extracts_structured_result():
    html = """
    <div data-component-type="s-search-result" data-asin="B012345678">
      <h2><a href="/dp/B012345678"><span>Example GPU</span></a></h2>
      <span class="a-price"><span class="a-offscreen">$499.99</span></span>
      <img class="s-image" src="https://img.test/gpu.jpg">
    </div>
    """
    result = AmazonHtmlCollector(delay_seconds=0).parse_page(html)
    assert len(result) == 1
    assert result[0].source_product_id == "B012345678"
    assert result[0].price == 499.99
    assert result[0].url == "https://www.amazon.com/dp/B012345678"
