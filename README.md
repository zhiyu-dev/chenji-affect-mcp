# Chenji Affect MCP Server

<!-- mcp-name: io.github.zhiyu-dev/chenji-affect-mcp -->

Turn raw text into structured affect signals — an **8-dimensional emotion vector**, **emotion texture labels**, **causal intent**, and **3D avatar driving parameters** — inside any MCP-capable client (Claude Desktop, Cursor, Qoder, etc.).

Powered by the [Chenji Affect API](https://rapidapi.com/zhiyudev/api/chenji-affect-api) (`taichusjs.cn`).

## Tools

| Tool | Level | Description |
| --- | --- | --- |
| `analyze_text` | L1 | Text → 8-dim affect vector + emotion texture + intent + state description |
| `generate_avatar_params` | L2 | Text → blendshape/AU/curve animation package + lighting/atmosphere package + upstream L1 |

## Install

Requires Python 3.10+.

```bash
pip install "mcp>=1.0,<2"
```

Get an API key:
- Free BASIC plan (100 req/day, 3,000/month): subscribe on [RapidAPI](https://rapidapi.com/zhiyudev/api/chenji-affect-api), or request a trial key at `https://taichusjs.cn/trial.html`.

## Configure (Claude Desktop example)

```json
{
  "mcpServers": {
    "chenji-affect": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "CHENJI_API_KEY": "cj-your-key-here"
      }
    }
  }
}
```

Environment variables:

| Variable | Required | Description |
| --- | --- | --- |
| `CHENJI_API_KEY` | Yes | Your Chenji API key |
| `CHENJI_API_BASE` | No | Defaults to `https://taichusjs.cn` |

## Notes

- L1 input is limited to 2000 characters (every 200 chars = 1 billing unit).
- `generate_avatar_params` requires a key tier that includes L2.
- Privacy: raw text is never persisted by the API; only key hashes and telemetry are retained.
- Wellness and affect-state simulation only — not a medical or diagnostic tool.

## Links

- Website: https://taichusjs.cn
- RapidAPI listing: https://rapidapi.com/zhiyudev/api/chenji-affect-api
- Machine-readable capability card: https://taichusjs.cn/.well-known/capability.jsonld
