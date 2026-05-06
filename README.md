# ThinkNEO MCP SMB Products

**8 standalone MCP servers for SMBs** — each a separate product, billed via TNC (ThinkNEO Credits).

[![Glama AAA](https://img.shields.io/badge/Glama-AAA-gold)](https://glama.ai/mcp/servers?q=thinkneo)
[![MCP Protocol](https://img.shields.io/badge/MCP-streamable--http-blue)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## Products

| Product | Tools | Cost/call | Endpoint |
|---------|-------|-----------|----------|
| **MCP SMB Guardrails** | 4 | 1-2 TNC | `mcp.thinkneo.app/smb/guardrails/mcp` |
| **MCP SMB FinOps** | 5 | 1-2 TNC | `mcp.thinkneo.app/smb/finops/mcp` |
| **MCP SMB Observability** | 5 | 0.5-2 TNC | `mcp.thinkneo.app/smb/observability/mcp` |
| **MCP SMB Router** | 4 | 0.5-2 TNC | `mcp.thinkneo.app/smb/router/mcp` |
| **MCP SMB Trust Score** | 4 | 1-5 TNC | `mcp.thinkneo.app/smb/trust-score/mcp` |
| **MCP SMB Memory** | 5 | 0.5-1 TNC | `mcp.thinkneo.app/smb/memory/mcp` |
| **MCP SMB ThinkSecure** | 5 | 0.5-3 TNC | `mcp.thinkneo.app/smb/thinksecure/mcp` |
| **MCP SMB A2A Lite** | 5 | 0.5-5 TNC | `mcp.thinkneo.app/smb/a2a-lite/mcp` |

## Quick Start

### Connect any MCP client (Claude Desktop, Cursor, etc.)

```json
{
  "mcpServers": {
    "thinkneo-smb-guardrails": {
      "url": "https://mcp.thinkneo.app/smb/guardrails/mcp",
      "transport": "streamable-http",
      "headers": {
        "Authorization": "Bearer YOUR_TNC_API_KEY"
      }
    }
  }
}
```

### Get your API key

1. Sign up at [thinkneo.app/signup](https://thinkneo.app/signup) — **500 TNC free**
2. Or buy credits: **$1 = 100 TNC** at [thinkneo.app/pricing](https://thinkneo.app/pricing)

## Architecture

```
thinkneo-mcp-products/
├── shared/              # Common library (auth, billing, database, server factory)
├── mcp-guardrails/      # Each product is a standalone MCP server
├── mcp-finops/
├── mcp-observability/
├── mcp-router/
├── mcp-trust-score/
├── mcp-memory/
├── mcp-thinksecure/
├── mcp-a2a-lite/
├── docker-compose.yml   # Orchestrates all 8 services
├── Dockerfile           # Shared base image
└── nginx-products.conf  # Nginx routing config
```

## Billing (TNC Credits)

All tools are billed via **TNC (ThinkNEO Credits)**:
- Each API call deducts credits from your balance
- Costs vary by tool complexity (0.5 - 5 TNC per call)
- Free trial: **500 TNC** on signup (no credit card)
- Top up: **$1 = 100 TNC**

## Self-Hosting

```bash
git clone https://github.com/thinkneo-ai/mcp-smb-products.git
cd mcp-smb-products
cp .env.example .env   # Configure DB + Redis
make migrate           # Create TNC tables
make build             # Build all 8 images
make up                # Start all services
```

## Transport

All servers use **streamable-http** transport (MCP spec 2025-03-26):
- Endpoint: `POST /mcp`
- Auth: `Authorization: Bearer <TNC_API_KEY>`
- Protocol: JSON-RPC 2.0

## Related

| Server | Description | Tools |
|--------|-------------|-------|
| [thinkneo-control-plane](https://glama.ai/mcp/servers/thinkneo-ai/mcp-server) | Enterprise AI Control Plane — full governance suite | 72 tools |
| [thinkneo-mcp-smb-products](https://glama.ai/mcp/servers/thinkneo-ai/mcp-smb-products) | SMB standalone products (this repo) | 37 tools |

## Enterprise

Need the full enterprise suite with 72 tools, SLA, and dedicated support?
See [mcp.thinkneo.ai](https://mcp.thinkneo.ai) or contact hello@thinkneo.ai.

## License

MIT — see [LICENSE](./LICENSE)
