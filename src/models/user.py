from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='consumer')  # consumer, brand_admin, platform_admin
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    puntos_totales = db.Column(db.Integer, default=0)
    nivel_actual = db.Column(db.Integer, default=1)
    
    # Relaciones
    activaciones = db.relationship('Activacion', backref='usuario', lazy=True)
    recompensas = db.relationship('UsuarioRecompensa', backref='usuario', lazy=True)
    marcas_administradas = db.relationship('Marca', backref='administrador', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'user_type': self.user_type,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'puntos_totales': self.puntos_totales,
            'nivel_actual': self.nivel_actual,
            'total_activaciones': len(self.activaciones)
        }

class Marca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activa = db.Column(db.Boolean, default=True)
    
    # Relaciones
    productos = db.relationship('Producto', backref='marca', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'logo_url': self.logo_url,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'total_productos': len(self.productos),
            'total_activaciones': sum(len(p.activaciones) for p in self.productos)
        }

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    codigo_activacion = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50))
    precio = db.Column(db.Float)
    imagen_url = db.Column(db.String(255))
    marca_id = db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    activaciones = db.relationship('Activacion', backref='producto', lazy=True)
    recompensas = db.relationship('Recompensa', backref='producto', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'codigo_activacion': self.codigo_activacion,
            'categoria': self.categoria,
            'precio': self.precio,
            'imagen_url': self.imagen_url,
            'marca': self.marca.nombre if self.marca else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'total_activaciones': len(self.activaciones),
            'activo': self.activo
        }

class Activacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    fecha_activacion = db.Column(db.DateTime, default=datetime.utcnow)
    puntos_ganados = db.Column(db.Integer, default=10)
    
    # Constraint para evitar activaciones duplicadas
    __table_args__ = (db.UniqueConstraint('usuario_id', 'producto_id', name='unique_user_product_activation'),)

    def to_dict(self):
        return {
            'id': self.id,
            'producto': self.producto.to_dict() if self.producto else None,
            'fecha_activacion': self.fecha_activacion.isoformat() if self.fecha_activacion else None,
            'puntos_ganados': self.puntos_ganados
        }

class Recompensa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False)  # descuento, puntos, contenido, producto_gratis
    valor = db.Column(db.String(100))  # "15%", "100 puntos", "Video exclusivo", etc.
    codigo_cupon = db.Column(db.String(50))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    fecha_expiracion = db.Column(db.DateTime)
    activa = db.Column(db.Boolean, default=True)
    
    # Relaciones
    usuarios_recompensas = db.relationship('UsuarioRecompensa', backref='recompensa', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'valor': self.valor,
            'codigo_cupon': self.codigo_cupon,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'activa': self.activa
        }

class UsuarioRecompensa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recompensa_id = db.Column(db.Integer, db.ForeignKey('recompensa.id'), nullable=False)
    fecha_otorgada = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_reclamada = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='disponible')  # disponible, reclamada, expirada

    def to_dict(self):
        return {
            'id': self.id,
            'recompensa': self.recompensa.to_dict() if self.recompensa else None,
            'fecha_otorgada': self.fecha_otorgada.isoformat() if self.fecha_otorgada else None,
            'fecha_reclamada': self.fecha_reclamada.isoformat() if self.fecha_reclamada else None,
            'estado': self.estado
        }

