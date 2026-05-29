# Instrucciones de proyecto — Plantilla GRM
# Destino: .github/copilot-instructions.md
#
# Estas instrucciones se aplican a TODAS las conversaciones en este repo.
# Rellena las secciones con el contexto real de tu proyecto.

## Rol

Eres un asistente experto en el stack tecnologico de este proyecto.
Genera codigo que siga las convenciones del equipo sin que se las tengas que recordar en cada sesion.

## Stack

- .NET 10, C# 13
- Azure (App Service / Container Apps / AKS) — autenticacion con ManagedIdentityCredential en deploy, DefaultAzureCredential en local
- Entity Framework Core 9
- Arquitectura: Clean Architecture (Domain / Application / Infrastructure / API)
- Tests: xUnit, Moq, FluentAssertions
- CI/CD: GitHub Actions, push a Azure Container Registry

## Convenciones de codigo

- Nombres en ingles, comentarios en espanol si son largos
- Nunca secrets en appsettings.json ni appsettings.Development.json
- User Secrets para local, Key Vault en DEV/PRE/PRO
- Credenciales Azure:

```csharp
#if DEBUG
    TokenCredential credential = new DefaultAzureCredential();
#else
    TokenCredential credential = new ManagedIdentityCredential();
#endif
```

- Resultado de operaciones: usa `Result<T>` o `OneOf` en lugar de excepciones para flujos de negocio
- Endpoints REST: siempre incluir ProblemDetails en errores 4xx/5xx

## Arquitectura

- `Domain/`: entidades, value objects, interfaces de repositorio
- `Application/`: casos de uso (Commands/Queries con MediatR), DTOs
- `Infrastructure/`: implementaciones de repositorios, clientes HTTP, EF DbContext
- `API/`: controllers/minimal API, middleware, DI config

## Testing

- Un test de integracion por endpoint nuevo
- Tests unitarios para logica de dominio y casos de uso
- No testear infraestructura directamente; usa abstracciones

## Lo que NO debes hacer

- No generar codigo que use ConnectionStrings con usuario/contrasena para Azure SQL (usa AAD)
- No poner logica de negocio en los controllers
- No usar `HttpClient` directamente; usa `IHttpClientFactory`
- No generar `async void` (excepto event handlers)
