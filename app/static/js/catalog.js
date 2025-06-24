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
            spaceList.appendChild(createElement('button', 'gallery_button prev'))
            spaces.forEach(space => {
                console.log(space.images)
                const space_item = createElement('li', 'category_item', {},
                    createElement('a', 'space_container', {href: `/space/${space.id}`},
                        space.images[0] ? createElement('img', 'space_image', {src: `/static/assets/${space.images[0].url}`, alt: space.images[0].alt}) : createElement('img', 'space_image', {src: '/static/assets/default_placeholder.jpeg', alt:'No image available'}),
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
            spaceList.appendChild(createElement('button', 'gallery_button next'))
            categoryFlex.appendChild(spaceList);
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

