"""Chenji Affect MCP Server.

Text -> 8-dimensional affect vector, emotion texture, causal intent,
and 3D avatar driving parameters, exposed as MCP tools.

Env vars:
    CHENJI_API_KEY   required, your Chenji API key (x-api-key)
    CHENJI_API_BASE  optional, default https://taichusjs.cn
"""
import json
import os
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP

API_BASE = os.environ.get("CHENJI_API_BASE", "https://taichusjs.cn").rstrip("/")
API_KEY = os.environ.get("CHENJI_API_KEY", "")

mcp = FastMCP(
    "chenji-affect",
    instructions=(
        "Chenji Affect tools convert natural-language text into structured affect "
        "signals: an 8-dimensional emotion vector, emotion texture labels, causal "
        "intent, and optional 3D avatar driving parameters. Requires CHENJI_API_KEY."
    ),
)


def _post(path: str, payload: dict) -> str:
    if not API_KEY:
        return json.dumps({"error": "CHENJI_API_KEY is not set"})
    req = urllib.request.Request(
        API_BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-api-key": API_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.dumps(json.loads(r.read()), ensure_ascii=False, indent=2)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return json.dumps({"error": f"HTTP {e.code}", "detail": body}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def analyze_text(text: str, lang: str = "") -> str:
    """L1 Affect Extraction: analyze text into an 8-dimensional emotion vector,
    emotion texture labels, causal intent classification, and a natural-language
    state description. text: input up to 2000 chars. lang: optional 'zh' or 'en'."""
    inp = {"text": text}
    if lang:
        inp["lang"] = lang
    return _post("/v1/chenji/analyze", {"input": inp})


@mcp.tool()
def generate_avatar_params(text: str) -> str:
    """L2 Avatar Driving Pipeline: one call returns blendshape/AU/curve animation
    parameters, lighting & material atmosphere package, adapter payload, plus the
    upstream L1 affect analysis. Requires a key tier that includes L2."""
    return _post("/v1/chenji/generate3d", {"input": {"text": text}})


if __name__ == "__main__":
    mcp.run()
