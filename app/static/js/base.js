window.addEventListener('load', function () {
    let isOpen = false;

    document.getElementById('burger_button').addEventListener('click', function () {
        const ani1 = document.getElementById('ani1');
        const ani1Back = document.getElementById('ani1-back');
        const ani2 = document.getElementById('ani2');
        const ani2Back = document.getElementById('ani2-back');
        const mobileMenu = document.querySelector('.header_nav');

        if (!isOpen) {
            ani1.beginElement();
            ani2.beginElement();
            mobileMenu.classList.toggle('active');
            document.body.classList.toggle('no-scroll');

        } else {
            ani1Back.beginElement();
            ani2Back.beginElement();
            mobileMenu.classList.toggle('active');
            document.body.classList.toggle('no-scroll');
        }

        isOpen = !isOpen;
    });
})