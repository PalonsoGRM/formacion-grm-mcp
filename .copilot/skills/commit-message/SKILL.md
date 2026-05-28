---
name: commit-message
description: >
  Genera un mensaje de commit siguiendo Conventional Commits.
  Usalo cuando se pida generar, mejorar o revisar un mensaje de commit,
  o cuando el usuario haya hecho cambios y quiera hacer commit.
---
# Destino: .github/skills/commit-message/SKILL.md

Cuando se invoca este skill:

## 1. Entender los cambios

Si no se ha proporcionado contexto, ejecuta:

```bash
git diff --staged --stat
git diff --staged
```

Analiza que tipo de cambio es: nueva funcionalidad, fix, refactor, docs, test, infra...

## 2. Formato

Genera siempre en este formato:

```
<tipo>(<scope>): <descripcion corta en imperativo>

[cuerpo opcional: que y por que, no como]

[footer opcional: breaking changes, issue refs]
```

Tipos validos:

| Tipo | Cuando usarlo |
|------|---------------|
| `feat` | Nueva funcionalidad visible para el usuario |
| `fix` | Correccion de bug |
| `refactor` | Cambio de codigo sin cambio de comportamiento |
| `test` | Cambios solo en tests |
| `docs` | Solo documentacion |
| `chore` | Build, deps, CI, config — sin codigo de produccion |
| `perf` | Mejora de rendimiento |
| `ci` | Cambios en workflows de GitHub Actions |

## 3. Reglas

- Descripcion corta en **imperativo** en ingles: "add", "fix", "remove" (no "added", "fixes")
- Maximo 72 caracteres en la primera linea
- Si hay breaking change, incluir `BREAKING CHANGE:` en el footer
- Referenciar issues si aplica: `Closes #123`

## 4. Ejemplo

Cambio: se anade validacion de email en `CreateUserCommand`

```
feat(users): add email format validation on user creation

Validates email format using a regex before persisting to avoid
invalid data entering the database.

Closes #42
```

## 5. Output

Da siempre exactamente UNO o DOS mensajes candidatos para que el usuario elija.
No hagas el commit automaticamente a menos que el usuario lo pida explicitamente.
