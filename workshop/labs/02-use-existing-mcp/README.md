# Lab 2 — Usar markitdown MCP existente

**Duración**: 25 min  
**Objetivo**: Instalar y configurar `microsoft/markitdown` como servidor MCP en VS Code y usarlo desde GitHub Copilot Chat para convertir documentos.

---

## Prerrequisitos

- VS Code con GitHub Copilot habilitado
- Python 3.11+ y uv instalados
- `uv` o `uvx` disponible en PATH

---

## Pasos

### 1. Instalar markitdown MCP

markitdown ofrece un servidor MCP que permite a cualquier LLM convertir documentos (PDF, Word, Excel, HTML, imágenes...) a Markdown.

```bash
# Instalar con uv (recomendado)
uv tool install markitdown-mcp

# Verificar
uvx markitdown-mcp --version
```

### 2. Configurar el servidor en VS Code

Crea o edita `.vscode/mcp.json` en tu workspace:

```json
{
  "servers": {
    "markitdown": {
      "command": "uvx",
      "args": ["markitdown-mcp"]
    }
  }
}
```

> Alternativa: en `settings.json` bajo la clave `"mcp.servers"`.

Reinicia VS Code o recarga la configuración MCP (Command Palette: `MCP: Restart Servers`).

### 3. Verificar que el servidor está activo

En VS Code, abre Copilot Chat y comprueba que aparece el icono de herramientas. Puedes listar las tools disponibles escribiendo:

```
@workspace ¿Qué tools tienes disponibles?
```

### 4. Convertir un documento

Prueba con un fichero local:

```
Convierte el fichero C:\ruta\a\tu\documento.pdf a Markdown
```

o

```
Lee https://github.com/microsoft/markitdown y conviértelo a Markdown resumido
```

### 5. Explorar otro servidor MCP (opcional)

Navega a [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) y elige otro servidor que te parezca útil (git, fetch, puppeteer...).

Instálalo y conéctalo de la misma forma.

---

## Qué ha pasado por debajo

Cuando Copilot usó markitdown:

1. VS Code (Host) lanzó `uvx markitdown-mcp` como subproceso (transporte **stdio**)
2. El Host envió `tools/list` para descubrir las tools
3. Copilot (LLM) recibió las definiciones de tools y decidió llamar a `convert`
4. El Host envió `tools/call` con los argumentos al servidor
5. El resultado (Markdown) llegó de vuelta al LLM para responder

---

## Preguntas de reflexión

1. ¿Qué transporte usa markitdown aquí? ¿stdio o SSE?
2. ¿Podría un cliente C# conectarse a este servidor? ¿Qué habría que cambiar?
3. ¿Qué otros servidores MCP podría ser útil tener en tu flujo de trabajo?

---

## Siguiente paso

[Lab 3 — Construir un servidor MCP en Python](../03-build-server/README.md)
