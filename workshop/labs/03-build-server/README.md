# Lab 3 — Construir un servidor MCP en Python

**Duración**: 35 min  
**Objetivo**: Crear un servidor MCP funcional en Python con `fastmcp`, exponer herramientas útiles y usar transporte HTTP+SSE para que pueda ser consumido desde un cliente C#.

---

## Prerrequisitos

- Python 3.11+ y `uv` instalados
- MCP Inspector disponible: `npx @modelcontextprotocol/inspector`

---

## Pasos

### 1. Crear el proyecto Python

```bash
cd sample-server
uv venv
# En Windows: .venv\Scripts\activate
# En macOS/Linux: source .venv/bin/activate
source .venv/bin/activate

uv pip install "mcp[cli]" fastmcp
```

### 2. Crear el servidor mínimo

Crea `server.py`:

```python
from fastmcp import FastMCP

mcp = FastMCP("grm-tools")

@mcp.tool()
def echo(message: str) -> str:
    """Returns the same message back."""
    return f"Echo: {message}"

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

Arrancar:

```bash
python server.py
```

### 3. Verificar con MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

Conéctate a `http://localhost:8000/sse`, lista las tools y llama a `echo`.

### 4. Añadir una tool más útil

Añade una tool que convierta texto a mayúsculas y extraiga las primeras N palabras:

```python
@mcp.tool()
def process_text(text: str, max_words: int = 50) -> dict:
    """Processes text: uppercases it and limits to max_words words.
    
    Args:
        text: Input text to process.
        max_words: Maximum number of words to return.
    """
    words = text.split()[:max_words]
    return {
        "original_length": len(text.split()),
        "truncated": len(text.split()) > max_words,
        "result": " ".join(words).upper()
    }
```

Reinicia el servidor y verifica la nueva tool en MCP Inspector.

### 5. Exponer un Resource (opcional)

```python
@mcp.resource("config://server-info")
def get_server_info() -> str:
    """Returns server configuration info."""
    return "GRM MCP Server v1.0 — HTTP+SSE transport"
```

---

## Estructura final del servidor

```
sample-server/
├── server.py          # FastMCP app con todas las tools
├── pyproject.toml     # (opcional: gestión de dependencias formal)
└── .venv/
```

---

## Preguntas de reflexión

1. ¿Por qué usamos `transport="sse"` y no `transport="stdio"`?
2. ¿Cómo añadirías autenticación Bearer al servidor?
3. ¿Qué pasa si el LLM llama a una tool con argumentos incorrectos? ¿Cómo manejarlo?

---

## Siguiente paso

[Lab 4 — Cliente C# con ModelContextProtocol.Client](../04-client-connect/README.md)
