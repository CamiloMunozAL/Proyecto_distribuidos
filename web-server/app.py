from flask import Flask, render_template, request, jsonify, session, redirect, send_from_directory
from pymongo import MongoClient
import requests, os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson import ObjectId
from flask_cors import CORS

load_dotenv()  # Cargar variables de entorno desde el archivo .env

app = Flask(__name__)
CORS(app)  # Habilitar CORS
app.secret_key = os.getenv("SECRET_KEY")
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:5000")
DB1_URL = os.getenv("DB1_URL")  # Conexion a la base de datos MongoDB 
DB2_URL = os.getenv("DB2_URL")  # Conexion a la base de datos MongoDB

# Conexion a la base datos MongoDB de productos
db1_client = MongoClient(DB1_URL)
db2_client = MongoClient(DB2_URL)

db1 = db1_client['products_db']
db2 = db2_client['products_db']

products_collection_db1 = db1['products']
products_collection_db2 = db2['products']

print(f"Conexiones a las bases de datos MongoDB establecidas")
print(f"DB1: {DB1_URL}")
print(f"DB2: {DB2_URL}")

# Middleware para verificar autenticacion
def verify_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'message': 'Token de autenticacion requerido'}), 401
    # Enviar el token al servidor de autenticacion para verificarlo por header authorization
    try:
        response = requests.post(
            f"{AUTH_SERVER_URL}/auth/verify",
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code != 200:
            return jsonify({'message': 'Token invalido o expirado'}), 401
        return None
    except requests.RequestException as e:
        return jsonify({'message': f'Error al verificar token: {str(e)}'}), 500

# Rutas de paginas web
@app.get("/")
def home():
    return redirect("/login")

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.get("/users-page")
def users_page():
    return render_template("users.html")

@app.get("/add-product")
def add_product_page():
    return render_template("add_product.html")

@app.get("/edit-product/<product_id>")
def edit_product_page(product_id):
    return render_template("edit_product.html")

@app.get("/register-user")
def register_user_page():
    return render_template("register_user.html")


# Funcion auxiliar para determinar en que BD guardar (fragmentacion por nombre)
def get_database_for_product(product_name):
    """Distribuye productos entre DB1 y DB2 basado en la primera letra del nombre
    DB1: Productos A-M
    DB2: Productos N-Z
    """
    if not product_name:
        raise ValueError("El nombre del producto es requerido")
    
    first_letter = product_name[0].upper()
    
    # DB1: A-M, DB2: N-Z
    if 'A' <= first_letter <= 'M':
        return products_collection_db1, 'DB1 (A-M)'
    elif 'N' <= first_letter <= 'Z':
        return products_collection_db2, 'DB2 (N-Z)'
    else:
        # Si no es una letra (números, símbolos), usar DB1 por defecto
        return products_collection_db1, 'DB1 (default)'

# ============ CRUD DE PRODUCTOS ============

# READ - Listar todos los productos
@app.route('/products', methods=['GET'])
def list_products():
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        # Listar productos desde ambas bases de datos
        products_db1 = list(products_collection_db1.find({}))
        products_db2 = list(products_collection_db2.find({}))
        
        # Convertir ObjectId a string para JSON
        for product in products_db1 + products_db2:
            product['_id'] = str(product['_id'])
            product['database'] = 'DB1' if product in products_db1 else 'DB2'
        
        all_products = products_db1 + products_db2
        return jsonify({
            'count': len(all_products),
            'products': all_products
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al listar productos: {str(e)}'}), 500

# READ - Obtener un producto por ID
@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        # Buscar en ambas bases de datos
        product = products_collection_db1.find_one({'_id': ObjectId(product_id)})
        database = 'DB1'
        
        if not product:
            product = products_collection_db2.find_one({'_id': ObjectId(product_id)})
            database = 'DB2'
        
        if not product:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        product['_id'] = str(product['_id'])
        product['database'] = database
        return jsonify(product), 200
    except Exception as e:
        return jsonify({'message': f'Error al obtener producto: {str(e)}'}), 500

# CREATE - Crear un nuevo producto
@app.route('/products', methods=['POST'])
def create_product():
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['name', 'price', 'stock']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Campo requerido: {field}'}), 400
        
        # Crear el nuevo producto (sin ID, MongoDB lo genera automáticamente)
        new_product = {
            'name': data['name'],
            'description': data.get('description', ''),
            'price': float(data['price']),
            'stock': int(data['stock']),
            'category': data.get('category', 'General'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Determinar en que base de datos guardar basado en el nombre
        target_db, db_label = get_database_for_product(data['name'])
        result = target_db.insert_one(new_product)
        
        new_product['_id'] = str(result.inserted_id)
        new_product['created_at'] = new_product['created_at'].isoformat()
        new_product['updated_at'] = new_product['updated_at'].isoformat()
        new_product['database'] = db_label
        
        return jsonify({
            'message': f'Producto creado exitosamente en {db_label}',
            'product': new_product
        }), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': f'Error al crear producto: {str(e)}'}), 500

# UPDATE - Actualizar un producto
@app.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        data = request.get_json()
        
        # Buscar el producto en ambas bases de datos
        product = products_collection_db1.find_one({'_id': ObjectId(product_id)})
        target_db = products_collection_db1
        
        if not product:
            product = products_collection_db2.find_one({'_id': ObjectId(product_id)})
            target_db = products_collection_db2
        
        if not product:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        # Actualizar campos
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'price' in data:
            update_data['price'] = float(data['price'])
        if 'stock' in data:
            update_data['stock'] = int(data['stock'])
        if 'category' in data:
            update_data['category'] = data['category']
        
        result = target_db.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            updated_product = target_db.find_one({'_id': ObjectId(product_id)})
            updated_product['_id'] = str(updated_product['_id'])
            updated_product['database'] = 'DB1' if target_db == products_collection_db1 else 'DB2'
            return jsonify({
                'message': 'Producto actualizado exitosamente',
                'product': updated_product
            }), 200
        else:
            return jsonify({'message': 'No se realizaron cambios'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al actualizar producto: {str(e)}'}), 500

# DELETE - Eliminar un producto
@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        # Intentar eliminar de DB1
        result = products_collection_db1.delete_one({'_id': ObjectId(product_id)})
        database = 'DB1'
        
        # Si no se encontro en DB1, intentar en DB2
        if result.deleted_count == 0:
            result = products_collection_db2.delete_one({'_id': ObjectId(product_id)})
            database = 'DB2'
        
        if result.deleted_count == 0:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        return jsonify({
            'message': 'Producto eliminado exitosamente',
            'deleted_from': database
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al eliminar producto: {str(e)}'}), 500

# Ruta documentacion API
@app.route('/docs', methods=['GET'])
def api_docs():
    docs = {
        'title': 'API de Gestión de Productos',
        'version': '1.0.0',
        'description': 'Servicio RESTful para gestión de productos con fragmentación distribuida por nombre',
        'base_url': request.host_url.rstrip('/'),
        'authentication': 'Se requiere token JWT en el header Authorization (Bearer token)',
        'database_distribution': {
            'DB1 (A-M)': 'Productos cuyo nombre comienza con letras A-M',
            'DB2 (N-Z)': 'Productos cuyo nombre comienza con letras N-Z'
        },
        'endpoints': [
            {
                'path': '/products',
                'method': 'GET',
                'title': 'Listar Productos',
                'description': 'Obtiene todos los productos de ambas bases de datos',
                'authentication': True,
                'headers': {
                    'Authorization': 'Bearer <token>'
                },
                'responses': [
                    {'code': '200', 'description': 'Lista de productos obtenida exitosamente'},
                    {'code': '401', 'description': 'Token no proporcionado o inválido'}
                ],
                'response_example': '''{
  "count": 2,
  "products": [
    {
      "_id": "673a1b2c3d4e5f6g7h8i9j0k",
      "name": "Manzana",
      "description": "Fruta fresca",
      "price": 2.5,
      "stock": 100,
      "category": "Frutas",
      "database": "DB1 (A-M)"
    }
  ]
}'''
            },
            {
                'path': '/products/<id>',
                'method': 'GET',
                'title': 'Obtener Producto',
                'description': 'Obtiene un producto específico por su ID',
                'authentication': True,
                'headers': {
                    'Authorization': 'Bearer <token>'
                },
                'responses': [
                    {'code': '200', 'description': 'Producto encontrado'},
                    {'code': '404', 'description': 'Producto no encontrado'},
                    {'code': '401', 'description': 'Token no proporcionado o inválido'}
                ],
                'response_example': '''{
  "_id": "673a1b2c3d4e5f6g7h8i9j0k",
  "name": "Pera",
  "description": "Fruta dulce",
  "price": 3.0,
  "stock": 80,
  "category": "Frutas",
  "database": "DB2 (N-Z)"
}'''
            },
            {
                'path': '/products',
                'method': 'POST',
                'title': 'Crear Producto',
                'description': 'Crea un nuevo producto. Se guarda automáticamente en DB1 (A-M) o DB2 (N-Z) según la primera letra del nombre',
                'authentication': True,
                'headers': {
                    'Authorization': 'Bearer <token>',
                    'Content-Type': 'application/json'
                },
                'request': {
                    'name': 'string (requerido) - Nombre del producto',
                    'description': 'string (opcional) - Descripción del producto',
                    'price': 'number (requerido) - Precio del producto',
                    'stock': 'number (requerido) - Cantidad en stock',
                    'category': 'string (opcional) - Categoría del producto'
                },
                'responses': [
                    {'code': '201', 'description': 'Producto creado exitosamente'},
                    {'code': '400', 'description': 'Datos inválidos o campos faltantes'},
                    {'code': '401', 'description': 'Token no proporcionado o inválido'}
                ],
                'example': '''{
  "name": "Naranja",
  "description": "Fruta cítrica",
  "price": 1.8,
  "stock": 150,
  "category": "Frutas"
}''',
                'response_example': '''{
  "message": "Producto creado exitosamente en DB2 (N-Z)",
  "product": {
    "_id": "673a1b2c3d4e5f6g7h8i9j0k",
    "name": "Naranja",
    "description": "Fruta cítrica",
    "price": 1.8,
    "stock": 150,
    "category": "Frutas",
    "database": "DB2 (N-Z)"
  }
}'''
            },
            {
                'path': '/products/<id>',
                'method': 'PUT',
                'title': 'Actualizar Producto',
                'description': 'Actualiza los datos de un producto existente',
                'authentication': True,
                'headers': {
                    'Authorization': 'Bearer <token>',
                    'Content-Type': 'application/json'
                },
                'request': {
                    'name': 'string (opcional)',
                    'description': 'string (opcional)',
                    'price': 'number (opcional)',
                    'stock': 'number (opcional)',
                    'category': 'string (opcional)'
                },
                'responses': [
                    {'code': '200', 'description': 'Producto actualizado exitosamente'},
                    {'code': '404', 'description': 'Producto no encontrado'},
                    {'code': '401', 'description': 'Token no proporcionado o inválido'}
                ],
                'example': '''{
  "price": 2.0,
  "stock": 200
}''',
                'response_example': '''{
  "message": "Producto actualizado exitosamente",
  "product": {
    "_id": "673a1b2c3d4e5f6g7h8i9j0k",
    "name": "Naranja",
    "price": 2.0,
    "stock": 200
  }
}'''
            },
            {
                'path': '/products/<id>',
                'method': 'DELETE',
                'title': 'Eliminar Producto',
                'description': 'Elimina un producto de la base de datos',
                'authentication': True,
                'headers': {
                    'Authorization': 'Bearer <token>'
                },
                'responses': [
                    {'code': '200', 'description': 'Producto eliminado exitosamente'},
                    {'code': '404', 'description': 'Producto no encontrado'},
                    {'code': '401', 'description': 'Token no proporcionado o inválido'}
                ],
                'response_example': '''{
  "message": "Producto eliminado exitosamente",
  "deleted_from": "DB1"
}'''
            }
        ]
    }
    # Usar la plantilla simple de docs del auth-server
    return render_template('api_docs.html', docs=docs)

# ============ RUTAS DE USUARIOS (CRUD) ============

# READ - Listar usuarios
@app.route('/users', methods=['GET'])
def list_users():
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        # Conexión a DB3 para obtener usuarios
        db3_client = MongoClient(os.getenv("DB3_URL"))
        db3 = db3_client['auth_db']
        users_collection = db3['users']
        
        users = list(users_collection.find({}, {'password': 0}))  # Excluir contraseñas
        
        # Convertir ObjectId a string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({
            'count': len(users),
            'users': users
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al listar usuarios: {str(e)}'}), 500

# CREATE - Registrar usuario (proxy al auth server)
@app.route('/users/register', methods=['POST'])
def register_user():
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if 'username' not in data or 'password' not in data:
            return jsonify({'message': 'Usuario y contraseña son requeridos'}), 400
        
        # Enviar solicitud al servidor de autenticación
        response = requests.post(
            f"{AUTH_SERVER_URL}/auth/register",
            json=data
        )
        
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'message': f'Error al comunicarse con el servidor de autenticación: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': f'Error al registrar usuario: {str(e)}'}), 500

# DELETE - Eliminar usuario
@app.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    # Verificar autenticacion
    auth_response = verify_token()
    if auth_response:
        return auth_response
    
    try:
        # Conexión a DB3 para eliminar usuario
        db3_client = MongoClient(os.getenv("DB3_URL"))
        db3 = db3_client['auth_db']
        users_collection = db3['users']
        
        result = users_collection.delete_one({'username': username})
        
        if result.deleted_count == 0:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al eliminar usuario: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)