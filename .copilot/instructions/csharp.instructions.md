---
applyTo: "**/*.cs"
---
# Destino: .github/instructions/csharp.instructions.md
#
# Se aplica SOLO cuando se edita un fichero .cs.
# Complementa a copilot-instructions.md con reglas especificas de C#.

## Credenciales Azure

En codigo desplegado usa siempre `ManagedIdentityCredential`.
`DefaultAzureCredential` unicamente en local (envuelto en `#if DEBUG` o `Debugger.IsAttached`).

## Inyeccion de dependencias

- Registra servicios en extension methods (`AddMiServicio(this IServiceCollection services)`)
- Usa `IOptions<T>` para configuracion tipada, nunca `IConfiguration` directamente en servicios de negocio

## Manejo de errores

- No captures `Exception` generica; captura tipos especificos
- Usa `ILogger<T>` para logging estructurado
- En operaciones de infraestructura, wrappea excepciones en tipos de dominio propios

## Async

- Todos los metodos de I/O deben ser async/await
- Propaga `CancellationToken` hasta el nivel mas bajo posible
- Usa `ConfigureAwait(false)` en librerias de infraestructura

## Nomenclatura

- Interfaces: `IRepository`, `IUserService`
- Implementaciones: `UserRepository`, `UserService` (sin prefijo)
- DTOs: `CreateUserRequest`, `UserResponse`
- Commands/Queries (MediatR): `CreateUserCommand`, `GetUserQuery`
