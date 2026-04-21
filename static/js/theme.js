(function () {
    const storageKey = 'planboost-theme';
    const light = 'light';
    const dark = 'dark';

    function systemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? dark : light;
    }

    function savedTheme() {
        try {
            const value = localStorage.getItem(storageKey);
            return value === light || value === dark ? value : null;
        } catch {
            return null;
        }
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try {
            localStorage.setItem(storageKey, theme);
        } catch {}
    }

    function iconElement(button) {
        return button ? button.querySelector('i') : null;
    }

    function syncToggle(themeButton, theme) {
        if (!themeButton) {
            return;
        }

        const icon = iconElement(themeButton);
        const isDark = theme === dark;

        themeButton.setAttribute('aria-pressed', String(isDark));
        themeButton.setAttribute('aria-label', isDark ? 'switch to light theme' : 'switch to dark theme');

        if (!icon) {
            return;
        }

        icon.classList.remove('fa-moon', 'fa-sun');
        icon.classList.add(isDark ? 'fa-sun' : 'fa-moon');
    }

    function currentTheme() {
        const value = document.documentElement.getAttribute('data-theme');
        if (value === light || value === dark) {
            return value;
        }
        const saved = savedTheme();
        return saved || systemTheme();
    }

    function apply(themeButton, theme) {
        setTheme(theme);
        syncToggle(themeButton, theme);
    }

    function toggle(themeButton) {
        const next = currentTheme() === dark ? light : dark;
        apply(themeButton, next);
    }

    document.addEventListener('DOMContentLoaded', function () {
        const themeButton = document.querySelector('.theme-button');
        apply(themeButton, currentTheme());

        if (!themeButton) {
            return;
        }

        themeButton.addEventListener('click', function () {
            toggle(themeButton);
        });
    });
})();
