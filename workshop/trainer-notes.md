# Trainer Notes — Formacion GRM: MCP

Guion del formador. No distribuir a los asistentes.

---

## Antes de la sesión

- [ ] Verificar que el repo es accesible en GitHub
- [ ] Tener `sample-server/` funcionando en tu máquina antes de la sesión
- [ ] Tener MCP Inspector instalado y probado
- [ ] Tener VS Code con markitdown MCP configurado (Lab 2)
- [ ] Tener .NET 10 SDK instalado (Lab 4)
- [ ] Compartir el link del repo y pedir a los asistentes que revisen PREREQUISITES.md con antelación

---

## Apertura (00:00 – 00:15)

- Presentar el objetivo: entender MCP de principio a fin, desde teoría hasta integración en nuestra plataforma MAF.
- Mostrar la agenda del día.
- Verificar rápidamente que todos tienen el entorno listo (pedir que ejecuten el script de PREREQUISITES.md).
- Contextualizar: MCP ya está integrado en MAF a través de `McpToolLoader.cs` — esta formación explica el "por qué" y el "cómo".

---

## Fundamentos MCP (00:15 – 00:50)

- Explicar `mcp-fundamentals/README.md` con el proyector.
- Dibujar el diagrama Host/Client/Server en pizarra si es presencial.
- Enfatizar la diferencia stdio vs HTTP+SSE — es relevante para nuestro stack.
- Mostrar el flujo JSON-RPC: puedes abrir las DevTools del navegador con MCP Inspector para ver los mensajes en tiempo real.
- Preguntas frecuentes anticipadas:
  - "¿Es lo mismo que function calling?" → No, MCP es agnóstico al modelo. Function calling es específico de cada provider.
  - "¿Necesitamos MCP si ya tenemos Semantic Kernel?" → MCP permite compartir tools entre distintos agentes/apps sin duplicar código.

---

## Lab 1 — Intro MCP (01:00 – 01:20)

- Los asistentes leen el README del lab y siguen los pasos.
- Facilita la discusión del diagrama.
- Asegúrate de que todos pueden conectar MCP Inspector a un servidor existente de `modelcontextprotocol/servers`.

---

## Lab 2 — markitdown MCP (01:20 – 01:45)

- Demostrar primero la instalación y configuración en VS Code.
- El caso de uso de markitdown es muy visual: convertir un PDF o imagen a Markdown desde Copilot Chat.
- Si hay problemas de configuración de VS Code, usar el MCP Inspector como alternativa.

---

## Lab 3 — Build Server Python (01:45 – 02:20)

- Es el lab más largo. Construir el servidor paso a paso.
- Empezar con una tool mínima, luego añadir más.
- Insistir en que el transporte es SSE (no stdio), porque el cliente C# del Lab 4 necesita SSE.
- Si el tiempo es justo, se puede omitir añadir una segunda tool y pasar al Lab 4.

---

## Lab 4 — Cliente C# (02:20 – 02:45)

- Contexto MAF: antes de empezar el lab, mostrar brevemente `McpToolLoader.cs` de `maf-agent-template` para que los asistentes vean el patrón real.
- El objetivo del lab es que entiendan el patrón de conexion SSE, no que hagan un proyecto completo de producción.
- El bonus (Azure Function como servidor MCP) es opcional si sobra tiempo.

---

## Lab 5 — Azure AI Agents + SK (02:45 – 03:15)

- Lab más conceptual. El foco es entender cómo encajan MCP, Azure AI Agents y Semantic Kernel.
- Mostrar el ejemplo de `ai-agents-for-beginners` cap. 11.
- Si hay código previo del Lab 4, se puede extender para añadir el agente.

---

## Cierre (03:15 – 03:30)

- Distribuir (o señalar) el `cheatsheet.md`.
- Abrir turno de preguntas.
- Mencionar `resources.md` para profundizar.
- Recordar que MAF ya usa `ModelContextProtocol.Client` — ahora saben cómo funciona por dentro.
