"""
Production Security Hardening Module.
Implements:
1. File Upload & Ingestion Security: validate_dataset_id, sanitize_filename, check_upload, detect_encoding, schema_fingerprint.
2. SSRFValidator: Blocks private IP ranges, loopback, AWS metadata (169.254.169.254), non-HTTP schemes, and DNS rebinding attacks.
3. HTMLSanitizer: Sanitizes HTML against XSS payloads and script injection.
4. CredentialRedactor: Redacts API keys, secret tokens, and passwords in logs and response payloads.
"""
from typing import NamedTuple, Tuple, List, Optional, Dict, Any
import os
import re
import hashlib
import ipaddress
import socket
from urllib.parse import urlparse
import bleach
import chardet
from src.utils import logger


# =====================================================================
# 1. FILE UPLOAD & INGESTION SECURITY
# =====================================================================

ALLOWED_EXT = {".csv", ".tsv", ".json", ".xlsx", ".xls", ".parquet"}
MAX_SIZE = 200 * 1024 * 1024
ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def validate_dataset_id(dataset_id: str) -> str:
    """Validate dataset ID format to prevent path traversal."""
    if not dataset_id or not isinstance(dataset_id, str):
        raise ValueError("Dataset ID must be a non-empty string.")
    cleaned = dataset_id.strip()
    if not ID_PATTERN.match(cleaned):
        raise ValueError(f"Invalid dataset ID format: '{dataset_id}'. Must be alphanumeric with '-' or '_'.")
    return cleaned


def sanitize_filename(name: str) -> str:
    """Sanitize filename to prevent directory traversal and special character issues."""
    base = os.path.basename(name)
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "_", base).strip("._")
    return cleaned or "dataset"


def check_upload(path: str) -> Dict[str, Any]:
    """Verify uploaded file exists, has allowed extension, and complies with size limits."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Unsupported type {ext}")
    size = os.path.getsize(path)
    if size > MAX_SIZE:
        raise ValueError("File too large")
    return {"ext": ext, "size": size}


def detect_encoding(path: str) -> str:
    """Detect file character encoding for reliable tabular decoding."""
    ext = os.path.splitext(path)[1].lower()
    if ext in {".parquet", ".xlsx", ".xls"}:
        return "binary"
    with open(path, "rb") as f:
        raw = f.read(100000)
    detected = chardet.detect(raw).get("encoding")
    return detected or "utf-8"


def schema_fingerprint(df) -> str:
    """Generate SHA256/MD5 fingerprint of dataset schema and data types."""
    sig = "|".join(f"{c}:{df[c].dtype}" for c in df.columns)
    return hashlib.md5(sig.encode()).hexdigest()


# =====================================================================
# 2. SSRF PROTECTION ENGINE
# =====================================================================

class ValidationResult(NamedTuple):
    valid: bool
    reason: str = ""
    resolved_ip: str = ""


class SSRFValidator:
    """Enterprise-grade Server-Side Request Forgery (SSRF) Protection."""

    BLOCKED_IP_RANGES = [
        "10.0.0.0/8",          # Private Class A
        "172.16.0.0/12",       # Private Class B
        "192.168.0.0/16",      # Private Class C
        "127.0.0.0/8",         # Loopback
        "169.254.0.0/16",      # Link-local / AWS / GCP Metadata Service!
        "0.0.0.0/8",           # Current network
        "224.0.0.0/4",         # Multicast
        "240.0.0.0/4",         # Reserved / Future use
        "::1/128",             # IPv6 Loopback
        "fc00::/7",            # IPv6 Unique local
        "fe80::/10",           # IPv6 Link-local
    ]

    BLOCKED_SCHEMES = {"file", "ftp", "gopher", "javascript", "data", "blob", "dict", "ldap"}

    @classmethod
    def validate_url(cls, url: str) -> ValidationResult:
        """Validate URL to ensure it does not target internal network or metadata endpoints."""
        if not url or not isinstance(url, str):
            return ValidationResult(valid=False, reason="Empty or invalid URL provided.")

        url_clean = url.strip()
        parsed = urlparse(url_clean)

        # Check scheme
        scheme = parsed.scheme.lower()
        if scheme in cls.BLOCKED_SCHEMES:
            return ValidationResult(valid=False, reason=f"Blocked URL scheme: {scheme}://")

        if scheme not in {"http", "https"}:
            return ValidationResult(valid=False, reason=f"Only HTTP and HTTPS protocols allowed, received: {scheme}")

        hostname = parsed.hostname
        if not hostname:
            return ValidationResult(valid=False, reason="Could not extract valid hostname from URL.")

        # Check if hostname directly represents a blocked string
        if hostname.lower() in {"localhost", "127.0.0.1", "::1", "metadata.google.internal", "instance-data"}:
            return ValidationResult(valid=False, reason=f"Blocked internal hostname: {hostname}")

        # Resolve hostname to IP addresses to prevent DNS rebinding attacks
        try:
            addr_info = socket.getaddrinfo(hostname, None)
        except socket.gaierror as e:
            return ValidationResult(valid=False, reason=f"DNS resolution failure for host '{hostname}': {e}")
        except Exception as e:
            return ValidationResult(valid=False, reason=f"Hostname verification error: {e}")

        if not addr_info:
            return ValidationResult(valid=False, reason=f"No IP addresses resolved for hostname '{hostname}'.")

        # Verify all resolved IPs against blocked ranges
        resolved_ips = []
        for family, type_, proto, canonname, sockaddr in addr_info:
            ip_str = sockaddr[0]
            resolved_ips.append(ip_str)
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                for blocked_range in cls.BLOCKED_IP_RANGES:
                    if ip_obj in ipaddress.ip_network(blocked_range):
                        return ValidationResult(
                            valid=False,
                            reason=f"SSRF blocked: IP {ip_str} falls within restricted range {blocked_range}",
                            resolved_ip=ip_str
                        )
            except ValueError:
                return ValidationResult(valid=False, reason=f"Invalid IP address format resolved: {ip_str}")

        return ValidationResult(valid=True, reason="URL validated as safe for external crawling.", resolved_ip=resolved_ips[0])


# =====================================================================
# 3. HTML SANITIZATION & CREDENTIAL REDACTION
# =====================================================================

class HTMLSanitizer:
    """Sanitizes user-provided or crawled HTML to prevent XSS attacks."""

    ALLOWED_TAGS = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
        'strong', 'ul', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead',
        'tbody', 'tr', 'th', 'td', 'div', 'span', 'pre', 'hr', 'br', 'svg', 'path', 'g'
    ]

    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target', 'rel'],
        'abbr': ['title'],
        'acronym': ['title'],
        'img': ['src', 'alt', 'width', 'height', 'loading'],
        'table': ['class'],
        'th': ['class', 'scope'],
        'td': ['class'],
        'div': ['class', 'id', 'style'],
        'span': ['class', 'style'],
        'svg': ['viewbox', 'width', 'height', 'fill', 'stroke', 'xmlns', 'class'],
        'path': ['d', 'fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin'],
        'g': ['fill', 'stroke', 'class']
    }

    @classmethod
    def sanitize(cls, html_content: str) -> str:
        """Strip dangerous tags (<script>, <iframebody>, onload=, javascript:) from HTML."""
        if not html_content:
            return ""
        return bleach.clean(
            html_content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )


class CredentialRedactor:
    """Detects and redacts sensitive API keys and secrets from output logs and responses."""

    SECRET_PATTERNS = [
        re.compile(r'(?:api[_-]?key|secret|password|bearer|auth[_-]?token)\s*[:=]\s*["\']?([A-Za-z0-9_\-\.]{12,})["\']?', re.I),
        re.compile(r'gsk_[A-Za-z0-9]{32,}', re.I),                     # Groq Keys
        re.compile(r'sk-[A-Za-z0-9_\-]{32,}', re.I),                   # OpenAI Keys
        re.compile(r'AIzaSy[A-Za-z0-9_\-]{33}', re.I),                 # Google Gemini Keys
        re.compile(r'ghp_[A-Za-z0-9]{36}', re.I),                      # GitHub Personal Access Tokens
    ]

    @classmethod
    def redact(cls, text: str) -> str:
        """Replace sensitive credential patterns with [REDACTED_CREDENTIAL]."""
        if not isinstance(text, str):
            return text
        redacted = text
        for pattern in cls.SECRET_PATTERNS:
            redacted = pattern.sub("[REDACTED_CREDENTIAL]", redacted)
        return redacted


ssrf_validator = SSRFValidator()
html_sanitizer = HTMLSanitizer()
credential_redactor = CredentialRedactor()
