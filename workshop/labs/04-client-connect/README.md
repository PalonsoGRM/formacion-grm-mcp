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

## Primitivas en contexto

En los Labs 1-3 viste que MCP define tres primitivas: **tools**, **resources** y **prompts**. Antes de configurar las integraciones, veamos cómo se mapean a los servidores de este lab.

| Servidor | Transport | Tools | Resources | Prompts |
|---|---|---|---|---|
| `server-everything` (oficial, sin auth) | HTTP + SSE (`localhost:3001`) | `echo`, `get-sum`, ... | `demo://resource/dynamic/text/{n}` | `simple-prompt`, `args-prompt` |
| Postman MCP (`mcp.postman.com`) | HTTP | collections, workspaces, ... | No | No |
| Microsoft Learn MCP | HTTP + SSE | `microsoft_docs_search` | No | No |
| ApiPlugin RAG compliance | OpenAPI plugin — no es MCP | `ApiPlugin_RomeuCompliance` | — | — |
| Servidor Lab 3 (Python) | HTTP + SSE | `add`, `fetch_url` | `echo://` | `debug_error` |

**Por qué los MCPs comerciales solo usan tools:**

- **Tools** son la primitiva más universal: el LLM las invoca explícitamente cuando las necesita. Es lo mínimo que cualquier servidor MCP implementa.
- **Resources** son datos que el servidor expone pasivamente para que el cliente los adjunte al contexto (similar a adjuntar un documento). Útiles cuando la información es estática o cambia poco.
- **Prompts** son plantillas reutilizables que el cliente (el IDE, el agente) puede ofrecer al usuario como punto de partida. Aparecen más en entornos interactivos como VS Code Copilot.

En la práctica, los servidores comerciales solo implementan tools porque es lo que el LLM puede invocar autónomamente. Resources y prompts se usan principalmente en servidores de desarrollo y en los servidores de referencia.

> [!NOTE]
> El servidor oficial de referencia del equipo MCP, `server-everything`, demuestra las tres primitivas sobre HTTP. Corre localmente sin auth con `npx @modelcontextprotocol/server-everything sse` (puerto 3001) y se conecta exactamente igual que el servidor del Lab 3. Es el punto de partida para explorar resources y prompts antes de implementarlos en un servidor propio.

**OpenAPI plugin ≠ MCP.** El ApiPlugin del Paso 5 no implementa el protocolo MCP: la plantilla MAF lee la spec OpenAPI y genera `KernelFunction`s de Semantic Kernel a partir de los endpoints. No hay JSON-RPC, no hay primitivas — es una forma alternativa de exponer herramientas al LLM cuando ya tienes una API REST.

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

> [!NOTE]
> La configuración del servidor MCP vive en `03 - Infrastructure/Mcp/`. Las specs OpenAPI para el ApiPlugin van en `03 - Infrastructure/ApiPlugin/Specs/`. El punto de entrada HTTP está en `04 - Host/`.

---

## Paso 3 — Configurar los secrets del LLM e identidad

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

La plantilla no usa API Key. En su lugar, la autenticación con Azure AI Foundry se delega a `DefaultAzureCredential`, que en local usa la sesión de `az login`. El cliente Swagger de test está registrado en Entra con los scopes necesarios para poder invocar el recurso de AI Foundry directamente desde el navegador.

Configura también los datos de identidad del tenant y la aplicación:

```bash
# Identity
dotnet user-secrets set "Identity:AzureAd:TenantId"              "<tenant-id>"
dotnet user-secrets set "Identity:AzureAd:ClientId"              "<client-id>"
dotnet user-secrets set "Identity:SwaggerClient:ClientId"        "<swagger-client-id>"
dotnet user-secrets set "Identity:SwaggerClient:Scopes"          "api://<client-id>/.default"
```

> [!NOTE]
> En producción (DEV/PRE/PRO) se usa `ManagedIdentityCredential` en lugar de `DefaultAzureCredential`. El código de la plantilla ya contempla el cambio según el entorno con `#if DEBUG`.

Verifica que los secrets están registrados:

```bash
dotnet user-secrets list
```

`appsettings.json` solo debe contener defaults no sensibles (timeouts, feature flags, logging).

---

## Paso 4 — Conectar al MCP de Microsoft Learn

Microsoft expone un servidor MCP público que permite consultar la documentación oficial de Microsoft Learn directamente desde cualquier agente compatible. El agente invocará la tool `microsoft_docs_search` cuando el usuario haga preguntas técnicas sobre tecnologías Microsoft.

Añade la configuración en `appsettings.json`:

```json
{
  "Mcp": {
    "SseEndpoint": "https://learn.microsoft.com/api/mcp",
    "TimeoutSeconds": 30
  }
}
```

Arranca el agente y abre Swagger en `https://localhost:<puerto>/swagger`. Envía esta petición:

```json
{
  "prompt": "dame una descripcion de Agentic framework"
}
```

El agente invocará automáticamente `microsoft_docs_search` y devolverá la respuesta:

![Respuesta Swagger — Microsoft Learn MCP](assets/mcp-microsoft-learn-response.png)

En el log del agente verás la invocación de la tool:

![Log — microsoft_docs_search invocado](assets/mcp-microsoft-learn-log.png)

Prueba también con:

```json
{
  "prompt": "qué es el protocolo MCP y cómo se integra con agentes de IA?"
}
```

---

## Paso 5 — Conectar una API REST via OpenAPI plugin

Además de MCP, la plantilla MAF permite exponer APIs REST existentes al agente mediante su spec OpenAPI. No necesitas un servidor MCP adicional: el agente genera `KernelFunction`s automáticamente a partir de la spec y las registra como tools disponibles para el LLM.

En este ejemplo conectamos el RAG de compliance de GRM, que responde preguntas sobre la documentación interna de la empresa.

Añade la configuración en `appsettings.json`:

```json
{
  "ApiPlugin": {
    "Name": "RomeuCompliance",
    "BaseUrl": "https://<apim-host>/compliance/",
    "OpenApiDefinitionUrl": "https://<apim-host>/compliance/openapi/json"
  }
}
```

Arranca el agente y envía en Swagger:

```json
{
  "prompt": "Puedo llevar pantalones en la oficina según la documentación de compliance de GRM?"
}
```

En el log verás que el agente ha invocado el plugin:

![Log — ApiPlugin_RomeuCompliance invocado](assets/apiplugin-compliance-log.png)

Y la respuesta del agente con la información extraída del RAG:

![Respuesta Swagger — Compliance query](assets/apiplugin-compliance-response.png)

> [!NOTE]
> El nombre del plugin (`RomeuCompliance`) determina el prefijo que verás en los logs: `ApiPlugin_RomeuCompliance(userPrompt)`. Puedes cambiar el nombre en `appsettings.json` para adaptarlo a cualquier API.

---

## Paso 6 — Conectar al servidor MCP propio (Lab 3)

El servidor Python del Lab 3 es un servidor MCP válido. Para conectarlo al agente, modifica la configuración `Mcp` en `appsettings.json` apuntando a tu servidor local:

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

## Preguntas de reflexión

> [!NOTE]
> Intenta responder antes de desplegar. Son conceptos clave que conectan lo visto en los Labs anteriores con el trabajo real en la plataforma MAF.

---

**1. ¿Cuál es la diferencia entre conectar un servidor MCP y añadir un OpenAPI plugin al agente?**

<details>
<summary>Mostrar respuesta</summary>

> MCP usa el protocolo JSON-RPC 2.0 con primitivas estandarizadas (tools, resources, prompts). OpenAPI plugin no es MCP.

Con **MCP** el agente se conecta a un servidor externo que ya implementa el protocolo. La comunicación es JSON-RPC sobre SSE: el servidor gestiona sus propias herramientas, puede exponer resources y prompts, y cualquier cliente MCP compatible puede consumirlo.

Con **OpenAPI plugin** no hay servidor MCP. Semantic Kernel lee la spec OpenAPI y genera `KernelFunction`s dinámicamente — el agente llama directamente a los endpoints REST. Es más sencillo de integrar si ya tienes una API documentada, pero el servidor no puede iniciar comunicación ni exponer resources.

| | MCP | OpenAPI plugin |
|---|---|---|
| Protocolo | JSON-RPC 2.0 | HTTP REST directo |
| Tools | `CallTool` | `KernelFunction` generada |
| Resources | Sí | No |
| Prompts | Sí | No |
| Requiere servidor dedicado | Sí | No (basta la spec) |

</details>

---

**2. ¿Por qué la plantilla MAF usa `DefaultAzureCredential` en local y `ManagedIdentityCredential` en producción?**

<details>
<summary>Mostrar respuesta</summary>

> Porque en local no hay identidad gestionada — el desarrollador se autentica con `az login`. En producción, la aplicación tiene una identidad asignada por Azure.

`DefaultAzureCredential` prueba múltiples mecanismos en orden (env vars, workload identity, CLI, VS...). Es conveniente en desarrollo pero demasiado permisivo para producción.

`ManagedIdentityCredential` solo usa la identidad asignada al recurso (App Service, AKS pod, Container App). Es predecible, no depende de configuración del desarrollador y no requiere secretos — Azure gestiona el ciclo de vida del token.

```csharp
#if DEBUG
    TokenCredential credential = new DefaultAzureCredential();
#else
    TokenCredential credential = new ManagedIdentityCredential();
#endif
```

Ningún secreto de LLM se escribe en código — siempre se inyecta vía User Secrets (local) o Key Vault (producción).

</details>

---

**3. En la tabla "Primitivas en contexto", el Microsoft Learn MCP solo expone tools. ¿Qué tendría que añadir para exponer también resources y prompts? ¿Tiene sentido que lo haga?**

<details>
<summary>Mostrar respuesta</summary>

> Tendría que implementar los handlers `resources/list` + `resources/read` y `prompts/list` + `prompts/get` en su servidor.

**Resources** tendría sentido para exponer contenido estático o indexado: por ejemplo un catálogo de módulos de aprendizaje como `learn://modules/az-900` que el agente pueda leer antes de responder. Evitaría hacer búsquedas innecesarias para contenido conocido.

**Prompts** tendría sentido para ofrecer plantillas de consulta reutilizables: `explain-concept(topic, level)`, `learning-path(role, skills)` — el cliente las descubrirían con `prompts/list` y el usuario las seleccionaría en la UI del IDE.

En la práctica, los MCPs de terceros tienden a exponer solo tools porque es lo que los clientes actuales aprovechan mejor. Resources y prompts son primitivas menos explotadas en los hosts existentes (VS Code, Claude Desktop...).

</details>

---

**4. El campo `Tools` en la configuración MCP actúa como allowlist. ¿Qué problema resuelve esto desde el punto de vista de seguridad?**

<details>
<summary>Mostrar respuesta</summary>

> Evita que el LLM invoque herramientas que el agente no debería usar en ese contexto — especialmente si el servidor expone más tools de las necesarias.

Sin allowlist, si el servidor MCP añade nuevas tools en el futuro el agente las vería automáticamente. Esto puede ser un riesgo: una tool de administración que no debería estar disponible en el contexto del chat con usuarios finales podría ser invocada por el LLM si recibe el prompt adecuado.

Con la allowlist explícita:
- El equipo controla exactamente qué capacidades tiene el agente en producción
- Añadir una nueva tool al servidor no cambia el comportamiento del agente hasta que se actualiza la configuración intencionadamente
- Reduce la superficie de ataque ante prompt injection

</details>

---

**Siguiente**: [Lab 5 — Azure AI Agents + Semantic Kernel](../05-agent-integration/README.md)
