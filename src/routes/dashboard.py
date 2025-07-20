from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Marca, Producto, Activacion, UsuarioRecompensa
from sqlalchemy import func, desc
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('/user-dashboard', methods=['GET'])
@require_auth
def get_user_dashboard():
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Métricas básicas
        total_activaciones = Activacion.query.filter_by(usuario_id=user_id).count()
        recompensas_disponibles = UsuarioRecompensa.query.filter_by(
            usuario_id=user_id, 
            estado='disponible'
        ).count()
        
        # Activaciones recientes (últimas 5)
        activaciones_recientes = Activacion.query.filter_by(usuario_id=user_id)\
            .order_by(desc(Activacion.fecha_activacion))\
            .limit(5).all()
        
        # Recompensas recientes disponibles (últimas 3)
        recompensas_recientes = UsuarioRecompensa.query.filter_by(
            usuario_id=user_id, 
            estado='disponible'
        ).order_by(desc(UsuarioRecompensa.fecha_otorgada))\
         .limit(3).all()
        
        # Marcas activadas (únicas)
        marcas_activadas = db.session.query(Marca.nombre, func.count(Activacion.id).label('count'))\
            .join(Producto, Marca.id == Producto.marca_id)\
            .join(Activacion, Producto.id == Activacion.producto_id)\
            .filter(Activacion.usuario_id == user_id)\
            .group_by(Marca.id, Marca.nombre)\
            .order_by(desc('count'))\
            .limit(5).all()
        
        # Activaciones por mes (últimos 6 meses)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        activaciones_por_mes = db.session.query(
            func.strftime('%Y-%m', Activacion.fecha_activacion).label('mes'),
            func.count(Activacion.id).label('count')
        ).filter(
            Activacion.usuario_id == user_id,
            Activacion.fecha_activacion >= six_months_ago
        ).group_by('mes').order_by('mes').all()
        
        return jsonify({
            'usuario': user.to_dict(),
            'metricas': {
                'total_activaciones': total_activaciones,
                'recompensas_disponibles': recompensas_disponibles,
                'puntos_totales': user.puntos_totales,
                'nivel_actual': user.nivel_actual,
                'puntos_siguiente_nivel': max(0, (user.nivel_actual * 100) - user.puntos_totales)
            },
            'activaciones_recientes': [a.to_dict() for a in activaciones_recientes],
            'recompensas_recientes': [r.to_dict() for r in recompensas_recientes],
            'marcas_favoritas': [{'nombre': m[0], 'activaciones': m[1]} for m in marcas_activadas],
            'activaciones_por_mes': [{'mes': m[0], 'activaciones': m[1]} for m in activaciones_por_mes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@dashboard_bp.route('/brand-dashboard', methods=['GET'])
@require_brand_admin
def get_brand_dashboard():
    try:
        user_id = session['user_id']
        
        # Obtener la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        # Métricas básicas
        total_productos = Producto.query.filter_by(marca_id=marca.id).count()
        productos_activos = Producto.query.filter_by(marca_id=marca.id, activo=True).count()
        
        # Total de activaciones de todos los productos de la marca
        total_activaciones = db.session.query(func.count(Activacion.id))\
            .join(Producto)\
            .filter(Producto.marca_id == marca.id)\
            .scalar()
        
        # Usuarios únicos que han activado productos de la marca
        usuarios_unicos = db.session.query(func.count(func.distinct(Activacion.usuario_id)))\
            .join(Producto)\
            .filter(Producto.marca_id == marca.id)\
            .scalar()
        
        # Productos más activados
        productos_top = db.session.query(
            Producto.nombre,
            Producto.id,
            func.count(Activacion.id).label('activaciones')
        ).outerjoin(Activacion)\
         .filter(Producto.marca_id == marca.id)\
         .group_by(Producto.id, Producto.nombre)\
         .order_by(desc('activaciones'))\
         .limit(5).all()
        
        # Activaciones por día (últimos 30 días)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        activaciones_por_dia = db.session.query(
            func.date(Activacion.fecha_activacion).label('fecha'),
            func.count(Activacion.id).label('count')
        ).join(Producto)\
         .filter(
             Producto.marca_id == marca.id,
             Activacion.fecha_activacion >= thirty_days_ago
         ).group_by('fecha')\
          .order_by('fecha').all()
        
        # Activaciones recientes
        activaciones_recientes = db.session.query(Activacion)\
            .join(Producto)\
            .join(User, Activacion.usuario_id == User.id)\
            .filter(Producto.marca_id == marca.id)\
            .order_by(desc(Activacion.fecha_activacion))\
            .limit(10).all()
        
        # Recompensas otorgadas
        total_recompensas = db.session.query(func.count(UsuarioRecompensa.id))\
            .join(Recompensa, UsuarioRecompensa.recompensa_id == Recompensa.id)\
            .join(Producto, Recompensa.producto_id == Producto.id)\
            .filter(Producto.marca_id == marca.id)\
            .scalar()
        
        recompensas_reclamadas = db.session.query(func.count(UsuarioRecompensa.id))\
            .join(Recompensa, UsuarioRecompensa.recompensa_id == Recompensa.id)\
            .join(Producto, Recompensa.producto_id == Producto.id)\
            .filter(
                Producto.marca_id == marca.id,
                UsuarioRecompensa.estado == 'reclamada'
            ).scalar()
        
        return jsonify({
            'marca': marca.to_dict(),
            'metricas': {
                'total_productos': total_productos,
                'productos_activos': productos_activos,
                'total_activaciones': total_activaciones or 0,
                'usuarios_unicos': usuarios_unicos or 0,
                'total_recompensas': total_recompensas or 0,
                'recompensas_reclamadas': recompensas_reclamadas or 0,
                'tasa_reclamacion': round((recompensas_reclamadas / max(total_recompensas, 1)) * 100, 2)
            },
            'productos_top': [
                {
                    'nombre': p[0], 
                    'id': p[1], 
                    'activaciones': p[2] or 0
                } for p in productos_top
            ],
            'activaciones_por_dia': [
                {
                    'fecha': a[0].strftime('%Y-%m-%d') if a[0] else '', 
                    'activaciones': a[1]
                } for a in activaciones_por_dia
            ],
            'activaciones_recientes': [
                {
                    'id': a.id,
                    'producto_nombre': a.producto.nombre,
                    'usuario_nombre': a.usuario.nombre,
                    'fecha_activacion': a.fecha_activacion.isoformat(),
                    'puntos_ganados': a.puntos_ganados
                } for a in activaciones_recientes
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@dashboard_bp.route('/analytics', methods=['GET'])
@require_brand_admin
def get_analytics():
    try:
        user_id = session['user_id']
        
        # Obtener la marca del usuario
        marca = Marca.query.filter_by(admin_id=user_id).first()
        if not marca:
            return jsonify({'error': 'No tienes una marca asociada'}), 400
        
        # Parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            # Por defecto, últimos 30 días
            fecha_fin = datetime.utcnow()
            fecha_inicio = fecha_fin - timedelta(days=30)
        else:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            fecha_fin = datetime.fromisoformat(fecha_fin)
        
        # Activaciones en el período
        activaciones_periodo = db.session.query(func.count(Activacion.id))\
            .join(Producto)\
            .filter(
                Producto.marca_id == marca.id,
                Activacion.fecha_activacion >= fecha_inicio,
                Activacion.fecha_activacion <= fecha_fin
            ).scalar()
        
        # Usuarios únicos en el período
        usuarios_periodo = db.session.query(func.count(func.distinct(Activacion.usuario_id)))\
            .join(Producto)\
            .filter(
                Producto.marca_id == marca.id,
                Activacion.fecha_activacion >= fecha_inicio,
                Activacion.fecha_activacion <= fecha_fin
            ).scalar()
        
        # Distribución por categorías
        categorias = db.session.query(
            Producto.categoria,
            func.count(Activacion.id).label('activaciones')
        ).outerjoin(Activacion)\
         .filter(
             Producto.marca_id == marca.id,
             Activacion.fecha_activacion >= fecha_inicio,
             Activacion.fecha_activacion <= fecha_fin
         ).group_by(Producto.categoria)\
          .order_by(desc('activaciones')).all()
        
        return jsonify({
            'periodo': {
                'fecha_inicio': fecha_inicio.isoformat(),
                'fecha_fin': fecha_fin.isoformat()
            },
            'metricas_periodo': {
                'activaciones': activaciones_periodo or 0,
                'usuarios_unicos': usuarios_periodo or 0,
                'promedio_diario': round((activaciones_periodo or 0) / max((fecha_fin - fecha_inicio).days, 1), 2)
            },
            'distribucion_categorias': [
                {'categoria': c[0], 'activaciones': c[1] or 0} 
                for c in categorias if c[0]
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

