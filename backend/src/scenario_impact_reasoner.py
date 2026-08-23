"""
Scenario-Specific Impact & Practical Business Value Reasoner.
Explains exactly how DataForge AI features help in specific real-world industry scenarios.
Answers inquiries of the form:
"How will [Feature] be helpful for [Scenario/Industry]?"
e.g.
- "How will Causal DAGs help my e-commerce checkout churn?"
- "How does TRIZ help high-frequency trading bot latency?"
- "How does SSRF security protect a healthcare patient portal?"
- "How do Fat-Tail distributions help a SaaS startup forecast runway?"
"""
from typing import Dict, Any, Optional, NamedTuple
import re
from src.utils import logger


class ScenarioBreakdown(NamedTuple):
    feature_name: str
    scenario_name: str
    direct_benefit: str
    concrete_example: str
    avoided_mistake: str
    target_route: str
    target_label: str
    formatted_response: str


class ScenarioImpactReasoner:
    """Explains feature utility across diverse industrial and business contexts."""

    FEATURE_PATTERNS = {
        "causal_dag": ["causal", "dag", "cause", "causation", "driver", "churn"],
        "triz": ["triz", "contradiction", "invention", "tradeoff", "trade-off", "speed vs", "battery"],
        "fat_tail": ["fat tail", "black swan", "student-t", "pareto", "risk", "runway", "crash", "forecast"],
        "ssrf": ["ssrf", "security", "firewall", "metadata", "hack", "safe", "privacy"],
        "mice_imputation": ["mice", "imputation", "missing data", "nulls", "blanks", "clean"],
        "seo_audit": ["seo", "web vitals", "lighthouse", "search ranking", "google"],
        "svg_studio": ["svg", "icon", "vector", "design token", "figma", "react component"],
        "lead_scraper": ["scraper", "lead", "email", "b2b", "outreach", "prospect"]
    }

    def can_reason_scenario(self, query: str) -> bool:
        """Check if query is asking how a feature applies to a specific scenario."""
        q = query.lower()
        triggers = [
            "how will", "how would", "how does", "how is", "why is",
            "helpful for", "useful for", "apply to", "benefit", "use case for",
            "help with", "in the scenario", "for a scenario", "in case of"
        ]
        return any(t in q for t in triggers)

    def analyze_scenario_impact(self, query: str) -> Optional[ScenarioBreakdown]:
        """Synthesize a concrete scenario value breakdown with actionable redirection."""
        q = query.lower()
        feature_key = self._detect_feature(q)
        if not feature_key:
            return None

        scenario_topic = self._extract_scenario_topic(q)

        if feature_key == "causal_dag":
            return ScenarioBreakdown(
                feature_name="Causal Directed Acyclic Graph (DAG)",
                scenario_name=scenario_topic,
                direct_benefit=f"In **{scenario_topic}**, Causal DAGs separate real revenue drivers from misleading coincidences.",
                concrete_example="🛒 *Concrete Example:* If customers abandon checkouts on mobile, a correlation might blame the 'Sign Up' page. The Causal DAG isolates that a 1.2s delay in the payment payment gateway was the true root cause.",
                avoided_mistake="❌ *Avoided Mistake:* Wasting $50,000 redesigning checkout buttons when the real culprit was API network latency.",
                target_route="/eda",
                target_label="Open Causal EDA Studio",
                formatted_response=self._format_markdown(
                    "Causal DAG", scenario_topic,
                    f"In **{scenario_topic}**, Causal DAGs act like a forensic detective. Instead of assuming two things happening together are related (like summer heat and ice cream), it draws mathematical arrows to prove what *actually causes* your outcome.",
                    "🛒 *Concrete Walkthrough:* By controlling for hidden confounders (like user device type and browser speed), it isolates the single biggest lever to improve retention and revenue.",
                    "❌ *Common Pitfall Prevented:* Spending months fixing things that look correlated but have zero actual impact on business growth.",
                    "/eda", "Open Causal EDA Studio"
                )
            )

        elif feature_key == "triz":
            return ScenarioBreakdown(
                feature_name="TRIZ Contradiction Studio",
                scenario_name=scenario_topic,
                direct_benefit=f"In **{scenario_topic}**, TRIZ resolves conflicting technical requirements without compromise.",
                concrete_example="⚡ *Concrete Example:* When scaling a system where you need **Extreme Speed** (throughput) but cannot sacrifice **Data Consistency** or **RAM Cost**, TRIZ applies Principle #1 (Segmentation/MoE) to decouple memory load from latency.",
                avoided_mistake="❌ *Avoided Mistake:* Buying 10x more expensive server instances instead of applying a zero-cost architectural transformation.",
                target_route="/niche",
                target_label="Open Strategic Invention Studio",
                formatted_response=self._format_markdown(
                    "TRIZ Contradiction Studio", scenario_topic,
                    f"In **{scenario_topic}**, you often hit engineering walls where improving one thing (like speed) makes another thing worse (like memory cost). TRIZ gives you 40 proven architectural transformations to break through that wall.",
                    "⚡ *Concrete Walkthrough:* In modern AI/Cloud architectures, TRIZ replaces brute-force server scaling with smart algorithmic innovations (like Mixture-of-Experts or Speculative Decoding).",
                    "❌ *Common Pitfall Prevented:* Accepting suboptimal compromises that hurt product performance and balloon operational costs.",
                    "/niche", "Open Strategic Invention Studio"
                )
            )

        elif feature_key == "fat_tail":
            return ScenarioBreakdown(
                feature_name="Fat-Tail & Heavy-Tailed Risk Modeling",
                scenario_name=scenario_topic,
                direct_benefit=f"In **{scenario_topic}**, Fat-Tail modeling protects you against sudden black-swan events and viral spikes.",
                concrete_example="📈 *Concrete Example:* Traditional models assume standard bell curves where extreme crashes or 100x traffic surges have 0.001% probability. Fat-tail Student-t ($df=3$) modeling accurately prices extreme stress so you never run out of cash or crash servers.",
                avoided_mistake="❌ *Avoided Mistake:* Underestimating capital requirements and going bankrupt during an unexpected market downturn.",
                target_route="/niche",
                target_label="Open Scenario Planner",
                formatted_response=self._format_markdown(
                    "Fat-Tail Risk Modeling", scenario_topic,
                    f"In **{scenario_topic}**, extreme events happen far more frequently than normal math predicts (the 'Bill Gates walks into the bar' effect). Fat-tail distributions prepare your business for real-world volatility.",
                    "📈 *Concrete Walkthrough:* Computes Value at Risk (VaR 95%) and Expected Shortfall so your runway and infrastructure remain bulletproof.",
                    "❌ *Common Pitfall Prevented:* Basing business survival on naive averages that fail during the first market shock.",
                    "/niche", "Open Scenario Planner"
                )
            )

        elif feature_key == "ssrf":
            return ScenarioBreakdown(
                feature_name="Enterprise SSRF Security Shield",
                scenario_name=scenario_topic,
                direct_benefit=f"In **{scenario_topic}**, SSRF protection prevents attackers from hijacking your web crawlers to steal internal cloud credentials.",
                concrete_example="🔒 *Concrete Example:* If a crawler is asked to fetch user links, a malicious actor might submit `http://169.254.169.254/latest/meta-data/` to steal AWS IAM tokens. DataForge AI's multi-IP pre-connection filter drops the request before DNS rebinding can occur.",
                avoided_mistake="❌ *Avoided Mistake:* Catastrophic cloud infrastructure breaches and regulatory fines.",
                target_route="/intel",
                target_label="Open Web Intelligence Studio",
                formatted_response=self._format_markdown(
                    "SSRF Security Shield", scenario_topic,
                    f"In **{scenario_topic}**, external data ingestion is a massive attack vector. DataForge AI enforces a pre-flight socket validator that blocks requests to private LANs, AWS metadata servers, and loopback ports.",
                    "🔒 *Concrete Walkthrough:* Validates every URL against RFC 1918 subnets and resolves multi-A records to guarantee zero internal network leakage.",
                    "❌ *Common Pitfall Prevented:* Leaking private database records or cloud secrets to untrusted external websites.",
                    "/intel", "Open Web Intelligence Studio"
                )
            )

        elif feature_key == "mice_imputation":
            return ScenarioBreakdown(
                feature_name="MICE Multivariate Imputation",
                scenario_name=scenario_topic,
                direct_benefit=f"In **{scenario_topic}**, MICE fills missing data values using relationships across all other columns.",
                concrete_example="🏥 *Concrete Example:* If patient diagnostic tables have missing blood pressure records, MICE uses age, weight, and heart rate to mathematically reconstruct the missing value without introducing statistical bias.",
                avoided_mistake="❌ *Avoided Mistake:* Throwing away 40% of valuable dataset rows or using naive flat averages.",
                target_route="/clean",
                target_label="Open Cleaning Studio",
                formatted_response=self._format_markdown(
                    "MICE Imputation", scenario_topic,
                    f"In **{scenario_topic}**, missing data is unavoidable. Instead of throwing away rows or filling with simple averages (which distorts standard deviations), MICE models missing values via chained Bayesian regression.",
                    "🏥 *Concrete Walkthrough:* Preserves dataset sample size and covariance structure so downstream machine learning models achieve maximum accuracy.",
                    "❌ *Common Pitfall Prevented:* Skewing predictions and losing valuable edge-case data points.",
                    "/clean", "Open Cleaning Studio"
                )
            )

        return None

    def _detect_feature(self, text: str) -> Optional[str]:
        for feat, kws in self.FEATURE_PATTERNS.items():
            if any(kw in text for kw in kws):
                return feat
        return "causal_dag" # Default fallback

    def _extract_scenario_topic(self, query: str) -> str:
        q = query.lower()
        # Look for "for [scenario]" or "in [scenario]"
        match = re.search(r'(?:for|in|with|regarding)\s+(?:a\s+|an\s+|the\s+)?([a-zA-Z0-9\s\-]+?)(?:\?|$|\.|\,)', q)
        if match:
            topic = match.group(1).strip()
            if len(topic) > 3 and topic not in {"it", "this", "that", "me", "us", "you"}:
                return topic.title()
        return "Your Real-World Business Scenario"

    def _format_markdown(self, feat_name: str, scenario: str, benefit: str, example: str, pitfall: str, route: str, label: str) -> str:
        return (
            f"🎯 **How {feat_name} Solves Challenges in {scenario}:**\n\n"
            f"### 1. Direct Business & Technical Impact\n"
            f"{benefit}\n\n"
            f"### 2. Real-World Walkthrough\n"
            f"{example}\n\n"
            f"### 3. Critical Failure Avoided\n"
            f"{pitfall}\n\n"
            f"👉 **Next Step:** Click the button below to launch the workspace for this feature!"
        )


scenario_reasoner = ScenarioImpactReasoner()
