# Cheatsheet MCP

Referencia rápida para llevar durante y después de la sesión.

---

## Comandos esenciales

Arrancar servidor Python:
```powershell
cd sample-server && python server.py
```

Instalar MCP Inspector (una sola vez):
```powershell
npm install -g @modelcontextprotocol/inspector
```

Arrancar MCP Inspector con una o varias carpetas accesibles:
```powershell
mcp-inspector npx -y @modelcontextprotocol/server-filesystem "C:/ruta/carpeta1" "C:/ruta/carpeta2"
```

Instalar dependencias Python del servidor:
```powershell
uv pip install "mcp[cli]" fastmcp
```

Crear proyecto .NET para cliente MCP:
```powershell
dotnet new webapi -n SampleMcpClient
dotnet add package ModelContextProtocol
```

---

## Servidor MCP mínimo (Python)

```python
from fastmcp import FastMCP

mcp = FastMCP("mi-servidor")

@mcp.tool()
def hola(nombre: str) -> str:
    """Saluda al usuario."""
    return f"Hola, {nombre}!"

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

---

## Cliente MCP mínimo (C#)

```csharp
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol.Transport;

var client = await McpClientFactory.CreateAsync(
    new SseClientTransport(new SseClientTransportOptions
    {
        Endpoint = new Uri("http://localhost:8000/sse")
    }));

// Listar tools disponibles
var tools = await client.ListToolsAsync();
foreach (var tool in tools)
    Console.WriteLine($"{tool.Name}: {tool.Description}");

// Llamar una tool
var result = await client.CallToolAsync("hola", new { nombre = "World" });
Console.WriteLine(result.Content[0].Text);
```

---

## Configurar servidor MCP en VS Code (para Lab 2)

Añadir en `.vscode/mcp.json` o en `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "markitdown": {
        "command": "uvx",
        "args": ["markitdown-mcp"]
      }
    }
  }
}
```

---

## Primitivas MCP

| Primitiva | Para qué | Método |
|---|---|---|
| **Tool** | El LLM puede invocarla | `tools/call` |
| **Resource** | Datos de solo lectura por URI | `resources/read` |
| **Prompt** | Plantilla de mensaje reutilizable | `prompts/get` |

---

## Transports

| Transport | Conexión | Cuándo |
|---|---|---|
| stdio | Subproceso local | VS Code, CLI |
| HTTP+SSE | Servicio HTTP remoto | Microservicios, clientes C# |

---

## Links clave

| | URL |
|---|---|
| Spec MCP | https://spec.modelcontextprotocol.io |
| fastmcp docs | https://github.com/jlowin/fastmcp |
| ModelContextProtocol NuGet | https://www.nuget.org/packages/ModelContextProtocol |
| markitdown MCP | https://github.com/microsoft/markitdown |
| Servidores MCP oficiales | https://github.com/modelcontextprotocol/servers |
