function createElement(tag, className, props = {}, ...children) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  Object.entries(props).forEach(([key, value]) => el[key] = value);
  children.forEach(child => el.appendChild(child));
  return el;
}

window.addEventListener('load', function () {
    document.querySelectorAll('.admin_btn').forEach(element => {
        const userId = element.dataset.userId;
        element.addEventListener('click', async function() {
            try {
                const response = await fetch(`/master/users/${userId}/toggle-admin`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userId: userId })
                });

                const data = await response.json();
                if (data.error) throw new Error(data.error);
            } catch (error) {
                console.error('Error:', error);
                alert('Ошибка при обновлении: ' + error.message);
            }
        })

    })

    document.querySelectorAll('.ban_btn').forEach(element => {
        const userId = element.dataset.userId;
        element.addEventListener('click', async function() {
            try {
                const response = await fetch(`/master/users/${userId}/toggle-ban`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userId: userId })
                });

                const data = await response.json();
                if (data.error) throw new Error(data.error);
            } catch (error) {
                console.error('Error:', error);
                alert('Ошибка при обновлении: ' + error.message);
            }
        })

    })
})

window.onload = function () {
    document.querySelectorAll(".history_btn").forEach(element => {
        element.addEventListener("click", async function() {
            const userId = element.dataset.userId;
            const history = element.closest('.user').querySelector('.history')
            history.classList.toggle('display_none')
                try {
                    const response = await fetch(`/master/users/${userId}/bookings`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ userId: userId })
                    });

                    const data = await response.json();
                    if (data.error) throw new Error(data.error);

                    history.innerHTML = ''
                    for (let booking of data) {
                        const history_item = createElement('li', 'history_item', {
                            innerHTML: `
                                <h4>${booking.space_name}</h4>
                                <div>${booking.time} ${booking.date}</div>
                                <div>Успешное бронирование</div>
                                <div class="grid_span_2">${booking.comment || ''}</div>
                                <button class="submit_button">Отменить</button>
                            `
                        })

                        history.appendChild(history_item)
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Ошибка при обновлении: ' + error.message);
                }
            })
    });
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
