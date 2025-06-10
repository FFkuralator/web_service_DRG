document.addEventListener('DOMContentLoaded', function () {
    const slides = document.querySelectorAll('.slide');
    let currentIndex = 0;


    const prevBtn = document.getElementById('prev_btn');
    const nextBtn = document.getElementById('next_btn');

    function showFullscreen() {
        this.classList.toggle('fulscreen');
        document.body.classList.toggle('no-scroll');
    }

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
        });
        slides[index].classList.add('active');
    }

    slides.forEach((slide, i) => {
        slide.addEventListener('click', showFullscreen);
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
});

document.addEventListener('DOMContentLoaded', function () {
    function getIndex(slot) {
        return Array.from(slot.parentNode.children).indexOf(slot);
    }

    function formatDate(date) {
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
    }
    function formatDay(date) {
        return date.toLocaleDateString('ru-RU', { weekday: 'short' }).toUpperCase();
    }
    
    function generateDateList(count = 18) {
        const dates = [];
        const today = new Date();
        for (let i = 0; i < count; i++) {
            const nextDay = new Date();
            nextDay.setDate(today.getDate() + i);
            dates.push(nextDay);
        }
        return dates;
    }

    const allDates = generateDateList();

    let chosenDay = 0;
    let currentDaysSlide = 0
    let currentDayIndex = 0;
    let daySlots = document.querySelectorAll('.booking_day')

    function updateDays() {
        const container = document.getElementById('booking_days_container')
        container.innerHTML = ''
        for (let i = 0; i < 6; i++) {
            const index = currentDayIndex + i
            const date = allDates[index];
            const daySlot = document.createElement('div');
            daySlot.className = 'booking_day';
            daySlot.textContent = `${formatDate(date)}, ${formatDay(date)}`;
            if (index == chosenDay) {
                daySlot.classList.add('active')
            } else if (index >= 14) {
                daySlot.classList.add('inactive')
            }
            container.appendChild(daySlot);
        }
        daySlots = document.querySelectorAll('.booking_day')
        
        daySlots.forEach(slot => {
            slot.addEventListener('click', () => {
                daySlots.forEach(slot => {
                    slot.classList.remove('active')
                })
                chosenDay = getIndex(slot) + currentDaysSlide * 6
                slot.classList.add('active')
                generateTimeSlots([])
            })
        });

    }

    updateDays();

    function scrollDates(direction) {
        let newIndex = currentDayIndex + direction;
        currentDaysSlide += Number(direction / 6);
        if (newIndex > allDates.length - 6) {
            newIndex = allDates.length - 6;
            currentDaysSlide = 2;
        } else if (newIndex < 0) {
            newIndex = 0;
            currentDaysSlide = 0;
        }
        currentDayIndex = newIndex;
        updateDays();
    }

    document.getElementById("prev_day").addEventListener("click", function() {
        scrollDates(-6)
    });
    document.getElementById("next_day").addEventListener("click", function() {
        scrollDates(6)
    });
    
    function parseTime(timeStr) {
        const [h, m] = timeStr.split(":").map(Number);
        return h * 60 + m;
    }

    function generateTimeSlots(booked, start = "08:00", end="22:45", step=15) {
        const container = document.getElementById('booking_slots');
        container.innerHTML = ''
        let [hours, minutes] = start.split(":").map(Number);

        while (hours * 60 + minutes <= parseTime(end)) {
            const timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
            const timeSlot = document.createElement("div");
            timeSlot.className = "booking_slot";
            if (booked.includes(hours * 60 + minutes)) {
                timeSlot.classList.add("booked");
            }
            timeSlot.textContent = timeStr;
            container.appendChild(timeSlot);

            minutes += step;

            if (minutes >= 60) {
                hours += 1;
                minutes -= 60;
            }
        }
        slots = document.querySelectorAll('.booking_slot')
        addTimeSlotListeners()
    }
    

    let slots;

    let startSlot = null;
    let endSlot = null;

    generateTimeSlots([8*60, 8*60+15, 8*60+30]);

    function isWithinTwoHours(slot1, slot2) {
        let index1 = getIndex(slot1);
        let index2 = getIndex(slot2);
        const diff = Math.abs(index1 - index2);
        return diff < 8;
    }

    function clearSelection() {
        slots.forEach(slot => {
            slot.classList.remove('mid', 'end');
        });
        startSlot = null;
        endSlot = null;
    }

    function updateMidSlots(activeSlot) {
        const startIndex = getIndex(startSlot);
        const activeIndex = getIndex(activeSlot);
        if (!isWithinTwoHours(startSlot, activeSlot)) {
            if (startIndex > activeIndex) {
                slots.forEach((slot, i) => {
                    if (i > startIndex - 7 && i < startIndex) {
                        slot.classList.add('mid')
                    } else if (i == startIndex - 7) {
                        slot.classList.add('end')
                    } else {
                        slot.classList.remove('mid')
                    }
                });
            } else {
                slots.forEach((slot, i) => {
                    if (i > startIndex && i < startIndex + 7) {
                        slot.classList.add('mid')
                    } else if (i == startIndex + 7) {
                        slot.classList.add('end')
                    } else {
                        slot.classList.remove('mid')
                    }
                });
            }
        } else {
            slots.forEach((slot, i) => {
                if (i > Math.min(startIndex, activeIndex) && i < Math.max(startIndex, activeIndex)) {
                    slot.classList.add('mid')
                } else if (i == activeIndex) {
                    slot.classList.add('end')
                    slot.classList.remove('mid')
                } else {
                    slot.classList.remove('mid')
                }
                if (i != activeIndex && i != startIndex) {
                    slot.classList.remove('end')
                }
            });
        }
    }

    function mouseEnterFunc() {
        if (!startSlot || (startSlot && endSlot)) return
        updateMidSlots(this)
    }

    function mouseLeaveFunc() {
        if (!startSlot || (startSlot && endSlot)) return
        updateMidSlots(this)
    }

    function addTimeSlotListeners() {
        function add15Minutes(time) {
            const text = time.split(":").map(Number);
            let newTime;
            if (text[1] == '45') {
                newTime = `${text[0] + 1}:00`
            } else {
                newTime = `${text[0]}:${text[1] + 15}`
            }
            return newTime
        }
        
        slots.forEach(slot => {
            slot.addEventListener('click', () => {
                if (slot.classList.contains('booked')) return
                if (!startSlot) {
                    startSlot = slot
                    slot.classList.add('end')
                    document.getElementById('booking_submit_btn').textContent = 'Забронировать';
                } else if (startSlot && endSlot && slot != startSlot && slot != endSlot) {
                    clearSelection()
                    startSlot = slot
                    slot.classList.add('end')
                    document.getElementById('booking_submit_btn').textContent = 'Забронировать';
                } else if (slot == startSlot) {
                    clearSelection();
                    document.getElementById('booking_submit_btn').textContent = 'Забронировать';
                } else if (slot == endSlot) {
                    endSlot = null
                    slot.classList.remove('end')
                    slots.forEach((slot, i) => {
                        slot.classList.remove('mid')
                    });
                    document.getElementById('booking_submit_btn').textContent = 'Забронировать';
                } else {
                    if (isWithinTwoHours(startSlot, slot)) {
                        endSlot = slot
                        slot.classList.add('end')
                        let booking_text;
                        if (getIndex(startSlot) > getIndex(endSlot)) {
                            booking_text = `Забронировать на ${endSlot.textContent}-${add15Minutes(startSlot.textContent)}, ${daySlots[chosenDay].innerText}`
                        } else {
                            booking_text = `Забронировать на ${startSlot.textContent}-${add15Minutes(endSlot.textContent)}, ${daySlots[chosenDay].innerText}`
                        }
                        document.getElementById('booking_submit_btn').textContent = booking_text;
                    } else {
                        alert("Пространство можно забронировать не более чем на 2 часа")
                    }
                }
            });

            slot.addEventListener('mouseenter', mouseEnterFunc);

            slot.addEventListener('mouseleave', mouseLeaveFunc);
        });
    }

});
