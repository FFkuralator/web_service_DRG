from flask import Blueprint, render_template, session, current_app

from backend.database.db import Database
from backend.utils import login_required
from backend.database.models.user import User
from backend.database.models.booking import Booking

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    user = User()
    booking_model = Booking()
    db = Database(current_app.config['DATABASE'])

    user_data = db.execute(
        "SELECT email, full_name, number_phone FROM users WHERE id = ?",
        (session['user_id'],),
        fetch_one=True
    )

    bookings = booking_model.get_user_bookings(session['user_id'])
    return render_template('auth/profile.html',
                           user={
                               'email': user_data[0],
                               'full_name': user_data[1],
                               'number': user_data[2]
                           },
                           bookings=bookings)
