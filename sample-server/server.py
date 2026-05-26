from fastmcp import FastMCP
import httpx
import sqlite3
from pathlib import Path
from fastmcp.prompts import Message

mcp = FastMCP("grm-tools")

DB_PATH = Path(__file__).parent / "db" / "grm_demo.db"


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def echo(message: str) -> str:
    """Returns the same message back."""
    return f"Echo: {message}"


@mcp.tool()
def search_customers(name: str = "", city: str = "", segment: str = "") -> list[dict]:
    """Search customers in the database. All filters are optional and case-insensitive.

    Args:
        name:    Partial customer name to search for.
        city:    City to filter by.
        segment: Customer segment: A (top), B (medium) or C (small). Leave empty for all.
    """
    query = "SELECT * FROM clientes WHERE 1=1"
    params: list = []
    if name:
        query += " AND nombre LIKE ?"
        params.append(f"%{name}%")
    if city:
        query += " AND ciudad LIKE ?"
        params.append(f"%{city}%")
    if segment:
        query += " AND segmento = ?"
        params.append(segment.upper())
    query += " ORDER BY segmento, nombre"

    with _db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def get_customer_orders(customer_id: int, status: str = "") -> list[dict]:
    """Get orders for a specific customer. Optionally filter by status.

    Args:
        customer_id: The customer ID.
        status:      Order status filter: pendiente, enviado, entregado or cancelado.
    """
    query = "SELECT * FROM pedidos WHERE cliente_id = ?"
    params: list = [customer_id]
    if status:
        query += " AND estado = ?"
        params.append(status.lower())
    query += " ORDER BY fecha DESC"

    with _db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def fetch_url(url: str, max_chars: int = 2000) -> dict:
    """Fetches the content of a URL and returns it as text.

    Args:
        url: The URL to fetch.
        max_chars: Maximum number of characters to return (default 2000).
    """
    response = httpx.get(url, follow_redirects=True, timeout=10, verify=False)
    content = response.text[:max_chars]
    return {
        "url": url,
        "status_code": response.status_code,
        "content": content,
        "truncated": len(response.text) > max_chars,
    }


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("db://schema")
def get_db_schema() -> dict:
    """Returns the database schema: tables, columns and value ranges."""
    return {
        "tables": {
            "clientes": {
                "columns": ["id", "nombre", "ciudad", "email", "segmento"],
                "segmento_values": ["A (top)", "B (medium)", "C (small)"],
                "row_count": 10,
            },
            "pedidos": {
                "columns": ["id", "cliente_id", "fecha", "importe", "estado"],
                "estado_values": ["pendiente", "enviado", "entregado", "cancelado"],
                "row_count": 25,
            },
        },
        "relationships": "pedidos.cliente_id → clientes.id",
    }


@mcp.resource("db://customers/{customer_id}")
def get_customer_profile(customer_id: str) -> dict:
    """Returns the full profile and order summary for a specific customer.

    Args:
        customer_id: The customer ID.
    """
    with _db() as conn:
        customer = conn.execute(
            "SELECT * FROM clientes WHERE id = ?", [customer_id]
        ).fetchone()
        if not customer:
            return {"error": f"Customer {customer_id} not found"}

        orders = conn.execute(
            """SELECT estado, COUNT(*) as count, SUM(importe) as total
               FROM pedidos WHERE cliente_id = ? GROUP BY estado""",
            [customer_id],
        ).fetchall()

    return {
        "customer": dict(customer),
        "orders_by_status": [dict(r) for r in orders],
        "total_revenue": sum(r["total"] for r in orders),
    }


@mcp.resource("docs://coding-standards")
def get_coding_standards() -> dict:
    """Returns the team's coding standards and conventions."""
    return {
        "language": "C# / Python",
        "conventions": [
            "Use PascalCase for classes, camelCase for variables",
            "All secrets via User Secrets or Key Vault — never in appsettings",
            "Azure credential: DefaultAzureCredential in DEBUG, ManagedIdentity in deployed envs",
            "Max method length: 30 lines",
            "All public methods must have XML doc comments",
        ],
        "architecture": "Clean Architecture — Domain / Application / Infrastructure / API",
        "git": "Conventional Commits: feat:, fix:, docs:, refactor:",
    }


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

@mcp.prompt
def customer_summary(customer_id: str) -> str:
    """Generates an analysis prompt for a specific customer using live DB data."""
    with _db() as conn:
        customer = conn.execute(
            "SELECT * FROM clientes WHERE id = ?", [customer_id]
        ).fetchone()
        orders = conn.execute(
            "SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY fecha DESC",
            [customer_id],
        ).fetchall()

    if not customer:
        return f"No se encontró el cliente con ID {customer_id}."

    orders_text = "\n".join(
        f"  - Pedido {o['id']}: {o['fecha']}  {o['importe']:,.2f}€  [{o['estado']}]"
        for o in orders
    )
    total = sum(o["importe"] for o in orders)

    return f"""Eres un analista comercial. Analiza el siguiente cliente y sus pedidos:

CLIENTE:
  ID:       {customer['id']}
  Nombre:   {customer['nombre']}
  Ciudad:   {customer['ciudad']}
  Segmento: {customer['segmento']}

PEDIDOS ({len(orders)} en total, {total:,.2f}€ facturado):
{orders_text}

Por favor:
1. Resume el comportamiento de compra del cliente
2. Identifica si hay pedidos problemáticos (cancelados o pendientes antiguos)
3. Propón una acción comercial concreta para el próximo trimestre"""


@mcp.prompt
def debug_error(error_message: str, service: str = "unknown") -> str:
    """Generates a structured debugging prompt for a .NET error."""
    return f"""Eres un senior developer .NET. Analiza este error del servicio '{service}':

ERROR:
{error_message}

Por favor:
1. Identifica la causa raíz
2. Sugiere 3 posibles fixes ordenados por probabilidad
3. Muestra el código corregido si aplica"""


@mcp.prompt
def code_review(code: str, language: str = "csharp") -> list[Message]:
    """Generates a code review conversation."""
    return [
        Message("You are a senior developer specialized in Clean Architecture. Be concise and practical.", role="assistant"),
        Message(f"Review this {language} code:\n\n```{language}\n{code}\n```"),
    ]


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

