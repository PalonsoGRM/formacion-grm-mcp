# Lab 5 — Azure AI Agents + Semantic Kernel

**Duración**: 30 min  
**Objetivo**: Entender cómo integrar nuestro servidor MCP en un agente C# usando Azure AI Agents y Semantic Kernel, siguiendo el patrón de nuestra plataforma MAF.

---

## Prerrequisitos

- Lab 4 completado (cliente C# conectado al servidor Python)
- Conocimiento básico de Azure AI Agents o Semantic Kernel (no obligatorio)
- Acceso a Azure OpenAI o Azure AI Foundry (necesario para las llamadas reales al LLM)

---

## Contexto: la pila completa

```
┌──────────────────────────────────────────────────┐
│  HOST: ASP.NET Core / Azure Function (C# .NET 10) │
│                                                    │
│  ┌────────────────┐    ┌──────────────────────┐   │
│  │  Azure AI Agent │    │   Semantic Kernel    │   │
│  │  (IChatClient) │    │   (KernelFunction)   │   │
│  └───────┬────────┘    └──────────────────────┘   │
│          │ MCP tools via ModelContextProtocol       │
│  ┌───────▼──────────┐                              │
│  │  McpToolLoader   │ (como en maf-agent-template) │
│  └───────┬──────────┘                              │
└──────────┼───────────────────────────────────────┘
           │ HTTP+SSE
┌──────────▼──────────┐
│   MCP Server Python │  (sample-server/)
└─────────────────────┘
```

---

## Pasos

### 1. Añadir dependencias al proyecto del Lab 4

```bash
cd sample-client/src/SampleMcpClient
dotnet add package Azure.AI.Inference
dotnet add package Microsoft.SemanticKernel
dotnet add package Microsoft.Extensions.AI
```

### 2. Crear un agente simple que usa las tools MCP

```csharp
using Microsoft.Extensions.AI;
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol.Transport;

// 1. Conectar al servidor MCP y obtener las tools
var mcpClient = await McpClientFactory.CreateAsync(
    new SseClientTransport(new SseClientTransportOptions
    {
        Endpoint = new Uri("http://localhost:8000/sse")
    }));

var mcpTools = await mcpClient.ListToolsAsync();

// 2. Crear el cliente del LLM (Azure OpenAI en este ejemplo)
// Requiere variables de entorno: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY
var chatClient = new AzureOpenAIClient(
    new Uri(Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!),
    new System.ClientModel.ApiKeyCredential(
        Environment.GetEnvironmentVariable("AZURE_OPENAI_KEY")!))
    .AsChatClient("gpt-4o");

// 3. Convertir las tools MCP a AIFunction para el LLM
var aiTools = mcpTools.Select(t => t.AsAIFunction()).ToList();

// 4. Enviar un mensaje y dejar que el LLM use las tools
var response = await chatClient.CompleteAsync(
    "Procesa este texto con max 3 palabras: 'hola mundo desde mcp'",
    new ChatOptions { Tools = aiTools });

Console.WriteLine(response.Message.Text);
```

### 3. Explorar el patrón MAF (sin código)

Revisa `maf-agent-template/src/Infrastructure/Mcp/McpToolLoader.cs`:

- `GetToolsAsync()` conecta al servidor MCP configurado via SSE
- `PermissionGuardedAIFunction.WrapAll()` añade control de acceso antes de cada llamada
- Las tools resultantes se pasan al `AgentService` que llama al LLM

El agente completo sigue el patrón:
```
POST /chat → ChatCommandHandler → AgentService.ChatAsync() → [McpTools + LLM] → respuesta
```

### 4. Semantic Kernel: una alternativa

Semantic Kernel también puede trabajar con tools MCP usando `KernelFunction`:

```csharp
using Microsoft.SemanticKernel;

var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion("gpt-4o", endpoint, apiKey)
    .Build();

// Registrar tools MCP como KernelFunctions
foreach (var tool in mcpTools)
{
    kernel.Plugins.Add(KernelPluginFactory.CreateFromFunctions(
        tool.Name, [tool.AsKernelFunction()]));
}

var result = await kernel.InvokePromptAsync(
    "Procesa este texto con max 3 palabras: 'hola mundo desde mcp'");
Console.WriteLine(result);
```

---

## Referencias

- [ai-agents-for-beginners cap. 11 — Agentic Protocols](https://github.com/microsoft/ai-agents-for-beginners/tree/main/11-mcp)
- [Semantic Kernel + MCP](https://learn.microsoft.com/semantic-kernel/concepts/mcp)
- [Microsoft.Extensions.AI — IChatClient](https://learn.microsoft.com/dotnet/ai/microsoft-extensions-ai)
- [Azure AI Agents Service](https://learn.microsoft.com/azure/ai-services/agents/)

---

## Preguntas de reflexión

1. ¿Qué ventaja aporta `IChatClient` (Microsoft.Extensions.AI) frente a usar directamente el SDK de Azure OpenAI?
2. En MAF, ¿qué hace `PermissionGuardedAIFunction`? ¿Por qué es necesario en un entorno empresarial?
3. Si quisieras conectar tu agente a 3 servidores MCP distintos, ¿cómo lo harías?

---

## Fin del workshop

Revisa el [cheatsheet.md](../../cheatsheet.md) y [resources.md](../../../resources.md) para seguir aprendiendo.
