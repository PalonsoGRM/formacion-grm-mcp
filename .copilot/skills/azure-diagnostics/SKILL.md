---
name: azure-diagnostics
description: >
  Diagnostica problemas en despliegues de Azure (App Service, Container Apps, AKS).
  Usalo cuando haya un deploy fallido, un servicio caido, errores 500, crashloops,
  problemas de autenticacion con Managed Identity o configuracion incorrecta de Azure.
---
# Destino: .github/skills/azure-diagnostics/SKILL.md

Cuando se invoca este skill, sigue estos pasos:

## 1. Identificar el tipo de recurso

Pregunta (o deduce del contexto):
- Tipo: App Service / Container Apps / AKS / Azure Function
- Entorno: DEV / PRE / PRO
- Sintoma: crashloop, 500, timeout, error de autenticacion, configuracion...

## 2. Comandos de diagnostico por tipo

### App Service / Container Apps

```bash
# Ver logs en tiempo real
az webapp log tail --name <app> --resource-group <rg>

# Ver ultimas 100 lineas
az webapp log download --name <app> --resource-group <rg>

# Estado del recurso
az webapp show --name <app> --resource-group <rg> --query "{state:state,hostNames:hostNames}"
```

### AKS

```bash
# Ver pods con problemas
kubectl get pods -n <namespace> | grep -v Running

# Logs del pod
kubectl logs <pod-name> -n <namespace> --previous

# Describir pod (eventos, crashloops)
kubectl describe pod <pod-name> -n <namespace>

# Estado de deployments
kubectl get deployments -n <namespace>
```

### Managed Identity (autenticacion Azure)

```bash
# Verificar que la identidad tiene el rol correcto
az role assignment list --assignee <principal-id> --all --output table

# Comprobar que la identidad esta asignada al recurso
az webapp identity show --name <app> --resource-group <rg>
```

## 3. Clasificacion de errores comunes

| Error | Causa probable | Solucion |
|-------|---------------|----------|
| `ManagedIdentityCredential: no available credentials` | Identidad no asignada o sin rol | Asignar Managed Identity + rol en Azure Portal |
| `Connection refused` / timeout en startup | Healthcheck fallando antes de arrancar | Aumentar timeout de startup, revisar probe config |
| `ImagePullBackOff` (AKS) | Imagen no existe en ACR o falta acceso | Verificar tag, credenciales ACR en AKS |
| `WEBSITE_RUN_FROM_PACKAGE` | Variable de entorno faltante | Configurar en App Settings |
| Error 500 aleatorio en produccion | Memory pressure, leak, o cold start | Revisar metricas de memoria en Azure Monitor |

## 4. Recomendacion

Da siempre:
1. El comando exacto para obtener mas informacion
2. La causa probable basada en los logs/contexto
3. El paso de solucion concreto

Si se necesita acceso a Azure Monitor o Application Insights, indica la query KQL relevante:

```kql
// Errores de los ultimos 30 minutos
exceptions
| where timestamp > ago(30m)
| summarize count() by type, outerMessage
| order by count_ desc
```
