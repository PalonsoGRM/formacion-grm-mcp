# sample-client — Agente MAF con MCP

Agente de ejemplo construido durante el **Lab 4**.

## Stack

| | |
|---|---|
| Lenguaje | C# |
| Runtime | .NET 10 |
| Framework | Semantic Kernel + Azure AI Agents |
| Plantilla | `maf-agent-template` (repositorio interno) |
| Patrón | `McpToolLoader.cs` en MAF (`maf-agent-template`) |

## Lo que construye el Lab 4

El Lab 4 no crea un cliente MCP standalone — crea un **agente completo** a partir de la plantilla interna MAF. El agente conecta herramientas de dos formas:

| Integración | Mecanismo | Servidor |
|---|---|---|
| Microsoft Learn | MCP sobre SSE | `https://learn.microsoft.com/api/mcp` |
| Lab 3 (Python) | MCP sobre SSE | `http://localhost:8000/sse` |
| Compliance RAG | OpenAPI plugin | API interna GRM |

## Dónde vive el proyecto

El proyecto se genera fuera de este repositorio usando la plantilla:

```powershell
dotnet new maf-agent -n AgenteFormacionMcp -o C:\repos\AgenteFormacionMcp
```

La configuración de los servidores MCP vive en `03 - Infrastructure/Mcp/` dentro del proyecto generado.

## Inicio rápido

```powershell
# Con el servidor del Lab 3 corriendo en localhost:8000
cd C:\repos\AgenteFormacionMcp
dotnet run
```

Requiere el servidor Python de `sample-server/` corriendo en `http://localhost:8000/sse`.

---

El agente se construye paso a paso en [Lab 4](../workshop/labs/04-client-connect/README.md).

Para ver cómo se integra MCP en la plataforma, consulta `McpToolLoader.cs` en `maf-agent-template`.

