from flask import Blueprint, request, jsonify, current_app

from backend.database.db import Database
from backend.utils import login_required
from werkzeug.utils import secure_filename
import os

images_bp = Blueprint('images_bp', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@images_bp.route('/api/space/<int:space_id>/images', methods=['POST'])
@login_required
def add_space_image(space_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        db = Database(current_app.config['DATABASE'])
        db.execute(
            "INSERT INTO space_images (space_id, image_url, alt_text) VALUES (?, ?, ?)",
            (space_id, filename, request.form.get('alt_text', ''))
        )

        return jsonify({'message': 'Image uploaded successfully'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@images_bp.route('/api/image/<int:image_id>', methods=['DELETE'])
@login_required
def delete_space_image(image_id):
    db = Database(current_app.config['DATABASE'])
    image = db.execute(
        "SELECT image_url FROM space_images WHERE id = ?",
        (image_id,),
        fetch_one=True
    )

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image[0]))
    except OSError:
        pass

    db.execute("DELETE FROM space_images WHERE id = ?", (image_id,))
    return jsonify({'message': 'Image deleted successfully'}), 200