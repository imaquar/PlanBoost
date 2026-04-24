(function () {
    const mobileQuery = window.matchMedia('(max-width: 780px), (hover: none) and (pointer: coarse)');
    const menuSyncEvent = 'planboost:mobile-menu-open';

    function initHeaderMenu() {
        const menuContainer = document.querySelector('.header-menu-container');
        const menuTrigger = document.querySelector('.header-menu-trigger');

        if (!menuContainer || !menuTrigger) {
            return;
        }

        function isMobile() {
            return mobileQuery.matches;
        }

        function closeMenu() {
            menuContainer.classList.remove('is-open');
            menuTrigger.setAttribute('aria-expanded', 'false');
        }

        function openMenu() {
            menuContainer.classList.add('is-open');
            menuTrigger.setAttribute('aria-expanded', 'true');
            document.dispatchEvent(new CustomEvent(menuSyncEvent, { detail: { source: 'header' } }));
        }

        function toggleMenu(event) {
            if (!isMobile()) {
                return;
            }

            event.preventDefault();

            if (menuContainer.classList.contains('is-open')) {
                closeMenu();
                return;
            }

            openMenu();
        }

        menuTrigger.addEventListener('click', toggleMenu);

        document.addEventListener('pointerdown', function (event) {
            if (!isMobile()) {
                return;
            }

            if (!menuContainer.classList.contains('is-open')) {
                return;
            }

            if (!menuContainer.contains(event.target)) {
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

            if (event.detail && event.detail.source !== 'header') {
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

    document.addEventListener('DOMContentLoaded', initHeaderMenu);
})();
