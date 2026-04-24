(function () {
    const mobileQuery = window.matchMedia('(max-width: 780px), (hover: none) and (pointer: coarse)');
    const menuSyncEvent = 'planboost:mobile-menu-open';

    function initSortMenu() {
        const sortMenu = document.querySelector('.tasks-sort-menu');
        const sortTrigger = document.querySelector('.tasks-sort-trigger');

        if (!sortMenu || !sortTrigger) {
            return;
        }

        function isMobile() {
            return mobileQuery.matches;
        }

        function closeMenu() {
            sortMenu.classList.remove('is-open');
            sortTrigger.setAttribute('aria-expanded', 'false');
        }

        function openMenu() {
            sortMenu.classList.add('is-open');
            sortTrigger.setAttribute('aria-expanded', 'true');
            document.dispatchEvent(new CustomEvent(menuSyncEvent, { detail: { source: 'sort' } }));
        }

        function toggleMenu(event) {
            if (!isMobile()) {
                return;
            }

            event.preventDefault();

            if (sortMenu.classList.contains('is-open')) {
                closeMenu();
                return;
            }

            openMenu();
        }

        sortTrigger.addEventListener('click', toggleMenu);

        document.addEventListener('pointerdown', function (event) {
            if (!isMobile()) {
                return;
            }

            if (!sortMenu.classList.contains('is-open')) {
                return;
            }

            if (!sortMenu.contains(event.target)) {
                closeMenu();
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                closeMenu();
            }
        });

        document.addEventListener(menuSyncEvent, function (event) {
            if (!isMobile()) {
                return;
            }

            if (event.detail && event.detail.source !== 'sort') {
                closeMenu();
            }
        });

        if (typeof mobileQuery.addEventListener === 'function') {
            mobileQuery.addEventListener('change', closeMenu);
        } else if (typeof mobileQuery.addListener === 'function') {
            mobileQuery.addListener(closeMenu);
        }

        closeMenu();
    }

    document.addEventListener('DOMContentLoaded', initSortMenu);
})();
