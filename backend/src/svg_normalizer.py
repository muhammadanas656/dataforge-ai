"""
SVG Normalization, Sanitization & Framework Component Synthesis Engine.
Normalizes arbitrary crawled or user-supplied SVG strings into clean, accessible vector assets and typed React / Vue components.
"""
from typing import Dict, Any, NamedTuple
import re
from bs4 import BeautifulSoup
from src.utils import logger


class NormalizedSVG(NamedTuple):
    raw_svg: str
    react_jsx: str
    vue_component: str
    has_viewbox: bool
    is_accessible: bool
    cleaned_attributes: int


class SVGNormalizer:
    """Enterprise SVG Normalizer and Component Transpiler."""

    UNNECESSARY_ATTRS = [
        "xmlns:xlink", "xml:space", "enable-background", "data-name", "version", "id"
    ]

    REACT_CAMELCASE_MAP = {
        "stroke-width": "strokeWidth",
        "stroke-linecap": "strokeLinecap",
        "stroke-linejoin": "strokeLinejoin",
        "stroke-miterlimit": "strokeMiterlimit",
        "stroke-dasharray": "strokeDasharray",
        "stroke-dashoffset": "strokeDashoffset",
        "stroke-opacity": "strokeOpacity",
        "fill-rule": "fillRule",
        "fill-opacity": "fillOpacity",
        "clip-rule": "clipRule",
        "clip-path": "clipPath"
    }

    def normalize(self, svg_content: str, asset_name: str = "VectorIcon") -> NormalizedSVG:
        """Normalize SVG markup, enforce viewBox/a11y, and compile to React & Vue code."""
        if not svg_content or not isinstance(svg_content, str):
            raise ValueError("Invalid or empty SVG content.")

        soup = BeautifulSoup(svg_content, "html.parser")
        svg = soup.find("svg")
        if not svg:
            raise ValueError("No valid <svg> root element found in content.")

        cleaned_count = 0

        # 1. Enforce or Compute viewBox
        has_viewbox = bool(svg.get("viewBox"))
        if not has_viewbox:
            w = svg.get("width", "24")
            h = svg.get("height", "24")
            # Extract digits
            w_num = re.findall(r'\d+', str(w)) or ["24"]
            h_num = re.findall(r'\d+', str(h)) or ["24"]
            svg["viewbox"] = f"0 0 {w_num[0]} {h_num[0]}"
            has_viewbox = True
            cleaned_count += 1

        # 2. Strip Unnecessary & Bloated Attributes
        for attr in self.UNNECESSARY_ATTRS:
            if svg.has_attr(attr):
                del svg[attr]
                cleaned_count += 1

        # 3. Convert Inline CSS Styles to Native Attributes
        cleaned_count += self._convert_inline_styles(svg)

        # 4. Enforce Accessibility Standards (role="img", <title>)
        if not svg.find("title"):
            title_tag = soup.new_tag("title")
            title_tag.string = asset_name.replace("_", " ").title()
            svg.insert(0, title_tag)
        
        svg["role"] = "img"
        svg["aria-label"] = asset_name.replace("_", " ").title()

        # 5. Clean Sanitized Raw SVG String
        raw_str = str(svg).strip()

        # 6. Transpile to React JSX & Vue 3 Components
        react_code = self._transpile_to_react(raw_str, asset_name)
        vue_code = self._transpile_to_vue(raw_str, asset_name)

        return NormalizedSVG(
            raw_svg=raw_str,
            react_jsx=react_code,
            vue_component=vue_code,
            has_viewbox=has_viewbox,
            is_accessible=True,
            cleaned_attributes=cleaned_count
        )

    def _convert_inline_styles(self, svg_tag) -> int:
        """Convert style='fill: ...; stroke: ...' to direct element attributes."""
        count = 0
        all_tags = svg_tag.find_all(True) + ([svg_tag] if svg_tag.has_attr("style") else [])
        for elem in all_tags:
            if elem.has_attr("style"):
                style_str = elem["style"]
                pairs = [p.strip() for p in style_str.split(";") if ":" in p]
                for p in pairs:
                    k, v = p.split(":", 1)
                    k_clean = k.strip().lower()
                    v_clean = v.strip()
                    if k_clean in {"fill", "stroke", "stroke-width", "opacity"}:
                        elem[k_clean] = v_clean
                        count += 1
                del elem["style"]
                count += 1
        return count

    def _transpile_to_react(self, svg_str: str, asset_name: str) -> str:
        """Compile raw SVG into typed React JSX component with camelCase prop bindings."""
        component_name = re.sub(r'[^a-zA-Z0-9]', '', asset_name) or "CustomIcon"
        
        jsx_body = svg_str
        for dash_attr, camel_attr in self.REACT_CAMELCASE_MAP.items():
            jsx_body = jsx_body.replace(f'{dash_attr}=', f'{camel_attr}=')

        # Insert dynamic props into root SVG
        jsx_body = re.sub(r'<svg([^>]*)>', r'<svg\1 className={className} width={size} height={size} {...props}>', jsx_body, count=1)

        return (
            f"import React from 'react';\n\n"
            f"export const {component_name} = ({{ size = 24, className = '', ...props }}) => (\n"
            f"  {jsx_body}\n"
            f");\n"
            f"export default {component_name};"
        )

    def _transpile_to_vue(self, svg_str: str, asset_name: str) -> str:
        """Compile raw SVG into Vue 3 Single-File Component."""
        return (
            f"<template>\n"
            f"  {svg_str}\n"
            f"</template>\n\n"
            f"<script setup>\n"
            f"// {asset_name} - Generated by DataForge AI\n"
            f"defineProps({{\n"
            f"  size: {{ type: [Number, String], default: 24 }},\n"
            f"  color: {{ type: String, default: 'currentColor' }}\n"
            f"}});\n"
            f"</script>"
        )


svg_normalizer = SVGNormalizer()
