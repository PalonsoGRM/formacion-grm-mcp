# Copilot CLI — Personalización y extensibilidad

> Bloque previo a [Fundamentos MCP](../mcp-fundamentals/README.md). La idea es que cuando lleguemos a MCP ya tengamos claro el contexto: Copilot CLI es uno de los hosts MCP más usados en el equipo, y entender cómo se personaliza ayuda a situar para qué sirve un servidor MCP propio.

---

## Por qué personalizar Copilot CLI

Por defecto, Copilot CLI es un asistente de terminal de propósito general. Sin configuración extra, no sabe nada de:

- Tu stack tecnológico (C# .NET 10, fastmcp, Azure)
- Tus convenciones de código (sin secretos en appsettings, `ManagedIdentityCredential` en producción)
- Tus flujos de trabajo (ramas por feature, PRs con plantilla)
- Herramientas internas que el equipo usa (Jira, Azure DevOps, Postman)

La personalización resuelve esto a dos niveles:

| Nivel | Mecanismo | Scope |
|---|---|---|
| Contexto e instrucciones | `copilot-instructions.md`, `*.instructions.md`, `AGENTS.md` | Siempre presente |
| Capacidades adicionales | Skills, Custom Agents | Cargadas bajo demanda |
| Automatizacion | Hooks | Eventos del ciclo de sesion |

---

## 1. Custom Instructions — dar contexto permanente

Las instrucciones se inyectan en el contexto del LLM en cada sesión. Son texto plano (Markdown) que describe cómo debe comportarse el asistente.

### Ficheros reconocidos (por precedencia)

| Fichero | Scope | Cuándo usarlo |
|---|---|---|
| `.github/copilot-instructions.md` | Repositorio | Contexto del proyecto: stack, convenciones, arquitectura |
| `AGENTS.md` | Repositorio (raíz) | Compatible también con otros agentes (Claude, Gemini) |
| `.github/instructions/**/*.instructions.md` | Repositorio (segmentado) | Instrucciones por rol o área (`backend.instructions.md`) |
| `~/.copilot/copilot-instructions.md` | Usuario | Preferencias personales, estilo de respuesta |

### Estructura de un fichero de instrucciones

Un fichero de instrucciones es Markdown libre. Puede tener frontmatter `applyTo` para aplicarse solo cuando ciertos ficheros están abiertos:

```markdown
---
applyTo: "**/*.cs"
---

# Instrucciones para código C#

- Usa siempre `ManagedIdentityCredential` en entornos desplegados.
- Nunca pongas secretos en `appsettings.json`.
- Sigue Clean Architecture: separa Infra / Business / Domain.
```

Sin frontmatter, las instrucciones se aplican siempre.

### El fichero `.github/copilot-instructions.md` de este repo

Este repositorio ya tiene uno. Contiene el contexto de la formación: stack tecnológico, convenciones de los labs, y cómo debe comportarse Copilot al generar código de ejemplo. Puedes verlo en [.github/copilot-instructions.md](../.github/copilot-instructions.md).

---

## 2. Skills — capacidades bajo demanda

Las instrucciones siempre están presentes. Las **Skills** son diferentes: Copilot CLI las carga solo cuando son relevantes para la tarea.

Una Skill es una carpeta con un fichero `SKILL.md` que describe su propósito y, opcionalmente, scripts que puede ejecutar.

### Estructura

```
.github/skills/
└── grm-deploy/
    ├── SKILL.md          # descripcion + instrucciones
    └── deploy.sh         # script que la skill puede invocar
```

### Formato de SKILL.md

```markdown
---
name: grm-deploy
description: >
  Despliega servicios GRM a Azure. Usa esta skill cuando el usuario
  pida hacer un deploy, publicar, o subir cambios a DEV/PRE/PRO.
---

# GRM Deploy

## Prerrequisitos

- Azure CLI autenticado: `az login`
- Subscription seleccionada: `az account set -s <id>`

## Procedimiento

1. Verifica que los tests pasen: `dotnet test`
2. Construye la imagen: `docker build -t grm-service .`
3. Publica: `az acr build ...`
```

El campo `description` del frontmatter es lo que Copilot CLI usa para decidir si cargar la skill o no. Debe describir **cuándo** es relevante, no qué hace.

### Ubicaciones

| Ubicación | Scope |
|---|---|
| `.github/skills/<nombre>/SKILL.md` | Repositorio |
| `~/.copilot/skills/<nombre>/SKILL.md` | Usuario (disponible en todos los repos) |

---

## 3. Hooks — automatización en eventos del ciclo de sesión

Los Hooks ejecutan comandos automáticamente cuando ocurren eventos en Copilot CLI. Son útiles para:

- Inyectar contexto al inicio de sesión (rama activa, tickets abiertos)
- Registrar actividad
- Validar antes de que el agente use una herramienta concreta

### Formato

```json
{
  "version": 1,
  "hooks": [
    {
      "event": "sessionStart",
      "command": "echo Rama activa: $(git branch --show-current)"
    }
  ]
}
```

### Eventos disponibles

| Evento | Cuándo se dispara |
|---|---|
| `sessionStart` | Al iniciar una sesión de Copilot CLI |
| `sessionEnd` | Al cerrar la sesión |
| `userPromptSubmitted` | Cada vez que el usuario envía un mensaje |
| `preToolUse` | Antes de que el agente ejecute una herramienta |
| `postToolUse` | Después de que el agente ejecute una herramienta |
| `agentStop` | Cuando el agente termina su respuesta |
| `errorOccurred` | Cuando ocurre un error |

### Ejemplo: inyectar contexto Git al inicio

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

La salida del comando se añade al contexto de la sesión. El agente puede usarla para respuestas más contextuales sin que el usuario tenga que repetir en qué punto está el trabajo.

### Ubicaciones

| Ubicación | Scope |
|---|---|
| `.github/hooks/<nombre>.json` | Repositorio |
| `~/.copilot/hooks/<nombre>.json` | Usuario |

---

## 4. Custom Agents — asistentes especializados

Un Custom Agent es un asistente con un nombre, rol y herramientas específicas. A diferencia de las instrucciones (que modifican el agente por defecto), los Custom Agents son entidades separadas que el usuario invoca explícitamente.

### Formato

```markdown
---
name: grm-reviewer
description: >
  Revisor de PRs especializado en el stack GRM. Analiza cambios de C#,
  verifica convenciones de seguridad y arquitectura, y sugiere mejoras.
tools:
  - read_file
  - run_terminal_command
  - create_pull_request
---

# GRM Code Reviewer

Eres un revisor de código senior especializado en el stack GRM:
C# .NET 10, Clean Architecture, Azure, y los estándares de seguridad del equipo.

## Lo que debes verificar siempre

- No hay secretos hardcodeados ni en `appsettings.json`
- Los entornos desplegados usan `ManagedIdentityCredential`, no `DefaultAzureCredential`
- Las migraciones de base de datos son reversibles
- Los endpoints nuevos tienen tests de integración
```

### Ubicaciones

| Ubicación | Scope |
|---|---|
| `.github/agents/<nombre>.agent.md` | Repositorio |
| `~/.copilot/agents/<nombre>.agent.md` | Usuario |

---

## 5. Resumen: qué usar para cada necesidad

| Necesidad | Mecanismo | Fichero |
|---|---|---|
| "Que Copilot sepa siempre que usamos .NET 10 y Azure" | Custom Instructions | `.github/copilot-instructions.md` |
| "Instrucciones específicas para ficheros `.cs`" | Scoped instructions | `.github/instructions/csharp.instructions.md` |
| "Un procedimiento de deploy que Copilot aplica cuando se lo pido" | Skill | `.github/skills/grm-deploy/SKILL.md` |
| "Que al iniciar sesión tenga el contexto Git actualizado" | Hook `sessionStart` | `.github/hooks/git-context.json` |
| "Un asistente de PR reviews con rol y herramientas fijas" | Custom Agent | `.github/agents/grm-reviewer.agent.md` |
| "Preferencias personales que aplican en todos mis repos" | User instructions | `~/.copilot/copilot-instructions.md` |

---

## Conexión con MCP

Las Skills y los Custom Agents pueden usar **herramientas MCP**. Esto es lo que conecta este bloque con el resto de la formación:

```
Custom Agent (.agent.md)
    └── tools: [postman-mcp, azure-devops-mcp, jira-mcp]
                      │
                      └── MCP Server (HTTP+SSE / stdio)
                                │
                                └── API real (Postman, Azure DevOps, Jira)
```

Cuando construimos nuestro propio servidor MCP (Lab 3), lo que estamos haciendo es crear una herramienta que cualquier Custom Agent o Skill del equipo puede usar. La configuración de servidores MCP en Copilot CLI es exactamente el tema del bloque siguiente.

> Continúa en [mcp-fundamentals/README.md](../mcp-fundamentals/README.md)

---

## Referencias

- [GitHub Copilot CLI — Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [GitHub Copilot Extensions](https://docs.github.com/en/copilot/building-copilot-extensions)
- [AGENTS.md spec](https://docs.github.com/en/copilot/customizing-copilot/adding-personal-custom-instructions-for-github-copilot)
