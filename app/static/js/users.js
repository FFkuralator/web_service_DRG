window.onload = function () {
    document.querySelectorAll(".history_btn").forEach(element => {
        element.addEventListener("click", function() {
            element.parentElement.parentElement.querySelector('.history').classList.toggle('display_none');
        });
    })
};

function popup_function(popup_name) {
    filter_name = popup_name + "_filter"
    popup_name = popup_name + "_popup"
    document.getElementById(filter_name).addEventListener("click", function() {

        const target = this
        const popup = document.getElementById(popup_name);
        popup.classList.remove('display_none');
        let rect;
        if (document.documentElement.clientWidth > 768) {
            rect = target.getBoundingClientRect();
            popup.style.left = `${rect.left + window.scrollX}px`;

        } else {
            rect = document.querySelector('.filter_header').getBoundingClientRect();
        }
        popup.style.top = `${rect.bottom + window.scrollY + 12}px`;

        function quit_handler(e) {
            if (!popup.contains(e.target) && e.target.id !== 'target') {
                popup.classList.add('display_none');
                document.removeEventListener('click', quit_handler);
            }
        }
        setTimeout(() => {
            document.addEventListener('click', quit_handler);
        }, 1)
        if (popup_name === "status_popup") {
                document.querySelectorAll("#status_popup input[type=checkbox]").forEach(checkbox => {
                    checkbox.addEventListener("change", () => {
                        const statuses = Array.from(document.querySelectorAll("#status_popup input:checked")).map(el => el.value);
                        fetch(`/master/users?status=${statuses.join(",")}`)
                            .then(response => response.json())
                            .then(users => updateUserList(users));
                });
            });
        }

        function updateUserList(users) {
            const container = document.querySelector(".users");
            container.innerHTML = users.map(user => `
                <li class="user">
                    <h3>${user.full_name}</h3>
                    <div>${user.is_admin ? "Админ" : "Пользователь"}</div>
                    <button class="ban-btn" data-user-id="${user.id}">
                        ${user.is_banned ? "Разбанить" : "Забанить"}
                    </button>
                </li>
            `).join("");
        }
    });
}

window.addEventListener('load', function () {
    popup_function('active')
    popup_function('status')
})
