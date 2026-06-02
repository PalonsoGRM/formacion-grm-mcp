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
├── server.py          # FastMCP app con tools, resources y prompts
└── db/
    ├── seed.py        # Crea y puebla grm_demo.db (ejecutar una vez)
    └── grm_demo.db    # SQLite generado — no se sube al repo
```

## Lo que expone el servidor

| Primitiva | Nombre | Descripción |
|---|---|---|
| Tool | `echo` | Devuelve el mismo mensaje recibido |
| Tool | `search_customers` | Busca clientes por nombre, ciudad o segmento |
| Tool | `get_customer_orders` | Devuelve pedidos de un cliente, con filtro opcional por estado |
| Resource | `db://schema` | Esquema de la base de datos (tablas, columnas, valores) |
| Resource | `db://customers/{id}` | Perfil completo y resumen de pedidos de un cliente |
| Prompt | `customer_summary` | Genera un prompt de análisis comercial hidratado con datos reales |

## Inicio rápido

```powershell
cd sample-server
uv venv
.venv\Scripts\Activate.ps1
uv pip install "mcp[cli]" fastmcp --native-tls
python server.py
```

El servidor arranca en `http://localhost:8000/sse` por defecto.

Antes de usar las tools de base de datos, genera los datos de ejemplo:

```powershell
python db/seed.py
```

## Verificación

Abre MCP Inspector y conéctate a `http://localhost:8000/sse` para ver las tools disponibles.

```bash
npx @modelcontextprotocol/inspector
```

---

El código de este servidor se desarrolla paso a paso en [Lab 3](../workshop/labs/03-build-server/README.md).
