# Sistema Distribuido de Gestión de Productos

**Fecha:** Noviembre 2025  
**Tecnologías:** Incus, Python/Flask, MongoDB

---

## Introducción

Este proyecto es una aplicación web para gestionar productos usando contenedores Incus. La aplicación permite crear, leer, actualizar y eliminar productos desde un navegador web. Los datos están distribuidos entre dos bases de datos MongoDB según el nombre del producto, y cada base de datos tiene réplicas para evitar pérdida de información.

El sistema tiene 5 contenedores trabajando juntos:

- 1 servidor web con la interfaz
- 1 servidor de autenticación
- 3 bases de datos MongoDB

### Lo que se logró

- Sistema funcionando en contenedores Incus
- Interfaz web para gestionar productos
- Login con usuarios y contraseñas
- Datos divididos entre dos bases de datos
- Réplicas de MongoDB para no perder información
- Acceso desde internet con Ngrok

---

## Arquitectura del Sistema

El sistema usa 5 contenedores conectados en una red privada:

| Contenedor      | IP          | Puerto | Función                       |
| --------------- | ----------- | ------ | ----------------------------- |
| **web-server**  | 10.10.10.11 | 3000   | Interfaz web y dashboard      |
| **auth-server** | 10.10.10.10 | 5000   | Autenticación de usuarios     |
| **db1**         | 10.10.10.12 | 27017  | Base de datos (productos A-M) |
| **db2**         | 10.10.10.13 | 27017  | Base de datos (productos N-Z) |
| **db3**         | 10.10.10.14 | 27017  | Base de datos (usuarios)      |

**Cómo funciona:**

1. El usuario accede al web-server desde el navegador
2. Para hacer login, web-server le pregunta a auth-server si el usuario existe
3. Una vez autenticado, puede crear/editar/eliminar productos
4. Los productos se guardan en db1 o db2 según su nombre
5. Los usuarios se guardan en db3

---

## Tecnologías Usadas

**Lenguaje y Framework:**

- Python 3.11 para el backend
- Flask para crear la aplicación web
- HTML/CSS/JavaScript para el frontend

**Base de Datos:**

- MongoDB 7.0 (base de datos NoSQL)
- pymongo para conectar Python con MongoDB

**Seguridad:**

- JWT para manejo de sesiones
- bcrypt para encriptar contraseñas

**Contenedores:**

- Incus para crear y gestionar contenedores Linux
- VirtualBox para correr IncusOS en una máquina virtual

**Otros:**

- systemd para que los servicios arranquen automáticamente
- Ngrok para acceder a la aplicación desde internet

---

## Estructura del Proyecto

El proyecto tiene dos carpetas principales:

**auth-server/** - Maneja el registro y login de usuarios

- `app.py`: código del servidor de autenticación
- `requirements.txt`: librerías necesarias

**web-server/** - La aplicación web principal

- `app.py`: código del servidor web
- `templates/`: páginas HTML (login, dashboard, productos)
- `static/`: estilos CSS y JavaScript

**Archivos importantes:**

- `start.sh` en cada carpeta para iniciar los servidores
- `.env` con configuración (URLs de bases de datos, puertos)

---

## Fragmentación de Datos

La fragmentación es dividir los datos entre varias bases de datos. En este proyecto se dividió por el nombre del producto:

| Base de Datos | Nombres que guarda       | Ejemplos                |
| ------------- | ------------------------ | ----------------------- |
| **db1**       | Productos de la A a la M | Arroz, Café, Manzana    |
| **db2**       | Productos de la N a la Z | Naranja, Pan, Zanahoria |

**¿Cómo funciona?**

Cuando se crea un producto, el código mira la primera letra del nombre:

- Si empieza con A-M → se guarda en db1
- Si empieza con N-Z → se guarda en db2

Esto lo hace automáticamente esta función en `web-server/app.py`:

```python
def get_database_for_product(product_name):
    first_letter = product_name[0].upper()

    if 'A' <= first_letter <= 'M':
        return products_collection_db1
    else:
        return products_collection_db2
```

**Ventajas:**

- Los datos están balanceados entre las dos bases de datos
- Si una base de datos tiene problemas, la otra sigue funcionando
- Es fácil saber dónde buscar un producto

---

## Replicación y Alta Disponibilidad

La replicación significa tener copias de los datos para no perderlos. Cada base de datos (db1 y db2) tiene 3 copias de MongoDB corriendo en diferentes puertos:

**Contenedor db1 (productos A-M):**

- Puerto 27017: PRIMARY (copia principal)
- Puerto 27018: SECONDARY (copia de respaldo)
- Puerto 27019: SECONDARY (copia de respaldo)

**Contenedor db2 (productos N-Z):**

- Puerto 27017: PRIMARY (copia principal)
- Puerto 27018: SECONDARY (copia de respaldo)
- Puerto 27019: SECONDARY (copia de respaldo)

**Contenedor db3 (usuarios):**

- Puerto 27017: base de datos simple sin réplicas

**¿Para qué sirve?**

Si el PRIMARY se cae, automáticamente uno de los SECONDARY se convierte en PRIMARY. Así la aplicación sigue funcionando sin perder datos.

### Configuración de Réplicas

Para configurar las réplicas se ejecutó este comando en db1:

```bash
incus exec db1 -- mongosh --port 27017 --eval '
rs.initiate({
  _id: "rsA",
  members: [
    { _id: 0, host: "10.10.10.12:27017", priority: 1 },
    { _id: 1, host: "10.10.10.12:27018", priority: 1 },
    { _id: 2, host: "10.10.10.12:27019", priority: 1 }
  ]
})
'
```

Lo mismo se hizo en db2 pero con el nombre "rsB" y la IP 10.10.10.13.

---

## Implementación con Incus

### Crear los Contenedores

Primero se crearon 5 contenedores Ubuntu:

```bash
incus launch ubuntu:22.04 auth-server
incus launch ubuntu:22.04 web-server
incus launch ubuntu:22.04 db1
incus launch ubuntu:22.04 db2
incus launch ubuntu:22.04 db3
```

Luego se les asignaron IPs fijas:

```bash
incus config device set auth-server eth0 ipv4.address 10.10.10.10
incus config device set web-server eth0 ipv4.address 10.10.10.11
incus config device set db1 eth0 ipv4.address 10.10.10.12
incus config device set db2 eth0 ipv4.address 10.10.10.13
incus config device set db3 eth0 ipv4.address 10.10.10.14
```

### Instalar Programas

En los contenedores de base de datos:

```bash
incus exec db1 -- apt install -y mongodb-org
```

En los servidores web:

```bash
incus exec web-server -- apt install -y python3 python3-pip
incus exec web-server -- pip3 install flask pymongo pyjwt bcrypt
```

### Copiar el Código

Para pasar el código a los contenedores:

```bash
incus file push -r web-server/ web-server/home/ubuntu/
incus file push -r auth-server/ auth-server/home/ubuntu/
```

### Exportar e Importar

Para mover los contenedores a otra máquina:

```bash
incus export web-server web-server.tar.gz
incus import web-server.tar.gz
```

---

## Configuración de Servicios

### systemd para Inicio Automático

Para que los programas arranquen solos cuando se enciende el contenedor, se configuró systemd.

**Archivo de servicio para MongoDB en db1:**

Se creó `/etc/systemd/system/mongod-27017.service`:

```ini
[Unit]
Description=MongoDB Database Server
After=network.target

[Service]
Type=forking
User=mongodb
ExecStart=/usr/bin/mongod --replSet rsA --dbpath /var/lib/mongo1 --port 27017 --bind_ip 0.0.0.0 --fork
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Se crearon archivos similares para los puertos 27018 y 27019.

**Archivo de servicio para web-server:**

Se creó `/etc/systemd/system/web-server.service`:

```ini
[Unit]
Description=Web Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/web-server
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Para activar los servicios:**

```bash
incus exec web-server -- systemctl enable web-server
incus exec web-server -- systemctl start web-server
```

---

## Despliegue y Acceso Público

### Arquitectura de Red Completa

La conexión entre los contenedores y el usuario final funciona en varias capas:

**1. Dentro de la VM (Red Incus):**

- Los contenedores están en la red `incusbr0` (10.10.10.0/24)
- web-server tiene IP 10.10.10.11 puerto 3000
- auth-server tiene IP 10.10.10.10 puerto 5000

**2. Proxy de Incus:**

- Incus tiene un proxy interno que redirige peticiones
- El puerto 3000 de la VM → contenedor web-server (10.10.10.11:3000)
- El puerto 5000 de la VM → contenedor auth-server (10.10.10.10:5000)
- El puerto 8443 de la VM → Incus-UI (acceso completo a la VM como desarrollador)

**3. VirtualBox NAT Port Forwarding:**

- Redirige puertos de la VM al host Windows:
  - `Windows:3000` → `VM:3000` → `contenedor web-server:3000`
  - `Windows:8443` → `VM:8443` → `Incus-UI`

**4. Ngrok (Acceso Público):**

- Ngrok se ejecuta en el host Windows
- Apunta al mismo puerto que VirtualBox está exponiendo
- `ngrok http 3000` crea túnel a `Windows:3000`
- Genera URL pública: `https://abc123.ngrok-free.app`

### Configuración de VirtualBox

En VirtualBox se configuró NAT port forwarding:

**Para la aplicación web:**

- IP Anfitrión: 127.0.0.1
- Puerto Anfitrión: 3000
- IP Invitado: (IP de la VM)
- Puerto Invitado: 3000

**Para Incus-UI:**

- IP Anfitrión: 127.0.0.1
- Puerto Anfitrión: 8443
- IP Invitado: (IP de la VM)
- Puerto Invitado: 8443

Así se puede abrir `http://localhost:3000` en el navegador de Windows.

### Acceder desde Internet

Para acceso público se usó Ngrok en Windows:

```bash
ngrok http 3000
```

Esto genera una URL pública como `https://abc123.ngrok-free.app` que cualquiera puede abrir. El flujo completo es:

```
Internet → Ngrok → Windows:3000 → VM:3000 → web-server:3000
```

### Variables de Entorno

En `web-server/.env`:

```bash
PORT=3000
AUTH_SERVER_URL=http://10.10.10.10:5000
DB1_URL=mongodb://10.10.10.12:27017,10.10.10.12:27018,10.10.10.12:27019/products_db?replicaSet=rsA
DB2_URL=mongodb://10.10.10.13:27017,10.10.10.13:27018,10.10.10.13:27019/products_db?replicaSet=rsB
DB3_URL=mongodb://10.10.10.14:27017/auth_db
```

Estas URLs le dicen al web-server dónde están las bases de datos.

---

## Pruebas Realizadas

### Probar la Fragmentación

Para verificar que los productos se guardan en la base de datos correcta:

```bash
# Ver productos en db1 (A-M)
incus exec db1 -- mongosh --port 27017 --eval 'use products_db; db.products.find()'

# Ver productos en db2 (N-Z)
incus exec db2 -- mongosh --port 27017 --eval 'use products_db; db.products.find()'
```

### Probar la Replicación

Para ver el estado de las réplicas:

```bash
incus exec db1 -- mongosh --port 27017 --eval 'rs.status()'
```

Esto muestra qué puerto es PRIMARY y cuáles son SECONDARY.

### Probar el Failover

Para simular una falla del PRIMARY:

```bash
# Detener el PRIMARY
incus exec db1 -- systemctl stop mongod-27017

# Esperar 10 segundos
sleep 10

# Ver el nuevo PRIMARY
incus exec db1 -- mongosh --port 27018 --eval 'rs.status()'
```

Uno de los SECONDARY se convierte automáticamente en PRIMARY.

---

## Conclusiones

### Lo que se logró

- Sistema distribuido funcionando con 5 contenedores Incus
- Base de datos fragmentada entre db1 y db2
- Réplicas de MongoDB para evitar pérdida de datos
- Autenticación con JWT y contraseñas encriptadas
- Aplicación accesible desde internet con Ngrok

### Dificultades encontradas

- Configurar las réplicas de MongoDB en diferentes puertos del mismo contenedor
- Hacer que los servicios arranquen automáticamente con systemd
- Configurar la red para que los contenedores se comuniquen entre sí
- Exportar e importar contenedores a otra máquina

### Qué aprendimos

- Incus es útil para crear contenedores Linux completos
- MongoDB Replica Set permite recuperarse automáticamente de fallos
- La fragmentación ayuda a distribuir la carga entre bases de datos
- systemd facilita la gestión de servicios en Linux
- Es importante documentar bien el código

### Posibles mejoras

- Agregar más réplicas para db3 (usuarios)
- Implementar un sistema de caché con Redis
- Agregar más fragmentos si hay muchos productos
- Mejorar la interfaz web con más funcionalidades

---

**Proyecto de Sistemas Distribuidos**  
**Noviembre 2025**
