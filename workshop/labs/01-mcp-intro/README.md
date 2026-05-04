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

Vamos a inspeccionar el servidor MCP de `filesystem` (oficial de Anthropic).

> El servidor solo tiene acceso a las carpetas que le indiques al arrancarlo. Puedes pasar más de una.

Arranca el inspector apuntando a la carpeta que quieras explorar:

```powershell
mcp-inspector npx -y @modelcontextprotocol/server-filesystem "C:/Users/$env:USERNAME/Documents"
```

Puedes pasar más de una carpeta como argumento. Por ejemplo, para acceder también a este repositorio de formación:

```powershell
mcp-inspector npx -y @modelcontextprotocol/server-filesystem "C:/Users/$env:USERNAME/Documents" "C:/Users/$env:USERNAME/source/repos/formacion-grm-mcp"
```

Se abrirá el Inspector en `http://localhost:6274`. Conecta al servidor desde ahí.

### 3. Explorar las tools del servidor

En MCP Inspector:

1. Ve a la pestaña **Tools**
2. Llama a `list_directory` con uno de los paths configurados
3. Llama a `read_file` con la ruta completa del fichero

> **Windows**: usa siempre barras normales `/` en los argumentos de las tools, no `\`.
> Correcto: `C:/Users/TU_USUARIO/source/repos/formacion-grm-mcp/README.md`
> Incorrecto: `C:\Users\TU_USUARIO\source\repos\formacion-grm-mcp\README.md`

> El servidor solo puede leer ficheros dentro de las carpetas que le pasaste al arrancarlo.

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
