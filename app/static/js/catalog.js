function popup_function(popup_name) {
    filter_name = popup_name + "_filter"
    popup_name = popup_name + "_popup"
    document.getElementById(filter_name).addEventListener("click", function() {
        
        const target = this
        const popup = document.getElementById(popup_name);    
        popup.classList.remove('display_none');
        const rect = target.getBoundingClientRect();

        popup.style.top = `${rect.bottom + window.scrollY + 12}px`;
        popup.style.left = `${rect.left + window.scrollX}px`;

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
    popup_function('point')
    popup_function('building')
    popup_function('feature')
})