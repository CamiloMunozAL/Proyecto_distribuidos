# Sistema de Inventario Distribuido

Sistema de gestión de inventario con fragmentación horizontal automática de datos en MongoDB.

## Arquitectura del Sistema

### Bases de Datos

1. **DB1 (Puerto 27017)** - Productos A-M

   - Almacena productos cuyo nombre comienza con letras A hasta M
   - Ejemplo: Arroz, Café, Leche, Manzana

2. **DB2 (Puerto 27018)** - Productos N-Z

   - Almacena productos cuyo nombre comienza con letras N hasta Z
   - Ejemplo: Naranja, Pan, Queso, Tomate

3. **DB3 (Puerto 27019)** - Usuarios
   - Base de datos de autenticación
   - Almacena usuarios y credenciales

### Servidores

- **Auth Server (Puerto 5000)**: Servidor de autenticación con JWT
- **Web Server (Puerto 5001)**: Servidor principal de la aplicación

## Instalación

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (archivo `.env`):

```
SECRET_KEY=tu_clave_secreta
DB1_URL=mongodb://localhost:27017
DB2_URL=mongodb://localhost:27018
DB3_URL=mongodb://localhost:27019
AUTH_SERVER_URL=http://localhost:5000
```

3. Iniciar MongoDB (3 instancias):

```bash
# DB1
mongod --port 27017 --dbpath ./local_mongo/db1

# DB2
mongod --port 27018 --dbpath ./local_mongo/db2

# DB3
mongod --port 27019 --dbpath ./local_mongo/db3
```

4. Iniciar servidores:

```bash
# Auth Server
cd auth-server
python app.py

# Web Server
cd web-server
python app.py
```

## Uso de la Aplicación

### Acceso

1. Navegar a `http://localhost:5001/app`
2. Registrar un nuevo usuario
3. Iniciar sesión

### Funcionalidades

#### Dashboard

- Vista general del inventario
- Estadísticas de productos por base de datos
- Productos recientes

#### Gestión de Productos

- **Crear**: Agregar nuevos productos (se asigna automáticamente a DB1 o DB2)
- **Leer**: Ver todos los productos con filtros
- **Actualizar**: Editar información de productos
- **Eliminar**: Borrar productos del sistema

#### Gestión de Usuarios

- **Crear**: Registrar nuevos usuarios
- **Leer**: Ver lista de usuarios registrados
- **Eliminar**: Borrar usuarios del sistema

## API REST

### Autenticación

#### Registro

```
POST /auth/register
Body: {
  "username": "usuario",
  "email": "email@example.com",
  "password": "contraseña"
}
```

#### Login

```
POST /auth/login
Body: {
  "username": "usuario",
  "password": "contraseña"
}
Response: {
  "token": "jwt_token",
  "username": "usuario"
}
```

#### Verificar Token

```
POST /auth/verify
Headers: {
  "Authorization": "Bearer <token>"
}
```

### Productos

#### Listar Productos

```
GET /products
Headers: {
  "Authorization": "Bearer <token>"
}
```

#### Obtener Producto

```
GET /products/<id>
Headers: {
  "Authorization": "Bearer <token>"
}
```

#### Crear Producto

```
POST /products
Headers: {
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json"
}
Body: {
  "name": "Producto",
  "description": "Descripción",
  "category": "Categoría",
  "price": 10.50,
  "stock": 100
}
```

#### Actualizar Producto

```
PUT /products/<id>
Headers: {
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json"
}
Body: {
  "price": 12.00,
  "stock": 150
}
```

#### Eliminar Producto

```
DELETE /products/<id>
Headers: {
  "Authorization": "Bearer <token>"
}
```

### Usuarios

#### Listar Usuarios

```
GET /users
Headers: {
  "Authorization": "Bearer <token>"
}
```

#### Eliminar Usuario

```
DELETE /users/<username>
Headers: {
  "Authorization": "Bearer <token>"
}
```

## Fragmentación de Datos

La fragmentación es **automática** y se basa en la primera letra del nombre del producto:

- **A-M** → DB1 (Base de Datos 1)
- **N-Z** → DB2 (Base de Datos 2)

Ejemplo:

- "Arroz" → DB1
- "Manzana" → DB1
- "Naranja" → DB2
- "Zanahoria" → DB2

## Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos**: MongoDB
- **Autenticación**: JWT (JSON Web Tokens)
- **Frontend**: Bootstrap 5, Jinja2
- **Seguridad**: bcrypt para contraseñas

## Estructura del Proyecto

```
Proyecto_distribuidos/
├── auth-server/          # Servidor de autenticación
│   ├── app.py
│   └── templates/
│       └── docs.html
├── web-server/           # Servidor web principal
│   ├── app.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── products.html
│       ├── users.html
│       └── api_docs.html
├── local_mongo/          # Datos de MongoDB
│   ├── db1/
│   ├── db2/
│   └── db3/
├── requirements.txt
└── README.md
```

## Notas Importantes

1. **Tokens JWT**: Válidos por 1 hora después del login
2. **Contraseñas**: Hasheadas con bcrypt antes de almacenar
3. **CORS**: Habilitado para desarrollo
4. **Fragmentación**: No se puede cambiar la base de datos de un producto una vez creado

## Documentación API

Acceder a:

- Auth Server: `http://localhost:5000/`
- Web Server: `http://localhost:5001/docs`
