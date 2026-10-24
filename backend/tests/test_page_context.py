from backend.app.page_context import infer_page_type


def test_infers_page_type_from_url_path():
    assert infer_page_type("https://example.com/") == "homepage"
    assert infer_page_type("https://example.com/services/brand-a") == "service"
    assert infer_page_type("https://example.com/blog/seo-guide") == "blog"
    assert infer_page_type("https://example.com/products/a") == "product"


def test_unknown_page_type_is_safe_default():
    assert infer_page_type("https://example.com/our-story") == "unknown"
