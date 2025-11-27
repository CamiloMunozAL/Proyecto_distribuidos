# Sistema Distribuido de Gestión de Productos con Incus

**Autores:** Equipo de Desarrollo  
**Fecha:** Noviembre 2025  
**Tecnología Principal:** Incus, Python/Flask, MongoDB

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tecnologías y Herramientas](#tecnologías-y-herramientas)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Fragmentación de Datos](#fragmentación-de-datos)
6. [Replicación y Alta Disponibilidad](#replicación-y-alta-disponibilidad)
7. [Implementación con Incus](#implementación-con-incus)
8. [Configuración de Servicios](#configuración-de-servicios)
9. [Despliegue y Exposición](#despliegue-y-exposición)
10. [Conclusiones](#conclusiones)

---

## 📖 Descripción General

Este proyecto implementa una **plataforma web distribuida de gestión de productos** utilizando una arquitectura de microservicios desplegada en contenedores Linux mediante **Incus**. El sistema incluye autenticación de usuarios, operaciones CRUD sobre productos, y una estrategia de fragmentación y replicación de datos para garantizar disponibilidad y tolerancia a fallos.

### Objetivos Cumplidos

- ✅ Arquitectura distribuida en 5 contenedores Incus
- ✅ Dashboard web con gestión de productos
- ✅ Sistema de autenticación JWT
- ✅ Fragmentación horizontal de base de datos
- ✅ Replicación de datos con MongoDB Replica Set
- ✅ Gestión mediante Incus-UI-Canonical
- ✅ Exposición pública con Ngrok

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      INCUS HOST                             │
│                    (IncusOS - VM)                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                 Incus-UI-Canonical                    │ │
│  │          (Gestión Gráfica de Contenedores)            │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ web-server   │  │ auth-server  │  │    db1       │    │
│  │ 10.10.10.11  │  │ 10.10.10.10  │  │ 10.10.10.12  │    │
│  │ Puerto: 3000 │  │ Puerto: 5000 │  │ Puertos:     │    │
│  │              │  │              │  │ 27017-27019  │    │
│  │ Flask App    │◄─┤ Auth JWT     │  │              │    │
│  │ Dashboard    │  │              │  │ MongoDB      │    │
│  │ CRUD         │  └──────────────┘  │ Replica Set  │    │
│  │              │                     │ rsA          │    │
│  │ Conexión:    │                     │ (Prod. A-M)  │    │
│  │ - rsA:27017  │◄────────────────────┤ • :27017 (P) │    │
│  │ - rsA:27018  │◄────────────────────┤ • :27018 (S) │    │
│  │ - rsA:27019  │◄────────────────────┤ • :27019 (S) │    │
│  └──────────────┘                     └──────────────┘    │
│                                                            │
│  ┌──────────────┐         ┌──────────────┐               │
│  │    db2       │         │    db3       │               │
│  │ 10.10.10.13  │         │ 10.10.10.14  │               │
│  │ Puertos:     │         │ Puerto:27017 │               │
│  │ 27017-27019  │         │              │               │
│  │              │         │ MongoDB      │               │
│  │ MongoDB      │         │ Standalone   │               │
│  │ Replica Set  │         │ (Usuarios)   │               │
│  │ rsB          │◄────────┤              │               │
│  │ (Prod. N-Z)  │         │ Sin réplicas │               │
│  │ • :27017 (P) │         └──────────────┘               │
│  │ • :27018 (S) │                                         │
│  │ • :27019 (S) │                                         │
│  └──────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
         │
         │ VirtualBox Port Forward (3000 → Host Windows)
         │ Ngrok Tunnel (Exposición Pública)
         ▼
    🌐 Internet
```

### Contenedores Desplegados

| Contenedor      | IP Interna  | Puertos     | Función                                 | Base de Datos                         |
| --------------- | ----------- | ----------- | --------------------------------------- | ------------------------------------- |
| **web-server**  | 10.10.10.11 | 3000        | Aplicación web, CRUD productos          | Cliente MongoDB                       |
| **auth-server** | 10.10.10.10 | 5000        | Autenticación JWT                       | Cliente MongoDB                       |
| **db1**         | 10.10.10.12 | 27017-27019 | MongoDB Replica Set rsA (Productos A-M) | 3 instancias: 1 Primary + 2 Secondary |
| **db2**         | 10.10.10.13 | 27017-27019 | MongoDB Replica Set rsB (Productos N-Z) | 3 instancias: 1 Primary + 2 Secondary |
| **db3**         | 10.10.10.14 | 27017       | MongoDB Standalone (Usuarios)           | 1 instancia sin réplicas              |

---

## 🛠️ Tecnologías y Herramientas

### Backend

- **Python 3.11+**: Lenguaje de programación principal
- **Flask 2.3.0**: Framework web ligero
- **Flask-CORS 4.0.0**: Manejo de CORS para APIs REST

### Autenticación

- **PyJWT 2.8.0**: Generación y validación de tokens JWT
- **bcrypt 4.0.1**: Hash seguro de contraseñas

### Base de Datos

- **MongoDB 7.0**: Sistema de base de datos NoSQL
- **pymongo 4.6.0**: Driver oficial de MongoDB para Python
- **MongoDB Replica Set**: Configuración rsA con 1 primary y 2 secondaries

### Contenedorización

- **Incus**: Sistema de contenedores Linux (fork de LXD)
- **IncusOS**: Sistema operativo optimizado para Incus
- **Incus-UI-Canonical**: Interfaz gráfica de gestión

### Infraestructura

- **VirtualBox**: Virtualización de IncusOS
- **Ngrok**: Túnel seguro para exposición pública
- **systemd**: Gestión de servicios en contenedores

### Desarrollo

- **python-dotenv 1.0.0**: Gestión de variables de entorno
- **requests 2.31.0**: Cliente HTTP para comunicación entre servicios

---

## 📁 Estructura del Proyecto

```
Proyecto_distribuidos/
│
├── auth-server/                    # Servidor de autenticación
│   ├── app.py                      # API REST de autenticación
│   ├── requirements.txt            # Dependencias Python
│   ├── start.sh                    # Script de inicio
│   ├── .env                        # Variables de entorno
│   ├── .env.example                # Plantilla de configuración
│   └── templates/
│       └── docs.html               # Documentación API
│
├── web-server/                     # Servidor web principal
│   ├── app.py                      # API REST y frontend
│   ├── requirements.txt            # Dependencias Python
│   ├── start.sh                    # Script de inicio
│   ├── .env                        # Variables de entorno
│   ├── .env.example                # Plantilla de configuración
│   ├── templates/                  # Plantillas HTML
│   │   ├── base.html               # Layout base
│   │   ├── login.html              # Página de login
│   │   ├── dashboard.html          # Dashboard principal
│   │   ├── add_product.html        # Formulario crear producto
│   │   ├── edit_product.html       # Formulario editar producto
│   │   ├── users.html              # Gestión de usuarios
│   │   └── register_user.html      # Registro de usuarios
│   └── static/                     # Recursos estáticos
│       ├── style.css               # Estilos CSS
│       └── main.js                 # Lógica JavaScript
│
├── scripts/                        # Scripts de configuración
│   ├── setup-systemd-db1.sh        # Config systemd para db1
│   ├── setup-systemd-db2.sh        # Config systemd para db2
│   ├── setup-systemd-db3.sh        # Config systemd para db3
│   ├── setup-systemd-auth-server.sh # Config systemd auth-server
│   ├── setup-systemd-web-server.sh  # Config systemd web-server
│   ├── sync-auth-server.sh         # Sincroniza código a contenedor
│   ├── sync-web-server.sh          # Sincroniza código a contenedor
│   ├── start-db1.sh                # Inicia servicios MongoDB db1
│   ├── start-db2.sh                # Inicia servicios MongoDB db2
│   └── start-db3.sh                # Inicia servicios MongoDB db3
│
├── local_mongo/                    # Datos MongoDB locales (desarrollo)
│   ├── db1/                        # Productos A-M
│   ├── db2/                        # Productos N-Z
│   └── db3/                        # Usuarios
│
├── start-local-mongo.sh            # Inicia MongoDB local (3 instancias)
├── stop-local-mongo.sh             # Detiene MongoDB local
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Documentación principal
```

### Descripción de Archivos Clave

#### `auth-server/app.py`

Servidor de autenticación que gestiona:

- **Registro de usuarios**: Valida datos, hashea contraseñas con bcrypt, almacena en DB3
- **Login**: Valida credenciales y genera tokens JWT con expiración de 1 hora
- **Verificación de tokens**: Middleware para validar tokens en peticiones protegidas
- **Documentación API**: Endpoint `/` con guía interactiva de uso

#### `web-server/app.py`

Servidor web principal que incluye:

- **Middleware de autenticación**: Verifica tokens antes de operaciones CRUD
- **CRUD de productos**: Create, Read, Update, Delete con fragmentación automática
- **Gestión de usuarios**: Listar, crear, eliminar usuarios (proxy a auth-server)
- **Lógica de fragmentación**: Función `get_database_for_product()` distribuye productos por inicial del nombre
- **Proxy de autenticación**: Reenvía peticiones de login/register al auth-server interno

#### `scripts/setup-systemd-*.sh`

Scripts que configuran servicios systemd en cada contenedor para:

- Iniciar MongoDB automáticamente al arrancar el contenedor
- Configurar replica set con parámetros específicos
- Gestionar reinicio automático en caso de fallos
- Establecer permisos y directorios correctos

---

## 🗂️ Fragmentación de Datos

### Estrategia: Fragmentación Horizontal por Rango Alfabético

Se implementó una **fragmentación horizontal** basada en el **nombre del producto**, dividiendo el espacio alfabético en dos rangos:

| Base de Datos         | Rango de Nombres | Ejemplo de Productos           | Replica Set | Contenedor |
| --------------------- | ---------------- | ------------------------------ | ----------- | ---------- |
| **products_db (A-M)** | A - M            | Arroz, Café, Leche, Manzana    | rsA         | db1        |
| **products_db (N-Z)** | N - Z            | Naranja, Pan, Queso, Zanahoria | rsB         | db2        |

### Implementación en Código

```python
def get_database_for_product(product_name):
    """
    Distribuye productos entre DB1 y DB2 basado en la primera letra del nombre
    DB1: Productos A-M
    DB2: Productos N-Z
    """
    if not product_name:
        raise ValueError("El nombre del producto es requerido")

    first_letter = product_name[0].upper()

    if 'A' <= first_letter <= 'M':
        return products_collection_db1, 'DB1 (A-M)'
    elif 'N' <= first_letter <= 'Z':
        return products_collection_db2, 'DB2 (N-Z)'
    else:
        # Números o símbolos van a DB1 por defecto
        return products_collection_db1, 'DB1 (default)'
```

### Ventajas de Esta Estrategia

1. **Distribución automática**: No requiere intervención manual para fragmentar
2. **Escalabilidad**: Fácil agregar más rangos (DB3: símbolos/números)
3. **Balance de carga**: Distribución relativamente uniforme en español
4. **Búsqueda eficiente**: Sabemos dónde buscar un producto por su nombre

### Operaciones CRUD con Fragmentación

#### Crear Producto

```python
# El sistema determina automáticamente la BD según el nombre
target_db, db_label = get_database_for_product(data['name'])
result = target_db.insert_one(new_product)
```

#### Leer Todos los Productos

```python
# Consulta ambas bases de datos y combina resultados
products_db1 = list(products_collection_db1.find({}))
products_db2 = list(products_collection_db2.find({}))
all_products = products_db1 + products_db2
```

#### Actualizar/Eliminar Producto

```python
# Busca primero en DB1, si no está, busca en DB2
product = products_collection_db1.find_one({'_id': ObjectId(product_id)})
target_db = products_collection_db1

if not product:
    product = products_collection_db2.find_one({'_id': ObjectId(product_id)})
    target_db = products_collection_db2
```

---

## 🔄 Replicación y Alta Disponibilidad

### Arquitectura de Replicación

Se implementaron **dos Replica Sets independientes** de MongoDB, cada uno con 3 instancias dentro de un mismo contenedor:

**Replica Set rsA (Productos A-M) - Contenedor db1:**

```
┌─────────────────────────────┐
│      Contenedor db1         │
│      10.10.10.12            │
│                             │
│  ┌─────────────────────┐   │
│  │  :27017 PRIMARY     │   │ ◄── Escrituras y lecturas
│  └──────────┬──────────┘   │
│             │               │
│  ┌──────────▼──────────┐   │
│  │  :27018 SECONDARY   │   │ ◄── Solo lectura
│  └─────────────────────┘   │
│             │               │
│  ┌──────────▼──────────┐   │
│  │  :27019 SECONDARY   │   │ ◄── Solo lectura
│  └─────────────────────┘   │
│                             │
│  Replica Set: rsA           │
│  DB: products_db (A-M)      │
└─────────────────────────────┘
```

**Replica Set rsB (Productos N-Z) - Contenedor db2:**

```
┌─────────────────────────────┐
│      Contenedor db2         │
│      10.10.10.13            │
│                             │
│  ┌─────────────────────┐   │
│  │  :27017 PRIMARY     │   │ ◄── Escrituras y lecturas
│  └──────────┬──────────┘   │
│             │               │
│  ┌──────────▼──────────┐   │
│  │  :27018 SECONDARY   │   │ ◄── Solo lectura
│  └─────────────────────┘   │
│             │               │
│  ┌──────────▼──────────┐   │
│  │  :27019 SECONDARY   │   │ ◄── Solo lectura
│  └─────────────────────┘   │
│                             │
│  Replica Set: rsB           │
│  DB: products_db (N-Z)      │
└─────────────────────────────┘
```

**Base de Datos de Usuarios - Contenedor db3:**

```
┌─────────────────────────────┐
│      Contenedor db3         │
│      10.10.10.14            │
│                             │
│  ┌─────────────────────┐   │
│  │  :27017 STANDALONE  │   │ ◄── Sin réplicas
│  └─────────────────────┘   │
│                             │
│  DB: auth_db (Usuarios)     │
│  Sin Replica Set            │
└─────────────────────────────┘
```

### Configuración de los Replica Sets

#### 1. Inicialización del Replica Set rsA en db1

**Las 3 instancias MongoDB están en el mismo contenedor db1:**

```bash
# Iniciar las 3 instancias de MongoDB en db1
incus exec db1 -- systemctl start mongod-27017
incus exec db1 -- systemctl start mongod-27018
incus exec db1 -- systemctl start mongod-27019

# Configurar el replica set rsA
incus exec db1 -- mongosh --port 27017 --eval '
rs.initiate({
  _id: "rsA",
  members: [
    { _id: 0, host: "10.10.10.12:27017", priority: 3 },
    { _id: 1, host: "10.10.10.12:27018", priority: 2 },
    { _id: 2, host: "10.10.10.12:27019", priority: 1 }
  ]
})
'
```

#### 2. Inicialización del Replica Set rsB en db2

**Las 3 instancias MongoDB están en el mismo contenedor db2:**

```bash
# Iniciar las 3 instancias de MongoDB en db2
incus exec db2 -- systemctl start mongod-27017
incus exec db2 -- systemctl start mongod-27018
incus exec db2 -- systemctl start mongod-27019

# Configurar el replica set rsB
incus exec db2 -- mongosh --port 27017 --eval '
rs.initiate({
  _id: "rsB",
  members: [
    { _id: 0, host: "10.10.10.13:27017", priority: 3 },
    { _id: 1, host: "10.10.10.13:27018", priority: 2 },
    { _id: 2, host: "10.10.10.13:27019", priority: 1 }
  ]
})
'
```

#### 3. Configuración de db3 (Standalone - Sin Réplicas)

```bash
# Iniciar única instancia en db3
incus exec db3 -- systemctl start mongod-27017
# No requiere configuración de replica set
```

#### 4. Verificación del Estado

```bash
# Verificar rsA en db1
incus exec db1 -- mongosh --port 27017 --eval 'rs.status()'

# Verificar rsB en db2
incus exec db2 -- mongosh --port 27017 --eval 'rs.status()'

# Verificar db3 standalone
incus exec db3 -- mongosh --port 27017 --eval 'db.serverStatus().host'
```

### Funcionamiento de la Replicación

1. **Escrituras**: Solo el PRIMARY acepta operaciones de escritura
2. **Lectura**: Por defecto, solo el PRIMARY acepta lecturas (read preference)
3. **Replicación**: Los SECONDARIES copian continuamente el oplog del PRIMARY
4. **Failover automático**: Si el PRIMARY falla, se elige automáticamente un nuevo PRIMARY
5. **Consistencia eventual**: Los SECONDARIES pueden tener un pequeño retraso respecto al PRIMARY

### Bases de Datos Distribuidas

La arquitectura utiliza 3 contenedores MongoDB con propósitos específicos:

**Contenedor db1 (Replica Set rsA):**

- **products_db**: Almacena productos con nombres de A-M
- Tiene 3 instancias MongoDB (27017-27019) formando el replica set rsA
- Una instancia es PRIMARY, las otras dos SECONDARY

**Contenedor db2 (Replica Set rsB):**

- **products_db**: Almacena productos con nombres de N-Z
- Tiene 3 instancias MongoDB (27017-27019) formando el replica set rsB
- Una instancia es PRIMARY, las otras dos SECONDARY

**Contenedor db3 (Standalone):**

- **auth_db**: Almacena usuarios y credenciales de autenticación
- Tiene 1 única instancia MongoDB (27017)
- **No tiene réplicas** - configuración standalone

### Ventajas de Esta Arquitectura

✅ **Alta disponibilidad por fragmento**: Cada fragmento (A-M y N-Z) tiene su propio replica set  
✅ **Tolerancia a fallos local**: Si falla una instancia dentro de db1 o db2, las otras continúan  
✅ **Backup en caliente**: Cada PRIMARY tiene 2 SECONDARIES como respaldo  
✅ **Escalabilidad de lectura**: Se pueden distribuir lecturas entre las 3 instancias de cada replica set  
✅ **Aislamiento de fallos**: Un problema en rsA no afecta a rsB y viceversa  
✅ **Simplicidad en usuarios**: db3 standalone es suficiente para autenticación (sin necesidad de réplicas)

---

## 🚀 Implementación con Incus

### Fase 1: Desarrollo Local (Ubuntu)

#### Creación de Contenedores

```bash
# Crear contenedor base Ubuntu 22.04
incus launch ubuntu:22.04 auth-server
incus launch ubuntu:22.04 web-server
incus launch ubuntu:22.04 db1
incus launch ubuntu:22.04 db2
incus launch ubuntu:22.04 db3

# Configurar red incusbr0
incus network attach incusbr0 auth-server eth0
incus network attach incusbr0 web-server eth0
incus network attach incusbr0 db1 eth0
incus network attach incusbr0 db2 eth0
incus network attach incusbr0 db3 eth0

# Asignar IPs estáticas
incus config device set auth-server eth0 ipv4.address 10.10.10.10
incus config device set web-server eth0 ipv4.address 10.10.10.11
incus config device set db1 eth0 ipv4.address 10.10.10.12
incus config device set db2 eth0 ipv4.address 10.10.10.13
incus config device set db3 eth0 ipv4.address 10.10.10.14
```

#### Instalación de Dependencias en Contenedores

**Contenedores de Bases de Datos (db1, db2, db3):**

```bash
incus exec db1 -- bash -c '
  apt update && apt install -y mongodb-org
  systemctl enable mongod
  mkdir -p /var/lib/mongo{1,2,3}
  chown -R mongodb:mongodb /var/lib/mongo{1,2,3}
'
```

**Contenedores de Aplicación (auth-server, web-server):**

```bash
incus exec auth-server -- bash -c '
  apt update && apt install -y python3 python3-pip python3-venv
  pip3 install flask flask-cors pyjwt bcrypt pymongo requests python-dotenv
'
```

#### Sincronización de Código

```bash
# Script sync-auth-server.sh
incus file push -r auth-server/ auth-server/home/ubuntu/
incus file push auth-server/.env auth-server/home/ubuntu/auth-server/

# Script sync-web-server.sh
incus file push -r web-server/ web-server/home/ubuntu/
incus file push web-server/.env web-server/home/ubuntu/web-server/
```

### Fase 2: Exportación de Contenedores

Una vez configurados los contenedores en el entorno de desarrollo local:

```bash
# Detener contenedores antes de exportar
incus stop auth-server web-server db1 db2 db3

# Exportar cada contenedor a formato tar.gz
incus export auth-server auth-server.tar.gz
incus export web-server web-server.tar.gz
incus export db1 db1.tar.gz
incus export db2 db2.tar.gz
incus export db3 db3.tar.gz

# Transferir archivos tar.gz al compañero
# (USB, compartir en red, OneDrive, etc.)
```

### Fase 3: Despliegue en IncusOS (Máquina Virtual)

#### Instalación de IncusOS

1. Descargar ISO de **IncusOS** desde sitio oficial
2. Crear VM en VirtualBox con:
   - 4 GB RAM mínimo
   - 50 GB disco
   - Adaptador puente para red
3. Instalar IncusOS siguiendo wizard
4. Instalar **Incus-UI-Canonical** para gestión gráfica

#### Importación de Contenedores

```bash
# Copiar archivos tar.gz a la VM IncusOS
scp *.tar.gz ubuntu@incus-vm:/home/ubuntu/

# Importar contenedores en IncusOS
incus import auth-server.tar.gz
incus import web-server.tar.gz
incus import db1.tar.gz
incus import db2.tar.gz
incus import db3.tar.gz
```

#### Configuración de Red en IncusOS

```bash
# Verificar red incusbr0 existe
incus network list

# Si no existe, crear red bridge
incus network create incusbr0 \
  ipv4.address=10.10.10.1/24 \
  ipv4.nat=true

# Adjuntar contenedores a la red
incus network attach incusbr0 auth-server eth0
incus network attach incusbr0 web-server eth0
incus network attach incusbr0 db1 eth0
incus network attach incusbr0 db2 eth0
incus network attach incusbr0 db3 eth0

# Iniciar contenedores
incus start auth-server web-server db1 db2 db3
```

---

## ⚙️ Configuración de Servicios

### ¿Por Qué Usar systemd?

**systemd** es el sistema de inicialización estándar de Linux que gestiona servicios del sistema. Se utilizó por las siguientes razones:

1. **Inicio automático**: Los servicios arrancan automáticamente al encender el contenedor
2. **Reinicio ante fallos**: Si MongoDB o Flask se detienen inesperadamente, systemd los reinicia
3. **Gestión centralizada**: Comandos uniformes para iniciar/detener/verificar servicios
4. **Logs estructurados**: Integración con journalctl para depuración
5. **Dependencias**: Define orden de inicio (MongoDB antes que Flask)

### Configuración de MongoDB en db1 (3 instancias - Replica Set rsA)

El contenedor db1 ejecuta **3 instancias de MongoDB** en diferentes puertos, todas parte del replica set rsA.

**Archivo: `/etc/systemd/system/mongod-27017.service` (PRIMARY)**

```ini
[Unit]
Description=MongoDB Database Server rsA (Port 27017 - PRIMARY)
After=network.target

[Service]
Type=forking
User=mongodb
Group=mongodb
ExecStart=/usr/bin/mongod --replSet rsA --dbpath /var/lib/mongo1 --port 27017 --bind_ip 0.0.0.0 --fork --logpath /var/lib/mongo1/mongo.log --pidfilepath /var/lib/mongo1/mongod.pid
PIDFile=/var/lib/mongo1/mongod.pid
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Archivo: `/etc/systemd/system/mongod-27018.service` (SECONDARY)**

```ini
[Unit]
Description=MongoDB Database Server rsA (Port 27018 - SECONDARY)
After=network.target mongod-27017.service

[Service]
Type=forking
User=mongodb
Group=mongodb
ExecStart=/usr/bin/mongod --replSet rsA --dbpath /var/lib/mongo2 --port 27018 --bind_ip 0.0.0.0 --fork --logpath /var/lib/mongo2/mongo.log --pidfilepath /var/lib/mongo2/mongod.pid
PIDFile=/var/lib/mongo2/mongod.pid
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Archivo: `/etc/systemd/system/mongod-27019.service` (SECONDARY)**

```ini
[Unit]
Description=MongoDB Database Server rsA (Port 27019 - SECONDARY)
After=network.target mongod-27017.service

[Service]
Type=forking
User=mongodb
Group=mongodb
ExecStart=/usr/bin/mongod --replSet rsA --dbpath /var/lib/mongo3 --port 27019 --bind_ip 0.0.0.0 --fork --logpath /var/lib/mongo3/mongo.log --pidfilepath /var/lib/mongo3/mongod.pid
PIDFile=/var/lib/mongo3/mongod.pid
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Parámetros importantes:**

- `--replSet rsA`: Nombre del replica set (rsA para productos A-M)
- `--dbpath`: Directorio diferente para cada instancia (/var/lib/mongo1, mongo2, mongo3)
- `--port`: Puerto diferente para cada instancia (27017, 27018, 27019)
- `--bind_ip 0.0.0.0`: Acepta conexiones de cualquier IP (red Incus)
- `--fork`: Se ejecuta en background
- `Restart=on-failure`: Reinicio automático si falla

**Nota:** El contenedor db2 tiene una configuración idéntica pero con `--replSet rsB` para productos N-Z.

### Configuración de auth-server

Archivo: `/etc/systemd/system/auth-server.service`

```ini
[Unit]
Description=Auth Server - API de Autenticación JWT
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/auth-server
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Configuración de web-server

Archivo: `/etc/systemd/system/web-server.service`

```ini
[Unit]
Description=Web Server - Dashboard y CRUD Productos
After=network.target mongod-27017.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/web-server
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Nota:** `After=mongod-27017.service` asegura que MongoDB esté iniciado antes que Flask.

### Comandos de Gestión

```bash
# Habilitar inicio automático
incus exec auth-server -- systemctl enable auth-server
incus exec web-server -- systemctl enable web-server
incus exec db1 -- systemctl enable mongod-27017 mongod-27018 mongod-27019

# Iniciar servicios
incus exec auth-server -- systemctl start auth-server
incus exec web-server -- systemctl start web-server

# Verificar estado
incus exec web-server -- systemctl status web-server

# Ver logs en tiempo real
incus exec web-server -- journalctl -u web-server -f

# Reiniciar servicio
incus exec web-server -- systemctl restart web-server
```

---

## 🌐 Despliegue y Exposición

### Arquitectura de Red Completa

```
Internet
   │
   │ Ngrok Tunnel
   ▼
Windows Host (PC Local)
   │
   │ VirtualBox NAT + Port Forward 3000→3000
   ▼
IncusOS VM (VirtualBox)
   │
   │ incusbr0 Bridge (10.10.10.0/24)
   ▼
┌──────────────────────────────────────┐
│ Contenedores Incus                   │
│                                      │
│ web-server   (10.10.10.11:3000)     │
│ auth-server  (10.10.10.10:5000)     │
│ db1          (10.10.10.12:27017)    │
│ db2          (10.10.10.13:27017)    │
│ db3          (10.10.10.14:27017)    │
└──────────────────────────────────────┘
```

### Paso 1: Port Forwarding en VirtualBox

**Configuración de Red en VM:**

1. Abrir VirtualBox
2. Seleccionar VM IncusOS → Configuración → Red
3. Adaptador 1: NAT
4. Reenvío de puertos:
   - **Nombre:** web-server
   - **Protocolo:** TCP
   - **IP Anfitrión:** 127.0.0.1
   - **Puerto Anfitrión:** 3000
   - **IP Invitado:** 10.10.10.11
   - **Puerto Invitado:** 3000

Esto permite acceder desde Windows a `http://localhost:3000` y se reenvía al contenedor web-server.

### Paso 2: Acceso Remoto con Ngrok

**Instalación y Uso:**

```bash
# En Windows (descargado de ngrok.com)
ngrok http 3000

# Output:
# Forwarding  https://abc123.ngrok-free.app -> http://localhost:3000
```

**Ventajas de Ngrok:**

- ✅ Túnel HTTPS seguro sin configurar certificados
- ✅ URL pública temporal para demostración
- ✅ Acceso desde cualquier lugar con internet
- ✅ Logs de peticiones HTTP en tiempo real

### Paso 3: Gestión con Incus-UI-Canonical

**Exposición de Incus-UI con Ngrok:**

```bash
# En el host IncusOS, exponer puerto de Incus-UI (8443)
ngrok http https://localhost:8443

# Output:
# Forwarding  https://xyz789.ngrok-free.app -> https://localhost:8443
```

**Esto permitió al equipo:**

- Gestionar contenedores desde casa mediante navegador
- Monitorear recursos (CPU, RAM, disco)
- Ver logs en tiempo real
- Iniciar/detener contenedores remotamente
- Ajustar configuración de red

### Configuración de Variables de Entorno

**auth-server/.env:**

```bash
PORT=5000
DEBUG=False
SECRET_KEY=produccion_clave_segura_xyz
DB3_URL=mongodb://10.10.10.12:27017,10.10.10.13:27017,10.10.10.14:27017/auth_db?replicaSet=rsA
```

**web-server/.env:**

```bash
PORT=3000
DEBUG=False
SECRET_KEY=produccion_clave_segura_xyz
AUTH_SERVER_URL=http://10.10.10.10:5000

# Replica Set rsA (Productos A-M) - 3 instancias en db1
DB1_URL=mongodb://10.10.10.12:27017,10.10.10.12:27018,10.10.10.12:27019/products_db?replicaSet=rsA

# Replica Set rsB (Productos N-Z) - 3 instancias en db2
DB2_URL=mongodb://10.10.10.13:27017,10.10.10.13:27018,10.10.10.13:27019/products_db?replicaSet=rsB

# MongoDB Standalone (Usuarios) - 1 instancia en db3
DB3_URL=mongodb://10.10.10.14:27017/auth_db
```

**Notas importantes:**

- **DB1_URL**: Incluye las 3 instancias del replica set rsA (todas en IP 10.10.10.12)
- **DB2_URL**: Incluye las 3 instancias del replica set rsB (todas en IP 10.10.10.13)
- **DB3_URL**: Conexión directa a instancia standalone (sin replica set)
- El driver de MongoDB automáticamente se conecta al PRIMARY y distribuye lecturas

---

## 🧪 Pruebas y Validación

### Pruebas de Funcionalidad

#### 1. Autenticación

```bash
# Registro de usuario
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@test.com","password":"admin123"}'

# Login
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Respuesta: {"token":"eyJhbGc...", "username":"admin"}
```

#### 2. CRUD de Productos

```bash
# Crear producto (se guarda en DB1 por inicial 'A')
curl -X POST http://localhost:3000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Arroz","price":5.0,"stock":100,"category":"Granos"}'

# Crear producto (se guarda en DB2 por inicial 'P')
curl -X POST http://localhost:3000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pan","price":2.5,"stock":50,"category":"Panadería"}'

# Listar todos los productos (consulta DB1 + DB2)
curl -X GET http://localhost:3000/products \
  -H "Authorization: Bearer <token>"
```

#### 3. Verificación de Fragmentación

```bash
# Conectar a db1 y verificar productos A-M
incus exec db1 -- mongosh --port 27017 --eval '
  use products_db
  db.products.find({}, {name:1, _id:0})
'

# Conectar a db2 y verificar productos N-Z
incus exec db2 -- mongosh --port 27017 --eval '
  use products_db
  db.products.find({}, {name:1, _id:0})
'
```

### Pruebas de Replicación

#### 1. Verificar Estado del Replica Set rsA (db1)

```bash
# Verificar las 3 instancias del replica set rsA
incus exec db1 -- mongosh --port 27017 --eval 'rs.status()' | grep -E "name|stateStr"
```

**Salida esperada:**

```
name: "10.10.10.12:27017", stateStr: "PRIMARY"
name: "10.10.10.12:27018", stateStr: "SECONDARY"
name: "10.10.10.12:27019", stateStr: "SECONDARY"
```

#### 2. Verificar Estado del Replica Set rsB (db2)

```bash
# Verificar las 3 instancias del replica set rsB
incus exec db2 -- mongosh --port 27017 --eval 'rs.status()' | grep -E "name|stateStr"
```

**Salida esperada:**

```
name: "10.10.10.13:27017", stateStr: "PRIMARY"
name: "10.10.10.13:27018", stateStr: "SECONDARY"
name: "10.10.10.13:27019", stateStr: "SECONDARY"
```

#### 3. Prueba de Failover en rsA

```bash
# Detener el PRIMARY de rsA (puerto 27017 en db1)
incus exec db1 -- systemctl stop mongod-27017

# Esperar 10 segundos para elección de nuevo PRIMARY
sleep 10

# Verificar nuevo PRIMARY (debería ser 27018 o 27019)
incus exec db1 -- mongosh --port 27018 --eval 'rs.status()' | grep -E "name|stateStr"
```

**Resultado:** La instancia en puerto 27018 o 27019 se convierte automáticamente en PRIMARY.

#### 4. Verificar Sincronización Interna en rsA

```bash
# Insertar producto en PRIMARY de rsA (puerto 27017 en db1)
incus exec db1 -- mongosh --port 27017 --eval '
  use products_db
  db.products.insertOne({name:"Arroz",price:5,stock:100})
'

# Verificar en SECONDARY de rsA (puerto 27018 en db1)
incus exec db1 -- mongosh --port 27018 --eval '
  rs.secondaryOk()
  use products_db
  db.products.find({name:"Arroz"})
'
```

**Resultado:** El producto aparece en el SECONDARY, confirmando replicación exitosa dentro del mismo contenedor.

#### 5. Verificar Fragmentación Entre rsA y rsB

```bash
# Insertar producto A-M en rsA (db1)
curl -X POST http://10.10.10.11:3000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Manzana","price":2.5,"stock":50}'

# Insertar producto N-Z en rsB (db2)
curl -X POST http://10.10.10.11:3000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Naranja","price":3.0,"stock":60}'

# Verificar que Manzana está en rsA (db1)
incus exec db1 -- mongosh --port 27017 --eval '
  use products_db
  db.products.find({name:"Manzana"})
'

# Verificar que Naranja está en rsB (db2)
incus exec db2 -- mongosh --port 27017 --eval '
  use products_db
  db.products.find({name:"Naranja"})
'
```

**Resultado:** Cada producto se almacena en su replica set correspondiente según la inicial del nombre.

---

## 📊 Monitoreo y Logs

### Logs de Contenedores

```bash
# Logs de aplicación web-server
incus exec web-server -- journalctl -u web-server -n 50

# Logs de MongoDB db1
incus exec db1 -- tail -f /var/lib/mongo1/mongo.log

# Logs del sistema en contenedor
incus exec web-server -- dmesg
```

### Monitoreo de Recursos

```bash
# CPU y memoria de contenedor
incus info web-server

# Procesos activos
incus exec web-server -- top

# Conexiones de red
incus exec web-server -- ss -tuln | grep LISTEN
```

### Documentación de la API

Ambos servidores incluyen documentación interactiva:

- **Auth Server:** http://10.10.10.10:5000/
- **Web Server:** http://10.10.10.11:3000/docs

---

## 🎯 Conclusiones

### Logros Alcanzados

1. ✅ **Arquitectura Distribuida Completa**

   - 5 contenedores Incus interconectados
   - Separación de responsabilidades (auth, web, databases)
   - Comunicación fluida entre microservicios

2. ✅ **Fragmentación de Datos Efectiva**

   - División horizontal por rango alfabético
   - Distribución automática de productos
   - Balance de carga entre DB1 y DB2

3. ✅ **Alta Disponibilidad**

   - Replica Set MongoDB con 3 nodos
   - Failover automático ante fallos
   - Tolerancia a pérdida de 1 nodo

4. ✅ **Seguridad Implementada**

   - Autenticación JWT con tokens de 1 hora
   - Hash de contraseñas con bcrypt
   - Middleware de autorización en endpoints

5. ✅ **Gestión Simplificada**

   - systemd para administración de servicios
   - Scripts automatizados de sincronización
   - Incus-UI para gestión gráfica

6. ✅ **Despliegue Exitoso**
   - Exportación/importación de contenedores
   - Configuración en IncusOS en VM
   - Exposición pública con Ngrok

### Desafíos Superados

1. **Configuración de Replica Set**: Ajustar bind_ip y firewall para comunicación entre contenedores
2. **Sincronización de código**: Crear scripts para actualizar código en contenedores sin reiniciar
3. **Gestión de IPs estáticas**: Configurar red incusbr0 con direcciones fijas
4. **Port forwarding**: Configurar VirtualBox para exponer web-server al host Windows
5. **Variables de entorno**: Adaptar configuración entre desarrollo local y producción

### Aprendizajes Clave

- **Incus es más ligero que Docker**: Contenedores completos de Linux sin overhead de VM
- **MongoDB Replica Set es robusto**: Failover funciona automáticamente sin pérdida de datos
- **systemd simplifica gestión**: Servicios arrancan automáticamente y se reinician ante fallos
- **Fragmentación requiere planificación**: La estrategia elegida debe alinearse con patrones de acceso
- **La documentación es crucial**: APIs bien documentadas facilitan integración y debugging

### Trabajo Futuro

- **Balanceo de carga**: Implementar Nginx para distribuir peticiones entre múltiples web-servers
- **Monitoreo avanzado**: Integrar Prometheus + Grafana para métricas en tiempo real
- **Caché distribuida**: Agregar Redis para mejorar rendimiento de consultas frecuentes
- **CI/CD**: Automatizar despliegue con GitLab CI o GitHub Actions
- **HTTPS nativo**: Configurar certificados SSL con Let's Encrypt

### Reflexión Final

Este proyecto demostró exitosamente la capacidad de diseñar e implementar un **sistema distribuido completo** utilizando tecnologías modernas de contenedorización. La arquitectura con Incus permitió una separación clara de responsabilidades, mientras que MongoDB Replica Set garantizó alta disponibilidad y tolerancia a fallos. La experiencia de exportar contenedores desde un entorno de desarrollo local hacia una máquina virtual con IncusOS reflejó un flujo de trabajo realista de DevOps.

El uso de **systemd** para gestión de servicios, **fragmentación horizontal** para distribución de datos, y **JWT** para autenticación, representan prácticas estándar de la industria. Este proyecto no solo cumplió con los requisitos académicos, sino que también generó una base sólida para proyectos distribuidos futuros.

---

**Proyecto desarrollado para el curso de Sistemas Distribuidos**  
**Universidad:** [Tu Universidad]  
**Fecha de entrega:** Noviembre 2025
