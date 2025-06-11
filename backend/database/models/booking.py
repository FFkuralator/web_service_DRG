from flask import current_app
from backend.database.db import Database


class Booking:
    def __init__(self, db_path=None):
        self.db = Database(db_path or current_app.config['DATABASE'])

    def create_booking(self, user_id, space_id, booking_date, start_time, end_time, comment=None):
        required_fields = [user_id, space_id, booking_date, start_time, end_time]
        if not all(required_fields):
            return False, "Не заполнены обязательные поля"

        try:
            start_minutes = sum(x * int(t) for x, t in zip([60, 1], start_time.split(":")))
            end_minutes = sum(x * int(t) for x, t in zip([60, 1], end_time.split(":")))
        except:
            return False, "Неверный формат времени"

        overlapping = self.db.execute(
            """SELECT 1 FROM bookings 
               WHERE space_id = ? AND booking_date = ? 
               AND ((start_time < ? AND end_time > ?) 
               OR (start_time < ? AND end_time > ?) 
               OR (start_time >= ? AND end_time <= ?))""",
            (space_id, booking_date, end_time, start_time, end_time, start_time, start_time, end_time),
            fetch_one=True
        )

        if overlapping:
            return False, "Выбранное время уже занято"

        self.db.execute(
            """INSERT INTO bookings 
               (user_id, space_id, booking_date, start_time, end_time, comment) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, space_id, booking_date, start_time, end_time, comment)
        )
        return True, "Бронирование успешно создано"

    def get_user_bookings(self, user_id):
        bookings = self.db.execute(
            """SELECT b.id, b.booking_date, b.start_time, b.end_time, b.comment,
                      s.name as space_name, s.building, s.level, s.location
               FROM bookings b
               JOIN spaces s ON b.space_id = s.id
               WHERE b.user_id = ?
               ORDER BY b.booking_date, b.start_time""",
            (user_id,)
        )

        result = []
        for booking in bookings:
            result.append({
                'id': booking[0],
                'date': booking[1],
                'start_time': booking[2],
                'end_time': booking[3],
                'comment': booking[4],
                'space_name': booking[5],
                'building': booking[6],
                'level': booking[7],
                'location': booking[8]
            })
        return result

    def get_space_availability(self, space_id, date):
        return self.db.execute(
            """SELECT start_time, end_time 
               FROM bookings 
               WHERE space_id = ? AND booking_date = ?
               ORDER BY start_time""",
            (space_id, date)
        )
    