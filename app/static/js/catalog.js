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
    });
}

window.addEventListener('load', function () {
    popup_function('activity')
    popup_function('building')
    popup_function('feature')
})

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="activity"]').forEach(radio => {
        radio.addEventListener('change', applyFilters);
    });

    document.querySelectorAll('input[name="building"]').forEach(checkbox => {
        radio.addEventListener('change', applyFilters);
    });

    document.querySelectorAll('input[name="feature"]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });

    const resetBtn = document.getElementById('filter_reset')
    resetBtn.addEventListener('click', () => {
        document.querySelectorAll('input[type="checkbox').forEach(checkbox => checkbox.checked = false)
        document.querySelectorAll('input[type="radio').forEach(radio => radio.checked = false)
        applyFilters()
    })

    function applyFilters() {
        const activity = document.querySelector('input[name="activity"]:checked')?.value;
        const buildings = Array.from(document.querySelectorAll('input[name^="building"]:checked')).map(el => el.value);
        const features = Array.from(document.querySelectorAll('input[name^="feature"]:checked')).map(el => el.value);

        fetch(`/catalog/filter?activity=${activity || ''}&buildings=${features.join(',') || ''}&features=${features.join(',') || ''}`)
            .then(response => response.json())
            .then(data => updateCatalog(data));
    }

function updateCatalog(data) {
    const categoriesMap = new Map();
    data.forEach(space => {
        if (!categoriesMap.has(space.category_name)) {
            categoriesMap.set(space.category_name, []);
        }
        categoriesMap.get(space.category_name).push(space);
    });

    const catalogSection = document.querySelector('.catalog');

    catalogSection.innerHTML = '';

    categoriesMap.forEach((spaces, categoryName) => {
        const categorySection = document.createElement('section');
        categorySection.className = 'category_catalog';

        const title = document.createElement('h2');
        title.className = 'category_title';
        title.textContent = categoryName;
        categorySection.appendChild(title);

        const spaceList = document.createElement('ul');
        spaceList.className = 'category_list';

        spaces.forEach(space => {
            const spaceItem = document.createElement('li');
            spaceItem.className = 'category_item';

            const spaceLink = document.createElement('a');
            spaceLink.className = 'space_container';
            spaceLink.href = `/space/${space.id}`;

            const favButtonBox = document.createElement('button');
            favButtonBox.className = 'fav_button_box';

            const favButton = document.createElement('div');
            favButton.className = 'fav_button';
            favButton.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 21.593c-5.63-5.539-11-10.297-11-14.402 0-3.791 3.068-5.191 5.281-5.191 1.312 0 4.151.501 5.719 4.457 1.59-3.968 4.464-4.447 5.726-4.447 2.54 0 5.274 1.621 5.274 5.181 0 4.069-5.136 8.625-11 14.402m5.726-20.583c-2.203 0-4.446 1.042-5.726 3.238-1.285-2.206-3.522-3.248-5.719-3.248-3.183 0-6.281 2.187-6.281 6.191 0 4.661 5.571 9.429 12 15.809 6.43-6.38 12-11.148 12-15.809 0-4.011-3.095-6.181-6.274-6.181"/>
                </svg>
            `;

            const favCounter = document.createElement('span');
            favCounter.className = 'fav_button_counter';
            favCounter.textContent = space.likes_count || '0';

            favButtonBox.appendChild(favButton);
            favButtonBox.appendChild(favCounter);
            spaceLink.appendChild(favButtonBox);

            const spaceImage = document.createElement('img');
            spaceImage.className = 'space_image';
            spaceImage.src = `/static/${space.image_src}`;
            spaceImage.alt = space.image_alt;
            spaceLink.appendChild(spaceImage);

            const textContainer = document.createElement('div');
            textContainer.className = 'space_text_container';

            const spaceName = document.createElement('h3');
            spaceName.className = 'space_name';
            spaceName.textContent = space.name;
            textContainer.appendChild(spaceName);

            const characteristicsList = document.createElement('ul');
            characteristicsList.className = 'space_characteristics';

            const buildingItem = document.createElement('li');
            buildingItem.className = 'space_characteristics_item';
            buildingItem.textContent = `Корпус ${space.building}`;
            characteristicsList.appendChild(buildingItem);

            const levelItem = document.createElement('li');
            levelItem.className = 'space_characteristics_item';
            levelItem.textContent = `Уровень ${space.level}`;
            characteristicsList.appendChild(levelItem);

            const locationItem = document.createElement('li');
            locationItem.className = 'space_characteristics_item';
            locationItem.textContent = space.location;
            characteristicsList.appendChild(locationItem);

            textContainer.appendChild(characteristicsList);

            const description = document.createElement('p');
            description.className = 'space_description';
            description.textContent = space.description;
            textContainer.appendChild(description);

            spaceLink.appendChild(textContainer);
            spaceItem.appendChild(spaceLink);
            spaceList.appendChild(spaceItem);
        });

        categorySection.appendChild(spaceList);
        catalogSection.appendChild(categorySection);
    });

    if (categoriesMap.size === 0) {
        const noResults = document.createElement('p');
        noResults.className = 'no-results';
        noResults.textContent = 'По вашему запросу ничего не найдено';
        catalogSection.appendChild(noResults);
    }
}
});