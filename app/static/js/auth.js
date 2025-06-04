window.onload = function () {
    document.getElementById("login_swap_button").addEventListener("click", function() {
        document.getElementById('login_container').classList.add('display_none');
        document.getElementById('signup_container').classList.remove('display_none');
    });

    document.getElementById("signup_swap_button").addEventListener("click", function() {
        document.getElementById('login_container').classList.remove('display_none');
        document.getElementById('signup_container').classList.add('display_none');
    });
}