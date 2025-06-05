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
    const slots = document.querySelectorAll('.booking_slot')

    let startSlot = null;
    let endSlot = null;

    function getSlotIndex(slot) {
        return Array.from(slot.parentNode.children).indexOf(slot);
    }

    function isWithinTwoHours(slot1, slot2) {
        let index1 = getSlotIndex(slot1);
        let index2 = getSlotIndex(slot2);
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
        const startIndex = getSlotIndex(startSlot);
        const activeIndex = getSlotIndex(activeSlot);
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

    slots.forEach(slot => {
        slot.addEventListener('click', () => {
            if (!startSlot) {
                startSlot = slot
                slot.classList.add('end')
            } else if (startSlot && endSlot && slot != startSlot && slot != endSlot) {
                clearSelection()
                startSlot = slot
                slot.classList.add('end')
            } else if (slot == startSlot) {
                clearSelection();
            } else if (slot == endSlot) {
                endSlot = null
                slot.classList.remove('end')
                slots.forEach((slot, i) => {
                    slot.classList.remove('mid')
                });
            } else {
                if (isWithinTwoHours(startSlot, slot)) {
                    endSlot = slot
                    slot.classList.add('end')
                } else {
                    alert("Пространство можно забронировать не более чем на 2 часа")
                }
            }
        });

        slot.addEventListener('mouseenter', mouseEnterFunc);

        slot.addEventListener('mouseleave', mouseLeaveFunc);
    });
});