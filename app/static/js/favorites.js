document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.fav-button')) {
            const button = e.target.closest('.fav-button');
            const spaceId = button.dataset.spaceId;
            toggleFavorite(spaceId, button);
        }
    });

    document.querySelectorAll('.fav-button').forEach(button => {
        const spaceId = button.dataset.spaceId;
        checkFavoriteStatus(spaceId, button);
    });
});

function toggleFavorite(spaceId, buttonElement) {
    console.log(`Toggling favorite for space ${spaceId}`); // Debug

    fetch('/api/favorites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() // Если используете CSRF
        },
        body: JSON.stringify({
            space_id: spaceId
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
    })
    .then(data => {
        console.log('Server response:', data); // Debug
        const favButton = buttonElement.querySelector('.fav_button');
        if (data.status === 'added') {
            favButton.classList.add('active');
            favButton.querySelector('svg').setAttribute('fill', 'red');
        } else {
            favButton.classList.remove('active');
            favButton.querySelector('svg').setAttribute('fill', 'currentColor');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при обновлении избранного');
    });
}


function checkFavoriteStatus(spaceId, button) {
    fetch(`/api/favorites/check/${spaceId}`)
    .then(response => response.json())
    .then(data => {
        if (data.is_favorite) {
            button.classList.add('active');
            button.querySelector('svg').setAttribute('fill', 'red');
        }
    });
}
