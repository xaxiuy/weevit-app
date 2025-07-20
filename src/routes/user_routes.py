
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from src.models.user import User
from src.database.db import db

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')

UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Asegurar carpeta
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 🧑‍💻 Obtener perfil
@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


# ✏️ Editar perfil
@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.json

    user.full_name = data.get('full_name', user.full_name)
    user.bio = data.get('bio', user.bio)
    user.profile_picture_url = data.get('profile_picture_url', user.profile_picture_url)
    user.location = data.get('location', user.location)

    birth_date = data.get('birth_date')
    if birth_date:
        try:
            user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Fecha inválida. Usá formato YYYY-MM-DD"}), 400

    db.session.commit()
    return jsonify(user.to_dict()), 200


# 📷 Subida de foto de perfil local
@user_bp.route('/<int:user_id>/upload', methods=['POST'])
def upload_profile_picture(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if 'file' not in request.files:
        return jsonify({"error": "No se encontró ningún archivo"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Archivo inválido"}), 400

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    user.profile_picture_url = f"/static/uploads/{filename}"
    db.session.commit()

    return jsonify({"message": "Imagen subida correctamente", "url": user.profile_picture_url}), 200
