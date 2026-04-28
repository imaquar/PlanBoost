(function () {
    function replaceIdInPath(template, id) {
        return template.replace('/0/', '/' + id + '/');
    }

    function ensureList(sectionElement, listClass) {
        let list = sectionElement.querySelector('.' + listClass);
        if (list) {
            return list;
        }

        list = document.createElement('ul');
        list.className = 'dashboard-list ' + listClass;
        sectionElement.appendChild(list);
        return list;
    }

    function renderEmpty(sectionElement, text) {
        const existingList = sectionElement.querySelector('.dashboard-list');
        if (existingList) {
            existingList.remove();
        }

        let empty = sectionElement.querySelector('.dashboard-empty');
        if (!empty) {
            empty = document.createElement('p');
            empty.className = 'dashboard-empty';
            sectionElement.appendChild(empty);
        }
        empty.textContent = text;
    }

    function clearEmpty(sectionElement) {
        const empty = sectionElement.querySelector('.dashboard-empty');
        if (empty) {
            empty.remove();
        }
    }

    function renderStats(sectionElement, data) {
        const todayValue = sectionElement.querySelector('#dashboard-today-value');
        if (todayValue) {
            todayValue.textContent = String(data.today ?? 0);
        }

        const chart = sectionElement.querySelector('#dashboard-last7-chart');
        if (!chart) {
            return;
        }

        const values = Array.isArray(data.last7) ? data.last7 : [];
        chart.replaceChildren();

        values.forEach(function (count) {
            const wrap = document.createElement('div');
            wrap.className = 'stats-bar-wrap';

            const bar = document.createElement('div');
            bar.className = 'stats-bar';
            bar.style.setProperty('--count', String(count));

            const label = document.createElement('div');
            label.className = 'stats-bar-value';
            label.textContent = String(count);

            wrap.append(bar, label);
            chart.appendChild(wrap);
        });
    }

    function renderUpcomingTasks(sectionElement, tasks, options) {
        if (!Array.isArray(tasks) || tasks.length === 0) {
            renderEmpty(sectionElement, 'no upcoming tasks');
            return;
        }

        clearEmpty(sectionElement);
        const list = ensureList(sectionElement, 'dashboard-tasks-list');
        list.replaceChildren();

        const ajax = window.AjaxUtils;
        const csrfToken = ajax ? ajax.getCsrfToken() : '';

        tasks.forEach(function (task) {
            const item = document.createElement('li');
            item.className = 'dashboard-task-item dashboard-task-card';

            const form = document.createElement('form');
            form.className = 'dashboard-task-toggle';
            form.method = 'post';
            form.action = replaceIdInPath(options.taskToggleTemplate, task.id);
            form.dataset.ajaxUrl = replaceIdInPath(options.taskToggleAjaxTemplate, task.id);

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;

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
            link.className = 'dashboard-task-link';
            link.href = replaceIdInPath(options.taskDetailTemplate, task.id);
            link.textContent = task.label || '';

            const deadline = document.createElement('span');
            deadline.className = 'dashboard-task-deadline';
            deadline.textContent = task.deadline_display || '';

            item.append(form, link, deadline);
            list.appendChild(item);
        });
    }

    function renderRecentNotes(sectionElement, notes, options) {
        if (!Array.isArray(notes) || notes.length === 0) {
            renderEmpty(sectionElement, 'no recent notes');
            return;
        }

        clearEmpty(sectionElement);
        const list = ensureList(sectionElement, 'dashboard-notes-list');
        list.replaceChildren();

        notes.forEach(function (note) {
            const item = document.createElement('li');
            item.className = 'dashboard-note-card';

            const link = document.createElement('a');
            link.className = 'dashboard-note-link';
            link.href = replaceIdInPath(options.noteDetailTemplate, note.id);
            link.textContent = note.label || '';

            const created = document.createElement('span');
            created.className = 'dashboard-note-created';
            created.textContent = note.created_at_display || '';

            item.append(link, created);
            list.appendChild(item);
        });
    }

    function initDashboardRefresh() {
        const root = document.querySelector('.dashboard-layout');
        const ajax = window.AjaxUtils;
        if (!root || !ajax) {
            return;
        }

        const apiUrl = root.dataset.statsApiUrl;
        const taskToggleTemplate = root.dataset.taskToggleTemplate;
        const taskToggleAjaxTemplate = root.dataset.taskToggleAjaxTemplate;
        const taskDetailTemplate = root.dataset.taskDetailTemplate;
        const noteDetailTemplate = root.dataset.noteDetailTemplate;

        if (!apiUrl || !taskToggleTemplate || !taskToggleAjaxTemplate || !taskDetailTemplate || !noteDetailTemplate) {
            return;
        }

        const statsSection = root.querySelector('.dashboard-stats-section');
        const tasksSection = root.querySelector('.dashboard-tasks-section');
        const notesSection = root.querySelector('.dashboard-notes-section');

        if (!statsSection || !tasksSection || !notesSection) {
            return;
        }

        let busy = false;

        async function refresh(options) {
            const opts = options || {};
            if (busy) {
                return;
            }

            busy = true;
            if (!opts.silent) {
                ajax.renderLoading(root, 'refreshing dashboard...');
            }

            try {
                const data = await ajax.requestJson(apiUrl, { method: 'GET', csrf: false });
                renderStats(statsSection, data);
                renderUpcomingTasks(tasksSection, data.upcoming_tasks, {
                    taskToggleTemplate: taskToggleTemplate,
                    taskToggleAjaxTemplate: taskToggleAjaxTemplate,
                    taskDetailTemplate: taskDetailTemplate,
                });
                renderRecentNotes(notesSection, data.recent_notes, {
                    noteDetailTemplate: noteDetailTemplate,
                });
                ajax.clearStatus(root);
            } catch (error) {
                ajax.renderError(root, 'failed to refresh dashboard');
            } finally {
                busy = false;
            }
        }

        refresh();
        setInterval(refresh, 60000);

        tasksSection.addEventListener('change', async function (event) {
            const checkbox = event.target;
            if (!(checkbox instanceof HTMLInputElement) || checkbox.type !== 'checkbox') {
                return;
            }

            const form = checkbox.closest('.dashboard-task-toggle');
            if (!form || !form.dataset.ajaxUrl) {
                return;
            }

            const previousChecked = !checkbox.checked;
            checkbox.disabled = true;

            try {
                await ajax.requestJson(form.dataset.ajaxUrl, {
                    method: 'POST',
                    data: { status: checkbox.checked ? 'true' : 'false' },
                });
                await refresh({ silent: true });
            } catch (error) {
                checkbox.checked = previousChecked;
                ajax.renderError(root, 'failed to update task');
            } finally {
                checkbox.disabled = false;
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initDashboardRefresh);
})();
