# Sistema Distribuido de Gestión de Productos

**Proyecto de Sistemas Distribuidos - Noviembre 2025**

---

## ⚠️ Nota Importante

Este repositorio contiene la **versión de desarrollo local** del proyecto. Los archivos aquí presentes son el código fuente y scripts de configuración que fueron utilizados para desarrollar y configurar el sistema distribuido.

**Este NO es un repositorio listo para ejecutar.** El proyecto real corre en contenedores Incus exportados y desplegados en una máquina virtual con IncusOS.

---

## 📂 Contenido del Repositorio

### Carpetas Principales

- **`auth-server/`** - Código del servidor de autenticación JWT
- **`web-server/`** - Código de la aplicación web principal con interfaz de usuario
- **`local_mongo/`** - Datos de MongoDB usados durante el desarrollo local
- **`scripts/`** - Scripts de configuración y sincronización con contenedores Incus
- **`Diagrams/`** - Diagramas PlantUML de la arquitectura del sistema

### Archivos de Documentación

- **`DESARROLLO_COMPLETO.md`** - Documentación técnica detallada del proyecto
- **`PRESENTACION_CLASE.md`** - Guía de presentación para exposición
- **`INSTRUCCIONES_IMPORTACION.md`** - Pasos para importar contenedores en otra máquina

### Scripts de Utilidad

- `start-local-mongo.sh` - Inicia MongoDB localmente para desarrollo
- `stop-local-mongo.sh` - Detiene las instancias locales de MongoDB
- `scripts/sync-*.sh` - Sincroniza código con contenedores Incus

---

## 🏗️ Arquitectura del Sistema

El sistema distribuido consta de:

- 5 contenedores Incus (web-server, auth-server, db1, db2, db3)
- Fragmentación horizontal de datos por nombre de producto
- Replicación MongoDB con Replica Sets
- Autenticación JWT
- Exposición pública con Ngrok

Ver **`DESARROLLO_COMPLETO.md`** para más detalles técnicos.

---

## 🚀 Estado del Proyecto

**Ambiente de Desarrollo:** Ubuntu con Incus  
**Ambiente de Producción:** IncusOS en VirtualBox  
**Estado Actual:** Contenedores exportados y desplegados en IncusOS

Los contenedores ya configurados fueron exportados como archivos `.tar.gz` y transferidos a una máquina virtual para su ejecución. Este repositorio solo contiene el código fuente y configuraciones usadas durante el desarrollo.

---

## 📖 Documentación

Para entender cómo funciona el sistema completo, consulta:

1. **`DESARROLLO_COMPLETO.md`** - Explicación técnica del proyecto
2. **`PRESENTACION_CLASE.md`** - Presentación para exposición en clase
3. **`Diagrams/`** - Diagramas de arquitectura y flujos

---

## 👥 Equipo

Camilo Muñoz
Juan Pablo Medina
Sergio Andres Castellanos
