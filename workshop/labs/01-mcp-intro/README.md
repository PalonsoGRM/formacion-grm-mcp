# Lab 1 — Intro y arquitectura MCP

**Duración**: 20 min  
**Objetivo**: Entender la arquitectura MCP (Host / Client / Server), las primitivas del protocolo y explorar un servidor MCP existente con MCP Inspector.

---

## Prerrequisitos

- MCP Inspector instalado: `npm install -g @modelcontextprotocol/inspector`
- Acceso a internet para clonar `modelcontextprotocol/servers`

---

## Pasos

### 1. Revisar el diagrama de arquitectura

Lee [mcp-fundamentals/README.md](../../../mcp-fundamentals/README.md) y asegúrate de entender:

- El papel de **Host**, **Client** y **Server**
- Las tres primitivas: **Tools**, **Resources**, **Prompts**
- La diferencia entre transporte **stdio** y **HTTP+SSE**

### 2. Explorar un servidor MCP real

Vamos a inspeccionar el servidor MCP de `filesystem` (oficial de Anthropic):

```bash
# Arrancar el servidor MCP de filesystem y conectarlo a MCP Inspector
# (npm install -g @modelcontextprotocol/inspector si aun no lo tienes)
mcp-inspector npx -y @modelcontextprotocol/server-filesystem C:\Users\TU_USUARIO\Documents
```

> En macOS/Linux usa una ruta válida, p.ej. `~/Documents`.

### 3. Explorar las tools del servidor

En MCP Inspector:

1. Ve a la pestaña **Tools**
2. Lista las tools disponibles
3. Llama a `list_directory` con el path configurado
4. Llama a `read_file` con un fichero existente

### 4. Observar los mensajes JSON-RPC

En MCP Inspector, ve a **Messages** para ver el tráfico JSON-RPC 2.0 entre cliente y servidor.

Fíjate en:
- El mensaje `initialize` y la respuesta con las capacidades del servidor
- El mensaje `tools/list` y la respuesta con el schema de cada tool
- El mensaje `tools/call` y la respuesta con el resultado

---

## Preguntas de reflexión

1. ¿Qué diferencia hay entre una **Tool** y un **Resource**?
2. ¿Por qué el servidor `filesystem` usa transporte **stdio** y no SSE?
3. ¿Qué ventaja tiene MCP frente a implementar function calling directamente en el LLM?

---

## Siguiente paso

[Lab 2 — Usar markitdown MCP existente](../02-use-existing-mcp/README.md)
