# Lab 3 — Construir un servidor MCP en Python

**Duración**: 35 min  
**Objetivo**: Crear un servidor MCP funcional en Python con `fastmcp`, exponer herramientas útiles y usar transporte **HTTP+SSE** para que pueda ser consumido desde un cliente C# o cualquier cliente remoto.

## ¿Qué es FastMCP?

[FastMCP](https://github.com/jlowin/fastmcp) es un framework Python de alto nivel para construir servidores MCP. Abstrae todo el protocolo JSON-RPC y el ciclo de vida del servidor — tú solo defines funciones Python decoradas y FastMCP las expone automáticamente como tools, resources o prompts MCP.

```python
# Sin FastMCP: implementar JSON-RPC, schemas, transportes, lifecycle...
# Con FastMCP:
@mcp.tool()
def mi_tool(texto: str) -> str:
    return texto.upper()
```

FastMCP infiere el schema JSON de los type hints de Python, genera las descripciones a partir de los docstrings y gestiona la serialización. En el fondo usa [Pydantic](https://docs.pydantic.dev/) para la validación.

> **Referencias**
> - Repositorio: https://github.com/jlowin/fastmcp
> - Documentación: https://gofastmcp.com
> - SDK oficial MCP Python (nivel bajo, sin abstracciones): https://github.com/modelcontextprotocol/python-sdk

---

> [!NOTE]
> **El cambio de transporte que lo cambia todo**
>
> En los Labs 1 y 2 todos los servidores usaban `stdio`: se arrancan como subprocesos y solo aceptan un cliente a la vez (el proceso que los lanzó).
>
> A partir de este lab usamos `transport="sse"`: el servidor Python arranca como un **servicio HTTP** en `localhost:8000`. Cualquier cliente en la misma red puede conectarse — incluyendo el cliente C# del Lab 4 o el agente del Lab 5.

---

## Prerrequisitos

- Python 3.11+ y `uv` instalados
- MCP Inspector disponible: `npx @modelcontextprotocol/inspector`

---

## Pasos

### 1. Crear el proyecto Python

`uv venv` crea un entorno virtual Python aislado en `.venv/` — así las dependencias de este proyecto no interfieren con el resto del sistema. Después hay que **activarlo** para que el terminal use ese entorno al ejecutar `python` o `pip`.

**PowerShell (Windows):**

```powershell
cd sample-server
uv venv
.venv\Scripts\Activate.ps1

uv pip install "mcp[cli]" fastmcp --native-tls
```

> [!TIP]
> Con `uv` también puedes saltarte la activación manual y arrancar directamente con `uv run server.py`. El entorno se gestiona solo. Útil si no quieres activar/desactivar manualmente.

### 2. Crear el servidor mínimo

Crea `server.py` con VS Code y copia el código:

```powershell
code server.py
```

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

```powershell
python server.py
```

Verás la pantalla de arranque de FastMCP:

![FastMCP server startup](assets/server-startup.png)

El servidor está ahora escuchando peticiones HTTP.A diferencia del stdio de los labs anteriores, este proceso **no termina** hasta que lo paras manualmente.

### 3. Verificar con MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

En el Inspector, la configuración cambia respecto a los Labs 1 y 2:

| Campo | Valor |
|---|---|
| **Transport Type** | `SSE` (no stdio) |
| **URL** | `http://localhost:8000/sse` |

Haz clic en **Connect**. El indicador verde confirma la conexión.

![MCP Inspector conectado al servidor — Transport Type SSE, URL http://localhost:8000/sse, servidor grm-tools v3.2.4 conectado](assets/inspector-verify.png)

Ve a **Tools** y haz clic en **List Tools**: verás `echo`. Llámala con `message: "hola desde el inspector"`.

### 4. Añadir una tool que el LLM no puede hacer solo

El verdadero poder de MCP no está en manipular strings — está en dar al LLM **acceso a recursos externos** que por sí solo no puede alcanzar.

Instala `httpx` en el entorno virtual:

```powershell
uv pip install httpx
```

Añade la tool al `server.py`:

```python
import httpx

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
```

> [!NOTE]
> **Proxy corporativo**: si la red intercepta el tráfico TLS (proxy con certificado autofirmado), `httpx` fallará con `CERTIFICATE_VERIFY_FAILED`. El `verify=False` desactiva la verificación SSL — válido para un lab interno. En producción lo correcto es pasar el bundle del proxy: `verify="/ruta/al/cert.pem"`.

Reinicia el servidor y pruébala en el Inspector con `url: "https://example.com"`.

> [!NOTE]
> Un LLM sin tools no puede hacer peticiones HTTP — no tiene acceso a la red. Con esta tool, cualquier agente que use tu servidor MCP puede navegar URLs bajo demanda. Esto es exactamente lo que hacen los MCP servers de búsqueda web (Brave Search, Exa, etc.).

### 5. Exponer Resources

**El cambio de mental model**: las tools las *invoca el LLM* cuando decide que las necesita. Los resources los *lee el HOST* (tu agente, Claude Desktop...) y los inyecta en el contexto antes de que el LLM responda. Es RAG sin infraestructura.

| | Tool | Resource |
|---|---|---|
| **Quién decide usarlo** | El LLM | El HOST / el usuario |
| **Cuándo** | Acción o cálculo bajo demanda | Contexto que el LLM debe conocer antes de responder |
| **Analogía** | Función que llamas | Documento que adjuntas al chat |

**Resource estático** — contexto fijo que el LLM lee:

```python
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
```

**Resource template** — URI parametrizada, el verdadero poder: el host puede pedir `logs://errors/2025-05-05` y obtener datos dinámicos para esa fecha concreta:

```python
@mcp.resource("logs://errors/{date}")
def get_error_log(date: str) -> list:
    """Returns the error log for a given date (YYYY-MM-DD).

    Args:
        date: Date in YYYY-MM-DD format.
    """
    # En producción: consulta real a tu sistema de logs (App Insights, Seq, etc.)
    return [
        {"timestamp": f"{date}T10:23:11", "level": "ERROR", "service": "UserService", "message": "NullReferenceException in GetById"},
        {"timestamp": f"{date}T11:05:33", "level": "ERROR", "service": "OrderService", "message": "Timeout connecting to SQL Server"},
        {"timestamp": f"{date}T14:42:07", "level": "WARN",  "service": "AuthService",  "message": "Token expiry threshold reached"},
    ]
```

Reinicia el servidor y abre **Resources** en el Inspector:
- `docs://coding-standards` aparece como resource fijo — haz clic para leer el JSON
- Para el template, escribe `logs://errors/2025-05-05` en el campo URI y pulsa **Read Resource**

> [!TIP]
> En el Lab 5 el agente inyecta `docs://coding-standards` en el contexto antes de responder preguntas de código, y puede pedir `logs://errors/{hoy}` para hacer debugging con contexto real.

### 6. Exponer un Prompt

**Los prompts MCP no son el prompt del LLM** — son *plantillas de interacción* que el servidor expone para que cualquier cliente las invoque. El experto en dominio fabrica el prompt perfecto una vez; el equipo entero lo reutiliza con cualquier LLM.

En Claude Desktop aparecen como slash commands. En tu agente los invocas con `prompts/get`.

```python
from mcp.types import Message, TextContent

@mcp.prompt()
def debug_error(error_message: str, service: str = "unknown") -> list[Message]:
    """Generates a structured debugging prompt for a .NET error.

    Args:
        error_message: The full error message or stack trace.
        service: The service or component where the error occurred.
    """
    return [
        Message(
            role="user",
            content=TextContent(
                type="text",
                text=f"""Eres un senior developer .NET. Analiza este error del servicio '{service}':

ERROR:
{error_message}

Por favor:
1. Identifica la causa raíz
2. Sugiere 3 posibles fixes ordenados por probabilidad
3. Muestra el código corregido si aplica
4. Indica si hay riesgo de regresión en otros servicios""",
            ),
        )
    ]
```

Reinicia y abre **Prompts** en el Inspector. Rellena `error_message` con cualquier stack trace y pulsa **Get Prompt** — verás el mensaje estructurado listo para enviar al LLM.

> [!NOTE]
> La diferencia con una tool: la tool *ejecuta* algo y devuelve un resultado. El prompt *construye* el mensaje que el usuario enviará al LLM — el cliente decide cuándo y cómo usarlo. Esto permite al servidor exportar expertise de prompting sin acoplarse a ningún LLM concreto.

---

## Estructura final del servidor

```
sample-server/
├── server.py          # FastMCP app con todas las tools
├── pyproject.toml     # (opcional: gestión de dependencias formal)
└── .venv/
```

---

## Qué ha pasado por debajo

Con `transport="sse"` el flujo es muy diferente a stdio. El servidor levanta un servidor HTTP con dos endpoints:

- `GET /sse` — abre un stream de eventos que el cliente mantiene abierto para recibir notificaciones
- `POST /messages` — el cliente envía cada petición JSON-RPC aquí

```mermaid
sequenceDiagram
    participant C as Cliente (Inspector / C#)
    participant S as FastMCP server<br/>:8000

    Note over S: python server.py<br/>escuchando en :8000

    C->>S: GET /sse (HTTP, keep-alive)
    S-->>C: stream SSE abierto

    C->>S: POST /messages { initialize }
    S-->>C: SSE event: InitializeResult

    C->>S: POST /messages { tools/list }
    S-->>C: SSE event: [{ name, description, inputSchema }]

    C->>S: POST /messages { tools/call: echo }
    S-->>C: SSE event: CallToolResult { "Echo: ..." }

    Note over C,S: La conexión SSE permanece abierta<br/>mientras el cliente esté activo.<br/>Múltiples clientes pueden conectarse simultáneamente.
```

**Por qué HTTP+SSE y no WebSockets o polling:**
- SSE es unidireccional server→client, más simple de implementar y depurar
- Las peticiones del cliente van como POST HTTP normales — fáciles de proxiar, loguear y autenticar
- Los clientes `.NET` (`ModelContextProtocol.Client`) implementan SSE de forma nativa

> Para ver el JSON exacto de cada intercambio (`initialize`, `tools/list`, `tools/call`...), consulta la sección [Los mensajes en el cable](../../../mcp-fundamentals/README.md#los-mensajes-en-el-cable) en los fundamentos.

---

## Preguntas de reflexión

> [!NOTE]
> Intenta responder antes de desplegar. Son conceptos clave para el Lab 4 (cliente C#).

---

**1. ¿Por qué usamos `transport="sse"` en este lab y no `transport="stdio"` como en los labs anteriores?**

<details>
<summary>Mostrar respuesta</summary>

> Con stdio, el servidor solo acepta un cliente: el proceso que lo arrancó. Con SSE, el servidor escucha en un puerto HTTP y acepta conexiones simultáneas de múltiples clientes.

Esto es imprescindible para el Lab 4: el cliente C# (`ModelContextProtocol.Client`) no puede arrancar un subproceso Python — necesita conectarse a un endpoint HTTP ya levantado.

Además, en producción los servidores MCP son servicios remotos (deployados en Azure, por ejemplo). Un cliente en una máquina diferente no puede usar stdio.

</details>

---

**2. ¿Cómo añadirías autenticación Bearer al servidor?**

<details>
<summary>Mostrar respuesta</summary>

> `fastmcp` no tiene autenticación incorporada, pero el servidor corre sobre `uvicorn` (ASGI), así que puedes añadir middleware de autenticación.

Opción práctica con un middleware simple:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("Authorization", "")
        if token != "Bearer mi-token-secreto":
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)

mcp.app.add_middleware(BearerAuthMiddleware)
```

En producción lo habitual es usar un API Gateway (Azure APIM) delante del servidor MCP y delegar la autenticación ahí.

</details>

---

**3. ¿Qué pasa si el LLM llama a una tool con argumentos incorrectos? ¿Cómo manejarlo?**

<details>
<summary>Mostrar respuesta</summary>

> `fastmcp` valida automáticamente los argumentos contra el schema de la función (tipado Python + Pydantic). Si los argumentos no coinciden, el servidor devuelve un error JSON-RPC `InvalidParams` antes de ejecutar la función.

Para errores de negocio (argumentos válidos pero resultado imposible), lo correcto es lanzar una excepción en Python — `fastmcp` la captura y la convierte en un `CallToolResult` con `isError: true`:

```python
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divides a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

El LLM recibe el mensaje de error y puede decidir qué hacer (reintentar con otros argumentos, informar al usuario, etc.).

</details>

---

## Siguiente paso

[Lab 4 — Cliente C# con ModelContextProtocol.Client](../04-client-connect/README.md)

