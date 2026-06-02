# Copilot CLI — Controlar el contexto y ahorrar tokens

## El problema: el contexto cuesta tokens

Cada mensaje que envías a Copilot CLI incluye, además de tu pregunta, todo el **contexto** que el modelo necesita para responder bien: instrucciones del proyecto, historial de la conversación, salidas de herramientas, etc.

```
[ instrucciones ] + [ historial ] + [ tu pregunta ] + [ salidas de tools ]
                             = tokens consumidos = coste + calidad
```

Más contexto = respuestas más precisas, pero también más tokens. El objetivo es ser **intencional**: meter lo que importa, descartar lo que no.

Os adjuntamos una guía para optimizar el uso de créditos:
https://code.visualstudio.com/docs/copilot/guides/optimize-usage

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

## Referencias

- [Custom Instructions — docs oficiales](https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions)
- [Agent Skills — docs oficiales](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Custom Agents — docs oficiales](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli#use-custom-agents)
