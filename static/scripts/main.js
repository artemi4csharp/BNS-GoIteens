document.addEventListener('DOMContentLoaded', function() {
    // ========== Модальне вікно створення оголошення ==========
    const createBtn = document.querySelector('.create-btn');
    const createModal = document.getElementById('createModal');
    const closeBtn = document.querySelector('.modal-close');
    const overlay = document.querySelector('.modal-overlay');

    if (createBtn && createModal) {
        createBtn.addEventListener('click', function(e) {
            e.preventDefault();
            createModal.classList.remove('hidden');
        });
    }

    if (closeBtn && createModal) {
        closeBtn.addEventListener('click', function() {
            createModal.classList.add('hidden');
        });
    }

    if (overlay && createModal) {
        overlay.addEventListener('click', function() {
            createModal.classList.add('hidden');
        });
    }

    const optionCards = document.querySelectorAll('.option-card');
    optionCards.forEach(card => {
        card.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            if (type === 'item') {
                window.location.href = '/item/create_item/';
            } else if (type === 'service') {
                window.location.href = '/services/create/';
            }
        });
    });

    // ========== Модальне вікно категорій ==========
    const categoryModal = document.getElementById("categoryModal");
    const openCategoriesLink = document.getElementById("openCategories");
    const closeCategoryBtn = document.querySelector(".close");

    if (openCategoriesLink && categoryModal) {
        openCategoriesLink.addEventListener("click", function(event) {
            event.preventDefault();
            categoryModal.style.display = "block";
        });
    }

    if (closeCategoryBtn && categoryModal) {
        closeCategoryBtn.addEventListener('click', function() {
            categoryModal.style.display = "none";
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target === categoryModal) {
            categoryModal.style.display = "none";
        }
    });
});