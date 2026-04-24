(function () {
    const widthQuery = window.matchMedia('(max-width: 780px)');
    const touchQuery = window.matchMedia('(hover: none) and (pointer: coarse)');
    const menuSyncEvent = 'planboost:mobile-menu-open';

    function initSortMenu() {
        const sortMenu = document.querySelector('.tasks-sort-menu');
        const sortTrigger = document.querySelector('.tasks-sort-trigger');

        if (!sortMenu || !sortTrigger) {
            return;
        }

        let lastTouchToggleAt = 0;

        function isMobileLike() {
            return widthQuery.matches || touchQuery.matches || navigator.maxTouchPoints > 0 || 'ontouchstart' in window;
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
            if (!isMobileLike()) {
                return;
            }

            event.preventDefault();

            if (sortMenu.classList.contains('is-open')) {
                closeMenu();
                return;
            }

            openMenu();
        }

        sortTrigger.addEventListener('touchend', function (event) {
            lastTouchToggleAt = Date.now();
            toggleMenu(event);
        }, { passive: false });

        sortTrigger.addEventListener('click', function (event) {
            if (Date.now() - lastTouchToggleAt < 400) {
                event.preventDefault();
                return;
            }
            toggleMenu(event);
        });

        document.addEventListener('pointerdown', function (event) {
            if (!isMobileLike()) {
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
            if (!isMobileLike()) {
                return;
            }

            if (event.detail && event.detail.source !== 'sort') {
                closeMenu();
            }
        });

        function bindQuery(query, handler) {
            if (typeof query.addEventListener === 'function') {
                query.addEventListener('change', handler);
            } else if (typeof query.addListener === 'function') {
                query.addListener(handler);
            }
        }

        bindQuery(widthQuery, closeMenu);
        bindQuery(touchQuery, closeMenu);

        closeMenu();
    }

    document.addEventListener('DOMContentLoaded', initSortMenu);
})();
