# Contexto del repositorio: Formacion GRM — MCP

Este repositorio contiene el material de formación de media jornada sobre **Model Context Protocol (MCP)** para el equipo de developers de GRM.

## Estructura

- `mcp-fundamentals/` — teoria: arquitectura MCP, primitivas, transports
- `sample-server/` — servidor MCP Python (fastmcp) con HTTP+SSE
- `sample-client/` — cliente MCP C# .NET 10 (`ModelContextProtocol.Client`)
- `workshop/labs/` — 5 labs prácticos progresivos

## Stack tecnológico

- **Servidor**: Python 3.11+, fastmcp, transporte HTTP+SSE
- **Cliente**: C# .NET 10, `ModelContextProtocol.Client` NuGet
- **Agent framework**: Azure AI Agents (Microsoft.Extensions.AI) + Semantic Kernel
- **Plataforma interna referencia**: MAF (`maf-agent-template`)

## Convenciones

- Los labs son independientes pero progresivos: cada uno construye sobre el anterior.
- El código de ejemplo usa siempre nombres descriptivos en inglés.
- Los READMEs de los labs incluyen siempre: objetivo, prerrequisitos, pasos, verificacion.
- El servidor Python usa SSE (no stdio) para ser consumible desde clientes C#.
- Los snippets de C# siguen Clean Architecture (separacion Infra/Business/Domain).
