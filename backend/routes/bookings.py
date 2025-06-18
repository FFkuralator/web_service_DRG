from flask import Blueprint, jsonify, request, session
from backend.utils import login_required
from backend.database.models.booking import Booking

bookings_bp = Blueprint('bookings_bp', __name__)


@bookings_bp.route('/book', methods=['POST'])
@login_required
def book_space():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют данные'}), 400

        required_fields = ['space_id', 'booking_date', 'start_time', 'end_time']
        if any(field not in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            return jsonify({'error': f'Отсутствуют обязательные поля: {", ".join(missing)}'}), 400

        try:
            space_id = int(data['space_id'])
        except:
            return jsonify({'error': 'Неверный ID пространства'}), 400

        booking_model = Booking()
        success, message = booking_model.create_booking(
            session['user_id'],
            space_id,
            data['booking_date'],
            data['start_time'],
            data['end_time'],
            data.get('comment')
        )

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({'message': message})

    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500


@bookings_bp.route('/cancel_booking', methods=['POST'])
@login_required
def cancel_booking():
    data = request.get_json()

    required_fields = ['space_id', 'booking_date', 'start_time']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Не все обязательные поля переданы'}), 400

    try:
        space_id = int(data['space_id'])
    except:
        return jsonify({'error': 'Неверный формат ID пространства'}), 400

    booking_model = Booking()
    success, message = booking_model.cancel_booking_by_details(
        session['user_id'],
        space_id,
        data['booking_date'],
        data['start_time']
    )

    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400


@bookings_bp.route('/api/availability/<int:space_id>')
def get_availability(space_id):
    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    booking_model = Booking()
    bookings = booking_model.get_space_availability(space_id, date)

    booked_slots = [{'start': booking[0], 'end': booking[1]} for booking in bookings]
    return jsonify({'booked_slots': booked_slots})


@bookings_bp.route('/my-bookings')
@login_required
def my_bookings():
    booking_model = Booking()
    bookings = booking_model.get_user_bookings(session['user_id'])
    return render_template('bookings/my_bookings.html', bookings=bookings)