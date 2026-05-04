# Recursos y referencias

## Especificacion MCP

- [Spec oficial Model Context Protocol](https://spec.modelcontextprotocol.io) — documentación completa del protocolo
- [Repositorio oficial MCP](https://github.com/modelcontextprotocol) — SDKs, servidores de referencia, docs

## Servidores MCP de referencia

- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) — catálogo de servidores MCP oficiales (filesystem, git, GitHub, Postgres, Puppeteer, etc.)
- [microsoft/markitdown](https://github.com/microsoft/markitdown) — MCP server para convertir documentos a Markdown (PDF, Office, HTML, imágenes)

## Librería Python para servidores MCP

- [fastmcp](https://github.com/jlowin/fastmcp) — librería Python de alto nivel para crear servidores MCP
- [mcp (SDK oficial Python)](https://github.com/modelcontextprotocol/python-sdk) — SDK oficial de bajo nivel

## Cliente MCP para C# / .NET

- [ModelContextProtocol NuGet](https://www.nuget.org/packages/ModelContextProtocol) — cliente oficial .NET
- [ModelContextProtocol.NET GitHub](https://github.com/modelcontextprotocol/csharp-sdk) — código fuente del SDK C#

## Azure AI Agents y Semantic Kernel

- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel) — framework de Microsoft para agentes con LLMs
- [Microsoft.Extensions.AI](https://learn.microsoft.com/dotnet/ai/microsoft-extensions-ai) — abstracción IChatClient para .NET
- [Azure AI Agents Service](https://learn.microsoft.com/azure/ai-services/agents/) — servicio gestionado de agentes en Azure
- [ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners) — curso introductorio; ver capítulo 11 (agentic protocols / MCP)

## Plataforma interna (MAF)

- `maf-agent-template` — plantilla interna de agentes. Ver `Infrastructure/Mcp/McpToolLoader.cs` para ver cómo se integra `ModelContextProtocol.Client` en nuestra plataforma.

## Lecturas recomendadas

- [Introducing MCP (Anthropic blog)](https://www.anthropic.com/news/model-context-protocol) — post original de lanzamiento
- [MCP: The New Standard for AI Tool Integration](https://modelcontextprotocol.io/introduction) — introducción conceptual
- [Building agents with MCP (Semantic Kernel)](https://learn.microsoft.com/semantic-kernel/concepts/mcp) — integración MCP + SK
