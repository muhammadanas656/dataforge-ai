"""
Adaptive Explanation & Conceptual Analogy Engine.
Provides 3-tier explanation complexity:
1. Beginner / ELI5: Crystal-clear everyday analogies, metaphors, and no-jargon mental models.
2. Intermediate: Business value, operational workflows, and practical applications.
3. Advanced: Mathematical formulations, precision matrix inversion, and algorithmic proofs.
"""
from typing import Dict, Any, Optional
import re
from src.utils import logger


CONCEPTUAL_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "triz": {
        "beginner": (
            "💡 **TRIZ (Theory of Contradiction Resolution) in Simple Words:** Think of TRIZ like an inventor's cheat sheet based on Genrich Altshuller's research.\n\n"
            "Imagine you want a phone that has a huge battery (so it lasts 3 days), but you also want it to be super thin and light. "
            "Normally, a bigger battery makes the phone heavy and thick—these requirements fight each other in a contradiction!\n\n"
            "Instead of giving up, TRIZ gives you **40 proven tricks** (principles) that inventors discovered over 50 years to resolve that exact contradiction without making compromises."
        ),
        "analogy": "🍳 It's like cooking: when you want your soup spicy without burning your tongue, you use rich coconut milk instead of plain water—a proven trick that gives flavor without pain.",
        "example": "📱 *Real-World Example:* Making a phone lightweight AND durable by replacing plastic with lightweight aerospace titanium.",
        "intermediate": (
            "📈 **TRIZ (Theory of Inventive Problem Solving):** An algorithmic methodology for resolving engineering and business contradictions.\n"
            "When improving one system parameter (e.g. speed, throughput) degrades another (e.g. cost, complexity), TRIZ maps the trade-off to 40 Inventive Principles to formulate non-compromise breakthrough architectures."
        ),
        "advanced": (
            "🔬 **TRIZ Contradiction Matrix Formulation:** Evaluates paired system variables \\((P_{\\text{improve}}, P_{\\text{worsen}})\\) across Altshuller's 39 standard physical parameters. "
            "Identifies invariant topological transformations \\(\\mathcal{T} \\in \\{1, \\dots, 40\\}\\) (e.g., Segmentation, Dynamicity, Phase Inversion) to circumvent pareto-frontier compromises."
        )
    },

    "causal_dag": {
        "beginner": (
            "🌳 **Causal DAG in Simple Words:** Think of a Causal DAG like a **family tree for causes**.\n\n"
            "It acts like a detective that tells you what *actually caused* something to happen, instead of getting tricked by coincidences.\n\n"
            "For example: Ice cream sales and sunburns both go up in the summer. Does eating ice cream give you a sunburn? Of course not! The hot summer sun causes *both*."
        ),
        "analogy": "🕵️ Like a detective finding the real culprit: A causal DAG draws clear arrows showing who started the domino effect.",
        "example": "🛒 *Real-World Example:* Discovering that a slow checkout button *causes* customers to leave your website, not just that they happen at the same time.",
        "intermediate": (
            "📊 **Causal Directed Acyclic Graph (DAG):** A structural causal model that distinguishes true causation from spurious statistical correlation.\n"
            "By controlling for confounders and applying do-calculus, it reveals which specific business levers directly drive revenue and customer retention."
        ),
        "advanced": (
            "📐 **Causal Markov & Precision Matrix Inversion:** Given observation vector \\(\\mathbf{X} \\sim \\mathcal{N}(\\mathbf{\\mu}, \\mathbf{\\Sigma})\\), computes the regularized precision matrix \\(\\mathbf{\\Theta} = (\\mathbf{\\Sigma} + \\lambda \\mathbf{I})^{-1}\\). "
            "Identifies conditional independence \\(X_i \\perp\\!\\!\\!\\perp X_j \\mid \\mathbf{X}_{-(i,j)} \\iff \\Theta_{ij} = 0\\), isolating directed structural equation weights \\(\\mathbf{B}\\) via do-calculus."
        )
    },

    "fat_tail": {
        "beginner": (
            "📉 **Fat Tails & Black Swans in Simple Words:** Imagine measuring the height of 1,000 people. Nobody is going to be 50 feet tall—people stay close to average.\n\n"
            "Now imagine measuring wealth. If Bill Gates walks into the room, the average wealth shoots up to billions! That's a **fat tail**.\n\n"
            "Fat-tail statistics help you prepare for rare, extreme surprises (like sudden market crashes or viral TikTok explosions) that normal math ignores."
        ),
        "analogy": "⛈️ Normal math prepares you for a rainy day. Fat-tail math prepares you for a once-in-a-century hurricane.",
        "example": "🚀 *Real-World Example:* Planning a startup budget assuming you might get 100 sales, but having servers ready in case you go viral with 1,000,000 sales overnight.",
        "intermediate": (
            "⚠️ **Fat-Tail Risk Modeling:** Classical Gaussian bell curves underestimate extreme events. Fat-tail models (Student-t, Pareto) incorporate heavy tails to compute accurate Value at Risk (VaR 95%) and Expected Shortfall."
        ),
        "advanced": (
            "📈 **Non-Gaussian Heavy-Tailed Shocks:** Replaces normal increments \\(dW_t\\) with Student-t (\\(\\nu = 3\\)) or Lévy alpha-stable jump diffusions with characteristic function \\(\\mathbb{E}[e^{itX}] = \\exp(-|ct|^\\alpha)\\). "
            "Calculates Tail Value at Risk: \\(\\text{CVaR}_\\alpha(X) = \\frac{1}{1-\\alpha}\\int_\\alpha^1 \\text{VaR}_u(X) du\\)."
        )
    },

    "ssrf": {
        "beginner": (
            "🛡️ **SSRF Security in Simple Words:** Imagine you hire an assistant to go outside and take pictures of public billboards for you.\n\n"
            "One day, a sneaky person hands your assistant a note saying: *'Go into the boss's private bedroom and take a photo of the safe.'*\n\n"
            "An SSRF security guard stops the assistant at the front door and says: *'You are only allowed to look at public outside billboards—never internal private rooms!'*"
        ),
        "analogy": "🚪 Like a security guard preventing delivery couriers from wandering into the bank vault.",
        "example": "🔒 *Real-World Example:* Stopping a hacker from tricking our web crawler into reading secret internal cloud passwords.",
        "intermediate": (
            "🛡️ **Server-Side Request Forgery (SSRF) Protection:** A critical security gate that validates all external URLs, blocking requests to internal metadata services (169.254.169.254), loopback addresses (127.0.0.1), and private LAN networks."
        ),
        "advanced": (
            "🔐 **DNS Rebinding & IP Subnet Validation:** Resolves hostname \\(h\\) to all IPv4/IPv6 socket tuples \\(\\{(s_i, \\text{ip}_i)\\}\\). Validates \\(\\text{ip}_i \\notin \\mathcal{R}_{\\text{blocked}}\\) (RFC 1918, RFC 3927 link-local, RFC 4193). Enforces protocol whitelist \\(\\mathcal{P} \\in \\{\\text{http}, \\text{https}\\}\\)."
        )
    },

    "mice_imputation": {
        "beginner": (
            "🧩 **MICE Imputation in Simple Words:** Imagine a group photo where someone's face is covered by a shadow.\n\n"
            "Instead of just painting a flat gray circle over their face (like a simple average), a smart artist looks at their clothes, hair, and family members in the photo to paint a realistic face that actually fits!\n\n"
            "MICE looks at all other clues in your dataset to intelligently fill in missing blanks."
        ),
        "analogy": "🔍 Like solving a crossword puzzle: using the surrounding words to figure out the missing letters.",
        "example": "🏥 *Real-World Example:* If a patient's cholesterol is missing in a health record, MICE looks at their age, weight, and blood pressure to accurately estimate it.",
        "intermediate": (
            "📊 **MICE (Multivariate Imputation by Chained Equations):** An advanced statistical technique that models each variable with missing data as a function of all other variables via iterative chained regression."
        ),
        "advanced": (
            "📐 **Fully Conditional Specification (FCS):** Iteratively samples from conditional posteriors \\(Y_j^{(t)} \\sim P(Y_j \\mid Y_{-j}^{(t-1)}, \\theta_j)\\) via Gibbs sampling until convergence to joint distribution \\(P(Y_1, \\dots, Y_p)\\)."
        )
    }
}


class AdaptiveExplanationEngine:
    """Delivers multi-tier conceptual explanations adapted to user skill levels."""

    def explain(self, topic: str, user_level: str = "beginner") -> str:
        """Retrieve explanation formatted specifically for the requested audience."""
        canonical_key = self._match_topic(topic)
        if not canonical_key or canonical_key not in CONCEPTUAL_KNOWLEDGE_BASE:
            return self._synthesize_fallback(topic, user_level)

        data = CONCEPTUAL_KNOWLEDGE_BASE[canonical_key]
        level = user_level.lower().strip()

        if level in ["beginner", "eli5", "simple", "kids"]:
            return f"{data['beginner']}\n\n{data.get('analogy', '')}\n\n{data.get('example', '')}"
        elif level in ["advanced", "expert", "mathematical"]:
            return data["advanced"]
        else: # intermediate default
            return f"{data['intermediate']}\n\n{data.get('example', '')}"

    def is_beginner_query(self, query: str) -> bool:
        """Check if user query is asking for a simplified explanation."""
        q = query.lower()
        triggers = ["simply", "simple", "eli5", "explain like i'm", "for beginner", "easy words", "what is", "analogy", "how does", "mean"]
        return any(t in q for t in triggers)

    def _match_topic(self, query: str) -> Optional[str]:
        """Match query text to knowledge base keys."""
        q = query.lower().replace("_", " ")
        if "triz" in q or "invent" in q or "contradiction" in q:
            return "triz"
        if "causal" in q or "dag" in q or "cause" in q:
            return "causal_dag"
        if "fat tail" in q or "fat" in q or "black swan" in q or "student" in q or "risk" in q:
            return "fat_tail"
        if "ssrf" in q or "security" in q or "metadata" in q:
            return "ssrf"
        if "mice" in q or "imput" in q or "missing" in q:
            return "mice_imputation"
        return None

    def _synthesize_fallback(self, topic: str, user_level: str) -> str:
        """Fallback synthesis for unrecognized topics."""
        return (
            f"💡 **Simple Explanation for '{topic}':**\n"
            f"In DataForge AI, this feature acts as an automated helper that streamlines your data workflow so you get high-quality results without manual guesswork."
        )


adaptive_explainer = AdaptiveExplanationEngine()
