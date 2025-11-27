# 🎯 Presentación: Sistema Distribuido con Incus

**Proyecto:** Plataforma Web con Fragmentación y Replicación  
**Tecnología:** Incus, Python/Flask, MongoDB  
**Equipo:** [Nombres del equipo]  
**Fecha:** Noviembre 2025

---

## 📋 Agenda de Presentación

1. 🏗️ **Arquitectura del Sistema** (3 min)
2. 🗂️ **Fragmentación de Datos** (2 min)
3. 🔄 **Replicación y Alta Disponibilidad** (3 min)
4. 🔐 **Sistema de Autenticación** (2 min)
5. 🚀 **Despliegue con Incus** (2 min)
6. 💻 **Demo en Vivo** (4 min)
7. ✅ **Verificación de Requisitos** (2 min)
8. ❓ **Preguntas** (2 min)

**Duración total:** ~20 minutos

---

## 1. 🏗️ Arquitectura del Sistema

![Arquitectura General](Diagrams/1_arquitectura_general.png)

### ✔️ Requisito 1: Servidor Web con Dashboard

**✅ CUMPLIDO** - Contenedor `web-server` (10.10.10.11:3000)

- Dashboard centralizado con múltiples secciones
- Sección "Ventas" con CRUD completo de productos
- Interfaz web responsiva con HTML/CSS/JavaScript
- Backend Flask con rutas REST

**Evidencia:**

- Código: `web-server/app.py` y `web-server/templates/`
- Acceso: https://[ngrok-url]

---

### ✔️ Requisito 2: Base de Datos 1 (Fragmentación + Réplica)

**✅ CUMPLIDO** - Contenedor `db1` (10.10.10.12)

| Aspecto           | Implementación                                        |
| ----------------- | ----------------------------------------------------- |
| **Fragmentación** | Horizontal por rango alfabético (A-M)                 |
| **Replica Set**   | rsA con 3 instancias en mismo contenedor              |
| **Puertos**       | 27017 (PRIMARY), 27018 (SECONDARY), 27019 (SECONDARY) |
| **Replicación**   | Asíncrona con Oplog                                   |
| **Base de Datos** | MongoDB 7.0                                           |

**Productos almacenados:** Arroz, Café, Leche, Manzana, etc.

---

### ✔️ Requisito 3: Base de Datos 2 (Fragmentación + Réplica)

**✅ CUMPLIDO** - Contenedor `db2` (10.10.10.13)

| Aspecto           | Implementación                                        |
| ----------------- | ----------------------------------------------------- |
| **Fragmentación** | Horizontal por rango alfabético (N-Z)                 |
| **Replica Set**   | rsB con 3 instancias en mismo contenedor              |
| **Puertos**       | 27017 (PRIMARY), 27018 (SECONDARY), 27019 (SECONDARY) |
| **Replicación**   | Asíncrona con Oplog                                   |
| **Base de Datos** | MongoDB 7.0                                           |

**Productos almacenados:** Naranja, Pan, Queso, Zanahoria, etc.

---

### ✔️ Requisito 4: Servidor de Autenticación

**✅ CUMPLIDO** - Contenedor `auth-server` (10.10.10.10:5000)

- ✅ Registro de usuarios con validación
- ✅ Login con generación de tokens JWT
- ✅ Verificación de tokens en cada petición
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Conexión con db3 para gestión de usuarios
- ✅ Tokens con expiración de 1 hora

**Flujo:** Usuario → Register/Login → JWT Token → Acceso protegido

---

### ✔️ Requisito 5: Base de Datos 3 (Usuarios)

**✅ CUMPLIDO** - Contenedor `db3` (10.10.10.14:27017)

- MongoDB standalone (sin réplicas)
- Base de datos: `auth_db`
- Colección: `users`
- Almacena: username, email, password (hasheada), created_at

**Justificación de no usar réplicas:** Los datos de autenticación son críticos pero de bajo volumen. Para simplicidad del proyecto y enfoque en fragmentación de productos, se implementó como standalone.

---

### ✔️ Requisito 6: Interfaz de Gestión (Incus-UI)

**✅ CUMPLIDO** - Incus-UI integrado en IncusOS

- ✅ Gestión gráfica de contenedores
- ✅ Monitoreo de recursos (CPU, RAM, Disco)
- ✅ Logs en tiempo real
- ✅ Control de red incusbr0
- ✅ Acceso remoto via Ngrok

**Incus-UI viene preinstalado** con IncusOS en puerto 8443

**Acceso:** https://[ngrok-ui-url]:8443

---

## 2. 🏗️ Arquitectura del Sistema

> **[MOSTRAR DIAGRAMA: `1_arquitectura_general.png`]**

### Componentes Principales

```
┌─────────────────────────────────────────────────┐
│        VirtualBox VM - IncusOS                  │
│  ┌──────────────────────────────────────────┐  │
│  │   Red incusbr0 (10.10.10.0/24)           │  │
│  │                                           │  │
│  │  ┌──────────┐  ┌──────────┐             │  │
│  │  │web-server│  │auth-server│             │  │
│  │  │  :3000   │  │   :5000   │             │  │
│  │  └──────────┘  └──────────┘             │  │
│  │                                           │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐           │  │
│  │  │ db1  │  │ db2  │  │ db3  │           │  │
│  │  │ rsA  │  │ rsB  │  │stand │           │  │
│  │  │ A-M  │  │ N-Z  │  │alone │           │  │
│  │  └──────┘  └──────┘  └──────┘           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Características Clave

- **5 contenedores Incus** interconectados
- **Red bridge privada** (incusbr0) con IPs estáticas
- **Separación de responsabilidades** (microservicios)
- **Comunicación HTTP** entre servicios
- **Exposición pública** via Ngrok

---

## 2. 🗂️ Fragmentación de Datos

![Fragmentación Horizontal](Diagrams/2_fragmentacion_horizontal.png)

### Estrategia: Fragmentación Horizontal

**Criterio:** Primera letra del nombre del producto

| Rango     | Base de Datos | Ejemplo de Productos                           |
| --------- | ------------- | ---------------------------------------------- |
| **A - M** | db1 (rsA)     | **A**rroz, **C**afé, **L**eche, **M**anzana    |
| **N - Z** | db2 (rsB)     | **N**aranja, **P**an, **Q**ueso, **Z**anahoria |

### Código de Fragmentación

```python
def get_database_for_product(product_name):
    first_letter = product_name[0].upper()

    if 'A' <= first_letter <= 'M':
        return products_collection_db1, 'DB1 (A-M)'
    else:
        return products_collection_db2, 'DB2 (N-Z)'
```

### Ventajas

✅ **Balance automático** - Distribución uniforme de productos  
✅ **Escalabilidad** - Fácil agregar más rangos  
✅ **Búsqueda rápida** - Sabemos dónde está cada producto  
✅ **Sin intervención manual** - El sistema decide automáticamente

---

## 3. 🔄 Replicación y Alta Disponibilidad

![Replicación Asíncrona](Diagrams/3_replicacion_asincrona.png)

### Configuración de Replica Sets

**Replica Set rsA (db1):**

```javascript
rs.initiate({
  _id: "rsA",
  members: [
    { _id: 0, host: "10.10.10.12:27017", priority: 1 }, // PRIMARY
    { _id: 1, host: "10.10.10.12:27018", priority: 1 }, // SECONDARY
    { _id: 2, host: "10.10.10.12:27019", priority: 1 }, // SECONDARY
  ],
});
```

**Replica Set rsB (db2):** Idéntica configuración con IP 10.10.10.13

### ¿Cómo Funciona?

1. **Escritura** → Solo en PRIMARY
2. **PRIMARY** registra operación en **Oplog**
3. **SECONDARIES** leen Oplog cada 2 segundos
4. **SECONDARIES** replican datos automáticamente
5. **Heartbeat** cada 2 segundos para detectar fallos

### Replicación Asíncrona

- ✅ PRIMARY confirma **inmediatamente** (rápido)
- ✅ SECONDARIES replican **en background** (~50-200ms)
- ✅ Cliente **no espera** por réplicas

---

### Failover Automático

![Failover Automático](Diagrams/5_failover_automatico.png)

**Escenario:** PRIMARY falla (apagón, crash, systemctl stop)

```
1. SECONDARIES detectan fallo (~10 segundos)
2. Inicia elección automática
3. SECONDARY con datos más recientes gana
4. Nuevo PRIMARY elegido
5. Sistema continúa funcionando ✅
```

**Downtime:** ~10-15 segundos  
**Pérdida de datos:** CERO ✅

### Demo de Failover (Opcional)

```bash
# Detener PRIMARY
systemctl stop mongod-27017

# Ver nuevo PRIMARY (automático)
mongosh --port 27018 --eval 'rs.status()'
```

---

## 4. 🔐 Sistema de Autenticación

![Autenticación JWT](Diagrams/4_autenticacion_jwt.png)

### Tecnologías

- **JWT (JSON Web Tokens)** - Autenticación stateless
- **bcrypt** - Hash seguro de contraseñas (12 rounds)
- **db3** - Almacenamiento de usuarios

### Flujo de Autenticación

**1. Registro:**

```
Usuario → Formulario → auth-server → bcrypt.hashpw() → db3
```

**2. Login:**

```
Usuario → Credenciales → auth-server → Verifica bcrypt → Genera JWT → Cliente
```

**3. Petición Protegida:**

```
Cliente → Petición + Token JWT → web-server → Verifica con auth-server → Procesa
```

### Seguridad Implementada

✅ Contraseñas hasheadas (irreversibles)  
✅ Tokens con expiración (1 hora)  
✅ Verificación en cada petición  
✅ Salt aleatorio por contraseña  
✅ Middleware de autenticación

---

## 5. 🚀 Despliegue con Incus

![Despliegue Incus](Diagrams/6_despliegue_incus.png)

### Proceso de Desarrollo → Producción

**Fase 1: Desarrollo Local (Ubuntu)**

```bash
# Crear contenedores
incus launch ubuntu:22.04 web-server
incus launch ubuntu:22.04 auth-server
incus launch ubuntu:22.04 db1, db2, db3

# Configurar red y servicios
# Instalar dependencias
# Configurar systemd
```

**Fase 2: Exportación**

```bash
incus export web-server web-server.tar.gz
incus export auth-server auth-server.tar.gz
incus export db1 db1.tar.gz
# ... (~4 GB total)
```

**Fase 3: Transferencia**

- USB / Red / Cloud → Al compañero

**Fase 4: Importación en IncusOS**

```bash
incus import web-server.tar.gz
incus import auth-server.tar.gz
incus import db1.tar.gz
# Configurar red incusbr0
incus start --all
```

**Fase 5: Exposición Pública**

```bash
# Port Forward en VirtualBox (3000 → 10.10.10.11:3000)
# Ngrok para acceso público
ngrok http 3000
ngrok http 8443  # Incus-UI
```

---

## 6. 💻 Demo en Vivo

### Paso 1: Mostrar Incus-UI

> **[ABRIR NAVEGADOR: https://[ngrok-ui-url]:8443]**

✅ Mostrar los 5 contenedores activos  
✅ Verificar estado: Running  
✅ Mostrar uso de recursos (CPU, RAM)  
✅ Ver red incusbr0 configurada

---

### Paso 2: Acceder a la Aplicación

> **[ABRIR NAVEGADOR: https://[ngrok-web-url]]**

**2.1 Login**

- Usuario: `admin`
- Contraseña: `admin123`
- ✅ Muestra que genera token JWT

---

### Paso 3: Dashboard

> **[MOSTRAR PANTALLA]**

✅ Dashboard con secciones: Ventas, Usuarios  
✅ Navbar con usuario logueado  
✅ Botón de logout

---

### Paso 4: CRUD de Productos

**4.1 Listar Productos**

> **[CLICK: Ver Productos]**

- Muestra productos de **DB1 (A-M)** y **DB2 (N-Z)**
- Cada producto indica en qué base de datos está
- Tabla con: Nombre, Precio, Stock, Categoría, Base de Datos

---

**4.2 Crear Producto (DB1)**

> **[CLICK: Agregar Producto]**

**Ejemplo:**

- Nombre: `Azúcar`
- Precio: `4.50`
- Stock: `80`
- Categoría: `Endulzantes`

> **[CLICK: Crear]**

✅ Mensaje: "Producto creado en **DB1 (A-M)**"  
✅ Aparece en la lista  
✅ Primera letra 'A' → va a db1 (fragmentación)

---

**4.3 Crear Producto (DB2)**

**Ejemplo:**

- Nombre: `Sal`
- Precio: `2.00`
- Stock: `100`
- Categoría: `Condimentos`

> **[CLICK: Crear]**

✅ Mensaje: "Producto creado en **DB2 (N-Z)**"  
✅ Primera letra 'S' → va a db2 (fragmentación)

---

**4.4 Editar Producto**

> **[CLICK: Editar en "Azúcar"]**

- Cambiar precio: `4.50` → `5.00`

> **[CLICK: Actualizar]**

✅ Producto actualizado correctamente  
✅ El sistema busca automáticamente en la BD correcta

---

**4.5 Eliminar Producto**

> **[CLICK: Eliminar en "Sal"]**

✅ Producto eliminado  
✅ Desaparece de la lista

---

### Paso 5: Verificar Fragmentación (Terminal)

> **[ABRIR TERMINAL]**

**Verificar db1 (A-M):**

```bash
incus exec db1 -- mongosh --port 27017 --eval '
use products_db
db.products.find({}, {name:1, _id:0})
'
```

**Salida esperada:**

```json
{ "name": "Arroz" }
{ "name": "Café" }
{ "name": "Azúcar" }
```

---

**Verificar db2 (N-Z):**

```bash
incus exec db2 -- mongosh --port 27017 --eval '
use products_db
db.products.find({}, {name:1, _id:0})
'
```

**Salida esperada:**

```json
{ "name": "Pan" }
{ "name": "Queso" }
{ "name": "Naranja" }
```

✅ **Fragmentación funcionando correctamente**

---

### Paso 6: Verificar Replicación (Terminal)

**Ver estado del Replica Set rsA:**

```bash
incus exec db1 -- mongosh --port 27017 --eval 'rs.status()' | grep -E "name|stateStr"
```

**Salida esperada:**

```
name: "10.10.10.12:27017", stateStr: "PRIMARY"
name: "10.10.10.12:27018", stateStr: "SECONDARY"
name: "10.10.10.12:27019", stateStr: "SECONDARY"
```

✅ **Replica Set rsA funcionando**

---

**Ver estado del Replica Set rsB:**

```bash
incus exec db2 -- mongosh --port 27017 --eval 'rs.status()' | grep -E "name|stateStr"
```

**Salida esperada:**

```
name: "10.10.10.13:27017", stateStr: "PRIMARY"
name: "10.10.10.13:27018", stateStr: "SECONDARY"
name: "10.10.10.13:27019", stateStr: "SECONDARY"
```

✅ **Replica Set rsB funcionando**

---

### Paso 7: Gestión de Usuarios

> **[VOLVER AL NAVEGADOR]**

> **[CLICK: Usuarios]**

**Lista de usuarios registrados:**

- admin
- usuario1
- usuario2

> **[CLICK: Registrar Usuario]**

**Crear nuevo usuario:**

- Username: `demo`
- Email: `demo@test.com`
- Password: `demo123`

> **[CLICK: Registrar]**

✅ Usuario creado en **db3**  
✅ Contraseña hasheada con bcrypt

---

## 8. 📊 Resultados y Métricas

### Cumplimiento de Requisitos

| Requisito                                 | Estado  | Evidencia              |
| ----------------------------------------- | ------- | ---------------------- |
| Servidor Web + Dashboard                  | ✅ 100% | web-server funcionando |
| Base de Datos 1 (Fragmentación + Réplica) | ✅ 100% | db1 con rsA            |
| Base de Datos 2 (Fragmentación + Réplica) | ✅ 100% | db2 con rsB            |
| Servidor Autenticación                    | ✅ 100% | auth-server con JWT    |
| Base de Datos 3 (Usuarios)                | ✅ 100% | db3 standalone         |
| Interfaz de Gestión                       | ✅ 100% | Incus-UI integrado     |

---

### Tecnologías Utilizadas

**Backend:**

- Python 3.11
- Flask 2.3.0
- PyJWT 2.8.0
- bcrypt 4.0.1
- pymongo 4.6.0

**Base de Datos:**

- MongoDB 7.0
- Replica Sets (rsA, rsB)

**Infraestructura:**

- Incus 6.0.1
- IncusOS
- VirtualBox 7.0
- Ngrok

**Gestión:**

- systemd
- Incus-UI (preinstalado)

---

### Características Destacadas

✨ **Alta Disponibilidad:**

- 3 réplicas por fragmento
- Failover automático (~10-15 seg)
- Sin pérdida de datos

✨ **Escalabilidad:**

- Fragmentación horizontal
- Fácil agregar más rangos
- Balance de carga distribuido

✨ **Seguridad:**

- JWT con expiración
- bcrypt (12 rounds)
- Middleware de autenticación

✨ **Portabilidad:**

- Contenedores exportables
- Configuración reproducible
- Independiente del host

---

## 9. 🎯 Conclusiones y Aprendizajes

### Logros del Proyecto

1. ✅ **Sistema distribuido completo** - 5 contenedores interconectados
2. ✅ **Fragmentación horizontal** - Balance automático A-M / N-Z
3. ✅ **Alta disponibilidad** - 6 réplicas MongoDB (3 por fragmento)
4. ✅ **Seguridad robusta** - JWT + bcrypt implementados
5. ✅ **Despliegue exitoso** - De desarrollo local a producción en VM
6. ✅ **Acceso público** - Aplicación expuesta via Ngrok

---

### Desafíos y Soluciones

🔧 Configurar replica sets con 3 instancias en mismo contenedor  
🔧 Sincronización de código entre desarrollo y producción  
🔧 Port forwarding VirtualBox + Ngrok  
🔧 Gestión de servicios con systemd  
🔧 Red bridge incusbr0 con IPs estáticas

---

### Aprendizajes Clave

💡 **Incus vs Docker:** Contenedores de sistema completo vs aplicación  
💡 **MongoDB Replica Set:** Failover automático sin intervención  
💡 **Fragmentación:** Estrategia debe alinearse con patrones de acceso  
💡 **JWT:** Autenticación stateless escalable  
💡 **systemd:** Gestión automática de servicios

---

## 10. ❓ Preguntas Frecuentes

### ¿Por qué Incus y no Docker?

- Necesitamos ejecutar múltiples servicios por contenedor (3 MongoDB por contenedor)
- Contenedores de sistema completo (con systemd)
- Red bridge nativa sin complejidad adicional

### ¿Por qué db3 no tiene réplicas?

- Datos de usuarios son de bajo volumen
- Enfoque del proyecto en fragmentación de productos
- Simplificación para demostración académica

### ¿Qué pasa si falla el PRIMARY?

- Elección automática de nuevo PRIMARY (~10 seg)
- Sin pérdida de datos (replicas sincronizadas)
- Aplicación continúa funcionando (driver maneja failover)

### ¿Cómo se distribuyen los productos?

- Por primera letra del nombre
- A-M → db1 (rsA)
- N-Z → db2 (rsB)
- Automático en el código

---

## 📚 Referencias

**Código del Proyecto:**

- GitHub: [github.com/CamiloMunozAL/Proyecto_distribuidos]
- Documentación: `DESARROLLO_COMPLETO.md`
- Diagramas: Carpeta `Diagrams/`

**Documentación Técnica:**

- MongoDB Replica Sets: https://docs.mongodb.com/manual/replication/
- Incus Documentation: https://linuxcontainers.org/incus/
- JWT.io: https://jwt.io/

---

## 🙏 Agradecimientos

Gracias por su atención.

**¿Preguntas?**

---

**Equipo de Desarrollo**  
Universidad: [Tu Universidad]  
Curso: Sistemas Distribuidos  
Noviembre 2025
