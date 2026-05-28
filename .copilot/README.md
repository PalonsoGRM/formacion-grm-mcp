# .copilot — Kit de plantillas

> **Este directorio NO se carga automaticamente.**
> Es un kit de plantillas listo para copiar. Cada archivo indica en su cabecera a donde debe ir.

Copilot CLI carga configuracion desde dos ubicaciones:

| Ubicacion | Alcance | Se carga automaticamente |
|-----------|---------|--------------------------|
| `.github/` (raiz del repo) | Proyecto | Si |
| `~/.copilot/` (home del usuario) | Usuario/global | Si |

Lo que está aqui es una coleccion de ejemplos reales para el stack GRM (.NET, Azure, Clean Architecture) que puedes adaptar y copiar a las ubicaciones correctas.

---

## Donde copiar cada archivo

| Archivo en este repo | Destino | Tipo |
|----------------------|---------|------|
| `instructions/proyecto.instructions.md` | `.github/copilot-instructions.md` | Instrucciones de proyecto |
| `instructions/csharp.instructions.md` | `.github/instructions/csharp.instructions.md` | Instrucciones por tipo de fichero |
| `skills/debug-ci/SKILL.md` | `.github/skills/debug-ci/SKILL.md` | Skill |
| `skills/commit-message/SKILL.md` | `.github/skills/commit-message/SKILL.md` | Skill |
| `skills/azure-diagnostics/SKILL.md` | `.github/skills/azure-diagnostics/SKILL.md` | Skill |
| `hooks/sesion-git.json` | `.github/copilot/hooks/sesion-git.json` | Hook |
| `agents/revisor-pr.agent.md` | `.github/agents/revisor-pr.agent.md` | Agente personalizado |
| `mcp/mcp-config.json` | `~/.copilot/mcp-config.json` | Servidores MCP |

---

## Que pasa si tengo .github/ y ~/.copilot/?

Se cargan **los dos a la vez** (no hay jerarquia, son aditivos). Pero cada tipo de fichero tiene sus reglas:

| Tipo | `.github/` | `~/.copilot/` |
|------|-----------|----------------|
| Instructions (`copilot-instructions.md`) | Instrucciones del proyecto | Instrucciones personales del usuario |
| Instructions (`*.instructions.md`) | Por tipo de fichero en el repo | Por tipo de fichero del usuario |
| Skills | Skills del equipo | Skills personales del usuario |
| Hooks | Hooks del repo | Hooks personales del usuario |
| MCP config | No existe aqui | `~/.copilot/mcp-config.json` |

**Regla practica**: evita dar instrucciones contradictorias en ambos lugares. Si hay conflicto, el comportamiento no es determinista.

---

## Como verificar que se ha cargado

Una vez copiado a la ubicacion correcta, dentro de una sesion de Copilot CLI:

```
/instructions          # muestra las instrucciones activas
/skills list           # lista los skills disponibles
/skills info debug-ci  # detalle de un skill concreto
/mcp show              # muestra los servidores MCP configurados
/env                   # variables de entorno visibles en la sesion
```

---

## Referencias

- [Awesome Copilot](https://awesome-copilot.github.com) — cientos de skills y agentes de la comunidad
- [Docs: Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Docs: Skills](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-skills-to-github-copilot-in-your-organization)
- [Docs: Hooks](https://docs.github.com/en/copilot/customizing-copilot/managing-copilot-hooks)
