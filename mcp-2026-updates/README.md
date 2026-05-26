# MCP 2026: Lo que cambia en el protocolo este año

> Material de referencia — no es un lab practico.
> Fuentes: [Release Candidate 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) y [Roadmap 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

---

## Indice

1. [Contexto: de donde venimos](#1-contexto-de-donde-venimos)
2. [El cambio central: protocolo sin estado (stateless)](#2-el-cambio-central-protocolo-sin-estado-stateless)
3. [Nuevas cabeceras HTTP y cacheo](#3-nuevas-cabeceras-http-y-cacheo)
4. [Extensiones como ciudadanos de primera clase](#4-extensiones-como-ciudadanos-de-primera-clase)
5. [MCP Apps: interfaces de usuario renderizadas por el servidor](#5-mcp-apps-interfaces-de-usuario-renderizadas-por-el-servidor)
6. [Tareas (Tasks) se convierte en extension](#6-tareas-tasks-se-convierte-en-extension)
7. [Autorizacion reforzada (OAuth 2.0 / OIDC)](#7-autorizacion-reforzada-oauth-20--oidc)
8. [Deprecaciones: Roots, Sampling y Logging](#8-deprecaciones-roots-sampling-y-logging)
9. [JSON Schema 2020-12 completo para herramientas](#9-json-schema-2020-12-completo-para-herramientas)
10. [Politica de ciclo de vida del protocolo](#10-politica-de-ciclo-de-vida-del-protocolo)
11. [Roadmap 2026: areas prioritarias](#11-roadmap-2026-areas-prioritarias)
12. [Impacto practico para nuestro stack](#12-impacto-practico-para-nuestro-stack)
13. [Cronograma](#13-cronograma)

---

## 1. Contexto: de donde venimos

La version `2025-11-25` fue el primer aniversario de MCP. En ese momento, el protocolo ya era usado en produccion en empresas grandes y pequenas, con servidores remotos gracias al transporte **Streamable HTTP**.

Sin embargo, escalar esos servidores era doloroso:

- Cada cliente establecia una **sesion** con un servidor concreto (sticky session).
- Era necesario un **almacen de sesiones compartido** entre instancias.
- Los balanceadores de carga tenian que hacer **inspeccion profunda de paquetes** para enrutar correctamente.

La version `2026-07-28` — el mayor cambio desde el lanzamiento — resuelve todos estos problemas de raiz.

---

## 2. El cambio central: protocolo sin estado (stateless)

### El problema anterior

En `2025-11-25`, antes de llamar a cualquier herramienta habia que hacer un **handshake de inicializacion**:

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

El servidor respondia con un `Mcp-Session-Id` que el cliente debia incluir en **todas** las peticiones siguientes, atandolo a esa instancia:

```http
POST /mcp HTTP/1.1
Mcp-Session-Id: 1868a90c-3a3f-4f5b
Content-Type: application/json

{ "jsonrpc": "2.0", "id": 2, "method": "tools/call", ... }
```

### La solucion en 2026

El handshake `initialize`/`initialized` **desaparece**. Cada peticion es autocontenida:

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

La informacion que antes se intercambiaba una vez en el handshake (version, capacidades, info del cliente) ahora viaja en el campo `_meta` de cada peticion.

### Consecuencias directas

| Antes (`2025-11-25`) | Ahora (`2026-07-28`) |
|---|---|
| Sesion obligatoria por cliente | Sin sesion de protocolo |
| Sticky sessions en el balanceador | Round-robin puro |
| Almacen de sesiones compartido | No se necesita |
| Inspeccion de paquetes en el gateway | Enrutado por cabecera HTTP |

### Patron de estado explicito (handle pattern)

Que el protocolo sea sin estado **no significa que tu aplicacion deba serlo**. Los servidores que necesitan mantener estado entre llamadas deben usar el **patron de handle explicito**: devolver un identificador desde una herramienta y que el modelo lo pase como argumento en llamadas posteriores.

```
1. Cliente llama a create_basket()
2. Servidor devuelve { basket_id: "abc-123" }
3. Modelo llama a add_item(basket_id: "abc-123", item: "...")
```

Este patron es mas potente que el estado oculto en metadatos de sesion: el modelo puede razonar sobre los identificadores, combinarlos entre herramientas y pasarlos entre pasos de un flujo.

---

## 3. Nuevas cabeceras HTTP y cacheo

### Cabeceras de enrutado (SEP-2243)

El transporte Streamable HTTP ahora **exige** las cabeceras `Mcp-Method` y `Mcp-Name` en cada peticion:

```http
Mcp-Method: tools/call
Mcp-Name: search
```

Esto permite que balanceadores, gateways y rate-limiters enruten trafico **sin inspeccionar el cuerpo JSON**. El servidor rechaza peticiones donde las cabeceras y el cuerpo no coincidan.

### TTL y cacheo de listas (SEP-2549)

Los resultados de `tools/list`, `resources/list`, etc. ahora incluyen `ttlMs` y `cacheScope`, modelados sobre `Cache-Control` de HTTP:

```json
{
  "tools": [...],
  "ttlMs": 300000,
  "cacheScope": "user"
}
```

- `ttlMs`: cuanto tiempo es valida la respuesta (en milisegundos).
- `cacheScope`: si es seguro compartirla entre usuarios (`global`) o es especifica de un usuario (`user`).

Antes, la unica forma de saber que la lista habia cambiado era mantener un stream SSE abierto. Ahora el cliente sabe exactamente cuanto tiempo puede reutilizar la respuesta.

### Trazabilidad distribuida (SEP-414)

Se documenta la propagacion de **W3C Trace Context** en `_meta`, fijando los nombres de clave `traceparent`, `tracestate` y `baggage`. Varios SDKs ya lo hacian; ahora es parte del spec, lo que permite correlacionar trazas en backends OpenTelemetry desde el cliente hasta el servidor MCP y sus dependencias.

### Peticiones multi-round-trip (SEP-2322)

Cuando el servidor necesita input del usuario a mitad de una llamada (elicitacion), ya no necesita mantener un stream SSE abierto. Devuelve un `InputRequiredResult`:

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

El cliente recoge las respuestas y re-emite la llamada original incluyendo `inputResponses` y el `requestState` recibido. Cualquier instancia del servidor puede retomar la llamada porque todo el estado esta en el payload.

---

## 4. Extensiones como ciudadanos de primera clase

Antes existian extensiones pero sin proceso formal. El SEP-2133 establece:

- **Identificacion por reverse-DNS** (ej: `io.modelcontextprotocol.tasks`)
- **Negociacion** a traves del mapa `extensions` en las capacidades de cliente y servidor
- **Repositorios propios** (`ext-*`) con maintainers delegados
- **Versionado independiente** del spec principal
- **Extensions Track** en el proceso SEP: ruta formal de experimental a oficial

Las extensiones permiten que nuevas capacidades se desplieguen de forma opt-in y maduren antes de, eventualmente, entrar en el spec principal.

---

## 5. MCP Apps: interfaces de usuario renderizadas por el servidor

**MCP Apps** (SEP-1865) permite que los servidores envien interfaces HTML interactivas que el host renderiza en un iframe sandboxed.

Puntos clave:
- Las herramientas declaran sus plantillas de UI **de antemano**, antes de ejecutarse
- El host puede hacer prefetch, cachearlas y revisarlas por seguridad
- La UI se comunica con el host usando el mismo JSON-RPC del protocolo MCP
- Cada accion iniciada desde la UI pasa por el mismo flujo de auditoria y consentimiento que una llamada directa a una herramienta

Es la primera extension oficial junto con Tasks.

---

## 6. Tareas (Tasks) se convierte en extension

Tasks fue introducido como feature experimental en `2025-11-25`. El uso en produccion mostro que necesitaba un rediseno para adaptarse al modelo sin estado.

### Nuevo ciclo de vida

| Metodo | Descripcion |
|---|---|
| `tools/call` | El servidor puede responder con un handle de tarea en lugar del resultado directo |
| `tasks/get` | El cliente consulta el estado de la tarea |
| `tasks/update` | El cliente puede actualizar parametros de la tarea |
| `tasks/cancel` | El cliente cancela la tarea |

- La creacion de tareas es **dirigida por el servidor**: el cliente anuncia soporte para la extension y el servidor decide cuando una llamada debe ejecutarse como tarea.
- `tasks/list` se elimina porque no puede delimitarse de forma segura sin sesiones.

**Atencion**: quien haya implementado la API experimental de Tasks de `2025-11-25` debera migrar al nuevo ciclo de vida.

---

## 7. Autorizacion reforzada (OAuth 2.0 / OIDC)

Seis SEPs endurecen la especificacion de autorizacion para alinearse con los despliegues reales de OAuth 2.0 y OpenID Connect:

| Cambio | Motivo |
|---|---|
| Validacion del parametro `iss` en respuestas de autorizacion (RFC 9207) | Mitiga ataques de mix-up, mas prevalentes en el patron 1 cliente - N servidores de MCP |
| Declaracion de `application_type` en Dynamic Client Registration | Evita que servidores de autorizacion traten clientes desktop/CLI como aplicaciones web y rechacen sus redirect URIs de localhost |
| Vinculacion de credenciales registradas al `issuer` | El cliente vuelve a registrarse si el recurso migra entre servidores de autorizacion |
| Solicitud de refresh tokens con servidores OIDC | Documentado el flujo estandar |
| Acumulacion de scopes en step-up | Clarificacion del comportamiento esperado |
| Sufijo de discovery `.well-known` | Clarificacion para evitar ambiguedad en implementaciones |

---

## 8. Deprecaciones: Roots, Sampling y Logging

Tres features del core pasan a estado **Deprecated** bajo la nueva politica de ciclo de vida:

| Feature | Reemplazo recomendado |
|---|---|
| **Roots** | Parametros de herramientas, URIs de recursos, o configuracion de servidor |
| **Sampling** | Integracion directa con las APIs del proveedor LLM |
| **Logging** | `stderr` para transportes stdio; OpenTelemetry para observabilidad estructurada |

Son deprecaciones **solo de anotacion**: los metodos, tipos y flags de capacidad siguen funcionando en esta version y en cualquier version publicada dentro de un año. Eliminarlos requerira un SEP especifico bajo la politica de ciclo de vida.

---

## 9. JSON Schema 2020-12 completo para herramientas

`inputSchema` y `outputSchema` de las herramientas pasan a soportar **JSON Schema 2020-12** completo (SEP-2106):

- `inputSchema` sigue requiriendo `type: "object"` como raiz, pero ahora permite composicion (`oneOf`, `anyOf`, `allOf`), condicionales y referencias (`$ref`, `$defs`).
- `outputSchema` no tiene restricciones.
- `structuredContent` puede ser cualquier valor JSON, no solo un objeto.

**Atencion de seguridad**: las implementaciones no deben desreferenciar automaticamente URIs `$ref` externas y deben limitar la profundidad del schema y el tiempo de validacion.

Cambio adicional: el codigo de error para recurso no encontrado cambia de `-32002` (codigo propio de MCP) a `-32602` (Invalid Params, estandar JSON-RPC). Si tu cliente hace matching sobre el literal `-32002`, actualizalo.

---

## 10. Politica de ciclo de vida del protocolo

Tres SEPs de gobernanza establecen como evolucionara el protocolo sin romper lo construido:

### Ciclo de vida de features

```
Active  -->  Deprecated  -->  Removed
              (min. 12 meses entre cada transicion)
```

Un feature no puede pasar de Deprecated a Removed si no han pasado al menos 12 meses.

### Sistema de tiers para SDKs

Los SDKs oficiales se clasifican por tiers. Los de **Tier 1** deben soportar la nueva version dentro del periodo de validacion (ventana de 10 semanas entre el RC y la version final).

### Suite de conformidad

Un SEP del Standards Track no puede alcanzar el estado Final hasta que exista un escenario correspondiente en la suite de conformidad oficial. Esto garantiza que los cambios son verificables y que los SDKs pueden ser evaluados objetivamente.

---

## 11. Roadmap 2026: areas prioritarias

El roadmap de 2026 cambia de organizacion por releases a **areas prioritarias** gestionadas por Working Groups. Las cuatro areas principales donde se concentra la capacidad de los maintainers son:

### Evolucion del transporte y escalabilidad

- Protocolo sin estado para escalar horizontalmente (ya entregado en el RC)
- Mecanismos explicitos para sesiones de aplicacion (cuando el caso de uso lo necesite)
- Formato de metadatos estandar via `.well-known` para descubrir capacidades de un servidor sin conexion activa

**Nota explicita del equipo**: no se añadiran nuevos transportes oficiales en este ciclo. Streamable HTTP es el transporte remoto y asi seguira.

### Comunicacion entre agentes

- Semantica de reintentos cuando una tarea falla de forma transitoria
- Politicas de expiracion para retener resultados de tareas
- Enfoque: desplegar experimental, recoger feedback de produccion, iterar

### Madurez de gobernanza

- **Escalera de contribuidores** documentada: ruta clara de participante a maintainer
- **Modelo de delegacion**: los Working Groups aceptan SEPs en su dominio sin esperar revision completa del Core
- Los Core Maintainers mantienen supervision estrategica

### Preparacion para entornos enterprise

Areas identificadas: auditorias, SSO, comportamiento de gateways, portabilidad de configuracion.

Se espera que la mayoria del trabajo enterprise llegue como **extensiones**, no como cambios al spec base.

### En el horizonte (no prioritario pero bienvenido)

- Triggers y actualizaciones dirigidas por eventos
- Tipos de resultado en streaming y por referencia
- Trabajo adicional en seguridad y autorizacion (DPoP, Workload Identity Federation)
- Madurar el ecosistema de extensiones

---

## 12. Impacto practico para nuestro stack

Nuestro stack usa Python (fastmcp) en el servidor y C# .NET 10 con `ModelContextProtocol.Client` en el cliente.

### Servidor Python (fastmcp)

| Cambio | Accion necesaria |
|---|---|
| Protocolo sin estado | fastmcp debera eliminar la gestion de sesion de protocolo cuando actualice a `2026-07-28` |
| Cabeceras `Mcp-Method` / `Mcp-Name` | Verificar que el servidor las emite y valida |
| `ttlMs` en respuestas de lista | Considerar configurar TTL en herramientas que no cambian frecuentemente |
| Tasks API rediseñada | Si se usa Tasks experimental, planificar migracion al nuevo ciclo de vida |
| Deprecacion de Logging | Migrar a `stderr` o OpenTelemetry |

### Cliente C# (ModelContextProtocol.Client)

| Cambio | Accion necesaria |
|---|---|
| Sin handshake initialize | El SDK actualizara automaticamente; revisar codigo que asuma sesion activa |
| Validacion de `iss` en OAuth | Verificar que el cliente valida el parametro `iss` en respuestas de autorizacion |
| Codigo de error `-32002` → `-32602` | Actualizar cualquier matching sobre el codigo literal |
| JSON Schema 2020-12 | Las herramientas con schemas complejos podran usar `$ref`, `oneOf`, etc. |

### Lo que no cambia

- El formato JSON-RPC 2.0 base
- Las primitivas principales: Tools, Resources, Prompts
- El transporte HTTP (solo evoluciona, no se reemplaza)

---

## 13. Cronograma

| Fecha | Hito |
|---|---|
| 21 mayo 2026 | Release Candidate bloqueado (congelado) |
| Mayo – julio 2026 | Ventana de validacion para SDKs Tier 1 |
| **28 julio 2026** | **Version final `2026-07-28` publicada** |

El RC esta disponible hoy en la [especificacion draft](https://modelcontextprotocol.io/specification/draft). El [changelog](https://modelcontextprotocol.io/specification/draft/changelog) lista todos los cambios respecto a `2025-11-25`.

---

## Referencias

- [Blog: Release Candidate 2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [Blog: Roadmap 2026](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [Especificacion draft](https://modelcontextprotocol.io/specification/draft)
- [Changelog draft vs 2025-11-25](https://modelcontextprotocol.io/specification/draft/changelog)
- [Working Groups y Interest Groups](https://modelcontextprotocol.io/community/working-interest-groups)
- [SEP Guidelines](https://modelcontextprotocol.io/community/sep-guidelines)
- [Suite de conformidad](https://github.com/modelcontextprotocol/conformance)
