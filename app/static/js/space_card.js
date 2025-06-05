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
