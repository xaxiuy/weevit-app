from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Marca, Producto, Activacion, Recompensa, UsuarioRecompensa
from datetime import datetime, timedelta
import random
import string

products_bp = Blueprint('products', __name__)

def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_brand_admin(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        if session.get('user_type') not in ['brand_admin', 'platform_admin']:
            return jsonify({'error': 'Acceso denegado'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def generate_activation_code():
    """Genera un código de activación único"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        code = f"WEEV-{code}"
        if not Producto.query.filter_by(codigo_activacion=code).first():
            return code

@products_bp.route('/products', methods=['GET'])
def get_products():
    try:
        # Parámetros de filtrado
        marca_id = request.args.get('marca_id', type=int)
        categoria = request.args.get('categoria')
        activo = request.args.get('activo', 'true').lower() == 'true'
        
        query = Producto.query
        
        if marca_id:
            query = query.filter_by(marca_id=marca_id)
        if categoria:
            query = query.filter_by(categoria=categoria)
        if activo is not None:
            query = query.filter_by(activo=activo)
        
        productos = query.all()
        
        return jsonify({
            'productos': [p.to_dict() for p in productos]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/products', methods=['POST'])
@require_brand_admin
def create_product():
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        # Validar datos requeridos
        required_fields = ['nombre', 'descripcion', 'categoria']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Obtener la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        # Generar código de activación si no se proporciona
        codigo_activacion = data.get('codigo_activacion')
        if not codigo_activacion:
            codigo_activacion = generate_activation_code()
        else:
            # Verificar que el código no exista
            if Producto.query.filter_by(codigo_activacion=codigo_activacion).first():
                return jsonify({'error': 'El código de activación ya existe'}), 400
        
        # Crear producto
        producto = Producto(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            codigo_activacion=codigo_activacion,
            categoria=data['categoria'],
            precio=data.get('precio'),
            imagen_url=data.get('imagen_url'),
            marca_id=marca.id
        )
        
        db.session.add(producto)
        db.session.commit()
        
        # Crear recompensa por defecto
        recompensa = Recompensa(
            nombre=f"Recompensa por activar {producto.nombre}",
            descripcion="¡Gracias por activar este producto!",
            tipo="puntos",
            valor="10 puntos",
            producto_id=producto.id,
            fecha_expiracion=datetime.utcnow() + timedelta(days=365)
        )
        
        db.session.add(recompensa)
        db.session.commit()
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'producto': producto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_brand_admin
def update_product(product_id):
    try:
        user_id = session['user_id']
        
        # Obtener la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        # Obtener el producto
        producto = Producto.query.filter_by(id=product_id, marca_id=marca.id).first()
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'categoria' in data:
            producto.categoria = data['categoria']
        if 'precio' in data:
            producto.precio = data['precio']
        if 'imagen_url' in data:
            producto.imagen_url = data['imagen_url']
        if 'activo' in data:
            producto.activo = data['activo']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'producto': producto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/validate-code', methods=['POST'])
def validate_code():
    try:
        data = request.get_json()
        codigo = data.get('codigo_activacion', '').strip().upper()
        
        if not codigo:
            return jsonify({'error': 'Código de activación requerido'}), 400
        
        producto = Producto.query.filter_by(codigo_activacion=codigo, activo=True).first()
        
        if not producto:
            return jsonify({
                'valido': False,
                'mensaje': 'Código de activación inválido o producto inactivo'
            }), 200
        
        return jsonify({
            'valido': True,
            'producto': producto.to_dict(),
            'mensaje': 'Código válido'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/activate', methods=['POST'])
@require_auth
def activate_product():
    try:
        data = request.get_json()
        codigo = data.get('codigo_activacion', '').strip().upper()
        user_id = session['user_id']
        
        if not codigo:
            return jsonify({'error': 'Código de activación requerido'}), 400
        
        # Validar código
        producto = Producto.query.filter_by(codigo_activacion=codigo, activo=True).first()
        if not producto:
            return jsonify({'error': 'Código de activación inválido o producto inactivo'}), 400
        
        # Verificar si ya fue activado por este usuario
        activacion_existente = Activacion.query.filter_by(
            usuario_id=user_id, 
            producto_id=producto.id
        ).first()
        
        if activacion_existente:
            return jsonify({'error': 'Ya has activado este producto anteriormente'}), 400
        
        # Crear activación
        puntos_ganados = 10  # Puntos base
        activacion = Activacion(
            usuario_id=user_id,
            producto_id=producto.id,
            puntos_ganados=puntos_ganados
        )
        
        db.session.add(activacion)
        
        # Actualizar puntos del usuario
        user = User.query.get(user_id)
        user.puntos_totales += puntos_ganados
        
        # Calcular nuevo nivel (cada 100 puntos = 1 nivel)
        nuevo_nivel = (user.puntos_totales // 100) + 1
        user.nivel_actual = nuevo_nivel
        
        # Otorgar recompensas del producto
        recompensas_producto = Recompensa.query.filter_by(
            producto_id=producto.id, 
            activa=True
        ).all()
        
        recompensas_otorgadas = []
        for recompensa in recompensas_producto:
            usuario_recompensa = UsuarioRecompensa(
                usuario_id=user_id,
                recompensa_id=recompensa.id
            )
            db.session.add(usuario_recompensa)
            recompensas_otorgadas.append(recompensa.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': '¡Producto activado exitosamente!',
            'activacion': activacion.to_dict(),
            'puntos_ganados': puntos_ganados,
            'puntos_totales': user.puntos_totales,
            'nivel_actual': user.nivel_actual,
            'recompensas_otorgadas': recompensas_otorgadas
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/my-activations', methods=['GET'])
@require_auth
def get_my_activations():
    try:
        user_id = session['user_id']
        
        activaciones = Activacion.query.filter_by(usuario_id=user_id)\
            .order_by(Activacion.fecha_activacion.desc()).all()
        
        return jsonify({
            'activaciones': [a.to_dict() for a in activaciones]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        # Obtener categorías únicas de productos activos
        categorias = db.session.query(Producto.categoria)\
            .filter_by(activo=True)\
            .distinct().all()
        
        categorias_list = [cat[0] for cat in categorias if cat[0]]
        
        return jsonify({
            'categorias': categorias_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

