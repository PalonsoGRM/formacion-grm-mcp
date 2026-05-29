---
name: debug-ci
description: >
  Depura workflows fallidos de GitHub Actions.
  Usalo cuando se pida debugear un CI roto, un workflow fallido, un pipeline de GitHub Actions
  o cuando haya errores de build/test en el pipeline.
---
# Destino: .github/skills/debug-ci/SKILL.md

Cuando se invoca este skill, sigue estos pasos en orden:

## 1. Obtener el log del workflow

Usa `gh run list --limit 5` para identificar el run fallido reciente.
Luego `gh run view <run-id> --log-failed` para ver solo los pasos que fallaron.

Si el usuario ya pego el log, analiza directamente desde ahi.

## 2. Clasificar el fallo

Identifica a cual de estas categorias pertenece el error:

| Tipo | Ejemplos |
|------|----------|
| **Build** | error de compilacion, NuGet restore fallido, imagen Docker no encontrada |
| **Test** | tests unitarios/integracion fallidos, coverage insuficiente |
| **Deploy** | permisos Azure, imagen no publicada en ACR, variable de entorno faltante |
| **Infraestructura del CI** | runner sin memoria, timeout, secreto no configurado en el repo |

## 3. Diagnosticar la causa raiz

- Para errores de **build/NuGet**: revisa `*.csproj`, `nuget.config`, versiones de .NET en el workflow
- Para errores de **tests**: muestra el test fallido con el mensaje de error completo
- Para errores de **deploy en Azure**: comprueba que el Service Principal o Managed Identity tiene los permisos correctos
- Para **secretos faltantes**: lista con `gh secret list` los que esten configurados

## 4. Proponer solucion

Da un fix concreto:
- Si es codigo: muestra el cambio necesario
- Si es config del workflow: muestra el YAML corregido
- Si es un secreto faltante: explica exactamente como crearlo en el repo (`gh secret set NOMBRE`)

## 5. Verificacion

Despues de aplicar el fix, indica el comando para re-lanzar el workflow:

```bash
gh run rerun <run-id> --failed
```
