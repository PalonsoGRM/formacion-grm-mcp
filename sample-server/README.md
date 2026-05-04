# sample-server — Servidor MCP Python

Servidor MCP de ejemplo construido durante el **Lab 3**.

## Stack

| | |
|---|---|
| Lenguaje | Python 3.11+ |
| Librería MCP | fastmcp |
| Transporte | HTTP + SSE |
| Gestión de entorno | uv |

## Estructura (se construye en Lab 3)

```
sample-server/
├── README.md          # Este fichero
├── pyproject.toml     # Dependencias del proyecto
├── server.py          # Punto de entrada del servidor MCP
└── tools/             # Modulos con las tools expuestas
    └── converter.py   # Tool de conversión de documentos
```

## Inicio rápido

```bash
cd sample-server
uv venv
uv pip install "mcp[cli]" fastmcp
python server.py
```

El servidor arranca en `http://localhost:8000/sse` por defecto.

## Verificación

Abre MCP Inspector y conéctate a `http://localhost:8000/sse` para ver las tools disponibles.

```bash
npx @modelcontextprotocol/inspector
```

---

El código de este servidor se desarrolla paso a paso en [Lab 3](../workshop/labs/03-build-server/README.md).
