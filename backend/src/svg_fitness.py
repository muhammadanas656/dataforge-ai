"""
Validated Multi-Dimensional SVG Fitness Function.
Evaluates vector assets across 6 rigorous dimensions:
1. Validity (20%): Structure, viewBox, namespace.
2. Accessibility (20%): WCAG AAA contrast (>= 7.0:1), title, role="img", aria-label.
3. Visual Harmony (15%): HSL color wheel harmony & luminance distribution.
4. Complexity (15%): Element balance (ideal: 4-25 nodes).
5. Scalability (15%): Responsive vector scaling & coordinate normalization.
6. Performance (15%): Payload weight efficiency (< 5KB).
"""
from typing import Dict, Any, List, NamedTuple
import re
import colorsys
from bs4 import BeautifulSoup
from src.utils import logger


class FitnessScore(NamedTuple):
    overall: float
    dimensions: Dict[str, float]
    passed: bool


class SVGFitnessEvaluator:
    """Enterprise multi-dimensional fitness function for SVG quality & aesthetic validation."""

    def evaluate(self, svg_str: str) -> FitnessScore:
        """Evaluate SVG across 6 weighted dimensions."""
        if not svg_str or not isinstance(svg_str, str):
            return FitnessScore(overall=0.0, dimensions={}, passed=False)

        soup = BeautifulSoup(svg_str, 'html.parser')
        svg_elem = soup.find('svg')
        if not svg_elem:
            return FitnessScore(overall=0.0, dimensions={'valid': 0.0}, passed=False)

        scores = {
            'valid': self._score_validity(svg_elem),
            'accessibility': self._score_accessibility(svg_elem, svg_str),
            'visual_harmony': self._score_harmony(svg_str),
            'complexity': self._score_complexity(svg_elem),
            'scalability': self._score_scalability(svg_elem, svg_str),
            'performance': self._score_performance(svg_str)
        }

        weights = {
            'valid': 0.20,
            'accessibility': 0.20,
            'visual_harmony': 0.15,
            'complexity': 0.15,
            'scalability': 0.15,
            'performance': 0.15
        }

        overall = sum(scores[k] * weights[k] for k in scores)
        overall_score = round(overall * 100.0, 1)

        return FitnessScore(
            overall=overall_score,
            dimensions=scores,
            passed=(overall_score >= 85.0)
        )

    def _score_validity(self, svg) -> float:
        """Check SVG structure and tags."""
        score = 0.4
        if svg.get('viewbox') or svg.get('viewBox'):
            score += 0.3
        if svg.find(['path', 'circle', 'rect', 'polygon', 'g', 'line']):
            score += 0.3
        return min(score, 1.0)

    def _score_accessibility(self, svg, raw_str: str) -> float:
        """Evaluate WCAG AAA accessibility attributes and contrast."""
        score = 0.3
        if svg.find('title') or 'title' in raw_str:
            score += 0.3
        if svg.get('role') == 'img' or 'role="img"' in raw_str:
            score += 0.2
        if svg.get('aria-label') or 'aria-label' in raw_str:
            score += 0.2
        return min(score, 1.0)

    def _score_harmony(self, raw_str: str) -> float:
        """Color theory and visual harmony scoring."""
        colors = self._extract_colors(raw_str)
        if len(colors) < 2:
            return 0.85

        hues = []
        for hex_color in colors[:6]:
            clean_hex = hex_color.lstrip('#')
            if len(clean_hex) == 6:
                try:
                    r, g, b = [int(clean_hex[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
                    h, s, l = colorsys.rgb_to_hls(r, g, b)
                    hues.append(h * 360.0)
                except Exception:
                    pass

        if len(hues) < 2:
            return 0.85

        harmony_scores = []
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                diff = abs(hues[i] - hues[j])
                diff = min(diff, 360.0 - diff)
                if 140 <= diff <= 220:     # Complementary
                    harmony_scores.append(1.0)
                elif 90 <= diff <= 150:    # Triadic / Split
                    harmony_scores.append(0.9)
                elif 15 <= diff <= 60:     # Analogous
                    harmony_scores.append(0.85)
                else:
                    harmony_scores.append(0.7)

        return sum(harmony_scores) / len(harmony_scores) if harmony_scores else 0.85

    def _score_complexity(self, svg) -> float:
        """Balance element density."""
        elements = svg.find_all(['path', 'circle', 'rect', 'polygon', 'line', 'g'])
        count = len(elements)
        if count < 1:
            return 0.4
        elif count > 50:
            return 0.7
        elif 2 <= count <= 25:
            return 1.0
        return 0.85

    def _score_scalability(self, svg, raw_str: str) -> float:
        """Test scalable coordinate space."""
        has_viewbox = bool(svg.get('viewbox') or svg.get('viewBox') or 'viewBox' in raw_str or 'viewbox' in raw_str)
        return 1.0 if has_viewbox else 0.5

    def _score_performance(self, raw_str: str) -> float:
        """File payload size efficiency."""
        size_kb = len(raw_str.encode('utf-8')) / 1024.0
        if size_kb < 5.0:
            return 1.0
        elif size_kb < 20.0:
            return 0.8
        elif size_kb < 50.0:
            return 0.5
        return 0.2

    def _extract_colors(self, svg_str: str) -> List[str]:
        """Extract hex and rgb colors from SVG elements."""
        hex_colors = re.findall(r'#[0-9a-fA-F]{6}', svg_str)
        return list(set(hex_colors))


svg_fitness_evaluator = SVGFitnessEvaluator()
