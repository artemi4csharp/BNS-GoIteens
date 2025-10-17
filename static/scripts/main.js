document.addEventListener('DOMContentLoaded', function() {
    const createBtn = document.querySelector('.create-btn');
    const modal = document.getElementById('createModal');
    const closeBtn = document.querySelector('.modal-close');
    const overlay = document.querySelector('.modal-overlay');
    
    if (createBtn) {
        createBtn.addEventListener('click', function(e) {
            e.preventDefault();
            modal.classList.remove('hidden');
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.classList.add('hidden');
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', function() {
            modal.classList.add('hidden');
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
});