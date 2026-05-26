# MCP 2026: Lo que cambia en el protocolo este año

> Material de referencia — no es un lab práctico.
> Fuentes: [Release Candidate 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) y [Roadmap 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

---

## Índice

1. [Contexto: de dónde venimos](#1-contexto-de-dónde-venimos)
2. [El cambio central: protocolo sin estado (stateless)](#2-el-cambio-central-protocolo-sin-estado-stateless)
3. [Nuevas cabeceras HTTP y cacheo](#3-nuevas-cabeceras-http-y-cacheo)
4. [Extensiones como ciudadanos de primera clase](#4-extensiones-como-ciudadanos-de-primera-clase)
5. [MCP Apps: interfaces de usuario renderizadas por el servidor](#5-mcp-apps-interfaces-de-usuario-renderizadas-por-el-servidor)
6. [Tareas (Tasks) se convierte en extensión](#6-tareas-tasks-se-convierte-en-extensión)
7. [Autorización reforzada (OAuth 2.0 / OIDC)](#7-autorización-reforzada-oauth-20--oidc)
8. [Deprecaciones: Roots, Sampling y Logging](#8-deprecaciones-roots-sampling-y-logging)
9. [JSON Schema 2020-12 completo para herramientas](#9-json-schema-2020-12-completo-para-herramientas)
10. [Política de ciclo de vida del protocolo](#10-política-de-ciclo-de-vida-del-protocolo)
11. [Roadmap 2026: áreas prioritarias](#11-roadmap-2026-áreas-prioritarias)
12. [Impacto práctico para nuestro stack](#12-impacto-práctico-para-nuestro-stack)
13. [Cronograma](#13-cronograma)

---

## 1. Contexto: ¿De dónde venimos?

La versión `2025-11-25` fue el primer aniversario de MCP. En ese momento, el protocolo ya era usado en producción en empresas grandes y pequeñas, con servidores remotos gracias al transporte **Streamable HTTP**.

Sin embargo, escalar esos servidores era doloroso:

- Cada cliente establecía una **sesión** con un servidor concreto (sticky session).
- Era necesario un **almacén de sesiones compartido** entre instancias.
- Los balanceadores de carga tenían que hacer **inspección profunda de paquetes** para enrutar correctamente.

La versión `2026-07-28` — el mayor cambio desde el lanzamiento — resuelve todos estos problemas de raíz.

---

## 2. El cambio central: protocolo sin estado (stateless)

### El problema anterior

En `2025-11-25`, antes de llamar a cualquier herramienta había que hacer un **handshake de inicialización**:

```http
POST /mcp HTTP/1.1
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": { "name": "my-app", "version": "1.0" }
  }
}
```

El servidor respondía con un `Mcp-Session-Id` que el cliente debía incluir en **todas** las peticiones siguientes, atándolo a esa instancia:

```http
POST /mcp HTTP/1.1
Mcp-Session-Id: 1868a90c-3a3f-4f5b
Content-Type: application/json

{ "jsonrpc": "2.0", "id": 2, "method": "tools/call", ... }
```

### La solución en 2026

El handshake `initialize`/`initialized` **desaparece**. Cada petición es autocontenida:

```http
POST /mcp HTTP/1.1
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: search
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search",
    "arguments": { "q": "otters" },
    "_meta": {
      "io.modelcontextprotocol/clientInfo": { "name": "my-app", "version": "1.0" }
    }
  }
}
```

La información que antes se intercambiaba una vez en el handshake (versión, capacidades, info del cliente) ahora viaja en el campo `_meta` de cada petición.

### Consecuencias directas

| Antes (`2025-11-25`) | Ahora (`2026-07-28`) |
|---|---|
| Sesión obligatoria por cliente | Sin sesión de protocolo |
| Sticky sessions en el balanceador | Round-robin puro |
| Almacén de sesiones compartido | No se necesita |
| Inspección de paquetes en el gateway | Enrutado por cabecera HTTP |

### Patrón de estado explícito (handle pattern)

Que el protocolo sea sin estado **no significa que tu aplicación deba serlo**. Los servidores que necesitan mantener estado entre llamadas deben usar el **patrón de handle explícito**: devolver un identificador desde una herramienta y que el modelo lo pase como argumento en llamadas posteriores.

```
1. Cliente llama a create_basket()
2. Servidor devuelve { basket_id: "abc-123" }
3. Modelo llama a add_item(basket_id: "abc-123", item: "...")
```

Este patrón es más potente que el estado oculto en metadatos de sesión: el modelo puede razonar sobre los identificadores, combinarlos entre herramientas y pasarlos entre pasos de un flujo.

---

## 3. Nuevas cabeceras HTTP y cacheo

### Cabeceras de enrutado (SEP-2243)

El transporte Streamable HTTP ahora **exige** las cabeceras `Mcp-Method` y `Mcp-Name` en cada petición:

```http
Mcp-Method: tools/call
Mcp-Name: search
```

Esto permite que balanceadores, gateways y rate-limiters enruten tráfico **sin inspeccionar el cuerpo JSON**. El servidor rechaza peticiones donde las cabeceras y el cuerpo no coincidan.

### TTL y cacheo de listas (SEP-2549)

Los resultados de `tools/list`, `resources/list`, etc. ahora incluyen `ttlMs` y `cacheScope`, modelados sobre `Cache-Control` de HTTP:

```json
{
  "tools": [...],
  "ttlMs": 300000,
  "cacheScope": "user"
}
```

- `ttlMs`: cuánto tiempo es válida la respuesta (en milisegundos).
- `cacheScope`: si es seguro compartirla entre usuarios (`global`) o es específica de un usuario (`user`).

Antes, la única forma de saber que la lista había cambiado era mantener un stream SSE abierto. Ahora el cliente sabe exactamente cuánto tiempo puede reutilizar la respuesta.

### Trazabilidad distribuida (SEP-414)

Se documenta la propagacion de **W3C Trace Context** en `_meta`, fijando los nombres de clave `traceparent`, `tracestate` y `baggage`. Varios SDKs ya lo hacian; ahora es parte del spec, lo que permite correlacionar trazas en backends OpenTelemetry desde el cliente hasta el servidor MCP y sus dependencias.

### Peticiones multi-round-trip (SEP-2322)

Cuando el servidor necesita input del usuario a mitad de una llamada (elicitación), ya no necesita mantener un stream SSE abierto. Devuelve un `InputRequiredResult`:

```json
{
  "resultType": "inputRequired",
  "inputRequests": {
    "confirm": {
      "type": "elicitation",
      "message": "Eliminar 3 ficheros?",
      "schema": { "type": "boolean" }
    }
  },
  "requestState": "eyJzdGVwIjoxLCJmaWxlcyI6WyJhIiwiYiIsImMiXX0="
}
```

El cliente recoge las respuestas y re-emite la llamada original incluyendo `inputResponses` y el `requestState` recibido. Cualquier instancia del servidor puede retomar la llamada porque todo el estado está en el payload.

---

## 4. Extensiones como ciudadanos de primera clase

Antes existian extensiones pero sin proceso formal. El SEP-2133 establece:

- **Identificación por reverse-DNS** (ej: `io.modelcontextprotocol.tasks`)
- **Negociacion** a traves del mapa `extensions` en las capacidades de cliente y servidor
- **Repositorios propios** (`ext-*`) con maintainers delegados
- **Versionado independiente** del spec principal
- **Extensions Track** en el proceso SEP: ruta formal de experimental a oficial

Las extensiones permiten que nuevas capacidades se desplieguen de forma opt-in y maduren antes de, eventualmente, entrar en el spec principal.

---

## 5. MCP Apps: interfaces de usuario renderizadas por el servidor

**MCP Apps** (SEP-1865) permite que los servidores envíen interfaces HTML interactivas que el host renderiza en un iframe sandboxed.

Puntos clave:
- Las herramientas declaran sus plantillas de UI **de antemano**, antes de ejecutarse
- El host puede hacer prefetch, cachearlas y revisarlas por seguridad
- La UI se comunica con el host usando el mismo JSON-RPC del protocolo MCP
- Cada acción iniciada desde la UI pasa por el mismo flujo de auditoría y consentimiento que una llamada directa a una herramienta

Es la primera extension oficial junto con Tasks.

---

## 6. Tareas (Tasks) se convierte en extensión

Tasks fue introducido como feature experimental en `2025-11-25`. El uso en producción mostró que necesitaba un rediseño para adaptarse al modelo sin estado.

### Nuevo ciclo de vida

| Método | Descripción |
|---|---|
| `tools/call` | El servidor puede responder con un handle de tarea en lugar del resultado directo |
| `tasks/get` | El cliente consulta el estado de la tarea |
| `tasks/update` | El cliente puede actualizar parámetros de la tarea |
| `tasks/cancel` | El cliente cancela la tarea |

- La creación de tareas es **dirigida por el servidor**: el cliente anuncia soporte para la extensión y el servidor decide cuándo una llamada debe ejecutarse como tarea.
- `tasks/list` se elimina porque no puede delimitarse de forma segura sin sesiones.

**Atención**: quien haya implementado la API experimental de Tasks de `2025-11-25` deberá migrar al nuevo ciclo de vida.

---

## 7. Autorización reforzada (OAuth 2.0 / OIDC)

Seis SEPs endurecen la especificación de autorización para alinearse con los despliegues reales de OAuth 2.0 y OpenID Connect:

| Cambio | Motivo |
|---|---|
| Validación del parámetro `iss` en respuestas de autorización (RFC 9207) | Mitiga ataques de mix-up, más prevalentes en el patrón 1 cliente - N servidores de MCP |
| Declaración de `application_type` en Dynamic Client Registration | Evita que servidores de autorización traten clientes desktop/CLI como aplicaciones web y rechacen sus redirect URIs de localhost |
| Vinculación de credenciales registradas al `issuer` | El cliente vuelve a registrarse si el recurso migra entre servidores de autorización |
| Solicitud de refresh tokens con servidores OIDC | Documentado el flujo estándar |
| Acumulación de scopes en step-up | Clarificación del comportamiento esperado |
| Sufijo de discovery `.well-known` | Clarificación para evitar ambigüedad en implementaciones |

---

## 8. Deprecaciones: Roots, Sampling y Logging

Tres features del core pasan a estado **Deprecated** bajo la nueva política de ciclo de vida:

| Feature | Reemplazo recomendado |
|---|---|
| **Roots** | Parámetros de herramientas, URIs de recursos, o configuración de servidor |
| **Sampling** | Integración directa con las APIs del proveedor LLM |
| **Logging** | `stderr` para transportes stdio; OpenTelemetry para observabilidad estructurada |

Son deprecaciones **solo de anotación**: los métodos, tipos y flags de capacidad siguen funcionando en esta versión y en cualquier versión publicada dentro de un año. Eliminarlos requerirá un SEP específico bajo la política de ciclo de vida.

---

## 9. JSON Schema 2020-12 completo para herramientas

`inputSchema` y `outputSchema` de las herramientas pasan a soportar **JSON Schema 2020-12** completo (SEP-2106):

- `inputSchema` sigue requiriendo `type: "object"` como raíz, pero ahora permite composición (`oneOf`, `anyOf`, `allOf`), condicionales y referencias (`$ref`, `$defs`).
- `outputSchema` no tiene restricciones.
- `structuredContent` puede ser cualquier valor JSON, no solo un objeto.

**Atención de seguridad**: las implementaciones no deben desreferenciar automáticamente URIs `$ref` externas y deben limitar la profundidad del schema y el tiempo de validación.

Cambio adicional: el código de error para recurso no encontrado cambia de `-32002` (código propio de MCP) a `-32602` (Invalid Params, estándar JSON-RPC). Si tu cliente hace matching sobre el literal `-32002`, actualízalo.

---

## 10. Política de ciclo de vida del protocolo

Tres SEPs de gobernanza establecen cómo evolucionará el protocolo sin romper lo construido:

### Ciclo de vida de features

```
Active  -->  Deprecated  -->  Removed
              (min. 12 meses entre cada transición)
```

Un feature no puede pasar de Deprecated a Removed si no han pasado al menos 12 meses.

### Sistema de tiers para SDKs

Los SDKs oficiales se clasifican por tiers. Los de **Tier 1** deben soportar la nueva versión dentro del período de validación (ventana de 10 semanas entre el RC y la versión final).

### Suite de conformidad

Un SEP del Standards Track no puede alcanzar el estado Final hasta que exista un escenario correspondiente en la suite de conformidad oficial. Esto garantiza que los cambios son verificables y que los SDKs pueden ser evaluados objetivamente.

---

## 11. Roadmap 2026: áreas prioritarias

El roadmap de 2026 cambia de organización por releases a **áreas prioritarias** gestionadas por Working Groups. Las cuatro áreas principales donde se concentra la capacidad de los maintainers son:

### Evolución del transporte y escalabilidad

- Protocolo sin estado para escalar horizontalmente (ya entregado en el RC)
- Mecanismos explícitos para sesiones de aplicación (cuando el caso de uso lo necesite)
- Formato de metadatos estándar via `.well-known` para descubrir capacidades de un servidor sin conexión activa

**Nota explícita del equipo**: no se añadirán nuevos transportes oficiales en este ciclo. Streamable HTTP es el transporte remoto y así seguirá.

### Comunicación entre agentes

- Semántica de reintentos cuando una tarea falla de forma transitoria
- Políticas de expiración para retener resultados de tareas
- Enfoque: desplegar experimental, recoger feedback de producción, iterar

### Madurez de gobernanza

- **Escalera de contribuidores** documentada: ruta clara de participante a maintainer
- **Modelo de delegación**: los Working Groups aceptan SEPs en su dominio sin esperar revisión completa del Core
- Los Core Maintainers mantienen supervisión estratégica

### Preparación para entornos enterprise

Áreas identificadas: auditorías, SSO, comportamiento de gateways, portabilidad de configuración.

Se espera que la mayoría del trabajo enterprise llegue como **extensiones**, no como cambios al spec base.

### En el horizonte (no prioritario pero bienvenido)

- Triggers y actualizaciones dirigidas por eventos
- Tipos de resultado en streaming y por referencia
- Trabajo adicional en seguridad y autorización (DPoP, Workload Identity Federation)
- Madurar el ecosistema de extensiones

---

## 12. Impacto práctico para nuestro stack

Nuestro stack usa Python (fastmcp) en el servidor y C# .NET 10 con `ModelContextProtocol.Client` en el cliente.

### Servidor Python (fastmcp)

| Cambio | Acción necesaria |
|---|---|
| Protocolo sin estado | fastmcp deberá eliminar la gestión de sesión de protocolo cuando actualice a `2026-07-28` |
| Cabeceras `Mcp-Method` / `Mcp-Name` | Verificar que el servidor las emite y valida |
| `ttlMs` en respuestas de lista | Considerar configurar TTL en herramientas que no cambian frecuentemente |
| Tasks API rediseñada | Si se usa Tasks experimental, planificar migración al nuevo ciclo de vida |
| Deprecación de Logging | Migrar a `stderr` o OpenTelemetry |

### Cliente C# (ModelContextProtocol.Client)

| Cambio | Acción necesaria |
|---|---|
| Sin handshake initialize | El SDK actualizará automáticamente; revisar código que asuma sesión activa |
| Validación de `iss` en OAuth | Verificar que el cliente valida el parámetro `iss` en respuestas de autorización |
| Código de error `-32002` → `-32602` | Actualizar cualquier matching sobre el código literal |
| JSON Schema 2020-12 | Las herramientas con schemas complejos podrán usar `$ref`, `oneOf`, etc. |

### Lo que no cambia

- El formato JSON-RPC 2.0 base
- Las primitivas principales: Tools, Resources, Prompts
- El transporte HTTP (solo evoluciona, no se reemplaza)

---

## 13. Cronograma

| Fecha | Hito |
|---|---|
| 21 mayo 2026 | Release Candidate bloqueado (congelado) |
| Mayo – julio 2026 | Ventana de validación para SDKs Tier 1 |
| **28 julio 2026** | **Versión final `2026-07-28` publicada** |

El RC está disponible hoy en la [especificación draft](https://modelcontextprotocol.io/specification/draft). El [changelog](https://modelcontextprotocol.io/specification/draft/changelog) lista todos los cambios respecto a `2025-11-25`.

---

## Referencias

- [Blog: Release Candidate 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [Blog: Roadmap 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [Especificacion draft](https://modelcontextprotocol.io/specification/draft)
- [Changelog draft vs 2025-11-25](https://modelcontextprotocol.io/specification/draft/changelog)
- [Working Groups y Interest Groups](https://modelcontextprotocol.io/community/working-interest-groups)
- [SEP Guidelines](https://modelcontextprotocol.io/community/sep-guidelines)
- [Suite de conformidad](https://github.com/modelcontextprotocol/conformance)
