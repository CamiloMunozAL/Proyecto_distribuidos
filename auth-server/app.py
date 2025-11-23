#Aplicacion para el servidor de autenticacion
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import jwt, bcrypt, os
from datetime import datetime, timedelta, timezone
from flask_cors import CORS

load_dotenv() # Cargar variables de entorno desde el archivo .env

# Configuracion de la aplicacion Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Conexion a la base datos MongoDB de usuarios 
DB3_URL = os.getenv("DB3_URL") # Conexion a la base de datos MongoDB
client = MongoClient(DB3_URL) # Conectar al cliente de MongoDB
db = client['auth_db'] # Seleccionar la base de datos
users_collection = db['users'] # Seleccionar la coleccion de usuarios

print(f"Conexion a la base de datos MongoDB establecida: {DB3_URL}")

# Ruta de registro de usuario
@app.route('/auth/register', methods=['POST'])
def register():
    data=request.get_json()
    # Verificar si el usuario ya existe
    if users_collection.find_one({'username': data['username']}):
        return jsonify({'message': 'Usuario ya existe'}), 400
    # Verificar si correo ya existe
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'Correo ya registrado'}), 400
    # Hashear la contrasena
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    # Crear el nuevo usuario
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password,
        'created_at': datetime.now(timezone.utc)
    }
    # Insertar el nuevo usuario en la base de datos
    users_collection.insert_one(new_user)
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

# Ruta de inicio de sesion
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users_collection.find_one({'username': data['username']})
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    # Verificar la contrasena
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'message': 'Contrasena incorrecta'}), 401
    # Crear el token JWT
    token = jwt.encode({
        'username': data['username'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'username': data['username']}), 200

# Ruta de verificacion del token
@app.route('/auth/verify', methods=['POST'])
def verify_token():
    # Obtener el token del encabezado Authorization
    token = request.headers.get('Authorization','').replace('Bearer ', '')
    if not token:
        return jsonify({'message': 'Token no proporcionado'}), 401
    try:
        # Decodificar el token JWT
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'message': 'Token valido', 'username': decoded['username']}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token invalido'}), 401

# Ruta de documentacion de la API
@app.route('/', methods=['GET'])
def api_docs():
    docs = {
        "title": "API de Autenticación",
        "version": "1.0.0",
        "description": "Servicio RESTful de autenticación con JWT para gestión de usuarios",
        "base_url": request.host_url.rstrip('/'),
        "endpoints": [
            {
                "path": "/auth/register",
                "method": "POST",
                "title": "Registrar Usuario",
                "description": "Crea una nueva cuenta de usuario en el sistema",
                "request": {
                    "username": "Nombre de usuario único",
                    "email": "Correo electrónico único",
                    "password": "Contraseña (será hasheada)"
                },
                "responses": [
                    {"code": "201", "description": "Usuario registrado exitosamente"},
                    {"code": "400", "description": "Usuario ya existe o correo ya registrado"}
                ],
                "example": '''{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "mipassword123"
}'''
            },
            {
                "path": "/auth/login",
                "method": "POST",
                "title": "Iniciar Sesión",
                "description": "Autentica un usuario y devuelve un token JWT válido por 1 hora",
                "request": {
                    "username": "Nombre de usuario",
                    "password": "Contraseña"
                },
                "responses": [
                    {"code": "200", "description": "Login exitoso, devuelve token y username"},
                    {"code": "401", "description": "Contraseña incorrecta"},
                    {"code": "404", "description": "Usuario no encontrado"}
                ],
                "example": '''{
  "username": "johndoe",
  "password": "mipassword123"
}''',
                "response_example": '''{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "johndoe"
}'''
            },
            {
                "path": "/auth/verify",
                "method": "POST",
                "title": "Verificar Token",
                "description": "Valida un token JWT y verifica su vigencia",
                "headers": {
                    "Authorization": "Bearer <token>"
                },
                "responses": [
                    {"code": "200", "description": "Token válido"},
                    {"code": "401", "description": "Token no proporcionado, expirado o inválido"}
                ],
                "example": '''Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...''',
                "response_example": '''{
  "message": "Token valido",
  "username": "johndoe"
}'''
            }
        ]
    }
    return render_template('docs.html', docs=docs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)