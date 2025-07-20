import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.products import products_bp
from src.routes.rewards import rewards_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'weev-secret-key-2024-mvp-development'

# Habilitar CORS para todas las rutas
CORS(app, supports_credentials=True)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(rewards_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Crear tablas y datos de prueba
with app.app_context():
    db.create_all()
    
    # Crear datos de prueba si no existen
    from src.models.user import User, Marca, Producto, Recompensa
    from datetime import datetime, timedelta
    
    # Usuario de prueba (consumidor)
    if not User.query.filter_by(email='usuario@test.com').first():
        user_test = User(
            email='usuario@test.com',
            nombre='Usuario Test',
            user_type='consumer'
        )
        user_test.set_password('Test123!')
        db.session.add(user_test)
    
    # Usuario administrador de marca
    if not User.query.filter_by(email='marca@test.com').first():
        brand_admin = User(
            email='marca@test.com',
            nombre='Admin Marca Test',
            user_type='brand_admin'
        )
        brand_admin.set_password('Test123!')
        db.session.add(brand_admin)
        db.session.commit()
        
        # Crear marca de prueba
        marca_test = Marca(
            nombre='Marca Test',
            descripcion='Marca de prueba para el MVP de Weev',
            admin_id=brand_admin.id
        )
        db.session.add(marca_test)
        db.session.commit()
        
        # Crear productos de prueba
        productos_test = [
            {
                'nombre': 'Producto Premium',
                'descripcion': 'Nuestro producto estrella con beneficios exclusivos',
                'codigo_activacion': 'WEEV-PREMIUM',
                'categoria': 'Premium',
                'precio': 29.99,
                'imagen_url': 'https://via.placeholder.com/300x200?text=Producto+Premium'
            },
            {
                'nombre': 'Producto Básico',
                'descripcion': 'Producto de entrada con excelente calidad',
                'codigo_activacion': 'WEEV-BASIC',
                'categoria': 'Básico',
                'precio': 15.99,
                'imagen_url': 'https://via.placeholder.com/300x200?text=Producto+Básico'
            },
            {
                'nombre': 'Producto Especial',
                'descripcion': 'Edición limitada con características únicas',
                'codigo_activacion': 'WEEV-SPECIAL',
                'categoria': 'Especial',
                'precio': 49.99,
                'imagen_url': 'https://via.placeholder.com/300x200?text=Producto+Especial'
            }
        ]
        
        for prod_data in productos_test:
            producto = Producto(
                nombre=prod_data['nombre'],
                descripcion=prod_data['descripcion'],
                codigo_activacion=prod_data['codigo_activacion'],
                categoria=prod_data['categoria'],
                precio=prod_data['precio'],
                imagen_url=prod_data['imagen_url'],
                marca_id=marca_test.id
            )
            db.session.add(producto)
            db.session.commit()
            
            # Crear recompensas para cada producto
            recompensas = [
                {
                    'nombre': f'Puntos por {prod_data["nombre"]}',
                    'descripcion': f'Gana puntos por activar {prod_data["nombre"]}',
                    'tipo': 'puntos',
                    'valor': '10 puntos'
                },
                {
                    'nombre': f'Descuento en {prod_data["nombre"]}',
                    'descripcion': f'15% de descuento en tu próxima compra',
                    'tipo': 'descuento',
                    'valor': '15%',
                    'codigo_cupon': f'DESC15-{producto.id}'
                }
            ]
            
            for rec_data in recompensas:
                recompensa = Recompensa(
                    nombre=rec_data['nombre'],
                    descripcion=rec_data['descripcion'],
                    tipo=rec_data['tipo'],
                    valor=rec_data['valor'],
                    codigo_cupon=rec_data.get('codigo_cupon'),
                    producto_id=producto.id,
                    fecha_expiracion=datetime.utcnow() + timedelta(days=365)
                )
                db.session.add(recompensa)
        
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'OK', 'message': 'Weev MVP API funcionando correctamente'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

