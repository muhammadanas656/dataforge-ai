"""
Direct Browser Download & File Dispatch Test Suite.
Verifies:
1. Browser dispatcher creates valid Content-Disposition attachment headers.
2. Correct MIME types assigned for .svg, .jsx, .vue, .json, and .csv.
3. Generates 1-click client-side JavaScript Blob download snippets.
4. Produces standard FastAPI streaming Responses.
"""
import pytest
from src.browser_download_dispatcher import browser_download_dispatcher, BrowserDownloadContract


def test_browser_download_svg_contract():
    """Verify SVG direct browser attachment creation."""
    svg_code = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="20" fill="#6366f1"/></svg>'
    contract = browser_download_dispatcher.create_download_response(
        content=svg_code,
        filename="QuantumShield",
        file_format="svg"
    )

    assert isinstance(contract, BrowserDownloadContract)
    assert contract.filename == "QuantumShield.svg"
    assert contract.headers["Content-Disposition"] == 'attachment; filename="QuantumShield.svg"'
    assert "image/svg+xml" in contract.media_type
    assert "window.URL.createObjectURL" in contract.client_download_snippet_js
    assert "a.download = 'QuantumShield.svg'" in contract.client_download_snippet_js


def test_browser_download_multiple_framework_formats():
    """Verify React JSX, Vue SFC, JSON tokens, and CSV downloads."""
    formats = [
        ("Component", "jsx", "text/javascript"),
        ("Component", "vue", "text/plain"),
        ("tokens", "json", "application/json"),
        ("dataset", "csv", "text/csv")
    ]

    for name, fmt, expected_mime in formats:
        contract = browser_download_dispatcher.create_download_response(
            content=f"Sample {fmt} content",
            filename=name,
            file_format=fmt
        )
        assert contract.filename == f"{name}.{fmt}"
        assert expected_mime in contract.media_type
        assert f'attachment; filename="{name}.{fmt}"' == contract.headers["Content-Disposition"]


def test_fastapi_response_conversion():
    """Verify conversion to standard FastAPI streaming response."""
    contract = browser_download_dispatcher.create_download_response(
        content="id,val\n1,100",
        filename="cleaned_data",
        file_format="csv"
    )
    response = browser_download_dispatcher.to_fastapi_response(contract)

    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == 'attachment; filename="cleaned_data.csv"'
    assert response.media_type == "text/csv; charset=utf-8"
