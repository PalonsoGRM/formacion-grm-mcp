# Fundamentos MCP — Model Context Protocol

## Qué es MCP

**Model Context Protocol (MCP)** es un protocolo abierto, presentado por Anthropic en noviembre de 2024, que estandariza cómo los LLMs se conectan a herramientas y fuentes de datos externas.

Antes de MCP, cada aplicación de IA implementaba su propia integración con cada herramienta: function calling personalizado, formatos distintos, código duplicado. MCP define una interfaz común para que cualquier modelo pueda hablar con cualquier herramienta.

> MCP es a las herramientas de IA lo que USB-C es a los dispositivos: un conector estándar.

---

## Arquitectura: Host / Client / Server

```mermaid
graph LR
    subgraph HOST["HOST — tu aplicacion"]
        direction LR
        LLM["LLM\nGPT / Claude / Phi"]
        CLIENT["MCP Client\nModelContextProtocol.Client"]
        LLM <-->|"tool calls / results"| CLIENT
    end

    CLIENT <-->|"MCP Protocol\nJSON-RPC 2.0\nHTTP + SSE / stdio"| SERVER

    subgraph SERVER["MCP SERVER — herramienta o fuente de datos"]
        direction LR
        TOOLS["Tools\nfunciones invocables"]
        RESOURCES["Resources\ndatos de solo lectura"]
        PROMPTS["Prompts\nplantillas reutilizables"]
    end

    style HOST fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style SERVER fill:#dcfce7,stroke:#16a34a,color:#14532d
```

| Componente | Rol |
|---|---|
| **Host** | Aplicación principal (IDE, chatbot, agente). Contiene el cliente MCP y el LLM. |
| **MCP Client** | Mantiene la conexión con un servidor MCP. Envía requests y recibe respuestas. |
| **MCP Server** | Expone capacidades (tools, resources, prompts) a través del protocolo. |
| **LLM** | Decide cuándo y qué tool llamar, usando las descripciones que el servidor expone. |

---

## Primitivas del protocolo

### Tools

Funciones que el LLM puede invocar. Son el equivalente a _function calling_ pero estándar.

```json
{
  "name": "convert_to_markdown",
  "description": "Converts a document to Markdown format",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" }
    },
    "required": ["file_path"]
  }
}
```

### Resources

Datos que el servidor expone para que el LLM los lea (ficheros, registros, páginas web...). Son de solo lectura y se identifican por URI.

```
https://modelcontextprotocol.io/introduction
db://customers/42
https://api.example.com/products
```

### Prompts

Plantillas de mensajes parametrizadas que el servidor ofrece como shortcuts reutilizables.

---

## Transports

MCP es independiente del transporte. Los dos principales son:

| Transport | Descripción | Cuándo usarlo |
|---|---|---|
| **stdio** | El cliente lanza el servidor como subproceso y se comunica por stdin/stdout | Local, herramientas CLI, VS Code extensions |
| **HTTP + SSE** | El servidor es un servicio HTTP. El cliente envía requests POST y recibe eventos SSE | Servicios remotos, microservicios, clientes .NET/Java |

En esta formación usamos **HTTP+SSE** en el servidor Python porque nuestro cliente C# (MAF) se conecta a servidores remotos via SSE.

---

## Flujo de una llamada MCP

```mermaid
sequenceDiagram
    participant LLM as LLM
    participant Client as Host / MCP Client
    participant Server as MCP Server

    Note over LLM,Server: 1. Inicializacion — descubrimiento de herramientas

    Client->>Server: initialize
    Server-->>Client: capabilities
    Client->>Server: tools/list
    Server-->>Client: [tool definitions: nombre, descripcion, inputSchema]
    Client-->>LLM: Herramientas disponibles

    Note over LLM,Server: 2. Ciclo de inferencia — el LLM decide llamar una tool

    LLM->>Client: tool_call: convert_to_markdown(file="report.pdf")
    Client->>Server: tools/call {name, arguments}
    Server-->>Client: {content: "# Report..."}
    Client-->>LLM: Resultado de la herramienta

    Note over LLM,Server: 3. El LLM genera la respuesta final con el resultado
```


El protocolo de mensajería es **JSON-RPC 2.0** sobre el transport elegido.

---

## Los mensajes en el cable

Cada mensaje MCP es un objeto JSON-RPC 2.0 con esta estructura base:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "...",
  "params": { ... }
}
```

A continuación, los 4 intercambios que ocurren en cada conexión.

### 1. initialize

El cliente anuncia su versión del protocolo y sus capacidades. El servidor responde con las suyas.

**Request (cliente → servidor):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": {
      "name": "ModelContextProtocol.Client",
      "version": "1.0.0"
    }
  }
}
```

**Response (servidor → cliente):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": {}
    },
    "serverInfo": {
      "name": "grm-tools",
      "version": "1.0.0"
    }
  }
}
```

### 2. notifications/initialized

El cliente confirma que la inicialización ha completado. Es una notificación (no tiene `id`, no espera respuesta).

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

### 3. tools/list

El cliente pide el catálogo de herramientas disponibles.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "echo",
        "description": "Returns the same message back.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "message": { "type": "string" }
          },
          "required": ["message"]
        }
      }
    ]
  }
}
```

El cliente pasa este catálogo al LLM. El LLM lo usa para decidir qué tool invocar y con qué argumentos.

### 4. tools/call

El LLM ha decidido llamar una tool. El cliente envía el nombre y los argumentos al servidor.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "echo",
    "arguments": {
      "message": "hola desde el inspector"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Echo: hola desde el inspector"
      }
    ],
    "isError": false
  }
}
```

Si la tool lanza una excepción, `isError` es `true` y `content[0].text` contiene el mensaje de error. El LLM recibe ese resultado y decide si reintentar o informar al usuario.

> Para la spec completa: [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification/2024-11-05)

---

## MCP vs Function Calling clásico

| Aspecto | Function Calling clásico | MCP |
|---|---|---|
| Definición de tools | En el código de la app | En el servidor MCP (descubrimiento dinámico) |
| Reutilización | Cada app re-implementa | Un servidor sirve a múltiples clientes |
| Transporte | API del proveedor de LLM | Estándar abierto (stdio / HTTP+SSE) |
| Ecosistema | Específico del modelo | Agnóstico al modelo |
| Autenticación | Ad-hoc | Definida en el protocolo (Bearer / OAuth) |

## Stack completo de la formacion

```mermaid
graph LR
    subgraph AGENT["Agente C# .NET 10"]
        SK["Semantic Kernel"]
        MCPC["ModelContextProtocol.Client"]
        SK <-->|"KernelFunction"| MCPC
    end

    subgraph SERVER["MCP Server — Python"]
        FM["fastmcp\nHTTP + SSE :8000"]
        T1["convert_to_markdown"]
        T2["fetch_url"]
        FM --> T1
        FM --> T2
    end

    AZAI["Azure OpenAI\ngpt-4o"]
    MCPC <-->|"HTTP + SSE\nJSON-RPC 2.0"| FM
    SK <-->|"chat completions"| AZAI

    style AGENT fill:#dbeafe,stroke:#3b82f6,color:#1e3a5f
    style SERVER fill:#dcfce7,stroke:#16a34a,color:#14532d
    style AZAI fill:#fef9c3,stroke:#ca8a04
```


---

## Lecturas previas recomendadas

Antes del workshop, lee al menos:

1. [MCP Introduction](https://modelcontextprotocol.io/introduction) (5 min)
2. [Core Architecture](https://modelcontextprotocol.io/docs/concepts/architecture) (10 min)
3. Capítulo 11 de [ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners) (lectura ligera)
