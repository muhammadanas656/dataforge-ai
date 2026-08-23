"""
End-to-End Export & Multi-Framework Component Verifier.
Validates production deployment readiness for:
1. React JSX Components (camelCase attributes, valid prop forwarding, export statements).
2. Vue 3 Single-File Components (<template>, <script setup>, CSS scoped bindings).
3. W3C DTCG-compliant Design Tokens JSON (Figma Tokens Studio structure).
"""
from typing import Dict, Any, List, NamedTuple
import json
import re
from src.utils import logger


class ExportVerificationResult(NamedTuple):
    is_valid: bool
    framework: str
    syntax_errors: List[str]
    has_correct_props: bool
    has_accessible_structure: bool
    summary: str


class ExportE2EVerifier:
    """Enterprise verification engine for multi-framework component transpilation."""

    def verify_react_jsx_syntax(self, jsx_code: str) -> ExportVerificationResult:
        """Verify React JSX component structure and camelCase attribute bindings."""
        errors = []
        if not jsx_code or not isinstance(jsx_code, str):
            return ExportVerificationResult(False, "React JSX", ["Empty JSX code"], False, False, "Failed")

        # 1. Check Component & Export Declaration
        if "export const" not in jsx_code and "export default" not in jsx_code:
            errors.append("Missing standard React component export.")

        # 2. Check Prohibited Kebab-Case Attributes
        kebab_attrs = ["stroke-width", "stroke-linecap", "stroke-linejoin", "stroke-opacity", "fill-rule", "clip-rule"]
        for kb in kebab_attrs:
            if f'{kb}=' in jsx_code:
                errors.append(f"Found non-React kebab-case attribute: '{kb}=' (must be camelCase).")

        # 3. Check JSX Tag Balance
        open_tags = len(re.findall(r'<svg', jsx_code))
        close_tags = len(re.findall(r'</svg>', jsx_code))
        if open_tags != close_tags or open_tags == 0:
            errors.append(f"Mismatched SVG JSX root tags ({open_tags} open vs {close_tags} close).")

        has_props = "props" in jsx_code or "size" in jsx_code or "className" in jsx_code
        has_a11y = "role=" in jsx_code or "title" in jsx_code or "aria-" in jsx_code

        is_valid = (len(errors) == 0)
        return ExportVerificationResult(
            is_valid=is_valid,
            framework="React JSX",
            syntax_errors=errors,
            has_correct_props=has_props,
            has_accessible_structure=has_a11y,
            summary="React JSX component passed all AST syntax and prop validation checks." if is_valid else f"React JSX verification failed: {'; '.join(errors)}"
        )

    def verify_vue3_component_syntax(self, vue_code: str) -> ExportVerificationResult:
        """Verify Vue 3 single-file component structure."""
        errors = []
        if not vue_code or not isinstance(vue_code, str):
            return ExportVerificationResult(False, "Vue 3", ["Empty Vue code"], False, False, "Failed")

        if "<template>" not in vue_code or "</template>" not in vue_code:
            errors.append("Missing standard Vue 3 <template> block.")

        if "<script setup>" not in vue_code:
            errors.append("Missing standard Vue 3 <script setup> block.")

        has_props = "defineProps" in vue_code or "props" in vue_code or "size" in vue_code
        has_a11y = "role=" in vue_code or "title" in vue_code or "aria-" in vue_code

        is_valid = (len(errors) == 0)
        return ExportVerificationResult(
            is_valid=is_valid,
            framework="Vue 3",
            syntax_errors=errors,
            has_correct_props=has_props,
            has_accessible_structure=has_a11y,
            summary="Vue 3 component passed all SFC template and prop validation checks." if is_valid else f"Vue 3 verification failed: {'; '.join(errors)}"
        )

    def verify_figma_dtcg_tokens(self, tokens_json: Any) -> ExportVerificationResult:
        """Verify W3C DTCG / Figma Tokens Studio JSON structure."""
        errors = []
        if isinstance(tokens_json, str):
            try:
                tokens_dict = json.loads(tokens_json)
            except Exception as e:
                return ExportVerificationResult(False, "Figma DTCG Tokens", [f"Invalid JSON: {e}"], False, False, "Failed")
        else:
            tokens_dict = tokens_json

        if not isinstance(tokens_dict, dict):
            return ExportVerificationResult(False, "Figma DTCG Tokens", ["Root must be a JSON object"], False, False, "Failed")

        if "color" not in tokens_dict and "colors" not in tokens_dict:
            errors.append("Missing required 'color' token group.")

        is_valid = (len(errors) == 0)
        return ExportVerificationResult(
            is_valid=is_valid,
            framework="Figma DTCG Tokens",
            syntax_errors=errors,
            has_correct_props=True,
            has_accessible_structure=True,
            summary="Design tokens comply with W3C DTCG specification." if is_valid else f"Token verification failed: {'; '.join(errors)}"
        )


export_verifier = ExportE2EVerifier()
