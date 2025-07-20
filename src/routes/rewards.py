from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Recompensa, UsuarioRecompensa, Marca, Producto
from datetime import datetime, timedelta

rewards_bp = Blueprint('rewards', __name__)

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

@rewards_bp.route('/my-rewards', methods=['GET'])
@require_auth
def get_my_rewards():
    try:
        user_id = session['user_id']
        estado = request.args.get('estado', 'disponible')  # disponible, reclamada, expirada
        
        query = UsuarioRecompensa.query.filter_by(usuario_id=user_id)
        
        if estado:
            query = query.filter_by(estado=estado)
        
        usuario_recompensas = query.order_by(UsuarioRecompensa.fecha_otorgada.desc()).all()
        
        # Verificar recompensas expiradas
        now = datetime.utcnow()
        for ur in usuario_recompensas:
            if (ur.estado == 'disponible' and 
                ur.recompensa.fecha_expiracion and 
                ur.recompensa.fecha_expiracion < now):
                ur.estado = 'expirada'
        
        db.session.commit()
        
        return jsonify({
            'recompensas': [ur.to_dict() for ur in usuario_recompensas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@rewards_bp.route('/claim/<int:usuario_recompensa_id>', methods=['POST'])
@require_auth
def claim_reward(usuario_recompensa_id):
    try:
        user_id = session['user_id']
        
        usuario_recompensa = UsuarioRecompensa.query.filter_by(
            id=usuario_recompensa_id,
            usuario_id=user_id
        ).first()
        
        if not usuario_recompensa:
            return jsonify({'error': 'Recompensa no encontrada'}), 404
        
        if usuario_recompensa.estado != 'disponible':
            return jsonify({'error': 'Esta recompensa ya fue reclamada o ha expirado'}), 400
        
        # Verificar si no ha expirado
        if (usuario_recompensa.recompensa.fecha_expiracion and 
            usuario_recompensa.recompensa.fecha_expiracion < datetime.utcnow()):
            usuario_recompensa.estado = 'expirada'
            db.session.commit()
            return jsonify({'error': 'Esta recompensa ha expirado'}), 400
        
        # Reclamar recompensa
        usuario_recompensa.estado = 'reclamada'
        usuario_recompensa.fecha_reclamada = datetime.utcnow()
        
        # Si es recompensa de puntos, agregar puntos al usuario
        if usuario_recompensa.recompensa.tipo == 'puntos':
            try:
                puntos_str = usuario_recompensa.recompensa.valor
                puntos = int(puntos_str.split()[0])  # Extraer número de "10 puntos"
                
                user = User.query.get(user_id)
                user.puntos_totales += puntos
                
                # Recalcular nivel
                nuevo_nivel = (user.puntos_totales // 100) + 1
                user.nivel_actual = nuevo_nivel
                
            except (ValueError, IndexError):
                pass  # Si no se puede parsear, continuar sin agregar puntos
        
        db.session.commit()
        
        return jsonify({
            'message': 'Recompensa reclamada exitosamente',
            'recompensa': usuario_recompensa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@rewards_bp.route('/rewards', methods=['POST'])
@require_brand_admin
def create_reward():
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        # Validar datos requeridos
        required_fields = ['nombre', 'descripcion', 'tipo', 'valor', 'producto_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Verificar que el producto pertenece a la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        producto = Producto.query.filter_by(
            id=data['producto_id'],
            marca_id=marca.id
        ).first()
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado o no pertenece a tu marca'}), 404
        
        # Crear recompensa
        fecha_expiracion = None
        if data.get('dias_expiracion'):
            fecha_expiracion = datetime.utcnow() + timedelta(days=data['dias_expiracion'])
        
        recompensa = Recompensa(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            tipo=data['tipo'],
            valor=data['valor'],
            codigo_cupon=data.get('codigo_cupon'),
            producto_id=data['producto_id'],
            fecha_expiracion=fecha_expiracion
        )
        
        db.session.add(recompensa)
        db.session.commit()
        
        return jsonify({
            'message': 'Recompensa creada exitosamente',
            'recompensa': recompensa.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@rewards_bp.route('/rewards', methods=['GET'])
@require_brand_admin
def get_brand_rewards():
    try:
        user_id = session['user_id']
        
        # Obtener la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        # Obtener recompensas de productos de la marca
        recompensas = db.session.query(Recompensa)\
            .join(Producto)\
            .filter(Producto.marca_id == marca.id)\
            .order_by(Recompensa.id.desc())\
            .all()
        
        return jsonify({
            'recompensas': [r.to_dict() for r in recompensas]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@rewards_bp.route('/rewards/<int:reward_id>', methods=['PUT'])
@require_brand_admin
def update_reward(reward_id):
    try:
        user_id = session['user_id']
        
        # Obtener la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        # Verificar que la recompensa pertenece a un producto de la marca
        recompensa = db.session.query(Recompensa)\
            .join(Producto)\
            .filter(Recompensa.id == reward_id, Producto.marca_id == marca.id)\
            .first()
        
        if not recompensa:
            return jsonify({'error': 'Recompensa no encontrada'}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre' in data:
            recompensa.nombre = data['nombre']
        if 'descripcion' in data:
            recompensa.descripcion = data['descripcion']
        if 'tipo' in data:
            recompensa.tipo = data['tipo']
        if 'valor' in data:
            recompensa.valor = data['valor']
        if 'codigo_cupon' in data:
            recompensa.codigo_cupon = data['codigo_cupon']
        if 'activa' in data:
            recompensa.activa = data['activa']
        if 'dias_expiracion' in data:
            if data['dias_expiracion']:
                recompensa.fecha_expiracion = datetime.utcnow() + timedelta(days=data['dias_expiracion'])
            else:
                recompensa.fecha_expiracion = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Recompensa actualizada exitosamente',
            'recompensa': recompensa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@rewards_bp.route('/stats', methods=['GET'])
@require_auth
def get_reward_stats():
    try:
        user_id = session['user_id']
        
        # Estadísticas de recompensas del usuario
        total_recompensas = UsuarioRecompensa.query.filter_by(usuario_id=user_id).count()
        recompensas_disponibles = UsuarioRecompensa.query.filter_by(
            usuario_id=user_id, 
            estado='disponible'
        ).count()
        recompensas_reclamadas = UsuarioRecompensa.query.filter_by(
            usuario_id=user_id, 
            estado='reclamada'
        ).count()
        
        # Obtener información del usuario
        user = User.query.get(user_id)
        
        return jsonify({
            'total_recompensas': total_recompensas,
            'recompensas_disponibles': recompensas_disponibles,
            'recompensas_reclamadas': recompensas_reclamadas,
            'puntos_totales': user.puntos_totales,
            'nivel_actual': user.nivel_actual,
            'puntos_siguiente_nivel': ((user.nivel_actual * 100) - user.puntos_totales)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

