# Prerequisitos

Antes de la sesión, asegúrate de tener instalado y verificado todo lo que aparece en esta guia.

---

## Python (servidor MCP)

### Requisitos

| Herramienta | Version minima | Verificación |
|---|---|---|
| Python | 3.11 | `python --version` |
| uv | ultima | `uv --version` |
| fastmcp | ultima | `python -c "import fastmcp; print(fastmcp.__version__)"` |

### Instalación

```bash
# Instalar uv (gestor de entornos y paquetes Python moderno)
pip install uv

# Crear entorno virtual e instalar dependencias en sample-server/
cd sample-server
uv venv
uv pip install "mcp[cli]" fastmcp
```

---

## .NET (cliente MCP)

### Requisitos

| Herramienta | Version minima | Verificación |
|---|---|---|
| .NET SDK | 10.0 | `dotnet --version` |

### Instalación

Descarga el SDK desde https://dotnet.microsoft.com/download

---

## MCP Inspector

Herramienta visual para explorar y probar servidores MCP sin escribir código.

```bash
npx @modelcontextprotocol/inspector
```

Requiere Node.js 18+. Verifica con `node --version`.

---

## VS Code y extensiones

| Extension | Para qué |
|---|---|
| Python (Microsoft) | Servidor Python |
| C# Dev Kit (Microsoft) | Cliente C# |
| GitHub Copilot | Labs 1 y 2 |

---

## Script de verificación

Ejecuta este script para confirmar que tienes todo listo:

```bash
python --version          # >= 3.11
uv --version
dotnet --version          # >= 10.0
node --version            # >= 18 (para MCP Inspector)
npx @modelcontextprotocol/inspector --version
```

Si algún comando falla, revisa la sección correspondiente y contacta al formador antes de la sesión.
