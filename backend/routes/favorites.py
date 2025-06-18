from flask import Blueprint, render_template, session, jsonify, request
from backend.utils import login_required
from backend.database.models.space import Space
import logging

favorites_bp = Blueprint('favorites_bp', __name__)

@favorites_bp.route('/favorites')
@login_required
def favorites():
    space_model = Space()
    spaces = space_model.get_favorites(session['user_id'])
    return render_template('spaces/favorites.html', favorites={"spaces": spaces})

@favorites_bp.route('/api/favorites', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")

        space_id = data.get('space_id')
        user_id = session.get('user_id')

        if not space_id or not user_id:
            return jsonify({'error': 'Missing parameters'}), 400

        space_model = Space()

        if space_model.is_favorite(user_id, space_id):
            space_model.remove_from_favorites(user_id, space_id)
            return jsonify({'status': 'removed'})
        else:
            space_model.add_to_favorites(user_id, space_id)
            return jsonify({'status': 'added'})

    except Exception as e:
        logging.info(f"Error in toggle_favorite: {e}")
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/api/favorites/check/<int:space_id>')
@login_required
def check_favorite(space_id):
    user_id = session['user_id']
    space_model = Space()
    is_fav = space_model.is_favorite(user_id, space_id)
    return jsonify({'is_favorite': is_fav})