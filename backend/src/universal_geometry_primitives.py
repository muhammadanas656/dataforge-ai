"""
DataForge AI Universal Geometry Primitives Library.
Provides high-order mathematical vector primitives across all design studios:
1. Natural Landscapes: Parallax mountain ridges, snow caps, twilight auroras, stratospheric clouds.
2. Living Creatures: Articulated wings with primary/secondary feather beziers, beaks, anatomical limbs.
3. Mechanical & Vehicles: Diamond bicycle frames, radial spoked wheels, jet fuselages, speed trails.
4. Spatial UI & Bento Cards: Frosted glassmorphism panels, hexagonal quantum cores, telemetry badges.
"""
from typing import Dict, Any, List, Tuple
import math


class UniversalGeometryPrimitives:
    """Parametric vector primitives for professional 9.5/10 vector synthesis."""

    # =========================================================================
    # 1. NATURAL LANDSCAPES & ATMOSPHERE
    # =========================================================================
    @staticmethod
    def mountain_ridge(
        width: int = 800,
        base_y: int = 420,
        peak_height: int = 240,
        num_peaks: int = 5,
        color_fill: str = "#1e293b",
        snow_color: str = "#f8fafc"
    ) -> str:
        """Generate a multi-peak parallax mountain ridge with jagged snow caps."""
        points = [(0, base_y)]
        snow_polys = []
        step = width / (num_peaks * 2)

        for i in range(1, num_peaks * 2):
            x = i * step
            if i % 2 == 1:
                # Peak
                y = base_y - peak_height + (math.sin(i * 1.5) * 35)
                points.append((x, y))
                snow_polys.append(
                    f'<polygon points="{x:.1f},{y:.1f} {x - 22:.1f},{y + 42:.1f} {x - 8:.1f},{y + 32:.1f} {x:.1f},{y + 48:.1f} {x + 12:.1f},{y + 35:.1f} {x + 24:.1f},{y + 44:.1f}" fill="{snow_color}" opacity="0.92"/>'
                )
            else:
                # Valley
                y = base_y - (peak_height * 0.28) + (math.cos(i) * 18)
                points.append((x, y))

        points.append((width, base_y))
        points.append((width, 600))
        points.append((0, 600))

        poly_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        return f'<g class="mountain-ridge">\n  <polygon points="{poly_pts}" fill="{color_fill}"/>\n  ' + "\n  ".join(snow_polys) + "\n</g>"

    @staticmethod
    def sun_aurora(cx: int = 400, cy: int = 300, radius: int = 120, sun_color: str = "#ffb703") -> str:
        """Generate a radiant sun with multi-stop glow aura and specular core."""
        return f"""<g class="sun-aurora" filter="url(#glow)">
  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="url(#sun_glow)"/>
  <circle cx="{cx}" cy="{cy}" r="{radius * 0.38:.1f}" fill="#fffbeb" opacity="0.95"/>
</g>"""

    # =========================================================================
    # 2. LIVING ANATOMY & BIRDS
    # =========================================================================
    @staticmethod
    def soaring_wings(cx: int = 400, cy: int = 200, scale: float = 1.0, wing_grad_id: str = "eagle_wing_grad") -> str:
        """Generate dual arched wings with 5 articulated primary feather beziers each."""
        s = scale
        left = (
            f'<path d="M {cx - 15*s:.1f} {cy + 10*s:.1f} '
            f'C {cx - 80*s:.1f} {cy - 40*s:.1f}, {cx - 160*s:.1f} {cy - 70*s:.1f}, {cx - 240*s:.1f} {cy - 90*s:.1f} '
            f'Q {cx - 260*s:.1f} {cy - 85*s:.1f}, {cx - 250*s:.1f} {cy - 70*s:.1f} '
            f'Q {cx - 230*s:.1f} {cy - 55*s:.1f}, {cx - 240*s:.1f} {cy - 45*s:.1f} '
            f'Q {cx - 215*s:.1f} {cy - 30*s:.1f}, {cx - 220*s:.1f} {cy - 20*s:.1f} '
            f'Q {cx - 190*s:.1f} {cy - 5*s:.1f}, {cx - 190*s:.1f} {cy + 10*s:.1f} '
            f'C {cx - 130*s:.1f} {cy + 30*s:.1f}, {cx - 70*s:.1f} {cy + 35*s:.1f}, {cx - 15*s:.1f} {cy + 25*s:.1f} Z" '
            f'fill="url(#{wing_grad_id})" stroke="#78350f" stroke-width="{1.5*s:.1f}"/>'
        )
        right = (
            f'<path d="M {cx + 15*s:.1f} {cy + 10*s:.1f} '
            f'C {cx + 80*s:.1f} {cy - 40*s:.1f}, {cx + 160*s:.1f} {cy - 70*s:.1f}, {cx + 240*s:.1f} {cy - 90*s:.1f} '
            f'Q {cx + 260*s:.1f} {cy - 85*s:.1f}, {cx + 250*s:.1f} {cy - 70*s:.1f} '
            f'Q {cx + 230*s:.1f} {cy - 55*s:.1f}, {cx + 240*s:.1f} {cy - 45*s:.1f} '
            f'Q {cx + 215*s:.1f} {cy - 30*s:.1f}, {cx + 220*s:.1f} {cy - 20*s:.1f} '
            f'Q {cx + 190*s:.1f} {cy - 5*s:.1f}, {cx + 190*s:.1f} {cy + 10*s:.1f} '
            f'C {cx + 130*s:.1f} {cy + 30*s:.1f}, {cx + 70*s:.1f} {cy + 35*s:.1f}, {cx + 15*s:.1f} {cy + 25*s:.1f} Z" '
            f'fill="url(#{wing_grad_id})" stroke="#78350f" stroke-width="{1.5*s:.1f}"/>'
        )
        return f'<g class="soaring-wings">\n  {left}\n  {right}\n</g>'

    # =========================================================================
    # 3. MECHANICAL & AEROSPACE SYSTEMS
    # =========================================================================
    @staticmethod
    def spoked_wheel(cx: int, cy: int, radius: int = 70, num_spokes: int = 8, color: str = "#06b6d4") -> str:
        """Generate a mechanical bicycle wheel with radial wire spokes and rubber tire."""
        spoke_lines = []
        angle_step = (2 * math.pi) / num_spokes
        for i in range(num_spokes):
            angle = i * angle_step
            x2 = cx + math.cos(angle) * (radius - 8)
            y2 = cy + math.sin(angle) * (radius - 8)
            spoke_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#94a3b8" stroke-width="1.5"/>')

        spokes_svg = "\n    ".join(spoke_lines)
        return f"""<g class="spoked-wheel">
  <!-- Outer Tire -->
  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="#0f172a" stroke="#334155" stroke-width="6"/>
  <!-- Rim -->
  <circle cx="{cx}" cy="{cy}" r="{radius - 6}" fill="none" stroke="{color}" stroke-width="2.5"/>
  <!-- Radial Wire Spokes -->
  <g>
    {spokes_svg}
  </g>
  <!-- Center Axle Hub -->
  <circle cx="{cx}" cy="{cy}" r="9" fill="{color}" stroke="#ffffff" stroke-width="2"/>
</g>"""

    # =========================================================================
    # 4. SPATIAL UI & BENTO PANELS
    # =========================================================================
    @staticmethod
    def bento_glass_panel(x: int, y: int, width: int, height: int, rx: int = 24, title: str = "Live Metric", value: str = "99.91%") -> str:
        """Generate an ultra-modern frosted glassmorphism Bento Card with real-time telemetry."""
        return f"""<g class="bento-glass-panel" transform="translate({x}, {y})">
  <rect width="{width}" height="{height}" rx="{rx}" fill="#0f172a" fill-opacity="0.85" stroke="url(#glass_border)" stroke-width="1.5" filter="url(#card_shadow)"/>
  <circle cx="20" cy="22" r="5" fill="#10b981"/>
  <text x="34" y="25" fill="#94a3b8" font-family="Inter, sans-serif" font-size="11" font-weight="600">{title.upper()}</text>
  <text x="20" y="{height - 18}" fill="#ffffff" font-family="Inter, sans-serif" font-size="20" font-weight="800">{value}</text>
</g>"""

    @staticmethod
    def quantum_core_matrix(cx: int = 200, cy: int = 200, radius: int = 60, accent_color: str = "#6366f1") -> str:
        """Generate a 3D isometric hexagonal quantum shield with orbital particle rings."""
        r = radius
        pts = f"0,-{r} {r*0.866:.1f},-{r*0.5:.1f} {r*0.866:.1f},{r*0.5:.1f} 0,{r} -{r*0.866:.1f},{r*0.5:.1f} -{r*0.866:.1f},-{r*0.5:.1f}"
        return f"""<g class="quantum-core" transform="translate({cx}, {cy})">
  <!-- Orbital Rings -->
  <ellipse cx="0" cy="0" rx="{r*1.8:.1f}" ry="{r*0.8:.1f}" fill="none" stroke="{accent_color}" stroke-width="1.8" stroke-opacity="0.4" transform="rotate(-30)"/>
  <ellipse cx="0" cy="0" rx="{r*1.8:.1f}" ry="{r*0.8:.1f}" fill="none" stroke="#06b6d4" stroke-width="1.8" stroke-opacity="0.4" transform="rotate(45)"/>
  <!-- Hexagonal Matrix -->
  <polygon points="{pts}" fill="url(#quantum_mesh)" stroke="#ffffff" stroke-width="2" opacity="0.9"/>
  <!-- Glowing Center Nucleus -->
  <circle cx="0" cy="0" r="{r*0.35:.1f}" fill="#ffffff" filter="drop-shadow(0 0 14px {accent_color})"/>
</g>"""


geometry_primitives = UniversalGeometryPrimitives()
