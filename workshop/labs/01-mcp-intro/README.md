# Lab 1 — Intro y arquitectura MCP

**Duración**: 20 min  
**Objetivo**: Entender la arquitectura MCP (Host / Client / Server), las primitivas del protocolo y explorar un servidor MCP existente con MCP Inspector.

---

## Prerrequisitos

- MCP Inspector instalado: `npm install -g @modelcontextprotocol/inspector`
- Acceso a internet para descargar `@modelcontextprotocol/server-filesystem`

---

## Qué es MCP Inspector

**MCP Inspector** es una herramienta de desarrollo web que permite conectarse a cualquier servidor MCP, explorar sus capacidades e invocar sus tools manualmente — sin escribir código.

Es el equivalente a Postman o Swagger UI pero para el protocolo MCP. Resulta imprescindible para:

- Verificar que un servidor arranca y responde correctamente
- Explorar qué tools, resources y prompts expone
- Depurar los mensajes JSON-RPC 2.0 que se intercambian
- Probar argumentos de tools antes de integrarlos en un cliente

En producción no se usa, pero durante el desarrollo es la forma más rápida de validar que un servidor MCP funciona antes de conectarle un cliente C# o un agente.

---

## Pasos

### 1. Revisar el diagrama de arquitectura

Lee [mcp-fundamentals/README.md](../../../mcp-fundamentals/README.md) y asegúrate de entender:

- El papel de **Host**, **Client** y **Server**
- Las tres primitivas: **Tools**, **Resources**, **Prompts**
- La diferencia entre transporte **stdio** y **HTTP+SSE**

### 2. Arrancar MCP Inspector con el servidor filesystem

Vamos a inspeccionar el servidor MCP de `filesystem` (oficial de Anthropic).

> El servidor solo tiene acceso a las carpetas que le indiques al arrancarlo. Puedes pasar más de una.

Arranca el inspector apuntando a las carpetas que quieras explorar:

```powershell
mcp-inspector npx -y @modelcontextprotocol/server-filesystem "C:/Users/$env:USERNAME/Documents" "C:/Users/$env:USERNAME/source/repos/formacion-grm-mcp"
```

Se abrirá el Inspector en `http://localhost:6274`.

### 3. Conectar al servidor

En el panel izquierdo del Inspector:

1. **Transport Type**: `STDIO` (el servidor filesystem usa stdio, no HTTP)
2. **Command**: `npx`
3. **Arguments**: `-y @modelcontextprotocol/server-filesystem C:/Users/TU_USUARIO/source/repos/formacion-grm-mcp`
4. Haz clic en **Connect**
5. El indicador verde **Connected** confirma la conexión

### 4. Listar las tools disponibles

1. Ve a la pestaña **Tools** (panel central)
2. Haz clic en **List Tools**
3. Aparecerá la lista de tools que expone el servidor: `read_file`, `read_text_file`, `list_directory`, `write_file`, etc.

### 5. Usar Read Text File

![MCP Inspector — Read Text File](./images/inspector-read-file.png)

1. Haz clic sobre **Read Text File** en la lista de tools
2. En el panel derecho aparece el formulario de argumentos
3. En el campo **path** (obligatorio, marcado con `*`) introduce la ruta con barras normales `/`:

```
C:/Users/TU_USUARIO/source/repos/formacion-grm-mcp/README.md
```

4. Haz clic en **Run Tool**
5. El resultado aparece debajo: el contenido del fichero en texto plano

> **Windows**: usa siempre `/` en los paths, nunca `\`. Node.js los acepta igual.

> El servidor solo puede leer ficheros dentro de las carpetas que le pasaste al arrancarlo. Si el fichero está fuera, obtendrás un error `ENOENT` o `Access denied`.

### 6. Observar los mensajes JSON-RPC

En la sección **History** (parte inferior del panel central) puedes ver los mensajes en orden:

1. `initialize` — handshake inicial con las capacidades del servidor
2. `tools/list` — petición y respuesta con el schema de cada tool
3. `tools/call` — llamada a la tool con los argumentos y la respuesta con el resultado

Abre cada uno para ver el JSON-RPC 2.0 raw. Esto es exactamente lo que el cliente C# enviará en el Lab 4.

---

## Preguntas de reflexión

1. ¿Qué diferencia hay entre una **Tool** y un **Resource**?
2. ¿Por qué el servidor `filesystem` usa transporte **stdio** y no SSE?
3. ¿Qué ventaja tiene MCP frente a implementar function calling directamente en el LLM?

---

## Siguiente paso

[Lab 2 — Usar markitdown MCP existente](../02-use-existing-mcp/README.md)

---

## Referencias

- [MCP Inspector — documentacion oficial](https://modelcontextprotocol.io/docs/tools/inspector)
- [Especificacion del protocolo MCP](https://modelcontextprotocol.io/docs/concepts/architecture)
- [Servidor MCP Filesystem (npm)](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem)
- [SDK MCP — repositorio oficial](https://github.com/modelcontextprotocol/modelcontextprotocol)
