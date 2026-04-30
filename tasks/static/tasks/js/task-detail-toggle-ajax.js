(function () {
    function buildTasksRedirect(nextUrl, wasCompleted) {
        const raw = String(nextUrl || '').trim();
        const safe = raw.startsWith('/tasks/') ? raw : '/tasks/';
        const url = new URL(safe, window.location.origin);
        const sort = url.searchParams.get('sort') || 'deadline';

        if (wasCompleted) {
            url.searchParams.set('show', 'completed');
        } else {
            url.searchParams.delete('show');
        }
        url.searchParams.set('sort', sort);

        return url.pathname + '?' + url.searchParams.toString();
    }

    function initTaskDetailToggleAjax() {
        const form = document.querySelector('.tasks-detail-toggle-form');
        const ajax = window.AjaxUtils;
        if (!form || !ajax) {
            return;
        }

        const checkbox = form.querySelector('input[type="checkbox"][name="status"]');
        if (!checkbox) {
            return;
        }

        checkbox.addEventListener('change', async function () {
            if (form.dataset.busy === '1') {
                checkbox.checked = !checkbox.checked;
                return;
            }

            const previousChecked = !checkbox.checked;
            form.dataset.busy = '1';
            checkbox.disabled = true;

            try {
                const data = await ajax.requestJson(form.dataset.ajaxUrl || form.action, {
                    method: 'POST',
                    data: { status: String(checkbox.checked) },
                });
                checkbox.checked = Boolean(data.status);
                const nextInput = form.querySelector('input[name="next"]');
                const nextUrl = nextInput ? String(nextInput.value || '').trim() : '';
                const redirectUrl = buildTasksRedirect(nextUrl, previousChecked);
                window.location.assign(redirectUrl);
                return;
            } catch (error) {
                checkbox.checked = previousChecked;
                ajax.renderError(document.body, 'failed to update task');
            } finally {
                checkbox.disabled = false;
                delete form.dataset.busy;
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initTaskDetailToggleAjax);
})();
