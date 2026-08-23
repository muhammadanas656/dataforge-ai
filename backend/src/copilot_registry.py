"""Central metadata and validation for Copilot capabilities.

The registry is deliberately small and dependency-light.  Operational code stays
in the existing domain modules; this layer defines what the Copilot may expose,
what is safe to preview, and which arguments are required.
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    category: str
    mutating: bool = False
    impact: str = "low"
    required_args: tuple = ()
    supports_dry_run: bool = False

    def to_dict(self):
        data = asdict(self)
        data["required_args"] = list(self.required_args)
        return data


TOOL_SPECS: Dict[str, ToolSpec] = {
    "get_current_context": ToolSpec(
        "get_current_context", "Read the current workspace, page, dataset, and recent activity.", "context"
    ),
    "get_token_usage": ToolSpec(
        "get_token_usage", "Read cumulative token usage and cost by scope.", "observability"
    ),
    "get_dataset_profile": ToolSpec(
        "get_dataset_profile", "Read the active dataset profile and quality execution summary.", "dataset", required_args=("dataset_id",)
    ),
    "get_learning_stats": ToolSpec(
        "get_learning_stats", "Read distilled models, learned fixes, and knowledge graph statistics.", "learning"
    ),
    "run_autopilot": ToolSpec(
        "run_autopilot", "Run the governed Auto-Pilot cleaning and analysis pipeline.", "dataset", True, "high", ("dataset_id",), True
    ),
    "extract_niche_leads": ToolSpec(
        "extract_niche_leads", "Extract niche leads and register the resulting dataset.", "research", True, "high", ("niche",), True
    ),
    "export_pipeline_code": ToolSpec(
        "export_pipeline_code", "Generate standalone pipeline code for a dataset.", "export", True, "medium", ("dataset_id",), True
    ),
    "resolve_triz": ToolSpec(
        "resolve_triz", "Resolve an engineering contradiction with TRIZ.", "research", False, "low", (), False
    ),
    "run_seo_audit": ToolSpec(
        "run_seo_audit", "Run a 360-degree technical and content SEO audit on a public website or URL.", "web", False, "low", (), True
    ),
    "extract_design_tokens": ToolSpec(
        "extract_design_tokens", "Extract WCAG-compliant color palettes and Figma/Tailwind design tokens from a website.", "web", False, "low", (), True
    ),
    "run_deep_web_audit": ToolSpec(
        "run_deep_web_audit", "Unified multi-vector deep audit: SEO, Design Tokens, and Lead Harvesting.", "web", True, "medium", (), True
    ),
    "audit_svg": ToolSpec(
        "audit_svg", "Audit SVG vector markup for security risks, accessibility, and path efficiency.", "design", False, "low", (), True
    ),
    "generate_svg_asset": ToolSpec(
        "generate_svg_asset", "Generate custom vector SVG icons with React and Vue component code.", "design", False, "low", (), True
    ),
    "execute_studio_workflow": ToolSpec(
        "execute_studio_workflow", "Execute chained multi-studio workflows across tabular, web, and invention studios.", "workflows", True, "high", (), True
    )
}


def get_tool_spec(tool_name: str) -> ToolSpec:
    if tool_name not in TOOL_SPECS:
        raise ValueError(f"Unknown Copilot tool: {tool_name}")
    return TOOL_SPECS[tool_name]


def list_tool_specs() -> List[Dict[str, Any]]:
    return [spec.to_dict() for spec in TOOL_SPECS.values()]


def validate_args(tool_name: str, args: Dict[str, Any]) -> None:
    spec = get_tool_spec(tool_name)
    args = args or {}
    missing = [key for key in spec.required_args if not str(args.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Missing required argument(s): {', '.join(missing)}")


def dry_run(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Return a non-mutating preview for a registered capability."""
    validate_args(tool_name, args)
    spec = get_tool_spec(tool_name)
    return {
        "status": "dry_run",
        "tool": spec.name,
        "summary": spec.description,
        "category": spec.category,
        "impact": spec.impact,
        "mutating": spec.mutating,
        "affected_resources": [args.get(key) for key in spec.required_args],
        "warnings": ["This operation changes application or dataset state."] if spec.mutating else [],
        "requires_confirmation": spec.mutating and spec.impact in ("medium", "high")
    }
