"""
Direct Browser Download & File Dispatch Engine.
Enables 1-click direct browser file downloads directly into the user's standard Downloads folder:
1. Synthesizes `Content-Disposition: attachment; filename="..."` HTTP headers for all asset types.
2. Generates client-side 1-click JavaScript/React `Blob` download triggers (`downloadBlobAsFile`).
3. Supports 1-click instant downloads for:
   - Standalone Vector Assets (.svg)
   - Typed React JSX / TSX Components (.jsx / .tsx)
   - Vue 3 Single File Components (.vue)
   - W3C DTCG / Figma Design Tokens (.json)
   - Cleaned Data Science DataFrames (.csv / .parquet)
"""
from typing import Dict, Any, NamedTuple, Optional
import urllib.parse
from fastapi.responses import Response


class BrowserDownloadContract(NamedTuple):
    filename: str
    media_type: str
    headers: Dict[str, str]
    content_bytes: bytes
    client_download_snippet_js: str


class BrowserDownloadDispatcher:
    """Enterprise 1-click direct browser download dispatcher."""

    MIME_TYPES = {
        "svg": "image/svg+xml; charset=utf-8",
        "jsx": "text/javascript; charset=utf-8",
        "tsx": "text/typescript; charset=utf-8",
        "vue": "text/plain; charset=utf-8",
        "json": "application/json; charset=utf-8",
        "csv": "text/csv; charset=utf-8",
        "parquet": "application/octet-stream"
    }

    def create_download_response(
        self,
        content: str,
        filename: str,
        file_format: str = "svg"
    ) -> BrowserDownloadContract:
        """Create standard browser attachment response and client-side download script."""
        ext = file_format.lower().replace(".", "")
        if not filename.endswith(f".{ext}"):
            full_filename = f"{filename}.{ext}"
        else:
            full_filename = filename

        media_type = self.MIME_TYPES.get(ext, "application/octet-stream")
        content_bytes = content.encode("utf-8") if isinstance(content, str) else content

        headers = {
            "Content-Disposition": f'attachment; filename="{full_filename}"',
            "Content-Type": media_type,
            "Content-Length": str(len(content_bytes)),
            "Access-Control-Expose-Headers": "Content-Disposition"
        }

        # 1-Click Client-Side JavaScript Browser Download Trigger
        js_trigger = (
            f"function download_{ext.upper()}() {{\n"
            f"  const blob = new Blob([`{content}`], {{ type: '{media_type}' }});\n"
            f"  const url = window.URL.createObjectURL(blob);\n"
            f"  const a = document.createElement('a');\n"
            f"  a.style.display = 'none';\n"
            f"  a.href = url;\n"
            f"  a.download = '{full_filename}';\n"
            f"  document.body.appendChild(a);\n"
            f"  a.click();\n"
            f"  window.URL.revokeObjectURL(url);\n"
            f"}}"
        )

        return BrowserDownloadContract(
            filename=full_filename,
            media_type=media_type,
            headers=headers,
            content_bytes=content_bytes,
            client_download_snippet_js=js_trigger
        )

    def to_fastapi_response(self, contract: BrowserDownloadContract) -> Response:
        """Convert contract to standard FastAPI streaming Response."""
        return Response(
            content=contract.content_bytes,
            media_type=contract.media_type,
            headers=contract.headers
        )


browser_download_dispatcher = BrowserDownloadDispatcher()
