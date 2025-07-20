from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Marca
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # Al menos 8 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['email', 'password', 'nombre', 'user_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        nombre = data['nombre'].strip()
        user_type = data['user_type']
        
        # Validaciones
        if not validate_email(email):
            return jsonify({'error': 'Email inválido'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 carácter especial'}), 400
        
        if user_type not in ['consumer', 'brand_admin']:
            return jsonify({'error': 'Tipo de usuario inválido'}), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Crear nuevo usuario
        user = User(
            email=email,
            nombre=nombre,
            user_type=user_type
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Si es brand_admin, crear marca por defecto
        if user_type == 'brand_admin':
            marca_nombre = data.get('marca_nombre', f'Marca de {nombre}')
            marca = Marca(
                nombre=marca_nombre,
                descripcion=f'Marca administrada por {nombre}',
                admin_id=user.id
            )
            db.session.add(marca)
            db.session.commit()
        
        # Iniciar sesión automáticamente
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user.activo:
            return jsonify({'error': 'Cuenta desactivada'}), 401
        
        # Iniciar sesión
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        
        return jsonify({
            'message': 'Login exitoso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout exitoso'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'user_type': session.get('user_type')}), 200
    else:
        return jsonify({'authenticated': False}), 200

