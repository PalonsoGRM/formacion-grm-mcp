# sample-client — Cliente MCP C#

Cliente MCP de ejemplo construido durante el **Lab 4**.

## Stack

| | |
|---|---|
| Lenguaje | C# |
| Runtime | .NET 10 |
| NuGet principal | `ModelContextProtocol.Client` |
| Tipo de host | ASP.NET Core Web API |
| Patrón | Similar a `McpToolLoader.cs` en MAF (`maf-agent-template`) |

## Estructura (se construye en Lab 4)

```
sample-client/
├── README.md                      # Este fichero
├── SampleMcpClient.sln
└── src/
    └── SampleMcpClient.Api/
        ├── Program.cs
        ├── appsettings.json       # URL del servidor MCP (no contiene secretos)
        └── Mcp/
            └── McpClientService.cs   # Conexion SSE + listado y llamada de tools
```

## Inicio rápido

```bash
cd sample-client/src/SampleMcpClient.Api
dotnet run
```

Requiere el servidor Python de `sample-server/` corriendo en `http://localhost:8000/sse`.

## Conexión al servidor

El cliente se conecta via SSE:

```csharp
var client = await McpClientFactory.CreateAsync(
    new SseClientTransport(new SseClientTransportOptions
    {
        Endpoint = new Uri("http://localhost:8000/sse")
    }));

var tools = await client.ListToolsAsync();
```

---

El código de este cliente se desarrolla paso a paso en [Lab 4](../workshop/labs/04-client-connect/README.md).

Para ver cómo se usa en producción, consulta `McpToolLoader.cs` en `maf-agent-template`.
