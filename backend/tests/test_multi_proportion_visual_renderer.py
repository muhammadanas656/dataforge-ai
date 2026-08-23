"""
Multi-Proportion Visual Renderer Test Suite.
Verifies:
1. Multi-proportion engine provides 1:1, 16:9, 9:16, and 3:1 aspect ratio specs.
2. High-DPI PNG canvas converter script generates valid client-side download triggers.
3. Multi-viewport HTML inspection card contains responsive previews and download buttons.
"""
import pytest
from src.multi_proportion_visual_renderer import multi_proportion_renderer, MultiProportionRenderResult


def test_multi_proportion_standard_ratios():
    """Verify all standard aspect ratios are registered."""
    ratios = multi_proportion_renderer.STANDARD_PROPORTIONS
    assert "square_1x1" in ratios
    assert "landscape_16x9" in ratios
    assert "portrait_9x16" in ratios
    assert "banner_3x1" in ratios

    assert ratios["square_1x1"].width_px == 512
    assert ratios["landscape_16x9"].width_px == 800


def test_multi_proportion_render_result_synthesis():
    """Verify HTML viewer and PNG conversion JavaScript generation."""
    sample_svg = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#6366f1"/></svg>'
    result = multi_proportion_renderer.render_all_proportions(
        asset_name="QuantumSecurityNode",
        svg_markup=sample_svg,
        domain_theme="Quantum_Glass",
        fitness_score=98.5
    )

    assert isinstance(result, MultiProportionRenderResult)
    assert result.asset_name == "QuantumSecurityNode"
    assert "downloadAssetAsPNG" in result.png_render_contract_js
    assert "canvas.toDataURL('image/png')" in result.png_render_contract_js
    assert "<!DOCTYPE html>" in result.interactive_viewer_html
    assert "1:1 Square (512x512)" in result.interactive_viewer_html
    assert "16:9 Landscape Card (800x450)" in result.interactive_viewer_html
