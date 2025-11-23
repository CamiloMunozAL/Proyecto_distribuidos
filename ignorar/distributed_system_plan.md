# Plan de Arquitectura - Sistema Distribuido Distribuido con Incus y MongoDB

## 🎯 Visión General Simplificada

**Objetivo**: Implementar una plataforma web con dashboard, gestión de productos (CRUD) y autenticación de usuarios, todo en contenedores Incus interconectados con MongoDB fragmentado y replicado.

---

## 📦 Arquitectura de 5 Contenedores + 1 Gestor

### **Contenedor 1: Web Server (Flask/Python)**
- **Puerto**: 5000
- **Función**: Dashboard principal con CRUD de productos
- **Responsabilidades**:
  - Interfaz web (HTML/CSS/JS)
  - Rutas CRUD: `/products` (GET, POST, PUT, DELETE)
  - Rutas de autenticación: `/login`, `/register`
  - Comunicación con Auth Server y Bases de Datos

### **Contenedor 2: Auth Server (Flask/Python)**
- **Puerto**: 5001
- **Función**: Gestionar login y registro
- **Responsabilidades**:
  - Validar credenciales
  - Generar JWT tokens
  - Comunicación con DB3 (usuarios)
  - Endpoints: `/auth/login`, `/auth/register`

### **Contenedor 3: MongoDB Primaria (DB1 - Fragmento A-M)**
- **Puerto**: 27017
- **Función**: Base de datos de productos - Fragmento Horizontal (A-M)
- **Estrategia de Fragmentación**:
  - **Rango Alfabético**: Productos cuyo nombre comienza de **A a M**
  - **Ejemplo**: Apple Watch, Laptop, Mochila, etc.
  - **Réplica integrada**: El mismo contenedor contiene replica set con datos replicados internamente
- **Datos**:
  - Colección `products` con documentos del rango A-M
  - Índices en el campo `name` para búsqueda rápida
  - Configuración de replica set

### **Contenedor 4: MongoDB Secundaria (DB2 - Fragmento N-Z)**
- **Puerto**: 27018
- **Función**: Base de datos de productos - Fragmento Horizontal (N-Z)
- **Estrategia de Fragmentación**:
  - **Rango Alfabético**: Productos cuyo nombre comienza de **N a Z**
  - **Ejemplo**: Nintendo Switch, Tablet, Zapatillas, etc.
  - **Réplica integrada**: Replica set interno en el mismo contenedor
- **Datos**:
  - Colección `products` con documentos del rango N-Z
  - Índices en el campo `name` para búsqueda rápida
  - Configuración de replica set

### **Contenedor 5: MongoDB Usuarios (DB3)**
- **Puerto**: 27019
- **Función**: Base de datos de autenticación
- **Datos**:
  - Colección `users` con credenciales hasheadas
  - Información de perfil

### **Contenedor 6: Incus UI Canonical**
- **Puerto**: 8443
- **Función**: Interfaz gráfica para gestionar contenedores Incus
- **Uso**: Monitoreo y administración visual del sistema

---

## 🗄️ Estrategia de Fragmentación (Horizontal - Rango Alfabético)

```
                    Web Server (Puerto 5000)
                            |
            __________________+__________________
            |                                    |
        Auth Server                        MongoDB Cluster
      (Puerto 5001)                              |
            |                    ________________+________________
            |                    |                               |
        DB3 Usuarios         DB1 Fragmento A-M            DB2 Fragmento N-Z
      (Puerto 27019)        (Puerto 27017)               (Puerto 27018)
                         Productos A-M                  Productos N-Z
                         (Apple, Laptop, etc.)          (Nintendo, Tablet, etc.)
                         Replica Set Interno            Replica Set Interno
```

**Lógica de distribución**:
- Si el producto comienza con A, B, C, ... M → va a **DB1**
- Si el producto comienza con N, O, P, ... Z → va a **DB2**
- Cada fragmento tiene su propio replica set para tolerancia a fallos

---

## 🔄 Replicación dentro del Mismo Contenedor

**Concepto clave**: Cada contenedor de BD (DB1 y DB2) ejecuta un **replica set de MongoDB** con múltiples instancias:
- **Instancia Primaria**: Lee/Escribe
- **Instancias Secundarias**: Solo lectura (para tolerancia a fallos)
- **Todo dentro del mismo contenedor** en diferentes puertos internos

**Ejemplo - DB1 (Puerto 27017)**:
```
Contenedor DB1
├── MongoDB Primaria (27017)
├── MongoDB Secundaria 1 (27018 interno)
└── MongoDB Secundaria 2 (27019 interno)
    └── Replica Set: "rs0"
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Orquestación | Incus | Última |
| Interfaz Gráfica | Incus UI Canonical | Última |
| Despliegue | Dockploy | Configuración SSH |
| Backend Web | Python + Flask | 3.11 |
| Backend Auth | Python + Flask | 3.11 |
| BD Productos | MongoDB | 6.0+ |
| BD Usuarios | MongoDB | 6.0+ |
| Frontend | HTML5 + Bootstrap 5 | - |
| Autenticación | JWT Tokens | PyJWT |
| Replicación BD | MongoDB Replica Sets | Integrada |

---

## 📋 Plan de Implementación Paso a Paso

### **Fase 1: Preparación (1-2 horas)**
1. Instalar Incus en máquina host
2. Configurar Incus UI Canonical en contenedor separado
3. Crear red Incus personalizada para los contenedores
4. Planificar direcciones IP de contenedores

### **Fase 2: Contenedores Base (2-3 horas)**
1. Crear 5 contenedores Incus con Ubuntu 22.04
2. Configurar conectividad entre contenedores
3. Instalar dependencias básicas (Python, MongoDB, etc.)

### **Fase 3: Bases de Datos MongoDB (2-3 horas)**
1. Instalar MongoDB en DB1
2. Configurar replica set interno (3 instancias en el mismo contenedor)
3. Instalar MongoDB en DB2 (misma configuración)
4. Instalar MongoDB en DB3 (sin replica set)
5. Pruebas de conectividad y replicación

### **Fase 4: Servidor de Autenticación (1.5-2 horas)**
1. Crear API Flask para auth
2. Implementar endpoints `/auth/login` y `/auth/register`
3. Hasheado de contraseñas (bcrypt)
4. Generación de JWT tokens
5. Conectar con DB3

### **Fase 5: Servidor Web (2-3 horas)**
1. Crear aplicación Flask con dashboard
2. Implementar CRUD completo de productos
3. Integrar autenticación con JWT
4. Lógica de fragmentación (DB1 vs DB2 según categoría)
5. Frontend con Bootstrap

### **Fase 6: Integración y Networking (1-2 horas)**
1. Configurar todas las conexiones de red
2. Validar comunicación entre contenedores
3. Pruebas end-to-end

### **Fase 7: Despliegue con Dockploy (1 hora)**
1. Configurar Dockploy para automatizar despliegue
2. Scripts de inicialización
3. Documentación de despliegue

### **Fase 8: Testing y Resiliencia (2-3 horas)**
1. Pruebas de CRUD completo
2. Pruebas de autenticación
3. Simular fallos (detener contenedores)
4. Verificar conmutación por error de replicas

---

## 💡 Simplificaciones Clave (Para Facilitar Explicación)

### ✅ LO QUE HACEMOS SIMPLE
- **Fragmentación**: Horizontal por rango alfabético A-M vs N-Z (fácil de visualizar)
- **Lógica de routing**: Función simple que verifica primera letra del producto
- **Replicas**: Dentro del mismo contenedor con replica sets (no duplicar contenedores)
- **Frontend**: Bootstrap simple y responsivo
- **Auth**: JWT básico sin OAuth
- **Red**: Una red Incus única para todos

### ⚠️ LO QUE EVITAMOS (Complejidad innecesaria)
- ❌ Fragmentación vertical + horizontal (solo horizontal)
- ❌ Múltiples contenedores para réplicas (todo en uno)
- ❌ Terraform inicial (use scripts bash primero)
- ❌ Microservicios adicionales (solo lo esencial)

---

## 📊 Estructura de Datos MongoDB

### **DB1 y DB2 - Colección `products`**
```json
{
  "_id": ObjectId,
  "product_id": 1000,
  "name": "Laptop Dell XPS",
  "description": "High-end laptop",
  "price": 999.99,
  "category": "Electrónica",
  "stock": 50,
  "image_url": "/images/laptop.jpg",
  "first_letter": "L",
  "created_at": ISODate("2024-01-15T10:00:00Z"),
  "updated_at": ISODate("2024-01-15T10:00:00Z")
}
```

**Nota**: El campo `first_letter` facilita búsquedas y distribución
- DB1 contiene: first_letter en [A-M]
- DB2 contiene: first_letter en [N-Z]

### **DB3 - Colección `users`**
```json
{
  "_id": ObjectId,
  "username": "johndoe",
  "email": "john@example.com",
  "password": "$2b$12$...",
  "last_login": ISODate("2024-01-15T10:00:00Z")
}
```

---

## 🌐 Rutas API Principales

### **Web Server (5000)**
- `GET /dashboard` → Mostrar dashboard
- `GET /products` → Listar productos (consulta DB1 y DB2)
- `POST /products` → Crear producto (redirige a DB1 o DB2)
- `PUT /products/{id}` → Actualizar producto
- `DELETE /products/{id}` → Eliminar producto
- `GET /login` → Formulario login
- `POST /login` → Procesar login (llama Auth Server)
- `GET /register` → Formulario registro
- `POST /register` → Procesar registro (llama Auth Server)

### **Auth Server (5001)**
- `POST /auth/login` → Validar credenciales, retornar JWT
- `POST /auth/register` → Crear usuario, retornar JWT
- `POST /auth/verify` → Validar token JWT
- `GET /auth/user/{id}` → Obtener datos usuario

---

## 📝 Documentación del Proyecto

### Estructura de carpetas recomendada:
```
proyecto-distribuido/
├── docker-compose.yml              (Para Dockploy)
├── incus-setup.sh                  (Script setup inicial)
├── web-server/
│   ├── app.py                      (Flask app)
│   ├── requirements.txt
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── products.html
│   │   └── login.html
│   └── static/
│       └── style.css
├── auth-server/
│   ├── app.py
│   ├── requirements.txt
│   └── models.py
├── db-setup/
│   ├── init-db1.js               (Replica set DB1)
│   ├── init-db2.js               (Replica set DB2)
│   └── init-db3.js               (BD usuarios)
├── tests/
│   ├── test_crud.py
│   ├── test_auth.py
│   └── test_failover.py
└── docs/
    ├── ARQUITECTURA.md
    ├── SETUP.md
    ├── CONEXIONES.md
    └── PRESENTACION.pptx
```

---

## 🚀 Comandos Iniciales (Resumen)

```bash
# 1. Crear contenedores
incus launch ubuntu:22.04 web-server
incus launch ubuntu:22.04 auth-server
incus launch ubuntu:22.04 db1
incus launch ubuntu:22.04 db2
incus launch ubuntu:22.04 db3
incus launch ubuntu:22.04 incus-ui

# 2. Configurar red
incus network create app-network
incus network attach app-network web-server
# ... (repetir para otros)

# 3. Instalar software
incus exec web-server -- bash -c "apt update && apt install -y python3 python3-pip"
incus exec db1 -- bash -c "apt update && apt install -y mongodb-org"
# ... (repetir según necesario)

# 4. Copiar archivos
incus file push web-server/app.py web-server/root/app/
incus file push db-setup/init-db1.js db1/root/

# 5. Ejecutar servicios
incus exec web-server -- python3 /root/app/app.py
```

---

## ✅ Checklist de Implementación

- [ ] Incus instalado y configurado
- [ ] Red Incus personalizada creada
- [ ] 6 contenedores creados
- [ ] MongoDB instalado en DB1, DB2, DB3
- [ ] Replica sets de MongoDB configurados en DB1 y DB2
- [ ] Auth Server funcionando
- [ ] Web Server con dashboard básico
- [ ] CRUD de productos implementado
- [ ] Fragmentación funcional (DB1 ↔ DB2)
- [ ] Autenticación JWT integrada
- [ ] Pruebas de conectividad exitosas
- [ ] Pruebas de failover completadas
- [ ] Incus UI Canonical accesible
- [ ] Dockploy configurado
- [ ] Documentación completa

---

## 💬 Notas Finales

**Ventajas de esta arquitectura**:
✅ Fácil de explicar (contenedores = bloques)
✅ Replica sets en un contenedor (ahorra recursos)
✅ Fragmentación horizontal clara
✅ Testing de resiliencia realista
✅ Escalable a microservicios futuros

**Tiempos estimados**:
- Desarrollo individual: 15-18 horas
- En grupo de 3-4 personas: 8-10 horas distribuidas
- Presentación y defensa: 20-30 minutos