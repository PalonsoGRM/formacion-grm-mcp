# Formacion GRM: Model Context Protocol (MCP)

Formación de media jornada para el equipo de developers sobre **MCP (Model Context Protocol)**: qué es, cómo usarlo, cómo construir un servidor y cómo integrarlo con nuestros agentes C#.

---

## Agenda

| Hora | Bloque | Material |
|---|---|---|
| 00:00 – 00:15 | Apertura y bienvenida | Este README |
| 00:15 – 00:40 | Copilot CLI — personalización y extensibilidad (25 min) | [copilot-customization/README.md](copilot-customization/README.md) |
| 00:40 – 01:15 | Fundamentos MCP (35 min) | [mcp-fundamentals/README.md](mcp-fundamentals/README.md) |
| 01:15 – 01:25 | Descanso | |
| 01:25 – 01:45 | Lab 1 — Intro y arquitectura MCP | [labs/01-mcp-intro](workshop/labs/01-mcp-intro/README.md) |
| 01:45 – 02:10 | Lab 2 — Usar markitdown MCP existente | [labs/02-use-existing-mcp](workshop/labs/02-use-existing-mcp/README.md) |
| 02:10 – 02:45 | Lab 3 — Construir un servidor MCP en Python | [labs/03-build-server](workshop/labs/03-build-server/README.md) |
| 02:45 – 03:10 | Lab 4 — Cliente C# con ModelContextProtocol.Client | [labs/04-client-connect](workshop/labs/04-client-connect/README.md) |
| 03:10 – 03:40 | Lab 5 — Azure AI Agents + Semantic Kernel | [labs/05-agent-integration](workshop/labs/05-agent-integration/README.md) |
| 03:40 – 03:55 | Foro abierto + cheatsheet | [cheatsheet.md](workshop/cheatsheet.md) |

---

## Estructura del repositorio

```
formacion-grm-mcp/
├── README.md                      # Este fichero
├── PREREQUISITES.md               # Instalación y verificación del entorno
├── resources.md                   # Links de referencia
├── .github/
│   ├── copilot-instructions.md
│   └── pull_request_template.md
├── copilot-customization/
│   └── README.md                  # Personalización y extensibilidad de Copilot CLI
├── mcp-fundamentals/
│   └── README.md                  # Bloque teórico completo
├── sample-server/
│   └── README.md                  # Servidor MCP Python (HTTP+SSE) — Lab 3
├── sample-client/
│   └── README.md                  # Cliente MCP C# .NET 10 — Lab 4
└── workshop/
    ├── README.md
    ├── cheatsheet.md
    ├── trainer-notes.md
    └── labs/
        ├── 01-mcp-intro/
        ├── 02-use-existing-mcp/
        ├── 03-build-server/
        ├── 04-client-connect/
        └── 05-agent-integration/
```

## Arquitectura de la formacion

```mermaid
graph LR
    subgraph AGENT["Agente C# .NET 10  (Lab 4 + 5)"]
        SK["Semantic Kernel"]
        MCPC["ModelContextProtocol.Client"]
        SK <-->|"KernelFunction"| MCPC
    end

    subgraph SERVER["MCP Server Python  (Lab 3)"]
        FM["fastmcp\nHTTP + SSE :8000"]
        T1["convert_to_markdown"]
        T2["fetch_url"]
        FM --> T1
        FM --> T2
    end

    AZAI["Azure OpenAI\ngpt-4o"]
    INSPECTOR["MCP Inspector\n(Lab 1)"]
    VSEXT["VS Code + Copilot\n(Lab 2)"]

    MDITDOWN["markitdown-mcp\n(stdio, Lab 2)"]

    MCPC <-->|"JSON-RPC 2.0\nHTTP + SSE"| FM
    SK <-->|"chat completions"| AZAI
    INSPECTOR --->|"HTTP + SSE\n(inspeccion manual)"| FM
    VSEXT --->|"stdio"| MDITDOWN

    style AGENT fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style SERVER fill:#dcfce7,stroke:#16a34a,color:#14532d
    style AZAI fill:#fef9c3,stroke:#ca8a04
    style INSPECTOR fill:#f3e8ff,stroke:#9333ea
    style VSEXT fill:#f3e8ff,stroke:#9333ea
    style MDITDOWN fill:#fce7f3,stroke:#db2777,color:#831843
```

---

## Guia de inicio rápido

| Paso | Acción |
|---|---|
| 1 | Revisa [PREREQUISITES.md](PREREQUISITES.md) y verifica tu entorno |
| 2 | Lee [copilot-customization/README.md](copilot-customization/README.md) para entender la personalización de Copilot CLI |
| 3 | Lee [mcp-fundamentals/README.md](mcp-fundamentals/README.md) antes de la sesión |
| 4 | Sigue los labs en orden durante el workshop |
| 5 | Usa [cheatsheet.md](workshop/cheatsheet.md) como referencia rápida |
| 6 | Consulta [resources.md](resources.md) para profundizar |

---

## Novedades del protocolo

- [MCP 2026: actualización del protocolo](mcp-2026-updates/README.md) — análisis en castellano del Release Candidate `2026-07-28` y el roadmap 2026: protocolo sin estado, extensiones, autorización reforzada, deprecaciones e impacto en nuestro stack.

---

## Referencias rápidas

- [Copilot CLI — Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Spec oficial MCP](https://spec.modelcontextprotocol.io)
- [microsoft/markitdown](https://github.com/microsoft/markitdown)
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- [ai-agents-for-beginners cap. 11](https://github.com/microsoft/ai-agents-for-beginners)
- [fastmcp](https://github.com/jlowin/fastmcp)
