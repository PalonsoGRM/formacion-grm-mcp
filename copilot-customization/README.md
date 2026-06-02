# Copilot CLI — Controlar el contexto y ahorrar tokens

## El problema: el contexto cuesta tokens

Cada mensaje que envías a Copilot CLI incluye, además de tu pregunta, todo el **contexto** que el modelo necesita para responder bien: instrucciones del proyecto, historial de la conversación, salidas de herramientas, etc.

```
[ instrucciones ] + [ historial ] + [ tu pregunta ] + [ salidas de tools ]
                             = tokens consumidos = coste + calidad
```

Más contexto = respuestas más precisas, pero también más tokens. El objetivo es ser **intencional**: meter lo que importa, descartar lo que no.

Copilot CLI ofrece cuatro mecanismos para controlar esto:

| Mecanismo | Cuándo se carga | Impacto en tokens |
|---|---|---|
| **Instructions** | Siempre, en cada prompt | Fijo — mantenerlas cortas y precisas |
| **Skills** | Solo cuando son relevantes | Bajo demanda — no consumen si no aplican |
| **Custom Agents** | Cuando los invocas | Contexto separado — no contamina la sesión principal |
| **Hooks** | En eventos concretos | Controlado — solo cuando ocurre el evento |

---

## Instructions — contexto permanente

Son ficheros Markdown que se inyectan en **cada prompt** de la sesión. Son el lugar donde describes tu proyecto, tu stack, y tus convenciones.

**Ficheros reconocidos:**

```
.github/copilot-instructions.md       → todo el repo, siempre
.github/instructions/*.instructions.md → solo cuando aplica el patrón applyTo
AGENTS.md                              → compatible con Claude, Gemini, etc.
~/.copilot/copilot-instructions.md    → tu usuario, todos los repos
```

**Truco de tokens:** usa `applyTo` para que las instrucciones de C# solo se carguen cuando hay ficheros `.cs` abiertos:

```markdown
---
applyTo: "**/*.cs"
---

- Usa ManagedIdentityCredential en entornos desplegados.
- Nunca pongas secretos en appsettings.json.
```

Sin `applyTo`, las instrucciones siempre están en el contexto. Cuanto más cortas y concretas, mejor.

> Este repo ya tiene `.github/copilot-instructions.md`. Muestra el stack, las convenciones, y cómo debe comportarse Copilot aquí.

---

## Skills — instrucciones bajo demanda

Las instrucciones siempre se cargan. Las Skills, no: Copilot las carga **solo si la `description` es relevante para lo que le pides**.

```
.github/skills/
└── grm-deploy/
    ├── SKILL.md       ← frontmatter con name + description
    └── deploy.sh      ← script opcional que la skill puede invocar
```

```markdown
---
name: grm-deploy
description: Despliega servicios GRM a Azure. Usa esto cuando el usuario pida hacer deploy, publicar o subir cambios.
---

1. Verifica tests: `dotnet test`
2. Build imagen: `docker build -t grm-service .`
3. Publica: `az acr build ...`
```

**Clave:** la `description` es el criterio de activación. El cuerpo del fichero (el procedimiento) solo entra en contexto cuando la skill se activa. Para tareas largas o especializadas, esto es mucho más eficiente que meterlo todo en las instructions.

---

## Custom Agents — contexto completamente separado

Un Custom Agent es un asistente con nombre, rol y herramientas propias que corre en una **ventana de contexto independiente**. Cuando le delegas trabajo, ese trabajo no contamina tu sesión principal.

```markdown
---
name: grm-reviewer
description: Revisor de PRs del stack GRM. Analiza C#, verifica convenciones de seguridad y arquitectura.
tools:
  - read_file
  - run_terminal_command
---

Eres un revisor senior. Comprueba siempre:
- Sin secretos hardcodeados ni en appsettings.json
- ManagedIdentityCredential en producción
- Nuevos endpoints con tests de integración
```

**Por qué ahorra tokens:** una revisión de PR puede generar miles de tokens de salida (diffs, análisis, sugerencias). Si eso ocurre en el agente principal, queda en el historial y consume contexto en cada turno siguiente. Con un Custom Agent, el trabajo pesado ocurre en su propia ventana y no arrastra tu sesión.

Invocación:

```
/agent        → selecciona de la lista
Use the grm-reviewer agent to review this PR  → invocación natural
```

---

## Hooks — inyección contextual en eventos

Los Hooks ejecutan un comando de shell y añaden su salida al contexto en momentos concretos del ciclo de sesión.

```json
{
  "version": 1,
  "hooks": [
    {
      "event": "sessionStart",
      "command": "git log --oneline -5 && git status --short"
    }
  ]
}
```

**Eventos útiles:**

| Evento | Uso típico |
|---|---|
| `sessionStart` | Inyectar estado Git, sprint activo, tickets abiertos |
| `preToolUse` | Validar antes de que el agente ejecute algo |
| `userPromptSubmitted` | Añadir contexto dinámico a cada mensaje |

**Truco:** sin un hook de `sessionStart`, tendrías que pegar manualmente `git status` cada vez que abres Copilot. Con el hook, ese contexto llega solo y no ocupa espacio en tu historial de conversación.

Ubicación: `.github/hooks/<nombre>.json` (repo) o `~/.copilot/hooks/<nombre>.json` (usuario).

---

## Gestionar el contexto en sesión

Copilot CLI incluye comandos para monitorizar y controlar el contexto en tiempo real:

| Comando | Qué hace |
|---|---|
| `/context` | Vista visual del uso actual del token window |
| `/usage` | Estadísticas de la sesión: tokens por modelo, requests premium |
| `/compact` | Comprime el historial manualmente para liberar espacio |
| `/instructions` | Ver qué ficheros de instrucciones están activos |
| `/env` | Ver todo lo cargado: instructions, skills, MCP servers, agents |

Copilot CLI también comprime el historial automáticamente al llegar al 95% del límite, sin interrumpir la sesión.

---

## Resumen: qué usar para cada necesidad

| Necesidad | Mecanismo |
|---|---|
| "Que Copilot sepa siempre nuestro stack y convenciones" | `copilot-instructions.md` |
| "Instrucciones solo para ficheros C#, no para todo" | `*.instructions.md` con `applyTo` |
| "Un procedimiento de deploy que Copilot aplica cuando se lo pido" | Skill en `.github/skills/` |
| "Que al abrir sesión ya tenga el estado de Git" | Hook `sessionStart` |
| "Revisar un PR sin llenar mi sesión de diffs" | Custom Agent en `.github/agents/` |
| "Ver cuántos tokens llevo gastados" | `/usage` o `/context` |
| "El historial está muy largo, quiero liberar espacio" | `/compact` |

---

## Plantillas listas para usar

En la carpeta [`.copilot/`](../.copilot/README.md) del repo encontras ejemplos reales para el stack GRM que puedes copiar directamente a tu proyecto:

- Instructions para .NET + Azure + Clean Architecture
- Skills: `debug-ci`, `commit-message`, `azure-diagnostics`
- Hook de `sessionStart` con estado Git
- Agente revisor de PRs
- Config MCP con Postman y Azure DevOps

> Ver guia de instalacion y tabla de destinos: [`.copilot/README.md`](../.copilot/README.md)

---

## Conexion con MCP

Skills y Custom Agents pueden declarar **herramientas MCP** en su frontmatter:

```
Custom Agent (.agent.md)
    └── tools: [postman-mcp, azure-devops-mcp, jira-mcp]
                    │
                    └── MCP Server  ←  esto es lo que construimos en Lab 3
```

Cuando creamos nuestro propio servidor MCP, estamos añadiendo una herramienta que cualquier agente o skill del equipo puede usar, sin que el modelo tenga que saber cómo funciona la API por dentro.

> Continúa en [mcp-fundamentals/README.md](../mcp-fundamentals/README.md)

---

## Optimizar el uso de creditos

Cada plan de Copilot incluye una cuota mensual de **AI credits**. Distintas acciones consumen creditos a ritmos diferentes según el modelo y los tokens procesados.

### Elige el modelo adecuado a la tarea

- Modelos **ligeros** para ediciones rápidas, boilerplate y preguntas sencillas.
- Modelos de **razonamiento** para refactorizaciones complejas, decisiones de arquitectura y depuración multi-paso.
- **Selección automática de modelo** para dejar que VS Code elija el modelo más eficiente según la petición.
- **Custom Agents** con modelo propio para enrutar subtareas a modelos especializados y económicos. Cuando invocas un agente como subagente, usa su modelo configurado, no el de la sesión principal.

### Separa planificación e implementación

Saltar directamente a la generación de código puede desperdiciar créditos si el enfoque es incorrecto. Un flujo eficiente:

1. Usa el **Plan agent** para investigar la tarea y crear un plan de implementación estructurado.
2. Revisa y refina el plan antes de que el agente escriba código.
3. Pasa el plan aprobado a un agente de implementación con un modelo más rápido.

### Thinking effort: usa los valores por defecto

El *thinking effort* controla cuánto razona el modelo. Niveles altos generan más tokens y mayor latencia. VS Code establece valores por defecto basados en evaluaciones y tiene razonamiento adaptativo activo. Solo aumenta el esfuerzo para problemas genuinamente complejos.

### Abre una sesión nueva para cada tarea

A medida que una conversación crece, acumula contexto de mensajes anteriores, salidas de herramientas y contenido de ficheros. Cuando cambias de tarea, el modelo sigue procesando todo ese historial irrelevante.

Abre una **nueva sesión de chat** (`Ctrl+N`) al cambiar de tema para dar al modelo un contexto limpio.

### Usa fork para explorar alternativas

En lugar de repromptear desde cero, usa **fork** para crear una sesión derivada que hereda el historial existente:

- `/fork` en el input del chat para bifurcar toda la sesión hasta el mensaje actual.
- Hover sobre un mensaje anterior y selecciona **Fork Conversation** para bifurcar desde un punto concreto.

### Desactiva herramientas y MCP servers que no necesites

Cada llamada a una herramienta produce output que consume espacio en el contexto y contribuye al gasto de creditos. Desactiva las herramientas que no necesites para la tarea actual:

- Botón **Configure Tools** en el input del chat para activar o desactivar herramientas o MCP servers.
- En Custom Agents, especifica solo las herramientas que el agente necesita via la propiedad `tools`.

### Excluye ficheros del contexto de Copilot

Ficheros generados, builds o directorios irrelevantes pueden incluirse en el contexto IA aumentando el consumo de tokens sin aportar valor:

- Usa `.gitignore` para excluir ficheros del índice semántico del workspace.
- Usa `files.exclude` para ocultar ficheros de VS Code completamente.

### Compacta el contexto con /compact

Cuando una conversación es muy larga, usa `/compact` para resumir las partes antiguas y recuperar espacio en el contexto. Puedes añadir instrucciones opcionales: `/compact focus on the API design decisions`.

### Monitoriza tu uso

- El **dashboard de estado de Copilot** en la Status Bar de VS Code muestra el porcentaje de cuota mensual consumido.
- El comando `/chronicle:cost-tips` en cualquier sesión de chat ofrece recomendaciones personalizadas basadas en tu actividad reciente.

### Inspecciona el uso de tokens y la caché

Usa los **Agent Debug Logs** para entender qué consume créditos en una sesión:

- **Summary view**: uso agregado de tokens de la sesión, número total de llamadas a herramientas y duración.
- **Cache Explorer view**: tasa de aciertos de la caché de prompts y tokens reutilizados. El caching de prompts permite a los proveedores reutilizar el prefijo de una petición que coincide con una anterior, reduciendo latencia y coste.

---

## Referencias

- [Custom Instructions — docs oficiales](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions)
- [Agent Skills — docs oficiales](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Custom Agents — docs oficiales](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli#use-custom-agents)
- [Optimizar uso de creditos — VS Code docs](https://code.visualstudio.com/docs/copilot/guides/optimize-usage)
