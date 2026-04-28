(function () {
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

    function setActiveSort(sort) {
        const links = document.querySelectorAll('.tasks-sort-link');
        links.forEach(function (link) {
            const linkUrl = new URL(link.href, window.location.origin);
            const linkSort = linkUrl.searchParams.get('sort') || 'deadline';
            link.classList.toggle('is-active', linkSort === sort);
        });
    }

    function setActiveFilter(showCompleted) {
        const links = document.querySelectorAll('.tasks-switch-link');
        links.forEach(function (link) {
            const linkUrl = new URL(link.href, window.location.origin);
            const linkShowCompleted = linkUrl.searchParams.get('show') === 'completed';
            link.classList.toggle('is-active', linkShowCompleted === showCompleted);
        });
    }

    function refreshControlUrls(listLayout) {
        const sort = listLayout.dataset.currentSort || 'deadline';
        const showCompleted = listLayout.dataset.showCompleted === '1';
        const basePath = window.location.pathname;

        const filterLinks = document.querySelectorAll('.tasks-switch-link');
        filterLinks.forEach(function (link) {
            const target = new URL(link.href, window.location.origin);
            const targetShowCompleted = target.searchParams.get('show') === 'completed';
            const params = new URLSearchParams();
            if (targetShowCompleted) {
                params.set('show', 'completed');
            }
            params.set('sort', sort);
            link.href = basePath + '?' + params.toString();
        });

        const sortLinks = document.querySelectorAll('.tasks-sort-link');
        sortLinks.forEach(function (link) {
            const target = new URL(link.href, window.location.origin);
            const targetSort = target.searchParams.get('sort') || 'deadline';
            const params = new URLSearchParams();
            if (showCompleted) {
                params.set('show', 'completed');
            }
            params.set('sort', targetSort);
            link.href = basePath + '?' + params.toString();
        });
    }

    async function fetchAndRender(listLayout, endpointUrl, sort, showCompleted, options) {
        const ajax = window.AjaxUtils;
        const fetchUrl = new URL(endpointUrl, window.location.origin);
        fetchUrl.searchParams.set('sort', sort || 'deadline');
        if (showCompleted) {
            fetchUrl.searchParams.set('show', 'completed');
        }

        const data = await ajax.requestJson(fetchUrl.toString(), { method: 'GET', csrf: false });

        listLayout.dataset.showCompleted = data.show_completed ? '1' : '0';
        listLayout.dataset.currentSort = data.sort || sort || 'deadline';

        renderTasks(listLayout, data, {
            csrfToken: options.csrfToken,
            showCompleted: Boolean(data.show_completed),
            toggleTemplate: options.toggleTemplate,
            toggleAjaxTemplate: options.toggleAjaxTemplate,
            taskDetailTemplate: options.taskDetailTemplate,
        });

        setActiveSort(listLayout.dataset.currentSort);
        setActiveFilter(listLayout.dataset.showCompleted === '1');
        refreshControlUrls(listLayout);

        closeSortMenu();

        const params = new URLSearchParams();
        if (listLayout.dataset.showCompleted === '1') {
            params.set('show', 'completed');
        }
        params.set('sort', listLayout.dataset.currentSort);
        history.replaceState(null, '', window.location.pathname + '?' + params.toString());
    }

    function initTaskSortFilterAjax() {
        const listLayout = document.querySelector('.tasks-list-layout');
        const ajax = window.AjaxUtils;
        if (!listLayout || !ajax) {
            return;
        }

        const listApiUrl = listLayout.dataset.listApiUrl;
        const filterApiUrl = listLayout.dataset.filterApiUrl;
        const toggleTemplate = listLayout.dataset.toggleTemplate;
        const toggleAjaxTemplate = listLayout.dataset.toggleAjaxTemplate;
        const taskDetailTemplate = listLayout.dataset.taskDetailTemplate;
        const csrfToken = ajax.getCsrfToken();

        if (!listApiUrl || !filterApiUrl || !toggleTemplate || !toggleAjaxTemplate || !taskDetailTemplate) {
            return;
        }

        document.addEventListener('click', async function (event) {
            const sortLink = event.target.closest('.tasks-sort-link');
            const filterLink = event.target.closest('.tasks-switch-link');

            if (!sortLink && !filterLink) {
                return;
            }

            event.preventDefault();

            const isSortAction = Boolean(sortLink);
            const sourceLink = sortLink || filterLink;

            try {
                const targetUrl = new URL(sourceLink.href, window.location.origin);
                const sort = targetUrl.searchParams.get('sort') || (listLayout.dataset.currentSort || 'deadline');
                const showCompleted = targetUrl.searchParams.get('show') === 'completed';

                await fetchAndRender(
                    listLayout,
                    isSortAction ? listApiUrl : filterApiUrl,
                    sort,
                    showCompleted,
                    {
                        csrfToken: csrfToken,
                        toggleTemplate: toggleTemplate,
                        toggleAjaxTemplate: toggleAjaxTemplate,
                        taskDetailTemplate: taskDetailTemplate,
                    }
                );
            } catch (error) {
                ajax.renderError(listLayout, 'network error, reloading...');
                window.location.assign(sourceLink.href);
            }
        });

        refreshControlUrls(listLayout);
    }

    document.addEventListener('DOMContentLoaded', initTaskSortFilterAjax);
})();
