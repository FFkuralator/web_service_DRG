function toggleNoScroll() {
    document.body.classList.toggle('no-scroll');
}

document.addEventListener('DOMContentLoaded', function () {
    const slides = document.querySelectorAll('.slide');
    let currentIndex = 0;
    const prevBtn = document.getElementById('prev_btn');
    const nextBtn = document.getElementById('next_btn');

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
        });
        slides[index].classList.add('active');
    }

    function toggleFullscreen() {
        this.classList.toggle('fulscreen');
        toggleNoScroll()
    }

    slides.forEach((slide, i) => {
        slide.addEventListener('click', toggleFullscreen);
    });

    prevBtn.addEventListener('click', function () {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        showSlide(currentIndex);
    });

    nextBtn.addEventListener('click', function () {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    });

    showSlide(currentIndex);

    const bookingForm = document.getElementById('bookingForm');
    let selectedDate = null;
    let slots = [];
    let startSlot = null;
    let endSlot = null;

    function formatDate(date) {
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
    }

    function formatDay(date) {
        return date.toLocaleDateString('ru-RU', { weekday: 'short' }).toUpperCase();
    }

    function generateDateList(count = 18) {
        return Array.from({ length: count }, (_, i) => {
            const date = new Date();
            date.setDate(date.getDate() + i);
            return date;
        });
    }

    function parseTime(timeStr) {
        const [h, m] = timeStr.split(":").map(Number);
        return h * 60 + m;
    }

    function add15Minutes(time) {
        const [h, m] = time.split(":").map(Number);
        let newM = m + 15;
        let newH = h;
        if (newM >= 60) {
            newM -= 60;
            newH += 1;
        }
        return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')}`;
    }

    function updateDays() {
        const container = document.getElementById('booking_days_container');
            container.innerHTML = '';

            allDates.slice(currentDayIndex, currentDayIndex + 6).forEach((date, i) => {
                const daySlot = document.createElement('div');
                daySlot.className = `booking_day ${i + currentDayIndex >= 14 ? 'inactive' : ''}`;
                daySlot.textContent = `${formatDate(date)}, ${formatDay(date)}`;
                daySlot.dataset.date = date.toISOString().split('T')[0];

                if (i === 0) {
                    daySlot.classList.add('active');
                    selectedDate = daySlot.dataset.date;
                }

                daySlot.addEventListener('click', () => {
                    document.querySelector('.booking_day.active')?.classList.remove('active');
                    daySlot.classList.add('active');
                    selectedDate = daySlot.dataset.date;
                    checkAvailability(selectedDate);
                });

                container.appendChild(daySlot);
            });
        }


    function scrollDates(direction) {
        const newIndex = currentDayIndex + direction;
        if (newIndex >= 0 && newIndex <= allDates.length - 6) {
            currentDayIndex = newIndex;
            updateDays();
            const firstDay = document.querySelector('.booking_day');
            if (firstDay) {
                document.querySelector('.booking_day.active')?.classList.remove('active');
                firstDay.classList.add('active');
                selectedDate = firstDay.dataset.date;
                checkAvailability(selectedDate);
            }
        }
    }

    function generateTimeSlots(bookedTimes = []) {
        const container = document.getElementById('booking_slots');
        container.innerHTML = '';

        for (let h = 8; h <= 22; h++) {
            for (let m = 0; m < 60; m += 15) {
                const timeStr = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
                const timeSlot = document.createElement("div");
                timeSlot.className = "booking_slot";
                timeSlot.textContent = timeStr;

                if (bookedTimes.includes(h * 60 + m)) {
                    timeSlot.classList.add("booked");
                }
                container.appendChild(timeSlot);
            }
        }

        slots = document.querySelectorAll('.booking_slot');
        addTimeSlotListeners();
    }

    function addTimeSlotListeners() {
        slots.forEach(slot => {
            slot.addEventListener('click', handleSlotClick);
            slot.addEventListener('mouseenter', handleSlotHover);
            slot.addEventListener('mouseleave', handleSlotHover);
        });
    }

    function handleSlotClick() {
        if (this.classList.contains('booked')) return;

        if (!startSlot) {
            startSlot = this;
            this.classList.add('end');
            updateSubmitButton();
        } else if (startSlot && !endSlot && this !== startSlot) {
            if (isWithinTwoHours(startSlot, this)) {
                endSlot = this;
                this.classList.add('end');
                updateSubmitButton();
            } else {
                alert("Максимальное время бронирования - 2 часа");
            }
        } else {
            clearSelection();
            if (this !== startSlot && this !== endSlot) {
                startSlot = this;
                this.classList.add('end');
            }
            updateSubmitButton();
        }
    }

    function handleSlotHover() {
        if (!startSlot || endSlot) return;
        updateMidSlots(this);
    }

    function updateMidSlots(hoveredSlot) {
        if (!startSlot) return;

        slots.forEach(slot => {
            slot.classList.remove('mid', 'end');
            if (slot === startSlot) slot.classList.add('end');
        });

        if (hoveredSlot !== startSlot && isWithinTwoHours(startSlot, hoveredSlot)) {
            const startIdx = getIndex(startSlot);
            const hoverIdx = getIndex(hoveredSlot);
            const [minIdx, maxIdx] = [Math.min(startIdx, hoverIdx), Math.max(startIdx, hoverIdx)];

            for (let i = minIdx + 1; i < maxIdx; i++) {
                slots[i].classList.add('mid');
            }
            hoveredSlot.classList.add('end');
        }
    }

    function updateSubmitButton() {
        const btn = document.getElementById('booking_submit_btn');
        if (startSlot && endSlot) {
            const startTime = startSlot.textContent;
            const endTime = add15Minutes(endSlot.textContent);
            btn.textContent = `Забронировать ${startTime}-${endTime}`;
            btn.disabled = false;
        } else {
            btn.textContent = 'Забронировать';
            btn.disabled = !startSlot;
        }
    }

    function clearSelection() {
        slots.forEach(slot => slot.classList.remove('mid', 'end'));
        startSlot = null;
        endSlot = null;
    }

    function isWithinTwoHours(slot1, slot2) {
        return Math.abs(getIndex(slot1) - getIndex(slot2)) < 8;
    }

    function getIndex(slot) {
        return Array.from(slot.parentNode.children).indexOf(slot);
    }

    async function checkAvailability(date) {
        const spaceId = document.getElementById('space_id').value;
        try {
            const response = await fetch(`/api/availability/${spaceId}?date=${date}`);
            const data = await response.json();

            const bookedSlots = data.booked_slots || [];
            const bookedTimes = bookedSlots.flatMap(slot => {
                const start = parseTime(slot.start);
                const end = parseTime(slot.end);
                return Array.from({ length: end - start }, (_, i) => start + i);
            });

            generateTimeSlots(bookedTimes);
        } catch (error) {
            console.error('Ошибка при проверке доступности:', error);
        }
    }

    function mouseMidSlotsUpdater() {
        if (!startSlot || (startSlot && endSlot)) return
        updateMidSlots(this)
    }

    function add15Minutes(time) {
        const [hours, minutes] = time.split(":").map(Number);
        let newTime;
        if (minutes == '45') {
            newTime = `${hours + 1}:00`
        } else {
            newTime = `${hours}:${minutes + 15}`
        }
        return newTime
    }
    function textToTime(text) {
        let [hours, minutes] = text.split(":").map(Number);
        return hours * 60 + minutes;
    }

    const submitBtn = document.getElementById('booking_submit_btn')

    function addTimeSlotListeners() {        
        slots.forEach(slot => {
            slot.addEventListener('click', () => {
                if (slot.classList.contains('booked')) return
                if (!startSlot) {
                    startSlot = slot
                    slot.classList.add('end')
                    submitBtn.textContent = 'Забронировать';
                } else if (startSlot && endSlot && slot != startSlot && slot != endSlot) {
                    clearSelection()
                    startSlot = slot
                    slot.classList.add('end')
                    submitBtn.textContent = 'Забронировать';
                } else if (slot == startSlot) {
                    clearSelection();
                    submitBtn.textContent = 'Забронировать';
                } else if (slot == endSlot) {
                    endSlot = null
                    slot.classList.remove('end')
                    slots.forEach((slot, i) => {
                        slot.classList.remove('mid')
                    });
                    submitBtn.textContent = 'Забронировать';
                } else {
                    if (isWithinTwoHours(startSlot, slot)) {
                        endSlot = slot
                        slot.classList.add('end')
                        let booking_text;
                        if (getIndex(startSlot) > getIndex(endSlot)) {
                            booking_text = `Забронировать на ${endSlot.textContent}-${add15Minutes(startSlot.textContent)}, ${selectedDate}`
                        } else {
                            booking_text = `Забронировать на ${startSlot.textContent}-${add15Minutes(endSlot.textContent)}, ${selectedDate}`
                        }
                        submitBtn.textContent = booking_text;
                    } else {
                        alert("Пространство можно забронировать не более чем на 2 часа")
                    }
                }
            });

            slot.addEventListener('mouseenter', mouseMidSlotsUpdater);

            slot.addEventListener('mouseleave', mouseMidSlotsUpdater);
        });
    }

    const allDates = generateDateList();
    let chosenDay = 0;
    let currentDayIndex = 0;
    let daySlots = [];

    updateDays();
    generateTimeSlots();
    checkAvailability(selectedDate);

    document.getElementById("prev_day").addEventListener("click", () => scrollDates(-6));
    document.getElementById("next_day").addEventListener("click", () => scrollDates(6));

    bookingForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const isLoggedIn = document.body.dataset.loggedIn === 'true';
        if (!isLoggedIn) {
            alert('Для бронирования необходимо войти в систему');
            window.location.href = '/auth/login';
            return;
        }

        if (!selectedDate || !startSlot || !endSlot) {
            alert('Бронирование невозможно, заполнены не все данные');
            return;
        }

        const formData = {
            space_id: parseInt(document.getElementById('space_id').value),
            booking_date: selectedDate,
            start_time: startSlot.textContent < endSlot.textContent ? startSlot.textContent : endSlot.textContent,
            end_time: add15Minutes(endSlot.textContent > startSlot.textContent ? endSlot.textContent : startSlot.textContent),
            comment: document.getElementById('comment').value || null
        };

        if (!formData.start_time || !formData.end_time) {
            alert('Пожалуйста, выберите временной интервал');
            return;
        }

        try {
            const response = await fetch('/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Ошибка сервера');

            document.getElementById('result_popup').classList.add('active')
            if (getIndex(startSlot) > getIndex(endSlot)) {
                booking_text = `${endSlot.textContent}-${add15Minutes(startSlot.textContent)}, ${selectedDate}`
            } else {
                booking_text = `${startSlot.textContent}-${add15Minutes(endSlot.textContent)}, ${selectedDate}`
            }

            document.getElementById('result_text').textContent = `Вы забронировали ${document.querySelector('.space_name').textContent} на ${booking_text}`
            toggleNoScroll()

            clearSelection();
            checkAvailability(selectedDate);
        } catch (error) {
            console.error('Ошибка:', error);
            document.getElementById('error_popup').classList.add('active')
            if (error.message == 'Too much bookings') {
                document.getElementById('error_text').textContent = 'Забронировать пространство не удалось, у вас уже достигнуто максимальное количество записей на человека'
            }
            toggleNoScroll()

        }
    });


    document.querySelector('.fav-button').addEventListener('click', async function() {
        const spaceId = this.dataset.spaceId;
        try {
            const response = await fetch('/api/favorites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ space_id: spaceId })
            });

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            this.classList.toggle('active');
            const svgPath = this.querySelector('path');
            svgPath.setAttribute('fill', this.classList.contains('active') ? 'red' : 'currentColor');
        } catch (error) {
            console.error('Error:', error);
            alert('Ошибка при обновлении избранного: ' + error.message);
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.popup').forEach((popup) => {
        popup.addEventListener('click', () => {
            popup.classList.remove('active');
            toggleNoScroll();
        })
    });
})
