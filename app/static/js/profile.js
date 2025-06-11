document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cancel_booking_btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const spaceId = btn.dataset.spaceId;
            const date = btn.dataset.date;
            const startTime = btn.dataset.startTime;

            const card = btn.closest('.history_item');

            fetch('/cancel_booking', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    space_id: spaceId,
                    booking_date: date,
                    start_time: startTime
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    console.log('Успех:', data.message);
                    card.remove();
                } else {
                    alert('Ошибка: ' + data.error);
                    console.error(data.error);
                }
            })
            .catch(error => {
                alert('Ошибка сети');
                console.error('Ошибка:', error);
            });
        });
    });
});