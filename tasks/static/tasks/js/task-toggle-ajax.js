(function () {
    function getCookie(name) {
        const escapedName = name.replace(/[-.]/g, '\\$&');
        const match = document.cookie.match(new RegExp('(?:^|; )' + escapedName + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : '';
    }

    function formatDateTime(isoValue) {
        if (!isoValue) {
            return '';
        }

        const date = new Date(isoValue);
        if (Number.isNaN(date.getTime())) {
            return '';
        }

        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = String(date.getFullYear()).slice(-2);
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return day + '.' + month + '.' + year + ' ' + hours + ':' + minutes;
    }

    function ensureEmptyState(listLayout) {
        const list = listLayout.querySelector('.tasks-list');
        if (!list || list.children.length > 0) {
            return;
        }

        let empty = listLayout.querySelector('.tasks-empty');
        if (!empty) {
            empty = document.createElement('p');
            empty.className = 'tasks-empty';
            empty.textContent = 'no tasks yet';
            list.insertAdjacentElement('afterend', empty);
        }

        list.remove();
    }

    function initTaskToggleAjax() {
        const listLayout = document.querySelector('.tasks-list-layout');
        if (!listLayout) {
            return;
        }

        const csrfToken = getCookie('csrftoken');

        listLayout.addEventListener('change', async function (event) {
            const checkbox = event.target.closest('.tasks-toggle-form input[type="checkbox"][name="status"]');
            if (!checkbox) {
                return;
            }

            const form = checkbox.closest('.tasks-toggle-form');
            const row = checkbox.closest('.tasks-list-item');
            if (!form || !row) {
                return;
            }

            if (form.dataset.busy === '1') {
                event.preventDefault();
                checkbox.checked = !checkbox.checked;
                return;
            }

            const ajaxUrl = form.dataset.ajaxUrl;
            const nextStatus = checkbox.checked;
            const prevStatus = !nextStatus;

            form.dataset.busy = '1';

            try {
                const body = new URLSearchParams();
                body.set('status', String(nextStatus));

                const response = await fetch(ajaxUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: body.toString(),
                    credentials: 'same-origin',
                });

                if (!response.ok) {
                    throw new Error('Toggle failed');
                }

                const data = await response.json();
                checkbox.checked = Boolean(data.status);

                const showCompleted = listLayout.dataset.showCompleted === '1';

                if (checkbox.checked !== showCompleted) {
                    row.remove();
                    ensureEmptyState(listLayout);
                    return;
                }

                const timeElement = row.querySelector('.tasks-item-time');
                if (timeElement && showCompleted) {
                    const formatted = formatDateTime(data.completed_at);
                    if (formatted) {
                        timeElement.textContent = formatted;
                    }
                }
            } catch (error) {
                checkbox.checked = prevStatus;
            } finally {
                delete form.dataset.busy;
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initTaskToggleAjax);
})();
