from flask import Blueprint, render_template, session, jsonify, request, current_app
from backend.utils import login_required
from backend.database.models.space import Space
from backend.database.db import Database

spaces_bp = Blueprint('spaces_bp', __name__)


@spaces_bp.route('/space/<int:id>')
def space(id):
    db = Database(current_app.config['DATABASE'])
    space_model = Space()
    space_data = db.execute(
        """SELECT s.*, c.name AS category_name 
           FROM spaces s JOIN categories c ON s.category_id = c.id 
           WHERE s.id = ?""",
        (id,),
        fetch_one=True
    )

    if not space_data:
        return "Space not found", 404

    space_dict = {
        'id': space_data[0],
        'name': space_data[1],
        'building': space_data[2],
        'level': space_data[3],
        'location': space_data[4],
        'description': space_data[5],
        'location_description': space_data[6],
        'likes': space_data[7],
        'map_url': space_data[8],
        'category_name': space_data[9],
        'images': space_model.get_space_images(id),
        'features': space_model.get_space_features(id)
    }

    if 'user_id' in session:
        space_dict['is_favorite'] = space_model.is_favorite(session['user_id'], id)
    else:
        space_dict['is_favorite'] = False

    return render_template('spaces/space_card.html', space=space_dict)


@spaces_bp.route('/catalog')
def catalog():
    db = Database(current_app.config['DATABASE'])
    space_model = Space()
    categories = db.execute("SELECT * FROM categories")

    space_categories = []
    for cat in categories:
        spaces = space_model.get_by_category(cat[0])
        enriched_spaces = []
        for space in spaces:
            is_fav = False
            if 'user_id' in session:
                is_fav = space_model.is_favorite(session['user_id'], space['id'])
            enriched_spaces.append({
                **space,
                'is_favorite': is_fav,
                'images': space['images'],
            })

        space_categories.append({
            "id": cat[0],
            "name": cat[1],
            "spaces": enriched_spaces
        })

    return render_template('spaces/catalog.html', space_categories=space_categories)


@spaces_bp.route('/catalog/filter')
def filtered_catalog():
    space_model = Space()
    activity = request.args.get('activity', '')
    buildings = request.args.get('building', '')
    features = request.args.get('features', '')

    building_list = buildings.split(',') if buildings else []
    features_list = features.split(',') if features else []

    if not activity and not building_list and not features_list:
        return jsonify(space_model.get_all_spaces())

    category_id = None
    if activity == 'dancing':
        category_id = 1
    elif activity == 'event':
        category_id = 2

    spaces = []
    if building_list:
        for building in building_list:
            filtered = space_model.get_filtered_spaces(
                category_id=category_id,
                building=building,
                features=features_list if features_list else None
            )
            spaces.extend(filtered)

        seen = set()
        spaces = [x for x in spaces if not (x['id'] in seen or seen.add(x['id']))]
    else:
        spaces = space_model.get_filtered_spaces(
            category_id=category_id,
            building=None,
            features=features_list if features_list else None
        )

    return jsonify(spaces)