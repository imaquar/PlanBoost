(function () {
    function getCookie(name) {
        const escapedName = name.replace(/[-.]/g, '\\$&');
        const match = document.cookie.match(new RegExp('(?:^|; )' + escapedName + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : '';
    }

    function replaceIdInPath(template, id) {
        return template.replace('/0/', '/' + id + '/');
    }

    function closeSortMenu() {
        const sortMenu = document.querySelector('.tasks-sort-menu');
        const sortTrigger = document.querySelector('.tasks-sort-trigger');
        if (!sortMenu || !sortTrigger) {
            return;
        }

        sortMenu.classList.remove('is-open');
        sortTrigger.setAttribute('aria-expanded', 'false');
    }

    function setActiveSort(sort) {
        const links = document.querySelectorAll('.tasks-sort-link');
        links.forEach(function (link) {
            const linkUrl = new URL(link.href, window.location.origin);
            const linkSort = linkUrl.searchParams.get('sort') || 'deadline';
            link.classList.toggle('is-active', linkSort === sort);
        });
    }

    function ensureListNode(listLayout) {
        let list = listLayout.querySelector('.tasks-list');
        if (list) {
            return list;
        }

        list = document.createElement('ul');
        list.className = 'tasks-list';

        const actions = listLayout.querySelector('.tasks-actions');
        if (actions) {
            listLayout.insertBefore(list, actions);
        } else {
            listLayout.appendChild(list);
        }

        return list;
    }

    function renderEmptyState(listLayout, isEmpty) {
        const existingEmpty = listLayout.querySelector('.tasks-empty');

        if (!isEmpty) {
            if (existingEmpty) {
                existingEmpty.remove();
            }
            return;
        }

        if (existingEmpty) {
            existingEmpty.textContent = 'no tasks yet';
            return;
        }

        const empty = document.createElement('p');
        empty.className = 'tasks-empty';
        empty.textContent = 'no tasks yet';

        const actions = listLayout.querySelector('.tasks-actions');
        if (actions) {
            listLayout.insertBefore(empty, actions);
        } else {
            listLayout.appendChild(empty);
        }
    }

    function buildTaskRow(task, options) {
        const row = document.createElement('li');
        row.className = 'tasks-list-item';

        const toggleUrl = replaceIdInPath(options.toggleTemplate, task.id);
        const toggleAjaxUrl = replaceIdInPath(options.toggleAjaxTemplate, task.id);
        const detailUrl = replaceIdInPath(options.taskDetailTemplate, task.id);

        const form = document.createElement('form');
        form.className = 'tasks-toggle-form';
        form.method = 'post';
        form.action = toggleUrl;
        form.dataset.ajaxUrl = toggleAjaxUrl;

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = options.csrfToken;

        const nextInput = document.createElement('input');
        nextInput.type = 'hidden';
        nextInput.name = 'next';
        nextInput.value = window.location.pathname + window.location.search;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'status';
        checkbox.checked = Boolean(task.status);

        form.append(csrfInput, nextInput, checkbox);

        const link = document.createElement('a');
        link.className = 'tasks-item-link';
        link.href = detailUrl + '?next=' + encodeURIComponent(window.location.pathname + window.location.search);
        link.textContent = task.label;

        const time = document.createElement('span');
        time.className = 'tasks-item-time';
        time.textContent = options.showCompleted ? (task.completed_at_display || '') : (task.deadline_display || '');

        row.append(form, link, time);
        return row;
    }

    function renderTasks(listLayout, data, options) {
        const list = ensureListNode(listLayout);
        list.replaceChildren();

        if (!Array.isArray(data.tasks) || data.tasks.length === 0) {
            list.remove();
            renderEmptyState(listLayout, true);
            return;
        }

        renderEmptyState(listLayout, false);
        data.tasks.forEach(function (task) {
            list.appendChild(buildTaskRow(task, options));
        });
    }

    function initTaskSortAjax() {
        const listLayout = document.querySelector('.tasks-list-layout');
        if (!listLayout) {
            return;
        }

        const apiUrl = listLayout.dataset.listApiUrl;
        const toggleTemplate = listLayout.dataset.toggleTemplate;
        const toggleAjaxTemplate = listLayout.dataset.toggleAjaxTemplate;
        const taskDetailTemplate = listLayout.dataset.taskDetailTemplate;
        const csrfToken = getCookie('csrftoken');

        if (!apiUrl || !toggleTemplate || !toggleAjaxTemplate || !taskDetailTemplate) {
            return;
        }

        document.addEventListener('click', async function (event) {
            const link = event.target.closest('.tasks-sort-link');
            if (!link) {
                return;
            }

            event.preventDefault();

            try {
                const targetUrl = new URL(link.href, window.location.origin);
                const sort = targetUrl.searchParams.get('sort') || 'deadline';
                const showCompleted = targetUrl.searchParams.get('show') === 'completed';

                const fetchUrl = new URL(apiUrl, window.location.origin);
                fetchUrl.searchParams.set('sort', sort);
                if (showCompleted) {
                    fetchUrl.searchParams.set('show', 'completed');
                }

                const response = await fetch(fetchUrl.toString(), {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin',
                });

                if (!response.ok) {
                    throw new Error('Sort request failed');
                }

                const data = await response.json();
                listLayout.dataset.showCompleted = data.show_completed ? '1' : '0';

                renderTasks(listLayout, data, {
                    csrfToken: csrfToken,
                    showCompleted: Boolean(data.show_completed),
                    toggleTemplate: toggleTemplate,
                    toggleAjaxTemplate: toggleAjaxTemplate,
                    taskDetailTemplate: taskDetailTemplate,
                });

                setActiveSort(data.sort || sort);
                closeSortMenu();
                history.replaceState(null, '', targetUrl.pathname + targetUrl.search);
            } catch (error) {
                window.location.assign(link.href);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initTaskSortAjax);
})();
