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

> [!NOTE]
> Intenta responder antes de desplegar. Son conceptos clave que aparecen en todos los labs siguientes.

---

**1. ¿Qué diferencia hay entre una Tool y un Resource?**

<details>
<summary>Mostrar respuesta</summary>

> **Tool = verbo. Resource = sustantivo.**

Una **Tool** es una acción que el LLM invoca para hacer algo: leer un fichero, llamar a una API, ejecutar código. Tiene argumentos de entrada y devuelve un resultado.

Un **Resource** es contenido estático o semi-estático que el servidor expone para que el cliente lo lea directamente, sin que el LLM lo "ejecute" (un documento, un esquema, el estado de una base de datos). El LLM puede incluirlo en su contexto pero no lo invoca como función.

</details>

---

**2. ¿Por qué el servidor `filesystem` usa transporte stdio y no SSE?**

<details>
<summary>Mostrar respuesta</summary>

> Porque es un proceso local, no un servicio de red.

El servidor filesystem se ejecuta como proceso hijo del host. El transporte `stdio` es lo más sencillo: el host arranca el proceso y se comunica con él a través de stdin/stdout, sin abrir puertos ni gestionar conexiones HTTP.

**SSE** (HTTP + Server-Sent Events) se usa cuando el servidor MCP es un servicio remoto al que varios clientes se conectan simultáneamente.

</details>

---

**3. ¿Qué ventaja tiene MCP frente a implementar function calling directamente en el LLM?**

<details>
<summary>Mostrar respuesta</summary>

> Con function calling nativo cada integración es ad-hoc y queda acoplada a un modelo concreto.

MCP estandariza la capa de herramientas con un protocolo único (JSON-RPC 2.0):

- El mismo servidor funciona con cualquier cliente compatible (Claude, GPT, Semantic Kernel...)
- Reutilizas servidores de terceros sin tocar tu código de agente
- El servidor puede evolucionar o desplegarse de forma independiente
- La seguridad y el control de acceso se gestionan en el servidor, no en el prompt

</details>

---

## Otros servidores para probar con el Inspector

Todos usan transporte `STDIO`. Sustitye `TU_USUARIO` por tu nombre de usuario de Windows.

**Everything** — servidor de prueba oficial con todas las primitivas (tools, resources, prompts):

```powershell
npx -y @modelcontextprotocol/server-everything
```

**Git** — expone el historial, diffs y ramas de un repositorio local:

```powershell
npx -y @modelcontextprotocol/server-git --repository "C:/Users/TU_USUARIO/source/repos/formacion-grm-mcp"
```

**GitHub** — acceso a repos, issues y PRs (requiere token):

En Arguments del Inspector:
```
-y @modelcontextprotocol/server-github
```
Y en Environment Variables añade `GITHUB_PERSONAL_ACCESS_TOKEN` con tu token.

**Fetch** — descarga y convierte URLs a texto/markdown, util para dar contexto web al LLM:

```powershell
npx -y @modelcontextprotocol/server-fetch
```

> Todos estos servidores son oficiales y están en [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers).

---

## Siguiente paso

[Lab 2 — Usar markitdown MCP existente](../02-use-existing-mcp/README.md)

---

## Referencias

- [MCP Inspector — documentacion oficial](https://modelcontextprotocol.io/docs/tools/inspector)
- [Especificacion del protocolo MCP](https://modelcontextprotocol.io/docs/concepts/architecture)
- [Servidor MCP Filesystem (npm)](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem)
- [SDK MCP — repositorio oficial](https://github.com/modelcontextprotocol/modelcontextprotocol)
