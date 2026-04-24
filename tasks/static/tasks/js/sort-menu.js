(function () {
    const mobileQuery = window.matchMedia('(max-width: 640px)');

    function initSortMenu() {
        const sortMenu = document.querySelector('.tasks-sort-menu');
        const sortTrigger = document.querySelector('.tasks-sort-trigger');

        if (!sortMenu || !sortTrigger) {
            return;
        }

        function isMobile() {
            return mobileQuery.matches;
        }

        function setOpen(isOpen) {
            sortMenu.classList.toggle('is-open', isOpen);
            sortTrigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }

        function toggleMenu(event) {
            if (!isMobile()) {
                return;
            }

            event.preventDefault();
            setOpen(!sortMenu.classList.contains('is-open'));
        }

        function closeMenu() {
            setOpen(false);
        }

        sortTrigger.addEventListener('click', toggleMenu);

        if (typeof mobileQuery.addEventListener === 'function') {
            mobileQuery.addEventListener('change', closeMenu);
        } else if (typeof mobileQuery.addListener === 'function') {
            mobileQuery.addListener(closeMenu);
        }

        closeMenu();
    }

    document.addEventListener('DOMContentLoaded', initSortMenu);
})();
