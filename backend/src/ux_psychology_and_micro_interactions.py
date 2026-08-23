"""
UX Psychology, Micro-Interactions & Scroll Dynamics Engine.
Synthesizes and audits advanced modern web design interactions:
1. Micro-Interactions: Spring physics, magnetic cursor pull, pulse glows, and morphing transitions (Framer Motion & CSS).
2. UX Psychology Principles: Fitts's Law (touch targets >= 44px), Hick's Law (decision latency minimization), Miller's Rule, and Visual Hierarchy.
3. Scroll Interactions: Scroll-driven timeline animations, parallax depth layers, intersection triggers, and sticky glass navigation.
"""
from typing import Dict, Any, List, NamedTuple, Optional
import math
from src.utils import logger


class UXPsychologyAudit(NamedTuple):
    fitts_law_compliant: bool
    hicks_law_score: float
    cognitive_load_index: float
    visual_hierarchy_balanced: bool
    is_psychology_optimized: bool
    recommendations: List[str]


class MicroInteractionPreset(NamedTuple):
    name: str
    trigger: str
    css_classes: str
    framer_motion_props: Dict[str, Any]
    physics_spring: Dict[str, float]


class ScrollInteractionContract(NamedTuple):
    trigger_type: str
    threshold: float
    animation_type: str
    css_scroll_timeline: str
    react_hook_code: str


class UXInteractionEngine:
    """Enterprise UX psychology, kinetic physics micro-interactions, and scroll dynamics synthesier."""

    # =========================================================================
    # 1. UX PSYCHOLOGY AUDITOR
    # =========================================================================
    def audit_component_psychology(
        self,
        element_size_px: int = 48,
        options_count: int = 4,
        nested_depth: int = 2
    ) -> UXPsychologyAudit:
        """Audit component against Fitts's Law, Hick's Law, and Miller's Cognitive Rule."""
        recs = []

        # Fitts's Law: Touch targets must be >= 44px for optimal motor acquisition
        fitts_ok = (element_size_px >= 44)
        if not fitts_ok:
            recs.append("Increase touch target to at least 44px to satisfy Fitts's Law.")

        # Hick's Law: Decision Time T = b * log2(n + 1). Optimal choice count <= 7
        hicks_score = round(max(1.0 - (options_count / 15.0), 0.2), 2)
        if options_count > 7:
            recs.append("Exceeds Miller's 7±2 rule: Implement progressive disclosure to reduce cognitive load.")

        # Cognitive Load Index: Based on nesting depth and decision complexity
        cognitive_load = round(min(0.2 * nested_depth + (options_count * 0.05), 1.0), 2)

        is_optimized = (fitts_ok and hicks_score >= 0.70 and cognitive_load <= 0.60)

        return UXPsychologyAudit(
            fitts_law_compliant=fitts_ok,
            hicks_law_score=hicks_score,
            cognitive_load_index=cognitive_load,
            visual_hierarchy_balanced=True,
            is_psychology_optimized=is_optimized,
            recommendations=recs
        )

    # =========================================================================
    # 2. MICRO-INTERACTION SYNTHESIZER
    # =========================================================================
    def get_micro_interaction(self, interaction_type: str = "magnetic_spring_card") -> MicroInteractionPreset:
        """Generate Framer Motion and Tailwind CSS v4 micro-interaction specs."""
        presets = {
            "magnetic_spring_card": MicroInteractionPreset(
                name="Magnetic Spring Card",
                trigger="onHover",
                css_classes="transition-all duration-300 hover:shadow-2xl hover:shadow-indigo-500/20 hover:-translate-y-1 active:scale-98",
                framer_motion_props={
                    "whileHover": {"scale": 1.02, "y": -4},
                    "whileTap": {"scale": 0.98},
                    "transition": {"type": "spring", "stiffness": 400, "damping": 25}
                },
                physics_spring={"stiffness": 400.0, "damping": 25.0, "mass": 0.8}
            ),
            "pulse_glow_button": MicroInteractionPreset(
                name="Pulse Glow Button",
                trigger="onFocus / onHover",
                css_classes="relative overflow-hidden transition-transform duration-200 hover:scale-105 active:scale-95 shadow-lg shadow-indigo-500/30",
                framer_motion_props={
                    "whileHover": {"boxShadow": "0 0 25px rgba(99, 102, 241, 0.6)"},
                    "transition": {"duration": 0.2}
                },
                physics_spring={"stiffness": 300.0, "damping": 20.0, "mass": 1.0}
            ),
            "icon_morph_ripple": MicroInteractionPreset(
                name="Icon Morph Ripple",
                trigger="onClick",
                css_classes="group relative inline-flex items-center justify-center p-2 rounded-xl backdrop-blur-md bg-white/5 hover:bg-white/10",
                framer_motion_props={
                    "initial": {"rotate": 0},
                    "whileTap": {"rotate": 15, "scale": 0.9},
                    "transition": {"type": "spring", "stiffness": 500, "damping": 15}
                },
                physics_spring={"stiffness": 500.0, "damping": 15.0, "mass": 0.5}
            )
        }
        return presets.get(interaction_type, presets["magnetic_spring_card"])

    # =========================================================================
    # 3. SCROLL DYNAMICS & PARALLAX CONTRACTS
    # =========================================================================
    def get_scroll_interaction_contract(self, style: str = "parallax_glass_entry") -> ScrollInteractionContract:
        """Synthesize scroll-driven CSS timeline and React Intersection Observer hooks."""
        return ScrollInteractionContract(
            trigger_type="intersection_observer",
            threshold=0.15,
            animation_type="fade_slide_up_parallax",
            css_scroll_timeline="@keyframes scrollFade { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }",
            react_hook_code=(
                "const useScrollFadeIn = () => {\n"
                "  const [isVisible, setIsVisible] = useState(false);\n"
                "  const ref = useRef(null);\n"
                "  useEffect(() => {\n"
                "    const observer = new IntersectionObserver(([entry]) => {\n"
                "      if (entry.isIntersecting) setIsVisible(true);\n"
                "    }, { threshold: 0.15 });\n"
                "    if (ref.current) observer.observe(ref.current);\n"
                "    return () => observer.disconnect();\n"
                "  }, []);\n"
                "  return { ref, isVisible };\n"
                "};"
            )
        )


ux_interaction_engine = UXInteractionEngine()
