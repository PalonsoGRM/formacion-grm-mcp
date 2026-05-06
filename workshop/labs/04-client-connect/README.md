# Lab 4 — Crear un agente con la plantilla MAF

**Duración**: 30 min  
**Objetivo**: Generar un agente real a partir de la plantilla interna MAF y conectarlo a servidores MCP externos y propios.

---

## Prerrequisitos

- .NET 10 SDK instalado
- Git con acceso al repositorio Azure DevOps de la organización
- Servidor Python del Lab 3 arrancado (`python server.py` en `sample-server/`)

---

## Intro — Dos caminos para dar tools a un agente

La plantilla MAF permite conectar herramientas al agente de dos formas:

| Camino | Mecanismo | Cuándo usarlo |
|---|---|---|
| **MCP** | Protocolo JSON-RPC 2.0 sobre SSE | Servidores MCP: Lab 3, herramientas de terceros |
| **OpenAPI plugin** | Spec OpenAPI → `KernelFunction` | APIs REST propias ya existentes (sin servidor MCP) |

En este lab vamos a crear un agente con la plantilla, configurar el LLM y conectar los dos tipos de fuente.

---

## Paso 1 — Clonar e instalar la plantilla

Clona el repositorio de la plantilla MAF:

```bash
git clone https://gruporomeu@dev.azure.com/gruporomeu/AgentPlatform-Core/_git/maf-agent-template
cd maf-agent-template
```

Instala la plantilla dotnet (el flag `--force` reinstala si ya estuviera registrada):

```bash
dotnet new install .\maf-agent-template\ --force
```

Verifica que la plantilla está disponible:

```bash
dotnet new list maf
```

Deberías ver `maf-agent` en la lista.

---

## Paso 2 — Crear el proyecto `AgenteFormacionMcp`

Genera el proyecto a partir de la plantilla:

```bash
dotnet new maf-agent -n AgenteFormacionMcp -o C:\Users\palonso\source\repos\AgenteFormacionMcp
cd C:\Users\palonso\source\repos\AgenteFormacionMcp
```

Abre la solución en Visual Studio o VS Code:

```bash
code .
```

Explora la estructura generada:

```
AgenteFormacionMcp/
├── 01 - Api/            # Controladores y endpoints HTTP
├── 02 - Business/       # Lógica del agente y configuración del LLM
├── 03 - Infrastructure/ # Conexiones a MCP, OpenAPI y servicios externos
└── appsettings.json     # Configuración no sensible
```

> [!NOTE]
> En `03 - Infrastructure/Mcp/` es donde se configura la conexión al servidor MCP.

---

## Paso 3 — Configurar los secrets del LLM

La plantilla usa [User Secrets](https://learn.microsoft.com/aspnet/core/security/app-secrets) para credenciales locales. Nunca uses `appsettings.Development.json` para valores sensibles.

Inicializa el almacén de secrets:

```bash
dotnet user-secrets init
```

Configura el endpoint y modelo del LLM:

```bash
# LLM
dotnet user-secrets set "Llm:Endpoint"        "https://<recurso>.openai.azure.com/"
dotnet user-secrets set "Llm:DeploymentName"  "gpt-4o"
```

Verifica que los secrets están registrados:

```bash
dotnet user-secrets list
```

Con esto el agente ya puede comunicarse con Azure OpenAI. `appsettings.json` solo debe contener defaults no sensibles (timeouts, feature flags).

---

## Paso 4 — Conectar al MCP de Microsoft Learn

> [!NOTE]
> Este paso se definirá en la siguiente iteración del lab. Se conectará al servidor MCP público de Microsoft Learn para consultar documentación técnica directamente desde el agente.

---

## Paso 5 — Conectar al servidor MCP propio (Lab 3)

El servidor Python del Lab 3 es un servidor MCP válido. Para conectarlo al agente, añade la siguiente configuración en `appsettings.json`:

```json
{
  "Mcp": {
    "SseEndpoint": "http://localhost:8000/sse",
    "TimeoutSeconds": 30,
    "Tools": {
      "add": "Suma dos números",
      "fetch_url": "Descarga el contenido de una URL como texto"
    }
  }
}
```

El campo `Tools` actúa como allowlist: solo las herramientas declaradas aquí serán expuestas al LLM. Si lo dejas vacío, el agente verá todas las que exponga el servidor.

Arranca el servidor del Lab 3 y luego el agente:

```bash
# Terminal 1 — servidor MCP (Lab 3)
cd sample-server
python server.py

# Terminal 2 — agente
cd C:\repos\AgenteFormacionMcp
dotnet run
```

Envía un mensaje al agente que requiera usar una de las tools del Lab 3, por ejemplo: *"Suma 17 y 25"*. El agente debería invocar la tool `add` y devolver el resultado.

---

## Paso 6 — Alternativa OpenAPI

> [!NOTE]
> Este paso se definirá en la siguiente iteración del lab. Se verá cómo exponer una API REST existente al agente mediante su spec OpenAPI, sin necesidad de un servidor MCP adicional.

---

**Siguiente**: [Lab 5 — Azure AI Agents + Semantic Kernel](../05-agent-integration/README.md)
