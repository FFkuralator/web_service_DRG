function createElement(tag, className, props = {}, ...children) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  Object.entries(props).forEach(([key, value]) => el[key] = value);
  children.forEach(child => el.appendChild(child));
  return el;
}

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
        checkbox.addEventListener('change', applyFilters);
    });

    document.querySelectorAll('input[name="feature"]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });

    const resetBtn = document.getElementById('filter_reset')
    resetBtn.addEventListener('click', () => {

    document.querySelectorAll('input[name="activity"][type="radio"]').forEach(radio => {
        radio.checked = false;
    });

    document.querySelectorAll('input[name="building"][type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });

    document.querySelectorAll('input[name="feature"][type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });

    applyFilters();
})
    function applyFilters() {
        const activity = document.querySelector('input[name="activity"]:checked')?.value;
        const buildings = Array.from(document.querySelectorAll('input[name="building"]:checked')).map(el => el.value);
        const features = Array.from(document.querySelectorAll('input[name="feature"]:checked')).map(el => el.value);

        const params = new URLSearchParams();
        if (activity) params.append('activity', activity);
        if (buildings.length) params.append('building', buildings.join(','));
        if (features.length) params.append('features', features.join(','));

        fetch(`/catalog/filter?${params.toString()}`)
            .then(response => response.json())
            .then(data => updateCatalog(data))
            .catch(error => console.error('Error:', error));
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

        categoriesMap.forEach((spaces, categoryName, index) => {
            const categorySection = createElement('section', 'category_catalog', {dataset: {categoryId: index}}, 
                createElement('h2', 'category_title', {textContent: categoryName})
            )
            const categoryFlex = createElement('div', 'category_row');
            const spaceList = createElement('ul', 'category_list');

            spaces.forEach(space => {
                const space_item = createElement('li', 'category_item', {},
                    createElement('a', 'space_container', {href: `/space/${space.id}`},
                        createElement('button', 'fav_button_box', {dataset: {spaceId: space.id}, disabled: true},
                            createElement('div', `fav_button ${space.is_favorite? active : ''}`, {innerHTML: `<svg width="14" height="14" viewBox="0 0 24 24" fill="{% if space.is_favorite %}red{% else %}currentColor{% endif %}" xmlns="http://www.w3.org/2000/svg"><path d="M12 21.593c-5.63-5.539-11-10.297-11-14.402 0-3.791 3.068-5.191 5.281-5.191 1.312 0 4.151.501 5.719 4.457 1.59-3.968 4.464-4.447 5.726-4.447 2.54 0 5.274 1.621 5.274 5.181 0 4.069-5.136 8.625-11 14.402m5.726-20.583c-2.203 0-4.446 1.042-5.726 3.238-1.285-2.206-3.522-3.248-5.719-3.248-3.183 0-6.281 2.187-6.281 6.191 0 4.661 5.571 9.429 12 15.809 6.43-6.38 12-11.148 12-15.809 0-4.011-3.095-6.181-6.274-6.181"/></svg>`})
                        ),
                        space.images[0] ? createElement('img', 'space_image', {src: `/static/assets/${space.images[0].url}`, alt: space.images[0].alt}) : createElement('img', 'space_image', {src: '/static/assets/default_placeholder.png', alt:'No image available'}),
                        createElement('div', 'space_text_container', {},
                            createElement('h3', 'space_name', {textContent: space.name}),
                                createElement('ul', 'space_characteristics', {},
                                    createElement('li', 'space_characteristics_item', {textContent: `Корпус ${space.building}`}),
                                    createElement('li', 'space_characteristics_item', {textContent: `Уровень ${space.level}`})
                                )

                        )
                    )
                )

                spaceList.appendChild(space_item)
            });

            categoryFlex.appendChild(createElement('button', 'gallery_button prev', {innerHTML: "&#9664"}));
            categoryFlex.appendChild(spaceList);
            categoryFlex.appendChild(createElement('button', 'gallery_button next', {innerHTML: "&#9658"}));
            categorySection.appendChild(categoryFlex)
            catalogSection.appendChild(categorySection);

            const id = categorySection.dataset.carouselId;
            carouselIndices.set(id, 0);

            const items = Array.from(spaceList.querySelectorAll('.category_item'));
            const prevBtn = categoryFlex.querySelector('.prev');
            const nextBtn = categoryFlex.querySelector('.next');

            while (items.length < 3) {
                const firstItem = items[0];
                const clone = firstItem.cloneNode(true);
                spaceList.appendChild(clone);
                items.push(clone);
            }

            for (let i = 0; i < 3; i++) {
                items[i].classList.remove('none')
                items[i].classList.add(i == 0 ? 'left' : i == 1 ? 'mid' : 'right')
            }

            [prevBtn, nextBtn].forEach(btn => {
                btn.addEventListener('click', () => {
                    const currentIndex = carouselIndices.get(id);
                    items.forEach(item => {
                        item.classList.remove('left')
                        item.classList.remove('mid')
                        item.classList.remove('right')
                    })

                    const newIndex = btn === prevBtn
                        ? (currentIndex - 1 + items.length) % items.length
                        : (currentIndex + 1) % items.length;

                    carouselIndices.set(id, newIndex);
                    items[newIndex].classList.add('left');
                    items[(newIndex + 1) % items.length].classList.add('mid');
                    items[(newIndex + 2) % items.length].classList.add('right');
                });
            });

        });

        if (categoriesMap.size === 0) {
            const noResults = createElement('p', 'no-results', {textContent: 'По вашему запросу ничего не найдено'});
            catalogSection.appendChild(noResults);
        }
    }

    const carouselIndices = new Map();

    applyFilters()

});

