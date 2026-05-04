# Lab 4 — Cliente C# con ModelContextProtocol.Client

**Duración**: 25 min  
**Objetivo**: Crear un cliente .NET 10 que se conecte via SSE al servidor Python del Lab 3, liste las tools disponibles y llame a una de ellas. Entender cómo esto encaja en nuestra plataforma MAF.

---

## Prerrequisitos

- .NET 10 SDK instalado
- Servidor Python del Lab 3 corriendo en `http://localhost:8000/sse`

---

## Contexto MAF

En `maf-agent-template`, el fichero `Infrastructure/Mcp/McpToolLoader.cs` hace exactamente esto:

1. Crea un `McpClient` conectado via SSE al servidor MCP configurado
2. Lista las tools disponibles con `ListToolsAsync()`
3. Envuelve cada tool con `PermissionGuardedAIFunction` para control de acceso
4. Las registra en el agente para que el LLM pueda invocarlas

Este lab replica ese patrón a escala mínima.

---

## Pasos

### 1. Crear el proyecto .NET

```bash
mkdir -p sample-client/src
cd sample-client/src
dotnet new console -n SampleMcpClient
cd SampleMcpClient
dotnet add package ModelContextProtocol
```

### 2. Conectar al servidor MCP via SSE

Reemplaza el contenido de `Program.cs`:

```csharp
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol.Transport;

Console.WriteLine("Connecting to MCP server...");

var client = await McpClientFactory.CreateAsync(
    new SseClientTransport(new SseClientTransportOptions
    {
        Endpoint = new Uri("http://localhost:8000/sse")
    }));

Console.WriteLine("Connected.");

// Listar tools disponibles
Console.WriteLine("\nAvailable tools:");
var tools = await client.ListToolsAsync();
foreach (var tool in tools)
{
    Console.WriteLine($"  - {tool.Name}: {tool.Description}");
}
```

### 3. Llamar a una tool

Añade al final de `Program.cs`:

```csharp
// Llamar a la tool "echo"
Console.WriteLine("\nCalling 'echo' tool...");
var result = await client.CallToolAsync(
    "echo",
    new Dictionary<string, object?> { ["message"] = "Hello from C#!" });

Console.WriteLine($"Result: {result.Content[0].Text}");
```

### 4. Ejecutar

Asegúrate de que el servidor Python está corriendo, luego:

```bash
dotnet run
```

Deberías ver las tools listadas y el resultado de la llamada a `echo`.

### 5. Llamar a `process_text` (opcional)

```csharp
var textResult = await client.CallToolAsync(
    "process_text",
    new Dictionary<string, object?>
    {
        ["text"] = "model context protocol is an open standard for connecting llms to tools",
        ["max_words"] = 5
    });

Console.WriteLine($"Processed: {textResult.Content[0].Text}");
```

---

## Bonus: Azure Function como servidor MCP

Un Azure Function (HTTP trigger) puede actuar como servidor MCP si:

1. Implementa los endpoints MCP (`/sse`, handling de `initialize`, `tools/list`, `tools/call`)
2. Usa el SDK MCP para .NET en modo servidor

Esto permite exponer capacidades de negocio como tools MCP sin levantar un servicio adicional. Ver la documentación de `ModelContextProtocol.AspNetCore` para más detalles.

---

## Preguntas de reflexión

1. ¿Qué diferencia hay entre `McpClientFactory.CreateAsync` con `SseClientTransport` vs `StdioClientTransport`?
2. ¿Cómo añadirías un header de autenticación Bearer a la conexión SSE?
3. En MAF, ¿qué hace `PermissionGuardedAIFunction` con las tools que carga McpToolLoader?

---

## Siguiente paso

[Lab 5 — Azure AI Agents + Semantic Kernel](../05-agent-integration/README.md)
