"""
Visual Asset Preview & Picture Rendering Test Suite.
Verifies:
1. Generator creates valid standalone .svg files on disk.
2. Generator creates valid interactive .html visual inspection cards.
3. Generator synthesizes base64 data-URI images for direct inline frontend rendering.
4. Thumbnail HTML snippet contains valid img tags and fitness metrics.
"""
import os
import pytest
from src.visual_asset_preview_generator import visual_preview_generator, VisualAssetPreview


def test_visual_preview_generator_creates_all_visual_artifacts():
    """Verify standalone SVG, HTML preview card, and base64 data-URI generation."""
    sample_svg = (
        '<svg viewBox="0 0 64 64" width="64" height="64" xmlns="http://www.w3.org/2000/svg">\n'
        '  <circle cx="32" cy="32" r="24" fill="#6366f1"/>\n'
        '</svg>'
    )
    
    preview = visual_preview_generator.generate_preview(
        asset_name="TestCyberIcon",
        svg_markup=sample_svg,
        fitness_score=96.5,
        domain_theme="CyberSecurity"
    )

    assert isinstance(preview, VisualAssetPreview)
    assert os.path.exists(preview.svg_filepath)
    assert os.path.exists(preview.html_preview_filepath)
    assert preview.data_uri_image.startswith("data:image/svg+xml;base64,")
    assert "<img" in preview.thumbnail_html
    assert "Fitness: 96.5" in preview.thumbnail_html

    # Clean up generated test files
    if os.path.exists(preview.svg_filepath):
        os.remove(preview.svg_filepath)
    if os.path.exists(preview.html_preview_filepath):
        os.remove(preview.html_preview_filepath)


def test_visual_preview_html_structure():
    """Verify generated HTML preview contains dark mode styling and Tailwind."""
    sample_svg = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#0f172a"/></svg>'
    preview = visual_preview_generator.generate_preview(
        asset_name="DarkVault",
        svg_markup=sample_svg,
        fitness_score=98.0,
        domain_theme="FinTech"
    )

    with open(preview.html_preview_filepath, "r", encoding="utf-8") as f:
        content = f.read()

    assert "<!DOCTYPE html>" in content
    assert "DarkVault" in content
    assert "Fitness: 98.0/100" in content
    assert "tailwindcss" in content

    # Clean up
    if os.path.exists(preview.svg_filepath):
        os.remove(preview.svg_filepath)
    if os.path.exists(preview.html_preview_filepath):
        os.remove(preview.html_preview_filepath)
