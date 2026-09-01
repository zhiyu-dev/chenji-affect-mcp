# -*- coding: utf-8 -*-
"""
沉基远程 MCP 服务 (Streamable HTTP)
端口: 8102 | 由 nginx /mcp 反代公网
链路: 客户端带 x-api-key 头 -> 本服务透传网关 127.0.0.1:8101 -> 引擎 8100
纪律: 原文不落盘, 只透传; 计费/限额全部复用网关既有逻辑
启动: python mcp_http.py
"""
import json
import os
import urllib.error
import urllib.request
from contextvars import ContextVar

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware

GATEWAY = os.environ.get("CHENJI_GATEWAY", "http://127.0.0.1:8101").rstrip("/")
API_KEY = ContextVar("chenji_api_key", default="")

mcp = FastMCP(
    "chenji-affect",
    # mcp 1.29 默认开启 DNS rebinding 防护: nginx 透传公网 Host, 须列入白名单, 否则 421
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["taichusjs.cn", "www.taichusjs.cn", "127.0.0.1:*", "localhost:*"],
        allowed_origins=["https://taichusjs.cn", "https://www.taichusjs.cn"],
    ),
    instructions=(
        "Chenji Affect tools convert natural-language text into structured affect "
        "signals: an 8-dimensional emotion vector, emotion texture labels, causal "
        "intent, optional 3D avatar driving parameters, plus empathy response "
        "strategies and somatic-sensation-to-emotion decoding. "
        "Calls are billed by the Chenji API key supplied via the x-api-key header."
    ),
)


class KeyMiddleware(BaseHTTPMiddleware):
    """每个 HTTP 请求把 x-api-key 放入 contextvar, 供工具调用时透传"""
    async def dispatch(self, request, call_next):
        token = API_KEY.set(request.headers.get("x-api-key", "").strip())
        try:
            return await call_next(request)
        finally:
            API_KEY.reset(token)


def _post(path: str, payload: dict) -> str:
    key = API_KEY.get()
    if not key:
        return json.dumps({"error": "missing x-api-key header"})
    req = urllib.request.Request(
        GATEWAY + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-api-key": key},
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


@mcp.tool()
def empathy_hint(text: str) -> str:
    """L3 Empathy Response Strategy: converts text into a deterministic response
    strategy (approach, tone temperature, pacing, focus points, avoid-list) for
    AI companions and conversational agents. Deterministic table lookup, no LLM,
    ~20ms; privacy-first. Not a medical or therapeutic tool."""
    return _post("/v1/chenji/empathy-hint", {"input": {"text": text}})


@mcp.tool()
def somatic_decode(text: str) -> str:
    """L4 Somatic Emotion Decode: converts body-sensation text (e.g. tight chest,
    clenched fists) into structured emotion: primary affect, valence/arousal,
    emotion texture, causal intent, plus somatic anchor cues. Grounded in the
    somatic decoding discipline; wellness simulation only, not a diagnostic tool."""
    return _post("/v1/chenji/somatic-decode", {"input": {"text": text}})


app = mcp.streamable_http_app()
app.add_middleware(KeyMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8102, log_level="warning")
