(function () {
    const noteForm = document.querySelector('.notes-form-shell');

    if (!noteForm) {
        return;
    }

    const titleInput = document.getElementById('id_label');
    const createButton = document.getElementById('create-btn');
    const textareas = noteForm.querySelectorAll('textarea');

    function autoGrow(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
    }

    function toggleCreateButton() {
        if (!titleInput || !createButton) {
            return;
        }
        createButton.disabled = !titleInput.value.trim();
    }

    textareas.forEach(function (textarea) {
        autoGrow(textarea);
        textarea.addEventListener('input', function () {
            autoGrow(textarea);
        });
    });

    if (titleInput) {
        titleInput.addEventListener('input', toggleCreateButton);
    }

    toggleCreateButton();
})();
